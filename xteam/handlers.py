from pytgcalls.types import Update
from pytgcalls.types.stream.stream_ended import StreamEnded
from pytgcalls.types.chats.chat_update import ChatUpdate
from xteam.vcbot import play_next_stream, clear_queue

async def unified_update_handler(client, update: Update) -> None:
    
    chat_id = update.chat_id
    
    CRITICAL = (
        ChatUpdate.Status.KICKED
        | ChatUpdate.Status.LEFT_GROUP
        | ChatUpdate.Status.CLOSED_VOICE_CHAT
    )

    if isinstance(update, StreamEnded):
        if update.stream_type == StreamEnded.Type.AUDIO:
            await play_next_stream(chat_id) 

    elif isinstance(update, ChatUpdate):
        status = update.status
        
        if (status & ChatUpdate.Status.LEFT_CALL) or (status & CRITICAL):
            clear_queue(chat_id) 
            
            try:
                await client.leave_call(chat_id) 
            except Exception:
                pass
