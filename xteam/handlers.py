from pytgcalls.types import Update
from pytgcalls.types.stream.stream_ended import StreamEnded
from pytgcalls.types.chats.chat_update import ChatUpdate
from xteam.vcbot import clear_queue, skip_current_song, QUEUE
import os
import logging
from xteam import call_py, bot as client

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
        # Pastikan antrean diproses jika ada lagu selanjutnya
        if chat_id in QUEUE:
            op = await skip_current_song(chat_id)
            
            # Jika op adalah list [songname, link], berarti ada lagu selanjutnya
            if isinstance(op, list):
                next_song_name, next_song_url = op[0], op[1] 
                await client.send_message(
                    chat_id,
                    f"**🎧 Sekarang Memutar:** [{next_song_name}]({next_song_url})",
                    link_preview=False,
                )
            # Jika op == 1 berarti antrean benar-benar habis
            elif op == 1:
                # Jika ingin bot tetap standby, hapus baris leave_call di bawah ini
                await client.send_message(
                    chat_id,
                    "**💡 Antrean habis. Bot Standby.**",
                )
                # await call_py.leave_call(chat_id) # Beri pagar (#) jika ingin standby
                
