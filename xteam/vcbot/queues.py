# File: Xteam/vcbot/queues.py

import os
import contextlib 

# QUEUE Global: {chat_id: [[songname, file_path, url_ref, type, quality], ...]}
QUEUE = {}


def add_to_queue(chat_id, songname, link, ref, type, quality):
    """
    Menambahkan item ke antrian.
    'link' di sini adalah path file lokal yang telah diunduh.
    """
    if chat_id in QUEUE:
        chat_queue = QUEUE[chat_id]
        chat_queue.append([songname, link, ref, type, quality])
        return int(len(chat_queue) - 1)
    QUEUE[chat_id] = [[songname, link, ref, type, quality]]


def get_queue(chat_id):
    """Mendapatkan antrian untuk chat_id."""
    if chat_id in QUEUE:
        return QUEUE[chat_id]
    return []


def pop_an_item(chat_id):
    """Menghapus item pertama (yang sedang dimainkan) dari antrian dan filenya."""
    if chat_id not in QUEUE:
        return 0

    # Dapatkan info file untuk dihapus dari disk
    song_data = QUEUE[chat_id][0] 
    file_path_to_delete = song_data[1]
    
    # Hapus dari antrian
    QUEUE[chat_id].pop(0)
    
    # Hapus file dari disk
    if os.path.exists(file_path_to_delete):
        with contextlib.suppress(Exception):
            os.remove(file_path_to_delete)
            # Anda bisa menambahkan logger di sini jika perlu, tapi harus diimport terpisah
    
    return 1


def clear_queue(chat_id: int):
    """Menghapus seluruh antrian dan membersihkan file yang tersisa."""
    if chat_id not in QUEUE:
        return 0

    # Hapus semua file dari item yang ada di antrian sebelum menghapus QUEUE
    for song_data in QUEUE[chat_id]:
        file_path_to_delete = song_data[1]
        if os.path.exists(file_path_to_delete):
            with contextlib.suppress(Exception):
                os.remove(file_path_to_delete)
    
    QUEUE.pop(chat_id)
    return 1
    
