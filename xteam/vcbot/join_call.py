from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
#from telethon.tl.types.phone import GroupCall
from pytgcalls.exceptions import NoActiveGroupCall 
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import VideoQuality, AudioQuality
from xteam import call_py, LOGS, bot
import os
import logging

FILE_PATH = os.path.join(os.getcwd(), 'resources', 'audio-man.mp3') 


async def join_call(chat_id: int, link: str, video: bool = False, resolution: int = 480):
    
    try:
        params = None(
            start_call=True,
        )
        
        await bot.join_group_call(
            chat_id,
            join_as=chat_id, 
            params=params
        )
        
        LOGS.info(f"Successfully joined VC in {chat_id} using xteam.bot.")
        
    except UserAlreadyParticipantError:
        LOGS.warning(f"Assistant already in VC in {chat_id}. Proceeding to play.")
        
    except Exception as e:
        if 'NoActiveGroupCall' in str(e):
             LOGS.warning(f"No active VC in {chat_id}. Cannot start playback.")
             return 0
        LOGS.error(f"Error trying to join VC in {chat_id}: {e}")
        return 0

    try:
        
        if video:
            video_params = VideoQuality.HD_720p if resolution >= 720 else VideoQuality.SD_480p 
            stream = MediaStream(
                media_path=link, 
                audio_parameters=AudioQuality.HIGH,
                video_parameters=video_params,
            )
        else:
            stream = MediaStream(
                media_path=link, 
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE, 
            )
            
        await call_py.play(chat_id, stream)
        
        LOGS.info(f"Started playback in {chat_id} successfully. Link: {link}")
        return 1
        
    except Exception as e:
        LOGS.error(f"Error during playback in {chat_id}: {e}")
        return 0
        
