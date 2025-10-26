# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from datetime import datetime as dt

from .. import udB


def get_stuff():
    return udB.get_key("AFK_DB") or []


def add_afk(msg, media_type, media, start_time_str, timezone):
    """Menyimpan status AFK, termasuk media, waktu mulai, dan zona waktu."""
    udB.set_key("AFK_DB", [msg, media_type, media, start_time_str, timezone])
    return


def is_afk():
    """Mengembalikan 5 nilai AFK yang tersimpan (msg, media_type, media, start_time_str, timezone)."""
    afk = get_stuff()
    if afk and len(afk) == 5:
        # Pastikan kita mengembalikan 5 nilai
        return afk[0], afk[1], afk[2], afk[3], afk[4]
    return False


def del_afk():
    return udB.del_key("AFK_DB")
    
