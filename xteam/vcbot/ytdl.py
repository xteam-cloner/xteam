# Man - UserBot
# Copyright (c) 2022 Man-Userbot
# Credits: @mrismanaziz || https://github.com/mrismanaziz
#
# This file is a part of < https://github.com/mrismanaziz/Man-Userbot/ >
# t.me/SharingUserbot & t.me/Lunatic0de

from youtubesearchpython import VideosSearch

from xteam import LOGS
from plugins import bash


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        videoid = data["id"]
        return [songname, url, duration, thumbnail, videoid]
    except Exception as e:
        LOGS.info(str(e))
        return 0


# Import atau definisikan kembali DOWNLOAD_DIR
import os
import yt_dlp
# Asumsi DOWNLOAD_DIR diimpor atau didefinisikan secara global
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads") 
# ... (pastikan folder dibuat jika belum ada) ...

async def ytdl(url):
    """
    Mengunduh audio dari URL YouTube dan menyimpannya di DOWNLOAD_DIR.
    """
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    ydl_opts = {
        # *** GANTI outtmpl MENGGUNAKAN ID UNTUK NAMA FILE BERSIH ***
        # '%(id)s' adalah ID video YouTube, selalu unik dan pendek.
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        'extract_flat': 'in_playlist',
        
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'ogg',
            'preferredquality': '192',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Mendapatkan ID unik untuk membangun nama file
            video_id = info_dict.get('id', 'unknown') 

            # Menggunakan ID video untuk membuat jalur file OGG akhir
            final_link = os.path.join(DOWNLOAD_DIR, f"{video_id}.ogg")
            
            # Jika Anda mengunduh, Anda mungkin ingin melakukan pemeriksaan
            # apakah file tersebut benar-benar ada di final_link sebelum kembali.
            
            return 1, final_link
            
    except Exception as e:
        return 0, f"Error: {e}"
    
