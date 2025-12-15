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



def pop_an_item(chat_id):
    if chat_id not in QUEUE:
        return 0

    song_data = QUEUE[chat_id][0] 
    
    QUEUE[chat_id].pop(0)
    
    return song_data # Ubah return 1 menjadi return song_data (Lebih informatif)
    


def clear_queue(chat_id: int):
    """
    Menghapus seluruh antrian dan SEMUA file fisik yang terkait.
    """
    if chat_id not in QUEUE:
        return 0

    for song_data in QUEUE[chat_id]:
        file_path_to_delete = song_data[1]
        if os.path.exists(file_path_to_delete):
            with contextlib.suppress(Exception):
                os.remove(file_path_to_delete)
    
    QUEUE.pop(chat_id)
    return 1
    
