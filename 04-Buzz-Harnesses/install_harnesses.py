#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Installer for Buzz Desktop
Tự động xác định các đường dẫn thực tế trên máy hiện tại và cài đặt các cấu hình Custom Harness.
"""
import os
import sys
import json
import shutil
from pathlib import Path

# Ensure UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("=" * 80)
    print("      CÀI ĐẶT CÁC CUSTOM HARNESS CHO BUZZ DESKTOP (ROTATOR & HUB)")
    print("=" * 80)

    user_home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    appdata = Path(os.environ.get("APPDATA") or (user_home / "AppData" / "Roaming"))
    buzz_harness_dir = appdata / "xyz.block.buzz.app" / "custom_harnesses"
    buzz_tools_dir = appdata / "Buzz" / "node-tools"
    repo_dir = user_home / "marketing-ai-system"
    venv_python = repo_dir / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")

    buzz_harness_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tìm node.exe
    node_exe = shutil.which("node") or shutil.which("node.exe")
    if not node_exe:
        local_appdata = Path(os.environ.get("LOCALAPPDATA") or (user_home / "AppData" / "Local"))
        possible_nodes = list(local_appdata.glob("Programs/node*/node.exe"))
        if possible_nodes:
            node_exe = str(possible_nodes[0])
        else:
            node_exe = "node"

    # 2. Đường dẫn codex-acp-rotator
    rotator_script = str(buzz_tools_dir / "codex-acp-rotator.js")
    if not (buzz_tools_dir / "codex-acp-rotator.js").exists():
        # Fallback to .codex/scripts
        rotator_script = str(user_home / ".codex" / "scripts" / "codex-acp-rotator.js")

    # Ghi codex-harness.json
    codex_harness = {
        "id": "codex-harness",
        "label": "Codex ACP Rotating (Multi-Account)",
        "installInstructionsUrl": "https://developers.openai.com/codex/cli/",
        "installHint": "npm install -g @agentclientprotocol/codex-acp",
        "command": node_exe,
        "args": [
            rotator_script
        ],
        "env": {}
    }
    codex_dest = buzz_harness_dir / "codex-harness.json"
    with open(codex_dest, "w", encoding="utf-8") as f:
        json.dump(codex_harness, f, indent=2)
    print(f"[+] Đã cài đặt Harness Codex Rotator: {codex_dest}")

    # Ghi marketing-hub.json
    python_cmd = str(venv_python) if venv_python.exists() else (shutil.which("python") or "python")
    hub_harness = {
        "id": "marketing-hub",
        "label": "Marketing System Hub (Zoho/Apollo/YouTube/Website)",
        "installInstructionsUrl": "https://github.com/thangngny/marketing-ai-system",
        "installHint": f"already installed at {repo_dir}",
        "command": python_cmd,
        "args": ["-m", "marketing_system.mcp_server"],
        "env": {}
    }
    hub_dest = buzz_harness_dir / "marketing-hub.json"
    with open(hub_dest, "w", encoding="utf-8") as f:
        json.dump(hub_harness, f, indent=2)
    print(f"[+] Đã cài đặt Harness Marketing Hub: {hub_dest}")

    print("\n✅ Cài đặt Custom Harnesses hoàn tất!")

if __name__ == "__main__":
    main()
