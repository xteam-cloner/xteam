import os
import asyncio
import yt_dlp
import logging
from typing import Tuple, Union, Any, List
from youtubesearchpython import VideosSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = "downloads"
COOKIES_FILE_PATH = "cookies.txt"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def ytsearch(query: str) -> Union[List[Any], int]:
    try:
        search = VideosSearch(query, limit=1).result()
        if not search["result"]:
            return 0
        data = search["result"][0]
        return [
            data["title"],
            data["link"],
            data["duration"],
            data["thumbnails"][0]["url"],
            data["id"],
            data["channel"]["name"]
        ]
    except Exception as e:
        logger.error(f"Search Error: {e}")
        return 0

async def ytdl(url: str, video_mode: bool = False, mode: str = None) -> Tuple[int, str]:
    loop = asyncio.get_running_loop()

    def download_sync():
        common_opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "cookiefile": COOKIES_FILE_PATH if os.path.exists(COOKIES_FILE_PATH) else None,
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        }

        if mode:
            selected_mode = mode
        elif video_mode:
            selected_mode = "video"
        else:
            selected_mode = "m4a"

        if selected_mode == "video":
            common_opts["format"] = "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            common_opts["merge_output_format"] = "mp4"
            target_ext = "mp4"
        elif selected_mode == "song_audio":
            common_opts["format"] = "bestaudio/best"
            common_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "128",
            }]
            target_ext = "m4a"
        else:
            common_opts["format"] = "bestaudio[ext=m4a]/bestaudio"
            target_ext = "m4a"

        with yt_dlp.YoutubeDL(common_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(video_id) and f.endswith(f'.{target_ext}')]
            if files:
                return os.path.abspath(os.path.join(DOWNLOAD_DIR, files[0]))
            return os.path.abspath(os.path.join(DOWNLOAD_DIR, f"{video_id}.{target_ext}"))

    try:
        result_path = await loop.run_in_executor(None, download_sync)
        return 1, result_path
    except Exception as e:
        logger.error(f"Download Error: {e}")
        return 0, str(e)

async def cleanup_file(filepath: str, delay: int = 1800):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"File dibersihkan: {filepath}")
    except Exception as e:
        logger.error(f"Gagal membersihkan file: {e}")
            
