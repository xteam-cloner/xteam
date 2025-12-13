# File: xteam/vcbot/join_call.py

from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from pytgcalls.exceptions import NoActiveGroupCall 
from pytgcalls.types import MediaStream 
from xteam import call_py, LOGS 

async def join_call(chat_id: int, link: str, video: bool = False):
    
    # 1. Tentukan Flags yang Benar
    # Mengakses Flags dari MediaStream karena class Flags ada di dalamnya
    if video:
        # Jika True, kita asumsikan streaming video diperlukan/diinginkan
        video_flag_value = MediaStream.Flags.AUTO_DETECT 
    else:
        # Jika False, kita setel IGNORE agar tidak mencari sumber video
        video_flag_value = MediaStream.Flags.IGNORE 

    try:
        # Menggunakan metode play() karena join_group_call tidak ada di PyTgCalls v2.2.8
        await call_py.play(
            chat_id,
            MediaStream(
                media_path=link, 
                video_flags=video_flag_value # Melewatkan objek Flags, bukan boolean
            ), 
        )
        LOGS.info(f"Joined VC and started playback in {chat_id} successfully.")

    except NoActiveGroupCall:
        LOGS.warning(f"No active VC in {chat_id}. Cannot start playback.")
        return 0
        
    except UserAlreadyParticipantError:
        # Pengecualian ini menangani kasus jika bot sudah ada di VC
        LOGS.info(f"Assistant already in VC in {chat_id}. Playback should start.")
        return 1
        
    except Exception as e:
        LOGS.error(f"Error joining VC in {chat_id}: {e}")
        return 0
        
