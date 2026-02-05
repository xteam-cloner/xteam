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
        if not search["result"]: return 0
        data = search["result"][0]
        return [data["title"], data["link"], data["duration"], data["thumbnails"][0]["url"], data["id"], data["channel"]["name"]]
    except:
        return 0

async def ytdl(url: str, video_mode: bool = False) -> Tuple[int, str]:
    loop = asyncio.get_running_loop()
    def download_sync():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "cookiefile": COOKIES_FILE_PATH if os.path.exists(COOKIES_FILE_PATH) else None,
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "noplaylist": True,
        }
        
        if video_mode:
            opts["format"] = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        else:
            opts["format"] = "bestaudio/best"

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    try:
        path = await loop.run_in_executor(None, download_sync)
        return 1, os.path.abspath(path)
    except Exception as e:
        return 0, str(e)

async def get_playlist_ids(link, limit):
    command = f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download '{link}'"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    try:
        return [key for key in stdout.decode().split("\n") if key.strip() != ""]
    except:
        return []

async def cleanup_file(filepath: str, delay: int = 1800):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass
    
