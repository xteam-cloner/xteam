from pytgcalls.types import Update
from pytgcalls.types.stream.stream_ended import StreamEnded, GroupCallClosed 
from xteam.vcbot import play_next_stream, clear_queue 

# ----------------------------------------------------
# FUNGSI HANDLER UTAMA
# ----------------------------------------------------
async def unified_update_handler(client, update: Update) -> None:
    
    chat_id = update.chat_id
    
    if isinstance(update, StreamEnded):
        if update.stream_type == StreamEnded.Type.AUDIO:
            print(f"[{chat_id}] Audio stream ended. Checking queue...")
            await play_next_stream(chat_id) 

    elif isinstance(update, GroupCallClosed):
        print(f"[{chat_id}] Group call closed by admin. Clearing queue...")
        clear_queue(chat_id)
        
    else:
        pass # Mengabaikan tipe update lainnya

# ----------------------------------------------------
# DAFTAR HANDLER SAAT STARTUP BOT
# ----------------------------------------------------

def register_vc_handlers():
    from xteam import call_py 
    
    call_py.on_update()(unified_update_handler)
    print("✅ Event handler PyTgCalls telah didaftarkan.")
  
