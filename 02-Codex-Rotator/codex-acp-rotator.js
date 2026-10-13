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
  path.join(USER_HOME, '.codex', 'scripts', 'codex-rotator.js'),
  'C:\\Users\\Admin\\.codex\\scripts\\codex-rotator.js'
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

const chosenProfile = (rotator && rotator.getNextProfile(tier)) || 'mkt';
const profileHome = rotator ? rotator.getProfileHome(chosenProfile) : path.join(USER_HOME, '.codex', 'profiles', chosenProfile);

const spawnEnv = Object.assign({}, process.env, {
  CODEX_HOME: profileHome,
  BUZZ_PRIVATE_KEY: process.env.BUZZ_PRIVATE_KEY || '',
  BUZZ_RELAY: process.env.BUZZ_RELAY || ''
});

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

child.stdout.on('data', (chunk) => {
  process.stdout.write(chunk);
});

child.stderr.on('data', (chunk) => {
  process.stderr.write(chunk);
  logDebug('STDERR', chunk.toString());
});

child.on('exit', (code) => {
  logDebug('EXIT', { code });
  process.exit(code || 0);
});
