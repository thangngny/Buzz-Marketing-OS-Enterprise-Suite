#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification & Diagnostics Suite for Buzz Marketing OS Full Enterprise
Kiểm tra toàn diện 10 chỉ số sẵn sàng của cả 3 Tầng trên máy tính.
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

def check_mark(status):
    return "✅ [PASS]" if status else "❌ [FAIL]"

def main():
    print("=" * 80)
    print("      KIỂM TRA CHUẨN ĐOÁN TOÀN DIỆN HỆ THỐNG BUZZ MARKETING OS FULL")
    print("=" * 80)

    user_home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    appdata = Path(os.environ.get("APPDATA") or (user_home / "AppData" / "Roaming"))
    suite_dir = Path(__file__).resolve().parent

    report = []

    # ----------------- TẦNG 1: KHUNG PHÒNG BAN & AGENT -----------------
    print("\n--- 1. KIỂM TRA TẦNG 1: KHUNG PHÒNG BAN & AGENT ---")
    c1_dir = suite_dir / "01-Community-OS"
    f_channels = c1_dir / "channels_master.json"
    f_agents = c1_dir / "agents_template.json"
    f_team = c1_dir / "Marketing-OS-Full.team.json"
    f_injector = c1_dir / "inject_framework.py"

    l1_files_ok = f_channels.exists() and f_agents.exists() and f_team.exists() and f_injector.exists()
    print(f" {check_mark(l1_files_ok)} Tệp dữ liệu mẫu phòng ban & 25 Agent")
    report.append(("Tầng 1 - Dữ liệu phòng ban & Agent", l1_files_ok))

    # Kiểm tra JSON hợp lệ
    json_valid = False
    try:
        with open(f_channels, "r", encoding="utf-8") as f:
            c_data = json.load(f)
        with open(f_agents, "r", encoding="utf-8") as f:
            a_data = json.load(f)
        json_valid = len(c_data) >= 20 and len(a_data) >= 20
        print(f" {check_mark(json_valid)} Số lượng cấu hình: {len(c_data)} phòng ban, {len(a_data)} Agent chuyên trách")
    except Exception as e:
        print(f" ❌ Lỗi đọc file JSON: {e}")
    report.append(("Tầng 1 - Số lượng kênh & Agent chuẩn", json_valid))

    # Kiểm tra phân quyền respond_to = anyone
    managed_json = appdata / "xyz.block.buzz.app" / "agents" / "managed-agents.json"
    access_policy_ok = False
    if managed_json.exists():
        try:
            with open(managed_json, "r", encoding="utf-8") as f:
                m_agents = json.load(f)
            non_anyone = [a.get("name") for a in m_agents if a.get("respond_to") != "anyone"]
            access_policy_ok = len(non_anyone) == 0
            print(f" {check_mark(access_policy_ok)} Phân quyền tương tác tự do (respond_to: anyone cho {len(m_agents)} Agent)")
        except Exception:
            pass
    else:
        print(f" ℹ️  Chưa tìm thấy managed-agents.json (sẽ được tạo khi chạy master_deploy.py)")
        access_policy_ok = True
    # Kiểm tra ứng dụng Buzz Desktop & Buzz CLI
    which_buzz = shutil.which("buzz") or shutil.which("buzz.exe")
    if not which_buzz and sys.platform == "win32":
        candidates = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Buzz\buzz.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Buzz\buzz.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Buzz\buzz.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Buzz\buzz.exe"),
            r"C:\Buzz\buzz.exe",
            r"D:\Buzz\buzz.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                which_buzz = c
                break
    elif not which_buzz and sys.platform == "darwin":
        if os.path.exists("/Applications/Buzz.app/Contents/MacOS/buzz"):
            which_buzz = "/Applications/Buzz.app/Contents/MacOS/buzz"

    buzz_cli_ok = bool(which_buzz)
    buzz_status_str = f"Buzz CLI: {which_buzz}" if buzz_cli_ok else "CHƯA TÌM THẤY (Cài Buzz Desktop tại https://buzz.xyz)"
    print(f" {check_mark(buzz_cli_ok)} {buzz_status_str}")
    report.append(("Tầng 1 - Buzz Desktop & Buzz CLI", buzz_cli_ok))

    # ----------------- TẦNG 2: BỘ XOAY TÀI KHOẢN (CODEX ROTATOR) -----------------
    print("\n--- 2. KIỂM TRA TẦNG 2: BỘ XOAY TÀI KHOẢN (ROTATOR) ---")
    node_bin = shutil.which("node") or shutil.which("node.exe")
    print(f" {check_mark(bool(node_bin))} Trình thực thi Node.js: {node_bin or 'CHƯA CÀI ĐẶT'}")
    report.append(("Tầng 2 - Node.js", bool(node_bin)))

    codex_scripts = user_home / ".codex" / "scripts" / "codex-rotator.js"
    codex_profiles_dir = user_home / ".codex" / "profiles"
    rotator_files_ok = codex_scripts.exists() and codex_profiles_dir.exists()
    print(f" {check_mark(rotator_files_ok)} Thư mục kịch bản & Profiles: {user_home / '.codex'}")
    report.append(("Tầng 2 - Cấu trúc .codex", rotator_files_ok))

    codex_harness = appdata / "xyz.block.buzz.app" / "custom_harnesses" / "codex-harness.json"
    harness_rotator_ok = codex_harness.exists()
    print(f" {check_mark(harness_rotator_ok)} Harness 'codex-harness' trong Buzz Desktop")
    report.append(("Tầng 2 - Harness codex-harness", harness_rotator_ok))

    # Đếm số lượng profile có auth.json
    logged_in_count = 0
    if codex_profiles_dir.exists():
        for d in codex_profiles_dir.iterdir():
            if d.is_dir() and (d / "auth.json").exists():
                logged_in_count += 1
    print(f" ℹ️  Số tài khoản ChatGPT Codex đã đăng nhập sẵn sàng xoay: {logged_in_count} tài khoản")

    # ----------------- TẦNG 3: MARKETING SYSTEM HUB (MCP TOOLS) -----------------
    print("\n--- 3. KIỂM TRA TẦNG 3: MARKETING SYSTEM HUB (MCP) ---")
    hub_repo = user_home / "marketing-ai-system"
    if not hub_repo.exists() and (suite_dir.parent / "marketing-ai-system").exists():
        hub_repo = suite_dir.parent / "marketing-ai-system"

    repo_ok = hub_repo.exists()
    print(f" {check_mark(repo_ok)} Thư mục mã nguồn Marketing Hub: {hub_repo}")
    report.append(("Tầng 3 - Mã nguồn marketing-ai-system", repo_ok))

    venv_python = hub_repo / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    venv_ok = venv_python.exists()
    print(f" {check_mark(venv_ok)} Môi trường ảo Python (.venv): {venv_python}")
    report.append(("Tầng 3 - Python Virtualenv", venv_ok))

    mcp_harness = appdata / "xyz.block.buzz.app" / "custom_harnesses" / "marketing-hub.json"
    mcp_harness_ok = mcp_harness.exists()
    print(f" {check_mark(mcp_harness_ok)} Harness 'marketing-hub' trong Buzz Desktop")
    report.append(("Tầng 3 - Harness marketing-hub", mcp_harness_ok))

    # Test module import
    mcp_run_ok = False
    if venv_ok:
        try:
            res = subprocess.run([str(venv_python), "-c", "import marketing_system.mcp_server; print('OK')"], capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and "OK" in res.stdout:
                mcp_run_ok = True
        except Exception:
            pass
    print(f" {check_mark(mcp_run_ok)} Khởi động thử nghiệm module MCP Server")
    report.append(("Tầng 3 - Khởi động MCP Server", mcp_run_ok))

    # ----------------- TỔNG KẾT BÁO CÁO -----------------
    print("\n" + "=" * 80)
    print("                       BẢNG TỔNG KẾT ĐÁNH GIÁ SẴN SÀNG")
    print("=" * 80)
    all_pass = True
    for name, status in report:
        if not status:
            all_pass = False
        print(f" {check_mark(status)} : {name}")
    print("=" * 80)

    if all_pass:
        print("\n🎉 XUẤT SẮC! HỆ THỐNG ĐÃ HOÀN TOÀN SẴN SÀNG 100% TRÊN MÁY TÍNH NÀY!")
    else:
        print("\n⚠️  CÒN MỘT SỐ HẠNG MỤC CHƯA CẤU HÌNH XONG. HÃY CHẠY: python master_deploy.py --all")

if __name__ == "__main__":
    main()
