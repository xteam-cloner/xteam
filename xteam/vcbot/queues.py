import os
import contextlib 

QUEUE = {}

def add_to_queue(chat_id, songname, link, ref, type, quality):
    if chat_id in QUEUE:
        QUEUE[chat_id].append([songname, link, ref, type, quality])
        return int(len(QUEUE[chat_id]) - 1)
    else:
        QUEUE[chat_id] = [[songname, link, ref, type, quality]]
        return 0

def get_queue(chat_id):
    return QUEUE.get(chat_id, [])

def clear_queue(chat_id: int):
    if chat_id in QUEUE:
        QUEUE.pop(chat_id)
        return 1
    return 0
