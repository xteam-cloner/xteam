# File: xteam/handlers.py (KODE FINAL YANG BERSIH)

from pytgcalls.types import Update
# Import Event Classes
from pytgcalls.types.stream.stream_ended import StreamEnded 
from pytgcalls.types.chats.chat_update import ChatUpdate # <-- Dipertahankan

# Impor fungsi helper (Core Logic)
from xteam.vcbot import play_next_stream, clear_queue # <-- Dipertahankan



# FUNGSI HANDLER UTAMA (Dipertahankan dan sudah async)
# ----------------------------------------------------
async def unified_update_handler(client, update: Update) -> None: 
    
    chat_id = update.chat_id
    
    # 1. PENANGANAN STREAM ENDED (Lagu Selesai)
    if isinstance(update, StreamEnded):
        if update.stream_type == StreamEnded.Type.AUDIO:
            print(f"[{chat_id}] Audio stream ended. Checking queue...")
            await play_next_stream(chat_id) 

    # 2. PENANGANAN CHAT UPDATE (Termasuk Penutupan VC)
    elif isinstance(update, ChatUpdate):
        if update.status & ChatUpdate.Status.CLOSED_VOICE_CHAT:
            print(f"[{chat_id}] Group call closed by admin. Clearing queue...")
            clear_queue(chat_id) 
        
    else:
        pass 
