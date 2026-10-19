#!/usr/bin/env node
/**
 * Broadcast Nostr Kind 10100 (Access Policy: anyone) for all Agents
 * Ensures client Buzz Desktop for ALL community members can mention and interact with agents.
 */
const path = require('path');
const fs = require('fs');
const os = require('os');

let nt;
const candidates = [
  path.join(__dirname, 'node_modules', 'nostr-tools'),
  path.join(process.env.APPDATA || '', 'Buzz', 'node-tools', 'node_modules', 'nostr-tools'),
  'nostr-tools'
];
for (const c of candidates) {
  try {
    nt = require(c);
    if (nt) break;
  } catch (e) {}
}

const args = process.argv.slice(2);
let relayUrl = '';
let ownerPubkey = '';
let agentsFile = '';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--relay' && args[i+1]) relayUrl = args[i+1];
  if (args[i] === '--owner-pubkey' && args[i+1]) ownerPubkey = args[i+1];
  if (args[i] === '--file' && args[i+1]) agentsFile = args[i+1];
}

if (!relayUrl) {
  relayUrl = process.env.BUZZ_RELAY || process.env.BUZZ_RELAY_URL || '';
}
if (!relayUrl) {
  console.log('[!] Vui lòng cung cấp Relay URL qua tham số --relay <url> hoặc biến BUZZ_RELAY');
  process.exit(0);
}
if (relayUrl.startsWith('http://')) relayUrl = 'ws://' + relayUrl.slice(7);
if (relayUrl.startsWith('https://')) relayUrl = 'wss://' + relayUrl.slice(8);

const userHome = process.env.USERPROFILE || process.env.HOME || os.homedir();
const appData = process.env.APPDATA || path.join(userHome, 'AppData', 'Roaming');
if (!agentsFile) {
  agentsFile = path.join(appData, 'xyz.block.buzz.app', 'agents', 'managed-agents.json');
}

if (!fs.existsSync(agentsFile)) {
  console.log(`[!] Không tìm thấy file: ${agentsFile}`);
  process.exit(0);
}

if (!nt) {
  console.log('[!] Lưu ý: nostr-tools chưa được cài đặt trong môi trường node. Bỏ qua bước phát sóng WebSocket.');
  process.exit(0);
}

const agents = JSON.parse(fs.readFileSync(agentsFile, 'utf8'));

async function publishForAgent(agent) {
  if (!agent.private_key_nsec || !agent.auth_tag) return { name: agent.name, skipped: true };
  let sk;
  try {
    const decoded = nt.nip19.decode(agent.private_key_nsec);
    sk = decoded.data;
  } catch (e) {
    return { name: agent.name, skipped: true, error: e.message };
  }
  const authTag = typeof agent.auth_tag === 'string' ? JSON.parse(agent.auth_tag) : agent.auth_tag;

  const targetOwner = ownerPubkey || (authTag && authTag[1]) || '';

  return new Promise((resolve) => {
    const ws = new WebSocket(relayUrl);
    let authed = false;
    let publishedId = null;

    const timer = setTimeout(() => {
      try { ws.close(); } catch (e) {}
      resolve({ name: agent.name, success: false, error: 'timeout' });
    }, 10000);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data[0] === 'AUTH') {
          const challenge = data[1];
          const tags = [
            ['relay', relayUrl],
            ['challenge', challenge]
          ];
          if (authTag) tags.push(authTag);
          const authEvent = nt.finalizeEvent({
            kind: 22242,
            created_at: Math.floor(Date.now() / 1000),
            tags: tags,
            content: ''
          }, sk);
          ws.send(JSON.stringify(['AUTH', authEvent]));
        } else if (data[0] === 'OK') {
          const [_, eventId, success, msg] = data;
          if (!authed && success) {
            authed = true;
            const tags = [];
            if (targetOwner) tags.push(['p', targetOwner, '', 'owner']);
            if (authTag) tags.push(authTag);

            const k10100 = nt.finalizeEvent({
              kind: 10100,
              created_at: Math.floor(Date.now() / 1000),
              tags: tags,
              content: JSON.stringify({
                respond_to: 'anyone',
                channel_add_policy: 'anyone'
              })
            }, sk);
            publishedId = k10100.id;
            ws.send(JSON.stringify(['EVENT', k10100]));
          } else if (eventId === publishedId) {
            clearTimeout(timer);
            try { ws.close(); } catch (e) {}
            resolve({ name: agent.name, success: success, eventId, msg });
          }
        }
      } catch (err) {
        clearTimeout(timer);
        try { ws.close(); } catch (e) {}
        resolve({ name: agent.name, success: false, error: err.message });
      }
    };

    ws.onerror = () => {
      clearTimeout(timer);
      resolve({ name: agent.name, success: false, error: 'ws error' });
    };
  });
}

async function main() {
  console.log(`[*] Đang phát sóng Nostr Kind 10100 (respond_to: anyone) lên Relay: ${relayUrl}...`);
  const seen = new Set();
  let count = 0;
  for (const a of agents) {
    if (!a.private_key_nsec || seen.has(a.pubkey)) continue;
    seen.add(a.pubkey);
    const res = await publishForAgent(a);
    if (res.success) {
      console.log(`  ✅ [Kind 10100] ${a.name} -> ID: ${res.eventId}`);
      count++;
    }
  }
  console.log(`[OK] Đã hoàn tất công bố quyền hạn Kind 10100 (anyone) cho ${count} Agent.`);
}

main();
