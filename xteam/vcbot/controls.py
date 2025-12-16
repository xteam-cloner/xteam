from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from xteam import LOGS, call_py
from xteam.vcbot.queues import QUEUE, clear_queue, get_queue, pop_an_item
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError

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
    bot_id = None
    
    try:
        bot_me = await call_py.client.get_me()
        bot_id = bot_me.id
    except Exception as e:
        LOGS.error(f"FATAL: Gagal mendapatkan ID bot dari call_py.client.get_me(): {e}")
        return

    if not bot_id:
        return
        
    try:
        bot_peer = await call_py.resolve_peer(bot_id)

        await call_py.set_call_status(
            chat_id,
            muted_status=False,  
            video_paused=False,
            video_stopped=True,
            presentation_paused=False,
            participant=bot_peer,
        )
    except Exception as e:
        LOGS.error(f"Error setting call status (unmute): {e}")

async def skip_current_song(chat_id: int):
    from plugins.vcplug import play_next_song
    
    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return 0 
    
    result = await play_next_song(chat_id) 
    
    if result is None:
        return 1
    else:
        return result
        
