from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
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
    pass

async def unmute_self(chat_id: int):
    # FUNGSI UNMUTE BARU
    bot_id = await call_py.get_id() 
    bot_peer = await call_py.resolve_peer(bot_id)

    try:
        await call_py.set_call_status(
            chat_id,
            muted_status=False,  
            video_paused=False,
            video_stopped=True,
            presentation_paused=False,
            participant=bot_peer,
        )
        LOGS.info(f"Self-unmute executed successfully in chat {chat_id}")
    except Exception as e:
        LOGS.error(f"Error setting call status (unmute): {e}")
    

async def skip_current_song(chat_id: int):
    from plugins.vcplug import play_next_song
    
    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return 0 
    
    # Memicu transisi yang sudah benar: menghapus lagu lama & memutar lagu baru.
    await play_next_song(chat_id) 
    
    # Ambil lagu yang BARU diputar (sekarang di indeks 0 yang baru) untuk respons
    chat_queue = get_queue(chat_id)
    
    if chat_queue:
        # songname, file_path, url_ref, media_type, resolution
        new_songname, new_url, new_link, new_type, new_RESOLUSI = chat_queue[0]
        return [new_songname, new_link, new_type] 
    else:
        # Antrian kosong setelah skip
        return 1
        
    songname = chat_queue[1][0]
    url = chat_queue[1][1]
    link = chat_queue[1][2]
    type = chat_queue[1][3]
    RESOLUSI = chat_queue[1][4]

    if type == "Audio":
        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH, 
            audio_flags=MediaStream.Flags.REQUIRED, 
            video_flags=MediaStream.Flags.IGNORE,
        )
        
    elif type == "Video":
        if RESOLUSI == 720:
            video_quality = VideoQuality.HD_720p
        elif RESOLUSI == 480:
            video_quality = VideoQuality.SD_480p
        elif RESOLUSI == 360:
            video_quality = VideoQuality.SD_360p
        else:
            video_quality = VideoQuality.SD_480p 

        stream = MediaStream(
            media_path=url,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=video_quality,
            audio_flags=MediaStream.Flags.REQUIRED, 
            video_flags=MediaStream.Flags.REQUIRED,
        )
    
    try:
        await call_py.play(chat_id, stream)
        # Panggil unmute setelah berhasil play
        await unmute_self(chat_id) 
        
    except Exception as e:
        LOGS.error(f"Error playing next stream: {e}. URL: {url}")
        pop_an_item(chat_id)
        return await skip_current_song(chat_id)
        
    pop_an_item(chat_id)
    return [songname, link, type]
    
