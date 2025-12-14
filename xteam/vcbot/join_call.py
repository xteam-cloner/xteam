from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from pytgcalls.exceptions import NoActiveGroupCall 
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import VideoQuality, AudioQuality
from xteam import call_py, LOGS 

async def join_call(chat_id: int, link: str, video: bool = False, resolution: int = 480):
    
    if video:
        video_params = VideoQuality.HD_720p if resolution >= 720 else VideoQuality.SD_480p 
        video_flags = MediaStream.Flags.AUTO_DETECT
    else:
        video_params = VideoQuality.NONE
        video_flags = MediaStream.Flags.IGNORE

    try:
        await call_py.join_group_call(chat_id)
        LOGS.info(f"Successfully joined VC in {chat_id}.")
        
    except UserAlreadyParticipantError:
        LOGS.warning(f"Assistant already in VC in {chat_id}. Proceeding to play.")
        
    except NoActiveGroupCall:
        LOGS.warning(f"No active VC in {chat_id}. Cannot start playback.")
        return 0
        
    except Exception as e:
        LOGS.error(f"Error trying to join VC in {chat_id}: {e}")
        return 0

    try:
        await call_py.play(
            chat_id,
            MediaStream(
                media_path=link, 
                audio_parameters=AudioQuality.HIGH,
                video_parameters=video_params,
                video_flags=video_flags,
            ), 
        )
        LOGS.info(f"Started playback in {chat_id} successfully. Link: {link}")
        return 1
        
    except Exception as e:
        LOGS.error(f"Error during playback in {chat_id}: {e}")
        return 0
        
