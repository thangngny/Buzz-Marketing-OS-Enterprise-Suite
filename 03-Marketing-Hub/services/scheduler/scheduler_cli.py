#!/usr/bin/env python3
"""
Marketing Post Scheduler CLI
Provides command line interface to schedule, list, and cancel social media posts.
"""
import sys
import os
import time
import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).parent))
import scheduler_db

def parse_schedule_time(time_str: str) -> tuple[float, str]:
    """Parse various natural time expressions into epoch and ISO string."""
    now = datetime.now()
    s = time_str.strip().lower()

    # Relative formats: +10m, +1h, +30s
    rel_match = re.match(r'^\+(\d+)\s*(m|min|minute|minutes|h|hr|hour|hours|s|sec|second|seconds)?$', s)
    if rel_match:
        val = int(rel_match.group(1))
        unit = rel_match.group(2) or "m"
        if unit.startswith("h"):
            dt = now + timedelta(hours=val)
        elif unit.startswith("s"):
            dt = now + timedelta(seconds=val)
        else:
            dt = now + timedelta(minutes=val)
        return dt.timestamp(), dt.isoformat()

    # Time only: 11:00, 11:00:00, 11:00 am, 11h, 11h30
    time_match = re.match(r'^(\d{1,2})(?:[:h](\d{2}))?(?:\s*(am|pm))?$', s)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        ampm = time_match.group(3)
        if ampm == "pm" and hour < 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dt < now:
            # If time has passed today, schedule for tomorrow
            dt += timedelta(days=1)
        return dt.timestamp(), dt.isoformat()

    # Standard formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.timestamp(), dt.isoformat()
        except ValueError:
            pass

    raise ValueError(f"Không nhận diện được định dạng thời gian: '{time_str}'. Hỗ trợ: '11:00', '11h30', '+15m', '2026-10-28 11:00'.")

def cmd_add(args):
    epoch, iso = parse_schedule_time(args.time)
    media_url = getattr(args, "media_url", None) or getattr(args, "media", None)
    media_path = getattr(args, "file_path", None) or getattr(args, "file", None)
    task_id = scheduler_db.add_task(
        channel=args.channel,
        title=args.title or "Bài viết Marketing",
        text=args.text or "",
        scheduled_epoch=epoch,
        scheduled_iso=iso,
        content_type=args.type or "post",
        media_url=media_url,
        media_path=media_path,
        reply_channel_id=args.channel_id or "Assistant Marketing",
        requester=args.requester or "Chị Lina"
    )
    dt_str = datetime.fromtimestamp(epoch).strftime('%H:%M:%S %d/%m/%Y')
    mins_left = max(0, int((epoch - time.time()) / 60))
    
    result = {
        "success": True,
        "task_id": task_id,
        "channel": args.channel.upper(),
        "scheduled_time": dt_str,
        "countdown_minutes": mins_left,
        "title": args.title,
        "status": "pending"
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("==================================================================")
        print(f" ✅ ĐÃ ĐẶT LỊCH ĐĂNG BÀI THÀNH CÔNG (ID: {task_id})")
        print(f" 📱 Kênh: {args.channel.upper()}")
        print(f" ⏰ Thời gian hẹn: {dt_str} (còn khoảng {mins_left} phút)")
        print(f" 📌 Tiêu đề: {args.title}")
        print("==================================================================")
    return 0

def cmd_list(args):
    tasks = scheduler_db.list_tasks(status=args.status, limit=args.limit or 15)
    if args.json:
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
        return 0

    print("=================== DANH SÁCH LỊCH HẸN BÀI VIẾT ===================")
    if not tasks:
        print("Hiện không có bài viết nào trong hàng đợi.")
    for t in tasks:
        dt_str = datetime.fromtimestamp(t['scheduled_epoch']).strftime('%H:%M:%S %d/%m/%Y')
        status_icon = "⏳" if t['status'] == 'pending' else ("✅" if t['status'] == 'published' else "❌")
        print(f"{status_icon} [{t['id']}] [{t['channel'].upper()}] - {dt_str} ({t['status'].upper()})")
        print(f"    Tiêu đề: {t['title']}")
        if t['error_message']:
            print(f"    Lỗi: {t['error_message']}")
    print("==================================================================")
    return 0

def cmd_cancel(args):
    ok = scheduler_db.cancel_task(args.id)
    if ok:
        print(f"✅ Đã hủy lịch hẹn task {args.id}.")
    else:
        print(f"❌ Không tìm thấy task {args.id} hoặc task không ở trạng thái pending.")
    return 0 if ok else 1

def main():
    parser = argparse.ArgumentParser(description="Marketing Post Scheduler CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    p_add = subparsers.add_parser("add", help="Đặt lịch đăng bài mới")
    p_add.add_argument("--channel", "-c", required=True, help="Kênh: zalo, tiktok, youtube, facebook, linkedin")
    p_add.add_argument("--time", "-t", required=True, help="Thời gian: 11:00, 11h30, +15m, 2026-10-28 11:00")
    p_add.add_argument("--title", help="Tiêu đề bài viết/video")
    p_add.add_argument("--text", "-m", help="Nội dung Caption/Bài viết")
    p_add.add_argument("--media", "--media-url", dest="media_url", help="URL media (Blossom hoặc http)")
    p_add.add_argument("--file", "--file-path", dest="file_path", help="Đường dẫn file media trên máy")
    p_add.add_argument("--type", choices=["post", "video", "article"], default="video", help="Loại nội dung")
    p_add.add_argument("--channel-id", help="ID kênh Buzz để gửi thông báo kết quả")
    p_add.add_argument("--requester", default="Chị Lina", help="Người yêu cầu")
    p_add.add_argument("--json", action="store_true")

    p_list = subparsers.add_parser("list", help="Xem danh sách bài hẹn giờ")
    p_list.add_argument("--status", choices=["pending", "published", "failed", "cancelled"])
    p_list.add_argument("--limit", type=int, default=15)
    p_list.add_argument("--json", action="store_true")

    p_cancel = subparsers.add_parser("cancel", help="Hủy lịch hẹn bài viết")
    p_cancel.add_argument("--id", required=True, help="Task ID cần hủy")

    args = parser.parse_args()
    if args.subcommand == "add":
        return cmd_add(args)
    elif args.subcommand == "list":
        return cmd_list(args)
    elif args.subcommand == "cancel":
        return cmd_cancel(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
