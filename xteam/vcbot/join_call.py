import os
import logging
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from telethon.tl import functions
from telethon.tl.types import InputPeerChannel, InputPeerChat
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    LiveStreamFound,
)
from ntgcalls import TelegramServerError, ConnectionNotFound 

from pytgcalls.types import MediaStream
from pytgcalls.types.stream import VideoQuality, AudioQuality
from xteam import call_py, LOGS, asst
from xteam.configs import Var

async def join_call(chat_id: int, link: str, title: str, duration: str, chat_name: str, video: bool = False):
    try:
        if video:
            stream = MediaStream(
                media_path=link, 
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
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
        LOGS.info(f"Berhasil memulai playback di VC {chat_id}. Link: {link}")
        
        if Var.LOG_CHANNEL:
            text = (
                "<blockquote>"
                "🎵 Music Started\n\n"
                f"📌 Title: <code>{title}</code>\n"
                f"🕒 Duration: <code>{duration}</code>\n"
                f"👥 Group: <code>{chat_name}</code>\n"
                f"🆔 ID: <code>{chat_id}</code>"
                "</blockquote>"
            )
            await asst.send_message(Var.LOG_CHANNEL, text, parse_mode='html')
            
        return 1
        
    except NoActiveGroupCall:
        LOGS.warning(f"Tidak ada VC aktif di {chat_id}. Gagal memutar.")
        return 0
        
    except LiveStreamFound:
        LOGS.warning(f"Ditemukan live stream di {link}. Playback gagal.")
        return 0
    
    except ConnectionNotFound:
        LOGS.error(f"Koneksi terputus saat mencoba join VC {chat_id}.")
        return 0

    except TelegramServerError:
        LOGS.error(f"Server Telegram sedang bermasalah di VC {chat_id}.")
        return 0
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'already' in error_msg:
             LOGS.warning(f"Asisten sudah ada di VC {chat_id}. Mencoba mengganti stream...")
             try:
                 await call_py.change_stream(chat_id, stream)
                 LOGS.info(f"Stream berhasil diperbarui di {chat_id}.")
                 return 1
             except Exception as sub_e:
                 LOGS.error(f"Gagal mengganti stream di VC {chat_id}: {sub_e}")
                 return 0

        LOGS.error(f"Error tidak dikenal di {chat_id}: {e}")
        return 0
        
