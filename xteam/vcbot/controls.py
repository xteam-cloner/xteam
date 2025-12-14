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
    

async def skip_current_song(chat_id: int):
    if chat_id not in QUEUE:
        return 0
    
    chat_queue = get_queue(chat_id)
    
    if len(chat_queue) == 1:
        try:
            await call_py.leave_call(chat_id)
        except Exception as e:
            LOGS.info(f"Error leaving call: {e}")
            pass
            
        clear_queue(chat_id)
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
    except Exception as e:
        LOGS.error(f"Error playing next stream: {e}")
        pop_an_item(chat_id)
        return await skip_current_song(chat_id)
        
    pop_an_item(chat_id)
    return [songname, link, type]
    
