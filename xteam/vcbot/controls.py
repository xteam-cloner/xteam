from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from xteam import LOGS, call_py, bot
from xteam.vcbot.queues import QUEUE, clear_queue, get_queue, pop_an_item
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.users import GetFullUserRequest
import os, contextlib

async def play_next_stream(chat_id: int, file_path: str, is_video: bool = False, ffmpeg_seek: str = None):
    pass

async def skip_item(chat_id: int, x: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    try:
        songname = chat_queue[x][0]
        file_path_to_delete = chat_queue[x][1]
        chat_queue.pop(x)
        
        if os.path.exists(file_path_to_delete):
            with contextlib.suppress(Exception):
                os.remove(file_path_to_delete)
                
        return songname
    except Exception as e:
        LOGS.info(str(e))
        return 0

async def skip_current_song(chat_id: int):
    from plugins.vcplug import play_next_song
    
    if chat_id not in QUEUE:
        return 0 
    
    if QUEUE[chat_id]:
        pop_an_item(chat_id) 
    
    if not QUEUE[chat_id]:
         return 1
         
    result = await play_next_song(chat_id) 
    
    if result is None:
        return 1
    else:
        return result
        
