import os
import asyncio
import yt_dlp
from typing import Tuple, Union, Any
from youtubesearchpython import VideosSearch
from xteam import LOGS
from xteam.fns.helper import bash
import logging

logger = logging.getLogger(__name__)

FFMPEG_ABSOLUTE_PATH = "/usr/bin/ffmpeg"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
COOKIES_FILE_PATH = "cookies.txt"

def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        if not search["result"]:
            return 0
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        videoid = data["id"]
        artist = data["channel"]["name"]
        return [songname, url, duration, thumbnail, videoid, artist]
    except Exception as e:
        LOGS.info(str(e))
        return 0

async def ytdl(url: str, video_mode: bool = False) -> Tuple[int, Union[str, Any]]:
    loop = asyncio.get_running_loop()
    
    if not os.path.isdir(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR)
        except OSError as e:
            return 0, f"Gagal membuat direktori unduhan: {e}"

    def vc_audio_dl_sync():
        common_opts = {
            "js_runtimes": ["deno", "node"],
            "remote_components": "ejs:github",
            "allow_dynamic_mpd": True,
            "nocheckcertificate": True,
            "noplaylist": True,
            "quiet": True,
            "prefer_ffmpeg": True,
            "exec_path": FFMPEG_ABSOLUTE_PATH,
            "cookiefile": COOKIES_FILE_PATH,
        }
        
        if video_mode:
            ydl_opts_vc = {
                **common_opts,
                "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "merge_output_format": "mp4",
                "postprocessors": [
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": "mp4"
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": False,
                    },
                ],
            }
        else:
            ydl_opts_vc = {
                **common_opts,
                "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s"), 
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "opus",
                        "preferredquality": "128",
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": False,
                    },
                ],
            }
        
        video_id = 'unknown' 
        
        try:
            x = yt_dlp.YoutubeDL(ydl_opts_vc)
            info = x.extract_info(url, download=True)
            video_id = info.get('id', 'unknown')
            
            if video_mode:
                target_ext = 'mp4'
            else:
                target_ext = 'opus'

            final_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(video_id) and f.endswith(f'.{target_ext}')]
            
            if not final_files:
                logger.error(f"FFmpeg gagal membuat file {target_ext.upper()} setelah processing untuk ID: {video_id}.")
                raise FileNotFoundError(f"Konversi {target_ext.upper()} gagal.")
                
            final_link = os.path.join(DOWNLOAD_DIR, final_files[0])
            return final_link
            
        except Exception as e:
            logger.error(f"YTDL VC Error during sync operation: {e}", exc_info=True)
            
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(video_id):
                    try:
                        os.remove(os.path.join(DOWNLOAD_DIR, f))
                    except OSError:
                        pass 
            
            raise 

    try:
        downloaded_file = await loop.run_in_executor(None, vc_audio_dl_sync)
        return 1, downloaded_file
    except Exception as e:
        return 0, f"Error saat mengunduh atau konversi: {e}"
