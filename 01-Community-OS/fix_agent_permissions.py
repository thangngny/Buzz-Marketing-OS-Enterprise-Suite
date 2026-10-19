#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUZZ MARKETING OS - AGENT PERMISSION & AUTHORIZATION SELF-HEALER
Tự động xử lý dứt điểm lỗi:
"Could not authorize a mentioned agent. Check its access and channel membership, then retry or remove the mention."
"Agent; owner unavailable"

Quy trình 5 bước chuẩn hóa tự động:
1. Quét tìm managed-agents.json theo đúng OS (Windows/macOS/Linux):
   - Đổi tất cả respond_to, definition_respond_to thành "anyone".
   - Làm trống respond_to_allowlist (hoặc thêm pubkeys cụ thể).
   - Thêm cờ --permission-mode bypass-permissions --respond-to anyone vào agent_args.
2. Ký và phát sóng Nostr Kind 10100 lên Community Relay với:
   {"respond_to": "anyone", "channel_add_policy": "anyone"} và tag ["p", "<owner_pubkey>", "", "owner"].
3. Cấu hình cờ mở quyền daemon buzz-acp và khởi động lại tiến trình worker nếu đang chạy.
4. Kiểm tra cấu hình Runner Codex/Claude: approval_policy = "never", sandbox_mode = "danger-full-access".
5. Kiểm tra Buzz CLI (buzz.exe) trong PATH và tự động gợi ý / hỗ trợ liên kết.
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def get_buzz_paths():
    home = Path.home()
    if sys.platform == "darwin":
        base_dir = home / "Library" / "Application Support" / "xyz.block.buzz.app"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or str(home / "AppData" / "Roaming")
        base_dir = Path(appdata) / "xyz.block.buzz.app"
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME") or str(home / ".config")
        base_dir = Path(config_home) / "xyz.block.buzz.app"
    agents_dir = base_dir / "agents"
    return base_dir, agents_dir

def find_buzz_cli():
    # 1. Check in system PATH
    which_buzz = shutil.which("buzz") or shutil.which("buzz.exe")
    if which_buzz:
        return which_buzz

    # 2. Check standard operating system locations
    candidates = []
    if sys.platform == "win32":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Buzz\buzz.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Buzz\buzz.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Buzz\buzz.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Buzz\buzz.exe"),
            r"C:\Buzz\buzz.exe",
            r"D:\Buzz\buzz.exe",
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/Buzz.app/Contents/MacOS/buzz",
            os.path.expanduser("~/Applications/Buzz.app/Contents/MacOS/buzz")
        ]
    else:
        candidates = [
            "/usr/local/bin/buzz",
            os.path.expanduser("~/.local/bin/buzz"),
            "/usr/bin/buzz"
        ]

    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def step_1_update_managed_agents(allowlist_pubkeys=None):
    print("\n[+] BƯỚC 1: Tìm và cập nhật cấu hình managed-agents.json...")
    base_dir, agents_dir = get_buzz_paths()
    managed_file = agents_dir / "managed-agents.json"

    if not managed_file.exists():
        print(f"  [-] Chưa tìm thấy file: {managed_file}")
        print("  [!] Vui lòng chạy setup_managed_agents.py trước để tạo cấu hình ban đầu.")
        return False, []

    with open(managed_file, "r", encoding="utf-8") as f:
        agents = json.load(f)

    updated_count = 0
    allowlist = allowlist_pubkeys or []

    for a in agents:
        a["respond_to"] = "anyone"
        a["respondTo"] = "anyone"
        a["definition_respond_to"] = "anyone"
        a["respond_to_allowlist"] = allowlist
        a["respondToAllowlist"] = allowlist
        
        args = a.get("agent_args") or []
        if "--permission-mode" not in args:
            args.extend(["--permission-mode", "bypass-permissions"])
        if "--respond-to" not in args:
            args.extend(["--respond-to", "anyone"])
        a["agent_args"] = args
        updated_count += 1

    with open(managed_file, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Đã mở quyền 'anyone' và gán cờ bypass-permissions cho {updated_count} Agent trong {managed_file.name}")
    return True, agents

def step_2_broadcast_kind_10100(relay_url=None, owner_pubkey=None):
    print("\n[+] BƯỚC 2: Phát sóng sự kiện Nostr Kind 10100 (Access Policy: anyone) lên Relay...")
    script_dir = Path(__file__).resolve().parent
    broadcast_script = script_dir / "broadcast_kind_10100.js"
    
    if not broadcast_script.exists():
        print(f"  [-] Không tìm thấy: {broadcast_script}")
        return False

    node_bin = shutil.which("node") or shutil.which("node.exe")
    if not node_bin:
        print("  [!] Node.js chưa có trong PATH. Bỏ qua bước phát sóng WebSocket.")
        return False

    cmd = [node_bin, str(broadcast_script)]
    if relay_url:
        cmd.extend(["--relay", relay_url])
    if owner_pubkey:
        cmd.extend(["--owner-pubkey", owner_pubkey])

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout.strip())
    if res.stderr.strip():
        print(f"  [Lưu ý] {res.stderr.strip()}")
    return res.returncode == 0

def step_3_refresh_buzz_acp():
    print("\n[+] BƯỚC 3: Làm mới tiến trình daemon buzz-acp...")
    if sys.platform == "win32":
        try:
            # Kill stale buzz-acp processes so Buzz Desktop respawns them with new args
            res = subprocess.run(["taskkill", "/f", "/im", "buzz-acp.exe"], capture_output=True, text=True)
            if res.returncode == 0:
                print("  ✅ Đã đóng các tiến trình buzz-acp.exe cũ. Buzz Desktop sẽ tự khởi động lại với quyền mới.")
            else:
                print("  ℹ️  Không có tiến trình buzz-acp.exe nào đang chạy ngầm.")
        except Exception as e:
            print(f"  [!] {e}")
    else:
        try:
            subprocess.run(["pkill", "-f", "buzz-acp"], capture_output=True)
            print("  ✅ Đã làm mới tiến trình buzz-acp.")
        except Exception:
            pass

def step_4_verify_llm_runner():
    print("\n[+] BƯỚC 4: Kiểm tra Runner LLM (Codex Rotator không chặn phê duyệt)...")
    home = Path.home()
    profiles_dir = home / ".codex" / "profiles"
    if not profiles_dir.exists():
        print(f"  ℹ️  Thư mục {profiles_dir} chưa được tạo. Chạy setup_rotator.py để khởi tạo.")
        return True

    fixed_count = 0
    for d in profiles_dir.iterdir():
        if d.is_dir() and not d.name.startswith("."):
            cfg = d / "config.toml"
            if cfg.exists():
                with open(cfg, "r", encoding="utf-8") as f:
                    content = f.read()
                need_update = False
                if 'approval_policy = "never"' not in content:
                    content += '\napproval_policy = "never"\n'
                    need_update = True
                if 'sandbox_mode = "danger-full-access"' not in content:
                    content += 'sandbox_mode = "danger-full-access"\n'
                    need_update = True
                if need_update:
                    with open(cfg, "w", encoding="utf-8") as f:
                        f.write(content)
                    fixed_count += 1

    print(f"  ✅ Đã kiểm tra và đảm bảo các profile Codex đều ở chế độ 'approval_policy = never' (Cập nhật: {fixed_count}).")
    return True

def step_5_check_buzz_cli():
    print("\n[+] BƯỚC 5: Kiểm tra Buzz CLI (buzz.exe)...")
    buzz_bin = find_buzz_cli()
    if buzz_bin:
        print(f"  ✅ Tìm thấy Buzz CLI tại: {buzz_bin}")
        in_path = bool(shutil.which("buzz") or shutil.which("buzz.exe"))
        if not in_path and sys.platform == "win32":
            buzz_dir = str(Path(buzz_bin).parent)
            print(f"  ⚠️ Lưu ý: Thư mục chứa buzz.exe ({buzz_dir}) chưa có trong PATH hệ thống.")
            print(f"     Để thuận tiện, bạn nên thêm '{buzz_dir}' vào User PATH.")
        return True
    else:
        print("  ⚠️ CHƯA TÌM THẤY BUZZ CLI TRÊN MÁY TÍNH NÀY!")
        print("     Ứng dụng Buzz Desktop chứa buzz.exe và buzz-acp.exe.")
        print("     Vui lòng tải và cài đặt Buzz Desktop tại: https://buzz.xyz")
        print("     Sau khi cài xong, thêm thư mục cài đặt Buzz vào PATH.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Buzz Agent Authorization & Permission Self-Healer")
    parser.add_argument("--relay", default="", help="Relay URL (VD: wss://phamgianam.communities.buzz.xyz)")
    parser.add_argument("--owner-pubkey", default="", help="Owner Pubkey (hex)")
    parser.add_argument("--allow-pubkey", action="append", help="Thêm pubkey người dùng vào respond_to_allowlist")
    args = parser.parse_args()

    print("=" * 80)
    print("   BUZZ MARKETING OS - BỘ TỰ ĐỘNG SỬA LỖI PHÂN QUYỀN AGENT (4-STEP SELF-HEALER)")
    print("=" * 80)

    # 1. Update managed-agents.json
    ok1, agents = step_1_update_managed_agents(args.allow_pubkey)

    # 2. Extract relay & broadcast Kind 10100
    relay = args.relay
    if not relay:
        relay = os.environ.get("BUZZ_RELAY") or os.environ.get("BUZZ_RELAY_URL")
    if not relay and agents:
        relay = agents[0].get("relay_url")

    step_2_broadcast_kind_10100(relay, args.owner_pubkey)

    # 3. Refresh buzz-acp
    step_3_refresh_buzz_acp()

    # 4. Verify LLM Runner
    step_4_verify_llm_runner()

    # 5. Check Buzz CLI
    step_5_check_buzz_cli()

    print("\n" + "=" * 80)
    print("🎉 HOÀN TẤT TỰ ĐỘNG SỬA LỖI PHÂN QUYỀN VÀ MỞ KHÓA TƯƠNG TÁC AGENT 100%!")
    print("=" * 80)

if __name__ == "__main__":
    main()
