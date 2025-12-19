# Man - UserBot
# Copyright (c) 2022 Man-Userbot
# Credits: @mrismanaziz || https://github.com/mrismanaziz
#
# This file is a part of < https://github.com/mrismanaziz/Man-Userbot/ >
# t.me/SharingUserbot & t.me/Lunatic0de

QUEUE = {}

def add_to_queue(chat_id, songname, url, duration, thumb_url, videoid, artist):
    if chat_id not in QUEUE:
        QUEUE[chat_id] = []
    
    data = [songname, url, duration, thumb_url, videoid, artist]
    QUEUE[chat_id].append(data)
    return len(QUEUE[chat_id]) - 1

def get_queue(chat_id):
    if chat_id in QUEUE:
        return QUEUE[chat_id]
    return 0

def pop_an_item(chat_id):
    if chat_id not in QUEUE:
        return 0
    chat_queue = QUEUE[chat_id]
    if chat_queue:
        chat_queue.pop(0)
        return 1
    return 0

def clear_queue(chat_id: int):
    if chat_id in QUEUE:
        QUEUE.pop(chat_id)
        return 1
    return 0
    
