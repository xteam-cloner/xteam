import os
from yt_dlp import YoutubeDL
from xteam.startup.loader import BASE_PATH 

DOWNLOAD_DIR = os.path.join(BASE_PATH, "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

COOKIES_FILE_PATH = os.path.join(BASE_PATH, "cookies.txt")

def get_ytdl_opts():
    return {
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "format": "bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "cookiefile": COOKIES_FILE_PATH if os.path.exists(COOKIES_FILE_PATH) else None,
        "noplaylist": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

async def download_song(url):
    opts = get_ytdl_opts()
    with YoutubeDL(opts) as ytdl:
        info_dict = ytdl.extract_info(url, download=True)
        file_path = ytdl.prepare_filename(info_dict)
        return file_path
        
