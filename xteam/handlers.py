# File: xteam/handlers.py

# ...

# FUNGSI HANDLER UTAMA
# ----------------------------------------------------
async def unified_update_handler(client, update: Update) -> None: # <-- Tambahkan 'async' di sini
    
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
            clear_queue(chat_id) # clear_queue asumsikan synchronous, jika async perlu await.
        
    else:
        pass 

# ... (lanjutkan ke register_vc_handlers)
