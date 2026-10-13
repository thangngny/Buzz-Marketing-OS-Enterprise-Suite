#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script for Layer 2: Multi-Account Codex Rotator
Tự động cấu hình môi trường xoay tua tài khoản Codex cho Buzz Desktop trên mọi máy tính.
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def print_step(msg):
    print(f"\n[+] {msg}")

def main():
    print("=" * 80)
    print("       TRIỂN KHAI TẦNG 2: BỘ XOAY TÀI KHOẢN CHATGPT / CODEX (ROTATOR)")
    print("=" * 80)

    user_home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    appdata = Path(os.environ.get("APPDATA") or (user_home / "AppData" / "Roaming"))
    
    codex_dir = user_home / ".codex"
    scripts_dir = codex_dir / "scripts"
    profiles_dir = codex_dir / "profiles"
    buzz_harness_dir = appdata / "xyz.block.buzz.app" / "custom_harnesses"
    buzz_tools_dir = appdata / "Buzz" / "node-tools"

    current_dir = Path(__file__).resolve().parent

    # 1. Tạo thư mục .codex/scripts và .codex/profiles
    print_step(f"Khởi tạo cấu trúc thư mục Codex tại: {codex_dir}")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    profiles_dir.mkdir(parents=True, exist_ok=True)
    buzz_harness_dir.mkdir(parents=True, exist_ok=True)
    buzz_tools_dir.mkdir(parents=True, exist_ok=True)

    # 2. Copy scripts
    print_step("Sao chép các kịch bản xoay tua tài khoản vào .codex/scripts:")
    files_to_copy = ["codex-rotator.js", "codex-acp-rotator.js", "account-manager.js"]
    for fname in files_to_copy:
        src = current_dir / fname
        dst = scripts_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  -> Đã sao chép: {fname} -> {dst}")
        # Đồng thời sao chép codex-acp-rotator.js vào %APPDATA%/Buzz/node-tools nếu cần
        if fname == "codex-acp-rotator.js":
            shutil.copy2(src, buzz_tools_dir / fname)
            print(f"  -> Đã liên kết: {fname} -> {buzz_tools_dir / fname}")

    # 3. Tạo profile mẫu
    template_config = current_dir / "profiles_template" / "config.toml"
    for acc in ["lina.ho", "mkt", "acc3"]:
        acc_dir = profiles_dir / acc
        acc_dir.mkdir(parents=True, exist_ok=True)
        config_dest = acc_dir / "config.toml"
        if not config_dest.exists() and template_config.exists():
            shutil.copy2(template_config, config_dest)
            print(f"  -> Đã tạo profile cấu hình: {acc}")

    # 4. Tìm kiếm Node.js
    node_exe = shutil.which("node") or shutil.which("node.exe")
    if not node_exe:
        # Check standard paths
        local_appdata = Path(os.environ.get("LOCALAPPDATA") or (user_home / "AppData" / "Local"))
        possible_nodes = list(local_appdata.glob("Programs/node*/node.exe")) + [
            Path("C:/Program Files/nodejs/node.exe"),
            Path("C:/Program Files (x86)/nodejs/node.exe")
        ]
        for p in possible_nodes:
            if p.exists():
                node_exe = str(p)
                break

    if not node_exe:
        node_exe = "node"
        print("  [!] Không tìm thấy đường dẫn tuyệt đối của node, sử dụng lệnh 'node' từ PATH.")
    else:
        print_step(f"Nhận diện Node.js tại: {node_exe}")

    # 5. Cài đặt hoặc kiểm tra codex-acp
    print_step("Kiểm tra thư viện @agentclientprotocol/codex-acp...")
    try:
        # Kiểm tra xem có thể chạy npm install trong buzz_tools_dir không
        pkg_json = buzz_tools_dir / "package.json"
        if not pkg_json.exists():
            with open(pkg_json, "w", encoding="utf-8") as f:
                json.dump({"dependencies": {"@agentclientprotocol/codex-acp": "^2.0.0"}}, f, indent=2)
        print("  -> Thư mục node-tools đã sẵn sàng.")
    except Exception as e:
        print(f"  [!] Lưu ý khi chuẩn bị node-tools: {e}")

    # 6. Ghi harness codex-harness.json vào Buzz Desktop
    harness_path = buzz_harness_dir / "codex-harness.json"
    rotator_script_path = str(buzz_tools_dir / "codex-acp-rotator.js")

    harness_config = {
        "id": "codex-harness",
        "label": "Codex ACP Rotating (Multi-Account)",
        "installInstructionsUrl": "https://developers.openai.com/codex/cli/",
        "installHint": "npm install -g @agentclientprotocol/codex-acp",
        "command": node_exe,
        "args": [
            rotator_script_path
        ],
        "env": {}
    }

    with open(harness_path, "w", encoding="utf-8") as f:
        json.dump(harness_config, f, indent=2)
    print_step(f"Đã cập nhật Harness Buzz Desktop tại: {harness_path}")

    print("\n" + "=" * 80)
    print("  ✅ HOÀN TẤT THIẾT LẬP TẦNG 2 (CODEX ROTATOR)")
    print("  Để đăng nhập các tài khoản ChatGPT vào hệ thống xoay:")
    print("  -> Chạy file: 02-Codex-Rotator/Quan-Ly-Tai-Khoan.bat")
    print("=" * 80)

if __name__ == "__main__":
    main()
