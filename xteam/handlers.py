from pytgcalls.types import Update
from pytgcalls.types.stream.stream_ended import StreamEnded
from pytgcalls.types.chats.chat_update import ChatUpdate
from xteam.vcbot import play_next_stream, clear_queue, skip_current_song, QUEUE
import os
import logging
from xteam import call_py, client

logger = logging.getLogger(__name__)

@call_py.on_update()
async def unified_update_handler(client, update: Update) -> None:
    
    chat_id = update.chat_id
    
    CRITICAL = (
        ChatUpdate.Status.KICKED
        | ChatUpdate.Status.LEFT_GROUP
        | ChatUpdate.Status.CLOSED_VOICE_CHAT
    )

    if isinstance(update, StreamEnded):
        if update.stream_type == StreamEnded.Type.AUDIO and chat_id in QUEUE:
            
            current_song = QUEUE[chat_id][0]
            file_to_delete = current_song[1]
            
            op = await skip_current_song(chat_id)
            
            if os.path.exists(file_to_delete):
                try:
                    os.remove(file_to_delete)
                    logger.info(f"Berhasil membersihkan file otomatis: {file_to_delete}")
                except Exception as e:
                    logger.error(f"Gagal menghapus file {file_to_delete} setelah diputar: {e}")
            
            if op not in [0, 1]:
                next_song_name, next_song_url = op[0], op[2] 
                await client.send_message(
                    chat_id,
                    f"**🎧 Sekarang Memutar:** [{next_song_name}]({next_song_url})",
                    link_preview=False,
                )
            elif op == 1:
                 await client.send_message(
                    chat_id,
                    "Antrian kosong. Meninggalkan obrolan suara.",
                 )


    elif isinstance(update, ChatUpdate):
        status = update.status
        
        if (status & ChatUpdate.Status.LEFT_CALL) or (status & CRITICAL):
            if chat_id in QUEUE:
                for song_data in QUEUE.get(chat_id, []):
                    file_path = song_data[1]
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            logger.info(f"Dihapus file karena VC ditutup: {file_path}")
                        except Exception:
                            pass
                            
            clear_queue(chat_id) 
            
            try:
                await client.leave_call(chat_id) 
            except Exception:
                pass
                
