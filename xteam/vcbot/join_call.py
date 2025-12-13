# File: xteam/vcbot/join_call.py

from telethon.errors.rpcerrorlist import UserAlreadyParticipantError 
from pytgcalls.exceptions import NoActiveGroupCall 
from pytgcalls.types import MediaStream # Diperlukan untuk join_group_call
from xteam import call_py, LOGS 

async def join_call(chat_id: int, link: str, video: bool = False):
    
    # PERINGATAN: Pastikan Anda menambahkan/mengekspor group_assistant di tempat lain
    # userbot = await group_assistant(chat_id) 

    try:
        await call_py.join_group_call(
            chat_id,
            MediaStream(link, video_flags=video),
        )
        LOGS.info(f"Joined VC in {chat_id} successfully.")

    except NoActiveGroupCall:
        LOGS.warning(f"No active VC in {chat_id}. Cannot join.")
        return 0
        
    except UserAlreadyParticipantError:
        LOGS.info(f"Assistant already in VC in {chat_id}.")
        return 1
        
    except Exception as e:
        LOGS.error(f"Error joining VC in {chat_id}: {e}")
        return 0
        
