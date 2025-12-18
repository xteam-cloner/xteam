import asyncio
import math
import re
from telethon import events, Button
import xteam

active_chats = {} 

MUSIC_BUTTONS = [
    [
        Button.inline("⏸", data="pauseit"),
        Button.inline("▶️", data="resumeit")
    ],
    [
        Button.inline("⏭", data="skipit"),
        Button.inline("⏹", data="stopit")
    ],
    [
        Button.inline("🗑", data="closeit")
    ]
]

def time_to_seconds(time_str):
    try:
        parts = str(time_str).split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except:
        return 0
    return 0

def telegram_markup_timer(played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / max(1, duration_sec)) * 10
    pos = min(max(math.floor(percentage), 0), 10)
    bar = ("─" * pos) + "◉" + ("─" * (10 - pos))
    timer_row = [[Button.inline(f"{played} {bar} {dur}", data="GetTimer")]]
    return timer_row + MUSIC_BUTTONS

async def timer_task(client, chat_id, message_id, duration):
    total_seconds = time_to_seconds(duration)
    played_seconds = 0
    active_chats[chat_id] = "playing"
    while chat_id in active_chats and played_seconds < total_seconds:
        await asyncio.sleep(15) 
        if active_chats.get(chat_id) == "paused":
            continue
        played_seconds += 15
        if played_seconds > total_seconds:
            played_seconds = total_seconds
        played_str = "{:02d}:{:02d}".format(*divmod(played_seconds, 60))
        markup = telegram_markup_timer(played_str, duration)
        try:
            await client.edit_message(chat_id, message_id, buttons=markup)
        except Exception:
            break
    active_chats.pop(chat_id, None)

@callback(data=re.compile(b"(pauseit|resumeit|stopit|skipit|closeit)"), owner=True)
async def music_manager(e):
    query = e.data.decode("utf-8")
    chat_id = e.chat_id
    try:
        if query == "pauseit":
            await call_py.pause_stream(chat_id)
            active_chats[chat_id] = "paused"
            await e.answer("⏸ Paused", alert=False)
        elif query == "resumeit":
            await call_py.resume_stream(chat_id)
            active_chats[chat_id] = "playing"
        elif query == "stopit":
            active_chats.pop(chat_id, None)
            await call_py.leave_call(chat_id)
            await e.delete()
        elif query == "skipit":
            active_chats.pop(chat_id, None)
            await skip_current_song(chat_id)
            await e.answer("⏭ Skipped", alert=False)
        elif query == "closeit":
            await e.delete()
    except Exception as err:
        await e.answer(f"⚠️ Error: {str(err)}", alert=True)
