#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Deployment Orchestrator for Buzz Marketing OS Full Enterprise Suite
Tự động hóa hoàn toàn quy trình triển khai 3 Tầng trên bất kỳ máy tính nào.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SUITE_ROOT = Path(__file__).resolve().parent

def run_script(script_path, args=None):
    if not script_path.exists():
        print(f"[LỖI] Không tìm thấy file: {script_path}")
        return False
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    print(f"\n[*] Đang thực thi: {script_path.name} ...")
    res = subprocess.run(cmd, cwd=str(script_path.parent))
    return res.returncode == 0

def deploy_layer_1(community_url=None, nsec=None):
    print("\n" + "=" * 80)
    print(">>> TIẾN TRÌNH 1: TRIỂN KHAI TẦNG 1 (KHUNG PHÒNG BAN & AGENT NOSTR)")
    print("=" * 80)
    # Bước 1.1: Đồng bộ Agents & Teams vào ứng dụng Buzz Desktop cục bộ
    setup_agents_script = SUITE_ROOT / "01-Community-OS" / "setup_managed_agents.py"
    cmd_agents = []
    if community_url:
        cmd_agents.extend(["--relay", community_url])
    run_script(setup_agents_script, cmd_agents)

    # Bước 1.2: Mở toàn quyền (Universal Public Access: anyone, bypass-permissions, Kind 10100)
    unlock_script = SUITE_ROOT / "01-Community-OS" / "unlock_full_permissions.py"
    cmd_unlock = ["--no-launch"]
    if community_url:
        cmd_unlock.extend(["--relay", community_url])
    run_script(unlock_script, cmd_unlock)

    # Bước 1.3: Xây dựng Kênh phòng ban & Phân quyền trên Community Relay
    injector_script = SUITE_ROOT / "01-Community-OS" / "inject_framework.py"
    cmd_args = []
    if community_url:
        cmd_args.extend(["--url", community_url])
    if nsec:
        cmd_args.extend(["--nsec", nsec])
    return run_script(injector_script, cmd_args)

def deploy_layer_2():
    print("\n" + "=" * 80)
    print(">>> TIẾN TRÌNH 2: TRIỂN KHAI TẦNG 2 (BỘ XOAY TÀI KHOẢN CODEX ROTATOR)")
    print("=" * 80)
    setup_rotator_script = SUITE_ROOT / "02-Codex-Rotator" / "setup_rotator.py"
    return run_script(setup_rotator_script)

def deploy_layer_3():
    print("\n" + "=" * 80)
    print(">>> TIẾN TRÌNH 3: TRIỂN KHAI TẦNG 3 (MARKETING SYSTEM HUB MCP)")
    print("=" * 80)
    setup_hub_script = SUITE_ROOT / "03-Marketing-Hub" / "setup_hub.py"
    return run_script(setup_hub_script)

def deploy_harnesses():
    print("\n" + "=" * 80)
    print(">>> TIẾN TRÌNH 4: CÀI ĐẶT HARNESSES CHO BUZZ DESKTOP")
    print("=" * 80)
    install_harnesses_script = SUITE_ROOT / "04-Buzz-Harnesses" / "install_harnesses.py"
    return run_script(install_harnesses_script)

def verify_all():
    print("\n" + "=" * 80)
    print(">>> TIẾN TRÌNH KIỂM THỬ: CHUẨN ĐOÁN TOÀN DIỆN CẢ 3 TẦNG")
    print("=" * 80)
    verify_script = SUITE_ROOT / "verify_system.py"
    return run_script(verify_script)

def interactive_menu():
    while True:
        print("\n" + "=" * 80)
        print("          BUZZ MARKETING OS FULL ENTERPRISE - BỘ ĐIỀU PHỐI TRIỂN KHAI")
        print("=" * 80)
        print("  [1] Triển khai TOÀN BỘ 3 TẦNG (Full Enterprise Setup)")
        print("  [2] Chỉ triển khai Tầng 1 (Khung 28 phòng ban & 25 Agent vào Community)")
        print("  [3] Chỉ triển khai Tầng 2 (Bộ xoay tài khoản Codex Rotator)")
        print("  [4] Chỉ triển khai Tầng 3 (Marketing System Hub MCP Server)")
        print("  [5] Cài đặt / Cập nhật Custom Harnesses cho Buzz Desktop")
        print("  [6] Chạy chuẩn đoán kiểm tra hệ thống (Verify System)")
        print("  [0] Thoát")
        print("=" * 80)
        
        choice = input("Nhập lựa chọn của bạn [0-6]: ").strip()
        if choice == "0":
            print("Đã thoát trình triển khai.")
            break
        elif choice == "1":
            print("\n>>> BẮT ĐẦU TRIỂN KHAI TRỌN GÓI 3 TẦNG <<<")
            deploy_layer_2()
            deploy_layer_3()
            deploy_harnesses()
            deploy_layer_1()
            verify_all()
        elif choice == "2":
            deploy_layer_1()
        elif choice == "3":
            deploy_layer_2()
        elif choice == "4":
            deploy_layer_3()
        elif choice == "5":
            deploy_harnesses()
        elif choice == "6":
            verify_all()
        else:
            print("[!] Lựa chọn không hợp lệ, vui lòng thử lại.")

def main():
    parser = argparse.ArgumentParser(description="Master Deployment Orchestrator for Buzz Marketing OS")
    parser.add_argument("--all", action="store_true", help="Triển khai toàn bộ 3 tầng và kiểm tra")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], help="Chỉ triển khai tầng tương ứng")
    parser.add_argument("--harnesses", action="store_true", help="Cài đặt Buzz Custom Harnesses")
    parser.add_argument("--verify", action="store_true", help="Chạy kiểm tra chuẩn đoán")
    parser.add_argument("--community-url", type=str, help="URL Community cho Tầng 1")
    parser.add_argument("--nsec", type=str, help="Mã khóa nsec cho Tầng 1")

    args = parser.parse_args()

    # Nếu có cờ dòng lệnh
    if args.all:
        deploy_layer_2()
        deploy_layer_3()
        deploy_harnesses()
        deploy_layer_1(args.community_url, args.nsec)
        verify_all()
    elif args.layer == 1:
        deploy_layer_1(args.community_url, args.nsec)
    elif args.layer == 2:
        deploy_layer_2()
    elif args.layer == 3:
        deploy_layer_3()
    elif args.harnesses:
        deploy_harnesses()
    elif args.verify:
        verify_all()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
