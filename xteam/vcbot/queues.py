import os
import contextlib 

QUEUE = {}


def add_to_queue(chat_id, songname, link, ref, type, quality):
    if chat_id in QUEUE:
        chat_queue = QUEUE[chat_id]
        chat_queue.append([songname, link, ref, type, quality])
        return int(len(chat_queue) - 1)
    QUEUE[chat_id] = [[songname, link, ref, type, quality]]


def get_queue(chat_id):
    if chat_id in QUEUE:
        return QUEUE[chat_id]
    return []



def pop_an_item(chat_id: int):
    if chat_id not in QUEUE or not QUEUE[chat_id]:
        return
        
    song_data = QUEUE[chat_id][0]
    file_path = song_data[1]

    try:
        QUEUE[chat_id].pop(0)
    except IndexError:
        pass
        

def clear_queue(chat_id: int):
    if chat_id not in QUEUE:
        return 0
    QUEUE.pop(chat_id)
    return 1

