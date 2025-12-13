# Man - UserBot
# Copyright (c) 2022 Man-Userbot
# Credits: @mrismanaziz || https://github.com/mrismanaziz
#
# This file is a part of < https://github.com/mrismanaziz/Man-Userbot/ >
# t.me/SharingUserbot & t.me/Lunatic0de


# --- PERBAIKAN IMPORT START ---
# Impor lama dari input_stream dan input_stream.quality dihapus.
# Impor baru menggunakan MediaStream, AudioQuality, dan VideoQuality (yang menggantikan kelas kualitas lama).

from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

# --- PERBAIKAN IMPORT END ---

from xteam import LOGS, call_py
from xteam.vcbot.queues import QUEUE, clear_queue, get_queue, pop_an_item


async def skip_item(chat_id: int, x: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    try:
        songname = chat_queue[x][0]
        chat_queue.pop(x)
        return songname
    except Exception as e:
        LOGS.info(str(e))
        return 0

async def play_next_stream(chat_id: int, file_path: str, is_video: bool = False, ffmpeg_seek: str = None):
    # Implementasikan logika untuk memulai lagu berikutnya
    pass
    

async def skip_current_song(chat_id: int):
    if chat_id not in QUEUE:
        return 0
    
    chat_queue = get_queue(chat_id)
    
    if len(chat_queue) == 1:
        await call_py.leave_group_call(chat_id)
        clear_queue(chat_id)
        return 1
        
    songname = chat_queue[1][0]
    url = chat_queue[1][1]
    link = chat_queue[1][2]
    type = chat_queue[1][3]
    RESOLUSI = chat_queue[1][4]

    # --- PERBAIKAN LOGIKA STREAMING ---
    
    if type == "Audio":
        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH, # Setara dengan HighQualityAudio()
            # Hanya audio yang dibutuhkan
            audio_flags=MediaStream.Flags.REQUIRED, 
            video_flags=MediaStream.Flags.IGNORE,
        )
        
    elif type == "Video":
        # Tentukan kualitas video berdasarkan RESOLUSI
        if RESOLUSI == 720:
            video_quality = VideoQuality.HD_720p # Setara dengan HighQualityVideo()
        elif RESOLUSI == 480:
            video_quality = VideoQuality.SD_480p # Setara dengan MediumQualityVideo()
        elif RESOLUSI == 360:
            video_quality = VideoQuality.SD_360p # Setara dengan LowQualityVideo()
        else:
            # Fallback jika resolusi tidak cocok
            video_quality = VideoQuality.SD_480p 

        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH, # Audio tetap kualitas tinggi
            video_parameters=video_quality,
            # Audio dan video dibutuhkan
            audio_flags=MediaStream.Flags.REQUIRED, 
            video_flags=MediaStream.Flags.REQUIRED,
        )
    
    await call_py.change_stream(chat_id, stream)
    pop_an_item(chat_id)
    return [songname, link, type]
    
