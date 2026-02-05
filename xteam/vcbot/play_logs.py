from xteam import asst, LOGS
from xteam.configs import Var

async def play_logs(event, title, duration, streamtype):
    if not Var.LOG_CHANNEL:
        return
        
    try:
        chat = await event.get_chat()
        chat_name = chat.title if hasattr(chat, 'title') else "Private Chat"
        user = await event.get_sender()
        user_mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        
        logger_text = (
            "<blockquote>"
            "🎵 Music Started\n\n"
            f"📌 Title: <code>{title}</code>\n"
            f"🕒 Duration: <code>{duration}</code>\n""</blockquote>\n"
            "<blockquote>"
            f"👥 Group: <code>{chat_name}</code>\n"
            f"🆔 ID: <code>{event.chat_id}</code>\n"
            f"👤 User: {user_mention}\n"
            f"🆔 User ID: <code>{user.id}</code>"
            "</blockquote>"
        )
        
        await asst.send_message(
            Var.LOG_CHANNEL,
            logger_text,
            parse_mode='html',
            link_preview=False
        )
    except Exception as e:
        LOGS.error(f"Gagal mengirim log: {e}")
      
