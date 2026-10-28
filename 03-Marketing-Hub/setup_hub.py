#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script for Layer 3: Marketing System Hub (MCP Server)
Tự động cấu hình mã nguồn Marketing Hub, Virtualenv và liên kết Harness vào Buzz Desktop.
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

REPO_URL = "https://github.com/thangngny/marketing-ai-system.git"
DEFAULT_BRANCH = "marketing-system-phase1"

def print_step(msg):
    print(f"\n[+] {msg}")

def run_cmd(cmd, cwd=None):
    print(f"  > Đang chạy: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [!] Lỗi khi thực thi: {res.stderr.strip()}")
    return res

def main():
    print("=" * 80)
    print("       TRIỂN KHAI TẦNG 3: MARKETING SYSTEM HUB (MCP TOOLS ENGINE)")
    print("=" * 80)

    user_home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    appdata = Path(os.environ.get("APPDATA") or (user_home / "AppData" / "Roaming"))
    target_repo_dir = user_home / "marketing-ai-system"
    buzz_harness_dir = appdata / "xyz.block.buzz.app" / "custom_harnesses"

    # 1. Kiểm tra mã nguồn kho marketing-ai-system
    print_step(f"Kiểm tra thư mục repo Marketing Hub tại: {target_repo_dir}")
    if not target_repo_dir.exists():
        print(f"  -> Thư mục chưa tồn tại. Đang clone từ GitHub ({REPO_URL})...")
        git_bin = shutil.which("git") or "git"
        clone_res = run_cmd([git_bin, "clone", "-b", DEFAULT_BRANCH, REPO_URL, str(target_repo_dir)])
        if clone_res.returncode != 0:
            print("  [!] Không thể clone qua branch, thử clone mặc định...")
            run_cmd([git_bin, "clone", REPO_URL, str(target_repo_dir)])
    else:
        print("  -> Đã tìm thấy thư mục mã nguồn Marketing Hub.")

    if not target_repo_dir.exists():
        print("  [LỖI] Không thể tạo thư mục marketing-ai-system. Vui lòng kiểm tra kết nối mạng hoặc clone thủ công.")
        return

    # 2. Tạo môi trường ảo Python (.venv)
    venv_dir = target_repo_dir / ".venv"
    python_bin = sys.executable
    venv_python = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")

    print_step("Kiểm tra môi trường ảo Python (.venv):")
    if not venv_python.exists():
        print("  -> Đang khởi tạo .venv mới...")
        run_cmd([python_bin, "-m", "venv", str(venv_dir)])
    else:
        print(f"  -> Đã có sẵn môi trường ảo tại: {venv_python}")

    # 3. Cài đặt các gói phụ thuộc
    print_step("Cài đặt các thư viện cần thiết vào .venv:")
    if venv_python.exists():
        # Ưu tiên pip install -e . hoặc cài đặt trực tiếp
        pyproject = target_repo_dir / "pyproject.toml"
        if pyproject.exists():
            print("  -> Cài đặt gói marketing_system ở chế độ editable (-e .)...")
            run_cmd([str(venv_python), "-m", "pip", "install", "-e", "."], cwd=str(target_repo_dir))
        else:
            print("  -> Cài đặt fastmcp, pydantic, httpx...")
            run_cmd([str(venv_python), "-m", "pip", "install", "fastmcp", "pydantic", "httpx", "python-dotenv"], cwd=str(target_repo_dir))

    # 4. Kiểm tra file .env
    print_step("Kiểm tra cấu hình biến môi trường (.env):")
    env_file = target_repo_dir / ".env"
    env_example = target_repo_dir / ".env.example"
    local_example = Path(__file__).resolve().parent / ".env.example"

    if not env_file.exists():
        src_example = env_example if env_example.exists() else local_example
        if src_example.exists():
            shutil.copy2(src_example, env_file)
            print(f"  -> Đã tạo file .env từ mẫu .env.example tại: {env_file}")
            print("  -> Mặc định hệ thống hoạt động ở chế độ 'mock' (an toàn, không phát sinh lỗi khi chưa có API keys).")
    else:
        print(f"  -> Đã tồn tại file .env: {env_file}")

    # 4.5 Cài đặt LinkedIn, Zalo OA & Scheduler Services
    print_step("Cài đặt bộ điều phối xuất bản đa kênh (LinkedIn, Zalo OA, Post Scheduler):")
    services_to_sync = ["linkedin", "zalo-oa", "scheduler"]
    for sname in services_to_sync:
        bundled_svc = Path(__file__).resolve().parent / "services" / sname
        user_buzz_svc = user_home / ".buzz" / "services" / sname
        if bundled_svc.exists():
            user_buzz_svc.mkdir(parents=True, exist_ok=True)
            for item in bundled_svc.glob("*.*"):
                if item.is_file() and not item.name.endswith(".db"):
                    shutil.copy2(item, user_buzz_svc / item.name)
            print(f"  -> Đã cài đặt dịch vụ {sname} -> {user_buzz_svc}")

    # 4.6 Tự động liên kết LinkedIn Controller vào catalog.py
    catalog_py = target_repo_dir / "src" / "marketing_system" / "tools" / "catalog.py"
    if catalog_py.exists():
        try:
            txt = catalog_py.read_text(encoding="utf-8")
            if 'elif args.channel == "linkedin":' not in txt:
                target_marker = '    else:\n        raise NotImplementedError(f"Publishing to channel \'{args.channel}\' is not enabled or requires product approval.")'
                linkedin_block = (
                    '    elif args.channel == "linkedin":\n'
                    '        import subprocess, json\n'
                    '        from pathlib import Path\n'
                    '        cli_path = Path.home() / ".buzz" / "services" / "linkedin" / "linkedin_cli.js"\n'
                    '        if cli_path.is_file():\n'
                    '            cmd = ["node", str(cli_path), "post", "--text", args.text]\n'
                    '            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")\n'
                    '            try:\n'
                    '                return json.loads(proc.stdout.strip())\n'
                    '            except Exception:\n'
                    '                return {"channel": "linkedin", "status": "published" if proc.returncode == 0 else "fallback_triggered", "output": proc.stdout.strip(), "error": proc.stderr.strip()}\n'
                    '        raise ToolUnavailable("NOT_CONFIGURED", f"LinkedIn CLI not found at {cli_path}")\n'
                    '    else:\n'
                    '        raise NotImplementedError(f"Publishing to channel \'{args.channel}\' is not enabled or requires product approval.")'
                )
                if target_marker in txt:
                    catalog_py.write_text(txt.replace(target_marker, linkedin_block), encoding="utf-8")
                    print("  ✅ Đã tự động tích hợp LinkedIn Multi-Tier vào catalog.py của Marketing Hub.")
        except Exception as e:
            print(f"  [!] Lưu ý cấu hình catalog.py: {e}")

    # 5. Đăng ký Harness vào Buzz Desktop
    print_step("Đăng ký Harness 'marketing-hub' vào Buzz Desktop:")
    buzz_harness_dir.mkdir(parents=True, exist_ok=True)
    harness_path = buzz_harness_dir / "marketing-hub.json"

    harness_config = {
        "id": "marketing-hub",
        "label": "Marketing System Hub (Zoho/Apollo/YouTube/Website)",
        "installInstructionsUrl": "https://github.com/thangngny/marketing-ai-system",
        "installHint": f"already installed at {target_repo_dir}",
        "command": str(venv_python) if venv_python.exists() else "python",
        "args": ["-m", "marketing_system.mcp_server"],
        "env": {}
    }

    with open(harness_path, "w", encoding="utf-8") as f:
        json.dump(harness_config, f, indent=2)
    print(f"  -> Đã ghi cấu hình Harness: {harness_path}")

    # 6. Kiểm tra chạy thử
    print_step("Kiểm tra khởi động Module MCP Server...")
    test_res = run_cmd([str(venv_python), "-c", "import marketing_system.mcp_server; print('MCP SERVER READY')"], cwd=str(target_repo_dir))
    if test_res.returncode == 0 and "MCP SERVER READY" in test_res.stdout:
        print("  ✅ KIỂM TRA THÀNH CÔNG: Marketing Hub MCP Server đã sẵn sàng hoạt động!")
    else:
        print(f"  [!] Lưu ý kiểm tra: {test_res.stdout} {test_res.stderr}")

    print("\n" + "=" * 80)
    print("  ✅ HOÀN TẤT THIẾT LẬP TẦNG 3 (MARKETING HUB MCP)")
    print("  Xem hướng dẫn cấu hình API tại: 03-Marketing-Hub/CONNECTOR_GUIDE.md")
    print("=" * 80)

if __name__ == "__main__":
    main()
