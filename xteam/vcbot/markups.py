import asyncio
import math
import re
from telethon import events, Button
from xteam._misc._assistant import callback
from xteam import call_py

active_chats = {} 

MUSIC_BUTTONS = [
    [
        Button.inline("II", data="pauseit"),
        Button.inline("▷", data="resumeit")
    ],
    [
        Button.inline("‣‣I", data="skipit"),
        Button.inline("▢", data="stopit")
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
    
    if duration_sec == 0:
        return MUSIC_BUTTONS
        
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    if umm <= 10: bar = "◉—————————"
    elif 10 < umm < 20: bar = "—◉————————"
    elif 20 <= umm < 30: bar = "——◉———————"
    elif 30 <= umm < 40: bar = "———◉——————"
    elif 40 <= umm < 50: bar = "————◉—————"
    elif 50 <= umm < 60: bar = "—————◉————"
    elif 60 <= umm < 70: bar = "——————◉———"
    elif 70 <= umm < 80: bar = "———————◉——"
    elif 80 <= umm < 95: bar = "————————◉—"
    else: bar = "—————————◉"
    
    timer_row = [[Button.inline(f"{played} {bar} {dur}", data="timer_info")]]
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
    from plugins.music import skip_current_song 
    
    query = e.data.decode("utf-8")
    chat_id = e.chat_id
    try:
        if query == "pauseit":
            await call_py.pause(chat_id)
            active_chats[chat_id] = "paused"
            await e.answer("⏸ Paused")
        elif query == "resumeit":
            await call_py.resume(chat_id)
            active_chats[chat_id] = "playing"
            await e.answer("▶️ Resumed")
        elif query == "stopit":
            active_chats.pop(chat_id, None)
            await call_py.leave_call(chat_id)
            await e.delete()
        elif query == "skipit":
            await skip_current_song(e)
            await e.answer("⏭ Skipped")
        elif query == "closeit":
            await e.delete()
    except Exception as err:
        await e.answer(f"⚠️ Error: {str(err)}", alert=True)
        
