#!/usr/bin/env python3
"""
Marketing Post & Task Scheduler Daemon
Monitors scheduled marketing posts across Zalo, TikTok, Facebook, LinkedIn, YouTube,
and dispatches them at the exact scheduled timestamp with automatic Buzz feedback.
"""
import sys
import os
import time
import json
import argparse
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).parent))
import scheduler_db
import scheduler_dispatcher

def tick_once():
    now_epoch = time.time()
    pending = scheduler_db.get_pending_tasks(cutoff_epoch=now_epoch)
    if not pending:
        return 0

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Tìm thấy {len(pending)} tác vụ đến hạn thực thi:")
    processed = 0
    for task in pending:
        task_id = task["id"]
        channel = task["channel"]
        print(f"  --> Bắt đầu xử lý task {task_id} [{channel.upper()}] - Tiêu đề: {task.get('title')}")
        scheduler_db.update_task_status(task_id, "processing")
        try:
            res = scheduler_dispatcher.execute_task(task)
            scheduler_db.update_task_status(task_id, "published", post_result=json.dumps(res, ensure_ascii=False))
            print(f"  ✅ Hoàn tất thành công task {task_id}!")
            processed += 1
        except Exception as e:
            err_str = str(e)
            print(f"  ❌ Thất bại task {task_id}: {err_str}", file=sys.stderr)
            scheduler_db.update_task_status(task_id, "failed", error_message=err_str)
            try:
                scheduler_dispatcher.notify_buzz(task, success=False, error_msg=err_str)
            except Exception:
                pass
    return processed

def run_daemon(interval_sec: int = 15):
    print("==================================================================")
    print(" 🚀 MARKETING POST SCHEDULER DAEMON IS RUNNING (AUTONOMOUS)")
    print(f" ⏱️  Chu kỳ quét: {interval_sec} giây | Database: {scheduler_db.DB_PATH}")
    print("==================================================================")
    while True:
        try:
            tick_once()
        except Exception as e:
            print(f"[Daemon Error] {e}", file=sys.stderr)
        time.sleep(interval_sec)

def main():
    parser = argparse.ArgumentParser(description="Marketing Post Scheduler Daemon")
    parser.add_argument("--once", action="store_true", help="Chạy 1 lần rồi thoát (Tick once)")
    parser.add_argument("--interval", type=int, default=15, help="Khoảng thời gian quét (giây)")
    args = parser.parse_args()

    if args.once:
        count = tick_once()
        print(f"Đã xử lý {count} tác vụ.")
        return 0
    else:
        run_daemon(interval_sec=args.interval)

if __name__ == "__main__":
    main()
