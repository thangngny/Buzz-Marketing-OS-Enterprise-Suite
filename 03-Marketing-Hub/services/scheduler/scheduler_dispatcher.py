import os
import sys
import json
import time
import re
import subprocess
from pathlib import Path

# Setup paths
BUZZ_EXE = r"D:\Buzz\buzz.exe"
DEFAULT_RELAY = "wss://phamgianam.communities.buzz.xyz"
OWNER_PRIV = "ec269056bc62ba33e2df8b32f1656d8f15d2acdb22a5c397dba0b4f02020d0cc"
CACHE_DIR = Path(r"C:\Users\Admin\.buzz\cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(r"C:\Users\Admin\marketing-ai-system\src")

def resolve_media_file(media_url: str = None, media_path: str = None) -> str:
    """Ensure media exists locally; download from Blossom if necessary."""
    if media_path and os.path.isfile(media_path):
        return media_path

    if not media_url:
        return None

    # Check if URL contains SHA-256
    sha_match = re.search(r'([a-fA-F0-9]{64})', media_url)
    if sha_match:
        sha = sha_match.group(1).lower()
        ext = ".mp4"
        if ".jpg" in media_url or ".png" in media_url:
            ext = ".jpg"
        target_path = CACHE_DIR / f"{sha}{ext}"
        if target_path.exists() and target_path.stat().st_size > 0:
            return str(target_path)

        # Download using buzz CLI
        cmd = [
            BUZZ_EXE,
            "--relay", DEFAULT_RELAY,
            "--private-key", OWNER_PRIV,
            "media", "get", sha,
            "-o", str(target_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if res.returncode == 0 and target_path.exists() and target_path.stat().st_size > 0:
            return str(target_path)

    # Direct local check
    if os.path.isfile(media_url):
        return media_url

    return None

def dispatch_zalo(task: dict) -> dict:
    local_media = resolve_media_file(task.get("media_url"), task.get("media_path"))
    title = task.get("title") or "Minh Vân Logistics"
    text = task.get("text") or ""
    desc = text[:280].replace("\n", " ").strip() if text else title

    oa_cli = r"C:\Users\Admin\.buzz\services\zalo-oa\oa_cli.js"

    # Check if media is video
    is_video = local_media and (local_media.endswith(".mp4") or local_media.endswith(".mov") or task.get("content_type") == "video")

    if is_video:
        # Check or generate cover
        cover_path = CACHE_DIR / f"cover_{Path(local_media).stem}.jpg"
        if not cover_path.exists():
            subprocess.run(["ffmpeg", "-y", "-i", local_media, "-ss", "00:00:01", "-vframes", "1", str(cover_path)], capture_output=True)

        cmd = [
            "node", oa_cli, "video-article-create",
            "--file", local_media,
            "--title", title[:140],
            "--desc", desc,
            "--status", "show"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            out = json.loads(res.stdout.strip())
            if out.get("success"):
                vid = out.get("video_id")
                return {
                    "channel": "zalo",
                    "status": "published",
                    "type": "video",
                    "video_id": vid,
                    "title": title,
                    "raw_response": out
                }
            else:
                raise RuntimeError(f"Zalo video-article-create failed: {res.stdout.strip()} {res.stderr.strip()}")
        except Exception as e:
            if res.returncode == 0 and "success" in res.stdout:
                return {"channel": "zalo", "status": "published", "output": res.stdout.strip()}
            raise RuntimeError(f"Zalo error: {e} | stdout: {res.stdout} | stderr: {res.stderr}")
    else:
        # Normal text / article post
        cmd = [
            "node", oa_cli, "article-create",
            "--title", title[:140],
            "--desc", desc,
            "--content", text,
            "--cover", "https://zalo-article-photo.zadn.vn/331f575f9b03725d2b12#435204888",
            "--status", "show"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            out = json.loads(res.stdout.strip())
            if out.get("success"):
                return {"channel": "zalo", "status": "published", "type": "article", "raw_response": out}
            raise RuntimeError(f"Zalo article-create failed: {res.stdout} {res.stderr}")
        except Exception as e:
            raise RuntimeError(f"Zalo article error: {e} | stdout: {res.stdout}")

def dispatch_tiktok(task: dict) -> dict:
    from marketing_system.config import Settings
    from marketing_system.constants import Environment
    from marketing_system.connectors.tiktok import TikTokConnector
    
    local_media = resolve_media_file(task.get("media_url"), task.get("media_path"))
    if not local_media or not os.path.isfile(local_media):
        raise FileNotFoundError(f"Video file required for TikTok publish: {task.get('media_url')}")

    settings = Settings.from_env()
    settings.environment = Environment.PRODUCTION
    connector = TikTokConnector(settings)
    title = task.get("title") or task.get("text") or "Minh Van Logistics Video"
    return connector.upload_video_file(file_path=local_media, title=title[:100], privacy_level="PUBLIC_TO_EVERYONE", publish_mode="auto")

def dispatch_facebook(task: dict) -> dict:
    from marketing_system.config import Settings
    from marketing_system.constants import Environment
    from marketing_system.connectors.meta_ads import MetaAdsConnector
    
    settings = Settings.from_env()
    settings.environment = Environment.PRODUCTION
    connector = MetaAdsConnector(settings)
    text = task.get("text") or task.get("title") or ""
    return connector.publish_page_post(text)

def dispatch_linkedin(task: dict) -> dict:
    cli_path = r"C:\Users\Admin\.buzz\services\linkedin\linkedin_cli.js"
    text = task.get("text") or task.get("title") or ""
    cmd = ["node", cli_path, "post", "--text", text]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode == 0:
        return {"channel": "linkedin", "status": "published", "output": proc.stdout.strip()}
    raise RuntimeError(f"LinkedIn CLI failed: {proc.stderr.strip() or proc.stdout.strip()}")

def dispatch_youtube(task: dict) -> dict:
    from marketing_system.config import Settings
    from marketing_system.constants import Environment
    from marketing_system.connectors.youtube import YouTubeConnector
    
    local_media = resolve_media_file(task.get("media_url"), task.get("media_path"))
    if not local_media or not os.path.isfile(local_media):
        raise FileNotFoundError(f"Video file required for YouTube publish: {task.get('media_url')}")

    settings = Settings.from_env()
    settings.environment = Environment.PRODUCTION
    connector = YouTubeConnector(settings)
    title = task.get("title") or "Minh Van Logistics Video"
    description = task.get("text") or task.get("description") or ""
    privacy = task.get("privacy") or "public"

    return connector.upload_video(
        file_path=local_media,
        title=title[:100],
        description=description,
        privacy=privacy
    )

def notify_buzz(task: dict, success: bool, result_details: dict = None, error_msg: str = None):
    channel = task.get("reply_channel_id") or "Assistant Marketing"
    target_channel = task.get("channel", "").upper()
    title = task.get("title") or "Nội dung Marketing"
    
    dispatch_script = r"C:\Users\Admin\marketing-ai-system\scripts\buzz_dispatch.py"
    python_exe = r"C:\Users\Admin\marketing-ai-system\.venv\Scripts\python.exe"
    
    if success:
        live_link = ""
        if result_details:
            url = result_details.get("video_url") or result_details.get("permalink") or result_details.get("url")
            if url:
                live_link = f"\n🌐 **Link xem trực tiếp:** {url}\n"
        msg = f"""🎉 **[HỆ THỐNG XUẤT BẢN TỰ ĐỘNG - HOÀN TẤT]**
⏰ **Thời gian thực thi:** {time.strftime('%H:%M:%S %d/%m/%Y')}
📱 **Kênh xuất bản:** {target_channel}
📌 **Tiêu đề:** {title}
✅ **Trạng thái:** Đã đăng thành công theo đúng lịch hẹn của @Lina.{live_link}
👉 Bài viết/Video đã chính thức hiển thị trên kênh. Trợ lý tổng hợp báo cáo hoàn thành nhiệm vụ!"""
    else:
        msg = f"""⚠️ **[HỆ THỐNG XUẤT BẢN - CÓ LỖI XẢY RA]**
⏰ **Thời gian:** {time.strftime('%H:%M:%S %d/%m/%Y')}
📱 **Kênh:** {target_channel}
❌ **Lỗi:** {error_msg}
👉 @Lina @troly Vui lòng kiểm tra lại cấu hình hoặc quyền của kênh {target_channel}."""

    try:
        channel_id = channel
        # If human name, map to known ID
        if channel == "Assistant Marketing":
            channel_id = "a6399188-f310-4985-a218-35c96209945c"

        cmd = [
            BUZZ_EXE,
            "--relay", DEFAULT_RELAY,
            "--private-key", OWNER_PRIV,
            "messages", "send",
            "--channel", channel_id,
            "--content", msg
        ]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except Exception as e:
        print(f"Error sending Buzz notification: {e}", file=sys.stderr)

def execute_task(task: dict) -> dict:
    channel = task.get("channel", "").lower()
    if channel == "zalo" or "zalo" in channel:
        res = dispatch_zalo(task)
    elif channel == "tiktok":
        res = dispatch_tiktok(task)
    elif channel in ("facebook", "meta"):
        res = dispatch_facebook(task)
    elif channel == "linkedin":
        res = dispatch_linkedin(task)
    elif channel == "youtube":
        res = dispatch_youtube(task)
    else:
        raise NotImplementedError(f"Channel '{channel}' is not supported yet.")

    notify_buzz(task, success=True, result_details=res)
    return res
