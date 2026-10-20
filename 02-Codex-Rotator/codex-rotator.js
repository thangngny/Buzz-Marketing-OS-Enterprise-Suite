/**
 * Shared Codex Profile Rotator with Multi-Tier Model Architecture
 * Manages load-balancing, auto-failover, and intelligent tier routing
 * across multiple OpenAI Codex accounts.
 *
 * PATH-AGNOSTIC: Automatically resolves user profile directory on any Windows/Unix machine.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const USER_HOME = process.env.USERPROFILE || process.env.HOME || os.homedir();
const PROFILES_DIR = process.env.CODEX_PROFILES_DIR || path.join(USER_HOME, '.codex', 'profiles');
const STATE_FILE = path.join(PROFILES_DIR, '.rotator-state.json');

const DEFAULT_BASE_ACCOUNTS = ['account-1', 'account-2', 'account-3'];

function getBaseAccount(profileName) {
  if (!profileName) {
    const available = getAvailableBaseAccounts();
    return available.length > 0 ? available[0] : 'account-1';
  }
  return profileName.replace(/-(light|heavy|balanced)$/, '');
}

function getAvailableBaseAccounts() {
  if (!fs.existsSync(PROFILES_DIR)) return DEFAULT_BASE_ACCOUNTS;
  try {
    const dirents = fs.readdirSync(PROFILES_DIR, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory() && 
        !dirent.name.startsWith('.') && 
        !dirent.name.endsWith('-light') && 
        !dirent.name.endsWith('-heavy') && 
        !dirent.name.endsWith('-balanced') && 
        dirent.name !== 'archive' && 
        dirent.name !== 'archive_profiles');
    
    // Ưu tiên các profile đã đăng nhập (có auth.json)
    const withAuth = dirents
      .filter(dirent => fs.existsSync(path.join(PROFILES_DIR, dirent.name, 'auth.json')))
      .map(dirent => dirent.name);
    if (withAuth.length > 0) return withAuth;

    // Nếu chưa đăng nhập profile nào, trả về tất cả các thư mục profile đã tạo
    const allDirs = dirents.map(dirent => dirent.name);
    if (allDirs.length > 0) return allDirs;
  } catch (e) {}
  return DEFAULT_BASE_ACCOUNTS;
}

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (e) {}
  return { last_index: -1, cooldowns: {} };
}

function saveState(state) {
  try {
    if (!fs.existsSync(PROFILES_DIR)) {
      fs.mkdirSync(PROFILES_DIR, { recursive: true });
    }
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  } catch (e) {}
}

function cleanExpiredCooldowns(state) {
  const now = Date.now();
  let changed = false;
  if (!state.cooldowns) state.cooldowns = {};
  for (const [name, until] of Object.entries(state.cooldowns)) {
    if (now >= until) {
      delete state.cooldowns[name];
      changed = true;
    }
  }
  if (changed) saveState(state);
}

function markCooldown(profileName, minutesOrTimestamp = 30) {
  const baseName = getBaseAccount(profileName);
  const state = loadState();
  if (!state.cooldowns) state.cooldowns = {};
  if (typeof minutesOrTimestamp === 'number' && minutesOrTimestamp > 1e11) {
    state.cooldowns[baseName] = minutesOrTimestamp;
  } else {
    state.cooldowns[baseName] = Date.now() + (minutesOrTimestamp * 60 * 1000);
  }
  saveState(state);
}

function removeCooldown(profileName) {
  const baseName = getBaseAccount(profileName);
  const state = loadState();
  if (state.cooldowns && state.cooldowns[baseName]) {
    delete state.cooldowns[baseName];
    saveState(state);
  }
}

/**
 * Returns the next profile name according to the desired tier ('light', 'balanced', 'heavy')
 * or a specific profile request.
 */
function getNextProfile(tierOrSpecific = 'light') {
  let tier = 'light';
  let specific = null;

  if (['light', 'balanced', 'heavy'].includes(tierOrSpecific)) {
    tier = tierOrSpecific;
  } else if (tierOrSpecific) {
    specific = tierOrSpecific;
  }

  const baseAccounts = getAvailableBaseAccounts();
  const baseProfiles = baseAccounts.filter(name => fs.existsSync(path.join(PROFILES_DIR, name, 'auth.json')));
  
  if (baseProfiles.length === 0) {
    // Return first configured or default account even if auth.json not yet created
    return baseAccounts[0] || 'default';
  }

  if (specific) {
    return specific;
  }

  const state = loadState();
  cleanExpiredCooldowns(state);

  const now = Date.now();
  const healthy = baseProfiles.filter(p => !state.cooldowns[p] || now >= state.cooldowns[p]);
  const pool = healthy.length > 0 ? healthy : baseProfiles;

  state.last_index = (state.last_index + 1) % pool.length;
  const chosenBase = pool[state.last_index];
  saveState(state);

  if (tier === 'light') {
    const lightPath = path.join(PROFILES_DIR, `${chosenBase}-light`);
    if (fs.existsSync(lightPath)) return `${chosenBase}-light`;
  }
  if (tier === 'heavy') {
    const heavyPath = path.join(PROFILES_DIR, `${chosenBase}-heavy`);
    if (fs.existsSync(heavyPath)) return `${chosenBase}-heavy`;
  }

  return chosenBase;
}

function getProfileHome(profileName) {
  return path.join(PROFILES_DIR, profileName);
}

function getStatus() {
  const state = loadState();
  cleanExpiredCooldowns(state);
  const now = Date.now();
  const baseAccounts = getAvailableBaseAccounts();

  return baseAccounts.map(name => {
    const inCooldown = state.cooldowns && state.cooldowns[name] && state.cooldowns[name] > now;
    const remainingMin = inCooldown ? Math.ceil((state.cooldowns[name] - now) / 60000) : 0;
    const hasAuth = fs.existsSync(path.join(PROFILES_DIR, name, 'auth.json'));
    return {
      account: name,
      status: !hasAuth ? 'CHƯA ĐĂNG NHẬP (NO AUTH)' : (inCooldown ? `COOLDOWN (${remainingMin}m remaining)` : 'READY'),
      tiers: {
        light: `gpt-5.6-luna [low] -> ${name}-light`,
        balanced: `gpt-5.6-sol [medium] -> ${name}`,
        heavy: `gpt-6-luna [medium] -> ${name}-heavy`
      }
    };
  });
}

function hasHealthyAccounts() {
  const baseAccounts = getAvailableBaseAccounts();
  const baseProfiles = baseAccounts.filter(name => fs.existsSync(path.join(PROFILES_DIR, name, 'auth.json')));
  if (baseProfiles.length === 0) return false;
  const state = loadState();
  cleanExpiredCooldowns(state);
  const now = Date.now();
  const healthy = baseProfiles.filter(p => !state.cooldowns || !state.cooldowns[p] || now >= state.cooldowns[p]);
  return healthy.length > 0;
}

module.exports = {
  PROFILES_DIR,
  DEFAULT_BASE_ACCOUNTS,
  getAvailableBaseAccounts,
  getBaseAccount,
  getNextProfile,
  getProfileHome,
  markCooldown,
  removeCooldown,
  getStatus,
  loadState,
  hasHealthyAccounts
};
