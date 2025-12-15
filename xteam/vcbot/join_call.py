from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from telethon.tl import functions
from telethon.tl.types import InputPeerChannel, InputPeerChat
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyInGroupCall
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import VideoQuality, AudioQuality
from xteam import call_py, LOGS, bot
import os
import logging

FILE_PATH = os.path.join(os.getcwd(), 'resources', 'audio-man.mp3') 


async def join_call(chat_id: int, link: str, video: bool = False, resolution: int = 480):
    
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
    except Exception as e:
        LOGS.error(f"Gagal menyiapkan MediaStream: {e}")
        return 0

    try:
        await call_py.play(chat_id, stream)
        
        LOGS.info(f"Berhasil memulai playback/bergabung di VC {chat_id}. Link: {link}")
        return 1
        
    except NoActiveGroupCall:
        LOGS.warning(f"No active VC in {chat_id}. Cannot start playback.")
        return 0
        
    except AlreadyInGroupCall:
        LOGS.warning(f"Asisten sudah ada di VC {chat_id}. Mencoba mengganti stream...")
        try:
             await call_py.change_stream(chat_id, stream)
             LOGS.info(f"Stream berhasil diganti di {chat_id}.")
             return 1
        except Exception as e:
             LOGS.error(f"Gagal mengganti stream di VC {chat_id}: {e}")
             return 0

    except Exception as e:
        LOGS.error(f"Error fatal selama playback/join di {chat_id}: {type(e).__name__} - {e}")
        return 0
        
