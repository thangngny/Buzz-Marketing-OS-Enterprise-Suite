#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner for Marketing Hub MCP Server
Kiểm tra khả năng nạp các công cụ kết nối của Marketing Hub.
"""
import os
import sys
from pathlib import Path

# Ensure UTF-8 stdout/stderr on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    user_home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME") or Path.home())
    candidates = [
        user_home / "marketing-ai-system",
        Path("C:/Users/Admin/marketing-ai-system")
    ]
    repo_dir = None
    for c in candidates:
        if c.exists():
            repo_dir = c
            break

    if not repo_dir:
        print("[LỖI] Không tìm thấy thư mục marketing-ai-system!")
        sys.exit(1)

    sys.path.insert(0, str(repo_dir / "src"))
    sys.path.insert(0, str(repo_dir))

    print(f"[*] Đang nạp module từ: {repo_dir}")
    try:
        from marketing_system.mcp_server import server, platform
        print("\n✅ MCP Server nạp thành công!")
        print(f"Tên server: {server.name} ({getattr(server, 'title', '')})")
        print(f"Mô tả: {server.description}")
        print("\nCác công cụ kết nối được hỗ trợ (Platform Hub Specs):")
        specs = platform.hub.specs()
        for s in specs[:15]:
            print(f"  - {s.mcp_name} [{s.connector}] : {s.description}")
        if len(specs) > 15:
            print(f"  ... và {len(specs) - 15} công cụ kết nối khác.")
        print(f"\nTổng số công cụ: {len(specs)}")
        print("\n✅ Trạng thái: SẴN SÀNG KẾT NỐI VỚI BUZZ AGENTS")
    except Exception as e:
        print(f"[LỖI] Không thể nạp module mcp_server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
