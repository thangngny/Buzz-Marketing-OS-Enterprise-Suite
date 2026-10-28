import sqlite3
import os
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path

DB_DIR = Path(r"C:\Users\Admin\.buzz\services\scheduler")
DB_PATH = DB_DIR / "scheduler.db"

def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                content_type TEXT NOT NULL DEFAULT 'post',
                title TEXT,
                text TEXT NOT NULL,
                media_url TEXT,
                media_path TEXT,
                scheduled_epoch REAL NOT NULL,
                scheduled_iso TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                reply_channel_id TEXT,
                requester TEXT,
                retries INTEGER DEFAULT 0,
                error_message TEXT,
                post_result TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status_epoch ON scheduled_posts (status, scheduled_epoch)")
    conn.close()

def add_task(channel: str, text: str, scheduled_epoch: float, scheduled_iso: str, 
             title: str = "", content_type: str = "post", media_url: str = None, 
             media_path: str = None, reply_channel_id: str = None, requester: str = None) -> str:
    init_db()
    conn = get_connection()
    task_id = f"sch_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    now = time.time()
    with conn:
        conn.execute("""
            INSERT INTO scheduled_posts 
            (id, channel, content_type, title, text, media_url, media_path, scheduled_epoch, scheduled_iso, status, reply_channel_id, requester, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
        """, (task_id, channel.lower().strip(), content_type, title, text, media_url, media_path, scheduled_epoch, scheduled_iso, reply_channel_id, requester, now, now))
    conn.close()
    return task_id

def get_pending_tasks(cutoff_epoch: float = None):
    init_db()
    if cutoff_epoch is None:
        cutoff_epoch = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM scheduled_posts 
        WHERE status = 'pending' AND scheduled_epoch <= ?
        ORDER BY scheduled_epoch ASC
    """, (cutoff_epoch,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def update_task_status(task_id: str, status: str, error_message: str = None, post_result: str = None):
    init_db()
    conn = get_connection()
    now = time.time()
    with conn:
        conn.execute("""
            UPDATE scheduled_posts
            SET status = ?, error_message = ?, post_result = ?, updated_at = ?
            WHERE id = ?
        """, (status, error_message, post_result, now, task_id))
    conn.close()

def list_tasks(status: str = None, limit: int = 20):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM scheduled_posts WHERE status = ? ORDER BY scheduled_epoch DESC LIMIT ?", (status, limit))
    else:
        cursor.execute("SELECT * FROM scheduled_posts ORDER BY scheduled_epoch DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def cancel_task(task_id: str) -> bool:
    init_db()
    conn = get_connection()
    with conn:
        res = conn.execute("UPDATE scheduled_posts SET status = 'cancelled', updated_at = ? WHERE id = ? AND status = 'pending'", (time.time(), task_id))
        cancelled = res.rowcount > 0
    conn.close()
    return cancelled

if __name__ == "__main__":
    init_db()
    print("Scheduler DB initialized at:", DB_PATH)
