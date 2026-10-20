#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUZZ MARKETING OS - UNLOCK FULL PERMISSIONS FOR ALL MEMBERS & COMMUNITY USERS
Mở toàn quyền 100% cho mọi người dùng trong cộng đồng tương tác với tất cả Buzz Agent:
- respond_to: "anyone"
- definition_respond_to: "anyone"
- agent_args: --permission-mode bypass-permissions --respond-to anyone
- start_on_app_launch: True
- is_active: True
- Nostr Kind 10100 (Access Policy: anyone) broadcasted to Relay
- Codex approval_policy = "never" & sandbox_mode = "danger-full-access"
"""

import os
import sys
import json
import shutil
import time
import argparse
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

APP_DATA = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))) / "xyz.block.buzz.app"
AGENTS_JSON = APP_DATA / "agents" / "managed-agents.json"
TEMPLATES_DIR = APP_DATA / "templates"
SUITE_DIR = Path(__file__).resolve().parent.parent

EXECUTIVE_AUTHORITY_CLAUSE = (
    "\n\n[QUYỀN HẠN PHỤC VỤ MỌI THÀNH VIÊN - UNIVERSAL PUBLIC ACCESS]\n"
    "Bạn là Chuyên gia AI phục vụ toàn thể thành viên trong cộng đồng và tổ chức. "
    "Mọi nhân viên, thành viên (ví dụ: Lina, Nam, quản trị viên, nhân sự) khi tag hoặc nhắn tin cho bạn "
    "đều có đầy đủ thẩm quyền giao nhiệm vụ. Bạn TUYỆT ĐỐI KHÔNG chặn quyền, KHÔNG từ chối vì lý do 'không phải owner', "
    "và tự động thực thi các tác vụ (tạo bài, phân tích, trích xuất dữ liệu, kiểm tra) theo đúng chuyên môn một cách tức thì."
)

def find_buzz_desktop():
    which_desk = shutil.which("buzz-desktop") or shutil.which("buzz-desktop.exe")
    if which_desk:
        return which_desk
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Buzz\buzz-desktop.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Buzz\buzz-desktop.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Buzz\buzz-desktop.exe"),
        r"C:\Buzz\buzz-desktop.exe",
        r"D:\Buzz\buzz-desktop.exe",
        "/Applications/Buzz.app/Contents/MacOS/buzz-desktop"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def detect_community_relay(explicit_relay=None):
    if explicit_relay:
        r = explicit_relay.strip()
        if r.startswith("http://"): r = "ws://" + r[7:]
        elif r.startswith("https://"): r = "wss://" + r[8:]
        return r
    env_r = os.environ.get("BUZZ_RELAY") or os.environ.get("BUZZ_RELAY_URL")
    if env_r:
        if env_r.startswith("http://"): env_r = "ws://" + env_r[7:]
        elif env_r.startswith("https://"): env_r = "wss://" + env_r[8:]
        return env_r
    try:
        import sqlite3
        db_path = APP_DATA / "channel-head-cache.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT scope FROM channel_head LIMIT 5")
            for row in cur.fetchall():
                if ":" in row[0]:
                    cand = row[0].split(":", 1)[1]
                    if cand.startswith("ws://") or cand.startswith("wss://"):
                        return cand
    except Exception:
        pass
    try:
        if AGENTS_JSON.exists():
            with open(AGENTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            for a in data:
                ru = a.get("relay_url")
                if ru and (ru.startswith("ws://") or ru.startswith("wss://")):
                    return ru
    except Exception:
        pass
    return "wss://phamgianam.communities.buzz.xyz"

def update_agent_record(a, relay_url):
    a["respond_to"] = "anyone"
    a["respondTo"] = "anyone"
    a["definition_respond_to"] = "anyone"
    a["respond_to_allowlist"] = []
    a["respondToAllowlist"] = []
    a["start_on_app_launch"] = True
    a["is_active"] = True
    a["relay_url"] = relay_url

    # Ensure bypass-permissions and respond-to anyone are in agent_args
    args = a.get("agent_args") or []
    if "--tier" not in args:
        args.extend(["--tier", "light"])
    if "--permission-mode" not in args:
        args.extend(["--permission-mode", "bypass-permissions"])
    else:
        idx = args.index("--permission-mode")
        if idx + 1 < len(args):
            args[idx + 1] = "bypass-permissions"
    if "--respond-to" not in args:
        args.extend(["--respond-to", "anyone"])
    else:
        idx = args.index("--respond-to")
        if idx + 1 < len(args):
            args[idx + 1] = "anyone"
    a["agent_args"] = args

    # Inject executive authority into system prompt if missing
    sp = a.get("system_prompt") or ""
    if "[QUYỀN HẠN PHỤC VỤ MỌI THÀNH VIÊN" not in sp:
        a["system_prompt"] = sp + EXECUTIVE_AUTHORITY_CLAUSE

def unlock_permissions(relay=None, restart_desktop=True):
    relay_url = detect_community_relay(relay)
    print("=" * 80)
    print(f"🚀 KHỞI CHẠY TIẾN TRÌNH MỞ TOÀN QUYỀN BUZZ AGENTS (FULL ACCESS FOR ANYONE)")
    print(f"[*] Mục tiêu Relay: {relay_url}")
    print("=" * 80)

    # 1. Update managed-agents.json
    if AGENTS_JSON.exists():
        backup_path = AGENTS_JSON.with_suffix(f".bak_{int(time.time())}")
        shutil.copy2(AGENTS_JSON, backup_path)
        print(f"[1/5] Đã sao lưu managed-agents.json -> {backup_path.name}")

        with open(AGENTS_JSON, "r", encoding="utf-8") as f:
            agents = json.load(f)

        for a in agents:
            update_agent_record(a, relay_url)

        with open(AGENTS_JSON, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)

        print(f"  ✅ Đã mở quyền 'anyone', cờ 'bypass-permissions' và quyền điều hành cho toàn bộ {len(agents)} Agent.")

    # 2. Update templates if present
    for tf in [
        SUITE_DIR / "01-Community-OS" / "agents_template.json",
        TEMPLATES_DIR / "Marketing-OS-Full.team.json",
        TEMPLATES_DIR / "Marketing-OS-NCTHANG04.team.json",
        TEMPLATES_DIR / "marketing-ops.team.json",
    ]:
        if tf.exists():
            try:
                with open(tf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for a in data:
                        if isinstance(a, dict):
                            update_agent_record(a, relay_url)
                elif isinstance(data, dict):
                    for k in ["agents", "personas", "managed_agents"]:
                        if k in data and isinstance(data[k], list):
                            for a in data[k]:
                                if isinstance(a, dict):
                                    update_agent_record(a, relay_url)
                with open(tf, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ Đã đồng bộ template: {tf.name}")
            except Exception as e:
                print(f"  [!] Lưu ý template {tf.name}: {e}")

    # 3. Broadcast Nostr Kind 10100 for all agents
    print(f"\n[2/5] Ký và phát sóng Nostr Kind 10100 (respond_to: anyone) lên Relay: {relay_url}...")
    b_script = SUITE_DIR / "01-Community-OS" / "broadcast_kind_10100.js"
    node_bin = shutil.which("node") or shutil.which("node.exe")
    if node_bin and b_script.exists():
        res = subprocess.run([node_bin, str(b_script), "--relay", relay_url], capture_output=True, text=True, encoding="utf-8")
        lines = res.stdout.strip().split("\n")
        print("\n".join(lines[-5:]))
        if res.returncode == 0:
            print("  ✅ Phát sóng Kind 10100 thành công 100% cho toàn bộ Agent.")
        else:
            print(f"  [!] Cảnh báo phát sóng: {res.stderr}")

    # 4. Check Codex Runner profiles
    print("\n[3/5] Đảm bảo Runner Codex Rotator không bao giờ chặn duyệt (approval_policy = never)...")
    profiles_dir = Path.home() / ".codex" / "profiles"
    if profiles_dir.exists():
        for d in profiles_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                cfg = d / "config.toml"
                if cfg.exists():
                    txt = cfg.read_text(encoding="utf-8")
                    mod = False
                    if 'approval_policy = "never"' not in txt:
                        txt += '\napproval_policy = "never"\n'
                        mod = True
                    if 'sandbox_mode = "danger-full-access"' not in txt:
                        txt += 'sandbox_mode = "danger-full-access"\n'
                        mod = True
                    if mod:
                        cfg.write_text(txt, encoding="utf-8")
        print("  ✅ Tất cả profile trong ~/.codex/profiles/ đều đã đặt approval_policy = never & sandbox_mode = danger-full-access.")

    # 5. Launch Buzz Desktop fresh if requested
    if restart_desktop:
        print("\n[4/5] Khởi động lại Buzz Desktop với cấu hình quyền mở mới...")
        buzz_desktop_path = find_buzz_desktop()
        if buzz_desktop_path and os.path.exists(buzz_desktop_path):
            try:
                # Terminate running buzz-acp and buzz-desktop if any
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/f", "/im", "buzz-acp.exe"], capture_output=True)
                    subprocess.run(["taskkill", "/f", "/im", "buzz-desktop.exe"], capture_output=True)
                time.sleep(1)
                subprocess.Popen([buzz_desktop_path], creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0)
                print(f"  ✅ Đã khởi chạy Buzz Desktop ({buzz_desktop_path})!")
                time.sleep(3)
            except Exception as e:
                print(f"  [!] Khởi động Buzz Desktop: {e}")
        else:
            print("  ℹ️  Chưa tìm thấy ứng dụng Buzz Desktop trong các đường dẫn mặc định.")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ AGENT ĐÃ ĐƯỢC MỞ TOÀN QUYỀN CHO MỌI THÀNH VIÊN TRONG CỘNG ĐỒNG!")
    print("   Bất kỳ thành viên nào (Lina, Nam, v.v.) hiện tại đều có thể tag @Agent và nhận phản hồi trực tiếp.")
    print("=" * 80)
    return True

def main():
    parser = argparse.ArgumentParser(description="Unlock full permissions for all Buzz agents")
    parser.add_argument("--relay", "--community-url", dest="relay", default=None, help="Relay URL (VD: wss://phamgianam.communities.buzz.xyz)")
    parser.add_argument("--no-launch", action="store_true", help="Không tự động khởi động Buzz Desktop")
    args = parser.parse_args()
    unlock_permissions(relay=args.relay, restart_desktop=not args.no_launch)

if __name__ == "__main__":
    main()
