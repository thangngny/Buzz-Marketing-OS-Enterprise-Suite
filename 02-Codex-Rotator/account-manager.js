#!/usr/bin/env node
/**
 * Codex Account Manager & Multi-Account Rotation Hub
 * Quản lý kết nối nhiều tài khoản ChatGPT Codex độc lập và kích hoạt xoay tua tự động.
 *
 * PATH-AGNOSTIC: Tự động nhận diện thư mục User trên mọi máy Windows/Unix.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync, spawn } = require('child_process');
const readline = require('readline');

const USER_HOME = process.env.USERPROFILE || process.env.HOME || os.homedir();
const PROFILES_DIR = process.env.CODEX_PROFILES_DIR || path.join(USER_HOME, '.codex', 'profiles');
const SCRIPTS_DIR = process.env.CODEX_SCRIPTS_DIR || path.join(USER_HOME, '.codex', 'scripts');

let rotator;
try {
  rotator = require(path.join(__dirname, 'codex-rotator.js'));
} catch (e) {
  try {
    rotator = require(path.join(SCRIPTS_DIR, 'codex-rotator.js'));
  } catch (err) {}
}

function ensureProfileConfig(profileName) {
  const profileDir = path.join(PROFILES_DIR, profileName);
  if (!fs.existsSync(profileDir)) {
    fs.mkdirSync(profileDir, { recursive: true });
  }
  const configDest = path.join(profileDir, 'config.toml');
  if (!fs.existsSync(configDest)) {
    const templateConfig = path.join(__dirname, 'profiles_template', 'config.toml');
    if (fs.existsSync(templateConfig)) {
      try {
        fs.copyFileSync(templateConfig, configDest);
      } catch (e) {}
    } else {
      try {
        fs.writeFileSync(configDest, '# Codex profile config\nmodel = "gpt-5.6-luna"\n', 'utf8');
      } catch (e) {}
    }
  }
}

function getProfileDetails(profileName) {
  const profilePath = path.join(PROFILES_DIR, profileName);
  const authPath = path.join(profilePath, 'auth.json');
  
  if (!fs.existsSync(authPath)) {
    return { name: profileName, status: 'CHƯA ĐĂNG NHẬP', email: '---', plan: '---' };
  }

  try {
    const auth = JSON.parse(fs.readFileSync(authPath, 'utf8'));
    let email = '---';
    if (auth.tokens && auth.tokens.id_token) {
      const parts = auth.tokens.id_token.split('.');
      if (parts.length > 1) {
        const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString('utf8'));
        email = payload.email || email;
      }
    }
    
    let isCooldown = false;
    let statText = 'ĐÃ KẾT NỐI (READY)';
    if (rotator && typeof rotator.getStatus === 'function') {
      const statusList = rotator.getStatus();
      const stat = statusList.find(s => s.account === profileName);
      if (stat && stat.status.startsWith('COOLDOWN')) {
        isCooldown = true;
        statText = stat.status;
      }
    }

    return {
      name: profileName,
      status: statText,
      email: email,
      path: profilePath
    };
  } catch (e) {
    return { name: profileName, status: 'LỖI FILE AUTH', email: '---' };
  }
}

function listAllProfiles() {
  const starterProfiles = ['account-1', 'account-2', 'account-3'];
  let existing = [];
  try {
    if (fs.existsSync(PROFILES_DIR)) {
      existing = fs.readdirSync(PROFILES_DIR, { withFileTypes: true })
        .filter(d => d.isDirectory() && !d.name.startsWith('.') && !d.name.includes('-') && d.name !== 'archive' && d.name !== 'archive_profiles')
        .map(d => d.name);
    }
  } catch (e) {}
  
  const allNames = existing.length > 0 ? existing : starterProfiles;
  return allNames.map(name => getProfileDetails(name));
}

function printStatusTable(list) {
  console.log('\n========================================================================================');
  console.log('              TRẠNG THÁI CÁC TÀI KHOẢN CHATGPT CODEX ĐANG KẾT NỐI');
  console.log('========================================================================================');
  console.log(' STT | Tên Profile     | Email Đăng Nhập                  | Tình Trạng');
  console.log('-----+-----------------+----------------------------------+-----------------------------');
  list.forEach((p, idx) => {
    const num = ` [${idx + 1}]`.padEnd(5);
    const name = ` ${p.name}`.padEnd(17);
    const email = ` ${p.email}`.padEnd(34);
    const status = ` ${p.status}`;
    console.log(`${num}|${name}|${email}|${status}`);
  });
  console.log('========================================================================================\n');
}

function showMenu(list) {
  printStatusTable(list);
  console.log('CÁC TÙY CHỌN THAO TÁC:');
  console.log('  [A] WIZARD LIÊN HOÀN: Đăng nhập lần lượt tất cả tài khoản trong 1 lần duy nhất');
  console.log('  --------------------------------------------------------------------------------------');
  list.forEach((p, idx) => {
    console.log(`  [${idx + 1}] Đăng nhập riêng Tài khoản ${idx + 1} (${p.name})`);
  });
  console.log('  [+] Thêm một tài khoản mới khác (Tự đặt tên)');
  console.log('  [R] Kiểm tra và xoay tua ngay (Test Rotator)');
  console.log('  [0] Thoát');
  console.log('----------------------------------------------------------------------------------------');
}

function loginProfile(profileName, callback) {
  ensureProfileConfig(profileName);
  const profileDir = path.join(PROFILES_DIR, profileName);

  console.log(`\n========================================================================================`);
  console.log(` [*] ĐANG KHỞI TẠO LIÊN KẾT CHO: ${profileName.toUpperCase()}`);
  console.log(` Thư mục lưu trữ độc lập: ${profileDir}`);
  console.log(`========================================================================================`);
  console.log(`[*] Đang mở trang web: https://auth.openai.com/codex/device`);
  console.log(`[*] Bạn hãy đăng nhập đúng tài khoản muốn dùng trên trình duyệt và nhập mã bên dưới:`);
  console.log(`----------------------------------------------------------------------------------------\n`);

  try {
    if (process.platform === 'win32') {
      spawn('cmd.exe', ['/c', 'start', 'https://auth.openai.com/codex/device'], { detached: true, stdio: 'ignore' });
    }
  } catch (e) {}

  const env = Object.assign({}, process.env, { CODEX_HOME: profileDir });
  spawnSync('codex', ['login', '--device-auth'], {
    env,
    stdio: 'inherit',
    shell: true
  });

  const authPath = path.join(profileDir, 'auth.json');
  if (fs.existsSync(authPath)) {
    if (rotator && typeof rotator.removeCooldown === 'function') {
      rotator.removeCooldown(profileName);
    }
    console.log(`\n========================================================================================`);
    console.log(`  ✅ ĐÃ KẾT NỐI THÀNH CÔNG: ${profileName}!`);
    console.log(`  File xác thực đã được lưu vĩnh viễn vào profile riêng.`);
    console.log(`========================================================================================\n`);
  } else {
    console.log(`\n[!] Chưa phát hiện file xác thực cho ${profileName}. Bạn có thể thử lại sau.`);
  }

  if (callback) callback();
}

function runInteractive() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  function promptMenu() {
    const list = listAllProfiles();
    showMenu(list);
    rl.question('Nhập lựa chọn của bạn: ', (answer) => {
      const choice = answer.trim().toUpperCase();
      if (choice === '0') {
        console.log('Đã thoát trình quản lý tài khoản.');
        rl.close();
        process.exit(0);
      } else if (choice === 'A') {
        const unauth = list.filter(p => !p.status.includes('ĐÃ KẾT NỐI'));
        const targets = unauth.length > 0 ? unauth : list;
        console.log(`\n>>> Bắt đầu tiến trình liên hoàn qua ${targets.length} tài khoản <<<`);
        
        function step(index) {
          if (index >= targets.length) {
            console.log('\n✅ Hoàn tất tiến trình liên hoàn!');
            promptMenu();
            return;
          }
          console.log(`\n>>> [${index + 1}/${targets.length}] Đang đăng nhập: ${targets[index].name} <<<`);
          loginProfile(targets[index].name, () => step(index + 1));
        }
        step(0);
      } else if (choice === '+' || choice === `${list.length + 1}`) {
        rl.question('Nhập tên profile mới (VD: marketing-01): ', (customName) => {
          const cleanName = customName.trim();
          if (cleanName) {
            loginProfile(cleanName, promptMenu);
          } else {
            promptMenu();
          }
        });
      } else if (choice === 'R' || choice === '5') {
        if (rotator) {
          const next = rotator.getNextProfile('light');
          console.log(`\n[Vận hành] Profile tiếp theo sẽ xử lý: ${next}`);
        }
        promptMenu();
      } else {
        const num = parseInt(choice, 10);
        if (!isNaN(num) && num >= 1 && num <= list.length) {
          loginProfile(list[num - 1].name, promptMenu);
        } else {
          promptMenu();
        }
      }
    });
  }

  promptMenu();
}

if (require.main === module) {
  runInteractive();
}

module.exports = {
  listAllProfiles,
  loginProfile
};
