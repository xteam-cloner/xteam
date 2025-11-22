# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import asyncio
import inspect
import re
import sys
from io import BytesIO
from pathlib import Path
from time import gmtime, strftime
from traceback import format_exc

from telethon import Button
from telethon import __version__ as telever
from telethon import events
from telethon.errors.common import AlreadyInConversationError
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    BotInlineDisabledError,
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserIsBotError,
)
from telethon.events import MessageEdited, NewMessage
from telethon.utils import get_display_name

from xteam.exceptions import DependencyMissingError
from strings import get_string

from .. import *
from .. import _ignore_eval
from ..dB import DEVLIST
from ..dB._core import LIST, LOADED
from ..fns.admins import admin_check
from ..fns.helper import bash
from ..fns.helper import time_formatter as tf
from ..version import __version__ as pyver
from ..version import ultroid_version as ult_ver
from . import SUDO_M, owner_and_sudos
from ._wrappers import eod

MANAGER = udB.get_key("MANAGER")
TAKE_EDITS = udB.get_key("TAKE_EDITS")
black_list_chats = udB.get_key("BLACKLIST_CHATS")
allow_sudo = SUDO_M.should_allow_sudo



def ultroid_cmd(
    pattern=None, manager=False, ultroid_bot=ultroid_bot, asst=asst, **kwargs
):
    # ... (Semua definisi kwargs tetap sama)

    def decor(dec):
        async def wrapp(ult):
            # ... (Semua logika wrapp, permission check, dan error handling tetap sama)
            # PASTIKAN LOGIKA INI BERJALAN DENGAN BAIK!
            try:
                await dec(ult)
            # ... (Semua except block tetap sama)
            # ... (Penanganan Exception umum dan pengiriman crash log tetap sama)
            
        # --- LOGIKA PENDAFTARAN HANDLER ---
        
        # 💥 BARU: Dapatkan objek modul saat ini 💥
        file = Path(inspect.stack()[1].filename) 
        module = sys.modules[file.stem]

        cmd = None
        blacklist_chats = False
        chats = None
        if black_list_chats:
            blacklist_chats = True
            chats = list(black_list_chats)
            
        _add_new = allow_sudo and HNDLR != SUDO_HNDLR

        # Inisialisasi daftar HANDLER jika belum ada
        if not hasattr(module, "HANDLER"):
            setattr(module, "HANDLER", [])

        # 1. Pendaftaran untuk Userbot Utama (Outgoing/Sudo)
        if _add_new:
            if pattern:
                cmd_sudo = compile_pattern(pattern, SUDO_HNDLR)
            
            # SIMPAN event handler Sudo (Incoming) ke module.HANDLER
            sudo_event = NewMessage(
                pattern=cmd_sudo,
                incoming=True,
                forwards=False,
                func=func,
                chats=chats,
                blacklist_chats=blacklist_chats,
            )
            module.HANDLER.append((wrapp, sudo_event))
            
            # ultroid_bot.add_event_handler(wrapp, sudo_event) # DIHAPUS/DIKOMENTARI

        # 2. Pendaftaran untuk Userbot Utama (Outgoing)
        if pattern:
            cmd = compile_pattern(pattern, HNDLR)
        
        # SIMPAN event handler utama (Outgoing) ke module.HANDLER
        main_event = NewMessage(
            outgoing=True if _add_new else None,
            pattern=cmd,
            forwards=False,
            func=func,
            chats=chats,
            blacklist_chats=blacklist_chats,
        )
        module.HANDLER.append((wrapp, main_event))
        
        # ultroid_bot.add_event_handler(wrapp, main_event) # DIHAPUS/DIKOMENTARI

        # 3. Pendaftaran untuk Pesan yang Diedit
        if TAKE_EDITS:
            def func_(x):
                return not x.via_bot_id and not (x.is_channel and x.chat.broadcast)

            edit_event = MessageEdited(
                pattern=cmd,
                forwards=False,
                func=func_,
                chats=chats,
                blacklist_chats=blacklist_chats,
            )
            module.HANDLER.append((wrapp, edit_event))
            
            # ultroid_bot.add_event_handler(wrapp, edit_event) # DIHAPUS/DIKOMENTARI

        # 4. Logika Manager dan DUAL_MODE
        # Keduanya HARUS TETAP menggunakan add_event_handler langsung ke asst, 
        # karena mereka adalah jalur spesifik untuk Bot Token/Asisten yang berbeda 
        # dari klien user sekunder di ALL_CLIENTS.
        if manager and MANAGER:
            # ... (Biarkan logika pendaftaran manager ke 'asst' tetap sama)
            pass
        if DUAL_MODE and not (manager and DUAL_HNDLR == "/"):
            # ... (Biarkan logika pendaftaran dual mode ke 'asst' tetap sama)
            pass
            
        # ... (Logika LIST dan LOADED tetap sama)

        return wrapp

    return decor
    
