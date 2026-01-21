import os
import asyncio
import yt_dlp
import logging
from typing import Tuple, Union, Any, List
from youtubesearchpython import VideosSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
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

async def ytdl(url: str, mode: str = "audio") -> Tuple[int, str]:
    loop = asyncio.get_running_loop()

    def download_sync():
        common_opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "cookiefile": COOKIES_FILE_PATH if os.path.exists(COOKIES_FILE_PATH) else None,
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        }

        if mode == "video":
            common_opts["format"] = "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
            target_ext = "mp4"

        elif mode == "song_audio":
            common_opts["format"] = "bestaudio/best"
            common_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            target_ext = "mp3"

        elif mode == "song_video":
            common_opts["format"] = "bestvideo+bestaudio/best"
            common_opts["merge_output_format"] = "mp4"
            target_ext = "mp4"

        else:
            common_opts["format"] = "bestaudio/best"
            common_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
                "preferredquality": "128",
            }]
            target_ext = "opus"

        with yt_dlp.YoutubeDL(common_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info['id']
            file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{target_ext}")

            if os.path.exists(file_path):
                return file_path

            ydl.download([url])
            return file_path

    try:
        result_path = await loop.run_in_executor(None, download_sync)
        return 1, result_path
    except Exception as e:
        logger.error(f"Download Error: {e}")
        return 0, str(e)
            
