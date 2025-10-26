
from datetime import datetime as dt

from .. import udB


def get_stuff():
    # Fungsi ini sudah benar: mengambil data dari DB
    return udB.get_key("AFK_DB") or []


def add_afk(msg, media_type, media, start_time_str, timezone):
    """Menyimpan status AFK, termasuk media, waktu mulai, dan zona waktu."""
    # Fungsi ini sudah benar: menyimpan 5 item
    udB.set_key("AFK_DB", [msg, media_type, media, start_time_str, timezone])
    return


def is_afk():
    """Mengembalikan 5 nilai AFK yang tersimpan (msg, media_type, media, start_time_str, timezone)."""
    afk = get_stuff()
    
    # 🌟 PERBAIKAN: Lebih eksplisit dalam mengembalikan tuple
    if afk and len(afk) == 5:
        # Jika ada 5 item, kembalikan sebagai tuple.
        # Ini penting agar unpacking di fungsi utama (on_afk, remove_afk) berhasil
        return tuple(afk) 
    
    # Jika tidak ada atau jumlah item salah, kembalikan False
    return False


def del_afk():
    return udB.del_key("AFK_DB")
    
