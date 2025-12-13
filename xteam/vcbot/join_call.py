# File: xteam/vcbot/join_call.py

from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from pytgcalls.exceptions import NoActiveGroupCall 
from pytgcalls.types import MediaStream 
from xteam import call_py, LOGS 

async def join_call(chat_id: int, link: str, video: bool = False):
    
    # 1. Tentukan Flags Video
    if video:
        video_flag_value = MediaStream.Flags.AUTO_DETECT 
    else:
        video_flag_value = MediaStream.Flags.IGNORE 

    try:
        await call_py.play(
            chat_id,
            MediaStream(
                media_path=link, 
                video_flags=video_flag_value,
                # --- PARAMETER FFmpeg UNTUK MENINGKATKAN STABILITAS ---
                # '-preset veryfast': Mengurangi beban CPU dan mempercepat encoding.
                # '-strict -2': Menangani beberapa masalah codec non-standar.
                ffmpeg_parameters='-preset veryfast -strict -2', 
                # -----------------------------------------------------
            ), 
        )
        LOGS.info(f"Joined VC and started playback in {chat_id} successfully.")

    except NoActiveGroupCall:
        LOGS.warning(f"No active VC in {chat_id}. Cannot start playback.")
        return 0
        
    except UserAlreadyParticipantError:
        LOGS.info(f"Assistant already in VC in {chat_id}. Playback should start.")
        return 1
        
    except Exception as e:
        LOGS.error(f"Error joining VC in {chat_id}: {e}")
        return 0
        
