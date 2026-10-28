#!/usr/bin/env node
/**
 * Codex ACP Rotator Wrapper for Buzz Agents
 * Assigns each Buzz agent invocation to an isolated profile from the multi-account pool
 * so quota is shared and balanced across accounts.
 *
 * PATH-AGNOSTIC: Automatically adapts to any user home directory on Windows/Unix.
 */
const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const readline = require('readline');

const USER_HOME = process.env.USERPROFILE || process.env.HOME || os.homedir();
const APPDATA_DIR = process.env.APPDATA || path.join(USER_HOME, 'AppData', 'Roaming');

// Resolve rotator engine
let rotator;
const candidateRotatorPaths = [
  path.join(__dirname, 'codex-rotator.js'),
  path.join(USER_HOME, '.codex', 'scripts', 'codex-rotator.js')
];

for (const p of candidateRotatorPaths) {
  if (fs.existsSync(p)) {
    try {
      rotator = require(p);
      break;
    } catch (e) {}
  }
}

const rawArgs = process.argv.slice(2);
let tier = 'light';
const tierIdx = rawArgs.indexOf('--tier');
if (tierIdx !== -1 && rawArgs[tierIdx + 1]) {
  tier = rawArgs[tierIdx + 1];
  rawArgs.splice(tierIdx, 2);
}

const fallbackProfile = (rotator && typeof rotator.getAvailableBaseAccounts === 'function' && rotator.getAvailableBaseAccounts()[0]) || 'account-1';
const chosenProfile = (rotator && rotator.getNextProfile(tier)) || fallbackProfile;
const profileHome = rotator ? rotator.getProfileHome(chosenProfile) : path.join(USER_HOME, '.codex', 'profiles', chosenProfile);

// Auto-sync fresh auth.json from base account if tier sub-profile is chosen
try {
  const chosenBase = (rotator && typeof rotator.getBaseAccount === 'function')
    ? rotator.getBaseAccount(chosenProfile)
    : chosenProfile.replace(/-(light|heavy|balanced)$/, '');
  const baseAuth = path.join(USER_HOME, '.codex', 'profiles', chosenBase, 'auth.json');
  const targetAuth = path.join(profileHome, 'auth.json');
  if (baseAuth !== targetAuth && fs.existsSync(baseAuth)) {
    fs.copyFileSync(baseAuth, targetAuth);
  }
} catch (e) {}

const spawnEnv = Object.assign({}, process.env, {
  CODEX_HOME: profileHome,
  BUZZ_PRIVATE_KEY: process.env.BUZZ_PRIVATE_KEY || '',
  BUZZ_RELAY: process.env.BUZZ_RELAY || '',
  BUZZ_ACP_PERMISSION_MODE: 'bypass-permissions',
  BUZZ_ACP_RESPOND_TO: 'anyone',
  OPENAI_APPROVAL_POLICY: 'never',
  CODEX_APPROVAL_POLICY: 'never'
});

// Ensure permission bypass & anyone response modes are always passed
if (!rawArgs.includes('--permission-mode')) {
  rawArgs.push('--permission-mode', 'bypass-permissions');
}
if (!rawArgs.includes('--respond-to')) {
  rawArgs.push('--respond-to', 'anyone');
}

// Locate codex-acp binary
function findCodexAcp() {
  if (process.env.CODEX_ACP_BIN && fs.existsSync(process.env.CODEX_ACP_BIN)) {
    return process.env.CODEX_ACP_BIN;
  }
  const appDataBuzzTools = path.join(APPDATA_DIR, 'Buzz', 'node-tools');
  const candidates = [
    path.join(appDataBuzzTools, 'codex-acp.exe'),
    path.join(appDataBuzzTools, 'codex-acp.cmd'),
    path.join(appDataBuzzTools, 'node_modules', '.bin', 'codex-acp.cmd'),
    'codex-acp.exe',
    'codex-acp.cmd',
    'codex-acp'
  ];

  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  // Fallback to checking PATH
  try {
    const whichCmd = process.platform === 'win32' ? 'where.exe codex-acp' : 'which codex-acp';
    const found = execSync(whichCmd, { encoding: 'utf8' }).trim().split('\n')[0].trim();
    if (found && fs.existsSync(found)) return found;
  } catch (e) {}

  return 'codex-acp';
}

const originalCmd = findCodexAcp();
const args = rawArgs;

// Spawn codex-acp with piped stdio so we can intercept and normalize protocol messages
const isCmd = originalCmd.endsWith('.cmd') || originalCmd.endsWith('.bat');
const child = spawn(originalCmd, args, {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: spawnEnv,
  shell: isCmd,
  windowsHide: true
});

const debugLogDir = path.join(USER_HOME, '.codex');
if (!fs.existsSync(debugLogDir)) {
  try { fs.mkdirSync(debugLogDir, { recursive: true }); } catch (e) {}
}
const debugLogPath = path.join(debugLogDir, 'rotator-debug.log');

function logDebug(prefix, data) {
  try {
    fs.appendFileSync(debugLogPath, `[${new Date().toISOString()}] [PID ${process.pid}] ${prefix}: ${typeof data === 'string' ? data : JSON.stringify(data)}\n`);
  } catch (e) {}
}

logDebug('INIT', { profile: chosenProfile, home: profileHome, binary: originalCmd, args });

// Read incoming JSON-RPC from parent (buzz-acp) line by line
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  if (!line || !line.trim()) return;
  try {
    const parsed = JSON.parse(line);
    // Normalize session/new parameters
    if (parsed.method === 'session/new' && parsed.params) {
      if (!parsed.params.mcpServers) {
        parsed.params.mcpServers = [];
      }
    }
    const modified = JSON.stringify(parsed);
    child.stdin.write(modified + '\n');
  } catch (e) {
    child.stdin.write(line + '\n');
  }
});

let failoverTriggered = false;

function checkQuotaDepleted(text) {
  if (!text) return false;
  return (
    text.includes('usageLimitExceeded') ||
    text.includes('usage_limit_exceeded') ||
    text.includes('workspace_member_credits_depleted') ||
    text.includes('Your workspace is out of credits') ||
    text.includes('rate_limit_reached_type') ||
    (text.includes('"code":-32000') && text.includes('Authentication required')) ||
    text.includes('handshake transport error http 401')
  );
}

function scanLatestSessionForQuotaError(dir) {
  try {
    const sessionsDir = path.join(dir, 'sessions');
    if (!fs.existsSync(sessionsDir)) return false;
    const now = new Date();
    const y = String(now.getFullYear());
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const dayDir = path.join(sessionsDir, y, m, d);
    if (!fs.existsSync(dayDir)) return false;
    const files = fs.readdirSync(dayDir).filter(f => f.endsWith('.jsonl')).map(f => path.join(dayDir, f));
    if (files.length === 0) return false;
    files.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    const latestFile = files[0];
    const stat = fs.statSync(latestFile);
    if (Date.now() - stat.mtimeMs < 180000) {
      const content = fs.readFileSync(latestFile, 'utf8');
      const tail = content.slice(-8192);
      return checkQuotaDepleted(tail);
    }
  } catch (e) {}
  return false;
}

function handleQuotaDepletion(sourceText) {
  if (failoverTriggered) return;
  failoverTriggered = true;

  logDebug('QUOTA_DEPLETED_DETECTED', { profile: chosenProfile, preview: (sourceText || '').slice(0, 200) });

  if (rotator && typeof rotator.markCooldown === 'function') {
    rotator.markCooldown(chosenProfile, 300); // 300 minutes = 5 hours
  }

  const canFailover = rotator && typeof rotator.hasHealthyAccounts === 'function'
    ? rotator.hasHealthyAccounts()
    : true;

  if (canFailover) {
    logDebug('FAILOVER_ACTION', {
      action: 'EXIT_FOR_BUZZ_RESPAWN',
      profileExhausted: chosenProfile,
      message: 'Terminating agent process so buzz-acp requeues and respawns on next healthy account.'
    });
    try {
      child.kill();
    } catch (e) {}
    process.exit(1);
  } else {
    logDebug('ALL_ACCOUNTS_EXHAUSTED', {
      profileExhausted: chosenProfile,
      message: 'All accounts in pool have exhausted quota. Allowing error to propagate to channel.'
    });
  }
}

child.stdout.on('data', (chunk) => {
  process.stdout.write(chunk);
  const str = chunk.toString();
  if (checkQuotaDepleted(str)) {
    handleQuotaDepletion(str);
  }
});

child.stderr.on('data', (chunk) => {
  process.stderr.write(chunk);
  const str = chunk.toString();
  logDebug('STDERR', str);
  if (checkQuotaDepleted(str)) {
    handleQuotaDepletion(str);
  } else if (str.includes('RequestError: Internal error')) {
    if (scanLatestSessionForQuotaError(profileHome)) {
      handleQuotaDepletion('scanLatestSessionForQuotaError: detected quota error in session rollout');
    }
  }
});

child.on('exit', (code) => {
  logDebug('EXIT', { code });
  process.exit(code || 0);
});
