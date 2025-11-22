# Xteam/startup/loader.py - VERSI MODIFIKASI

# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import os
import subprocess
import sys
from shutil import rmtree

from decouple import config
from git import Repo

from .. import *
from ..dB._core import HELP
from ..loader import Loader
from . import *
from .utils import load_addons
from strings import get_help # Diperlukan untuk _after_load

# --- FUNGSI HELPER ASLI UNTUK MENGELOLA DOKUMENTASI (HELP) ---
def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    # from strings import get_help # Sudah dipindahkan ke atas
    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error in {plugin_name}: {module}")
            return
        if loader.key in HELP.keys():
            update_cmd = HELP[loader.key]
            try:
                update_cmd.update({plugin_name: doc})
            except BaseException as er:
                loader._logger.exception(er)
        else:
            try:
                HELP.update({loader.key: {plugin_name: doc}})
            except BaseException as em:
                loader._logger.exception(em)
# -----------------------------------------------------------


# 👇 BARU: FUNGSI UNTUK MENDAFTARKAN HANDLERS KE SEMUA KLIEN
# Xteam/startup/loader.py - VERSI MODIFIKASI
# ... (Copyright dan Imports tetap sama)
from .. import ALL_CLIENTS # PASTIKAN INI DI-IMPORT

# ... (Fungsi _after_load tetap sama)

# 👇 MODIFIKASI: FUNGSI UNTUK MENDAFTARKAN HANDLERS KE SEMUA KLIEN
def _register_handlers(loader, module, plugin_name="", all_clients=None, asst_bot=None):
    """
    Mendaftarkan handlers dari modul yang dimuat ke semua klien yang tersedia.
    """
    
    # 1. Panggil fungsi asli untuk mengelola dokumentasi HELP
    _after_load(loader, module, plugin_name) 

    # 2. Logika Pendaftaran Handler Utama (Userbot & Klien Tambahan)
    # Gunakan HANDLER yang dikumpulkan dari decorator
    if hasattr(module, "HANDLER") and all_clients:
        handlers = getattr(module, "HANDLER")
        # Iterasi SEMUA klien Userbot di ALL_CLIENTS
        for client in all_clients:
            if client:
                for handler in handlers:
                    try:
                        # DAFTARKAN (fungsi, event) handler ke klien saat ini
                        client.add_handler(handler[0], handler[1])
                    except Exception as e:
                        loader._logger.error(f"Gagal mendaftarkan handler di klien {client.me.id}: {plugin_name}")
                        loader._logger.exception(e)
    
    # 3. Logika Pendaftaran Handler Bot Asisten (ASST_HANDLER)
    if asst_bot and hasattr(module, "ASST_HANDLER"):
        # ... (Biarkan logika ini tetap sama)
        pass


def load_other_plugins(all_clients=ALL_CLIENTS, addons=None, pmbot=None, manager=None, vcbot=None):
    
    def client_aware_after_load(loader, module, plugin_name=""):
        asst_client = pmbot or manager or vcbot 
        _register_handlers(
            loader, 
            module, 
            plugin_name, 
            all_clients=all_clients, # Melewatkan objek ALL_CLIENTS
            asst_bot=asst_client 
        )

    # for official
    # 💥 Gunakan client_aware_after_load untuk mendaftarkan handlers ke semua klien 💥
    Loader().load(include=_in_only, exclude=_exclude, after_load=client_aware_after_load)

    # for assistant
    # 💥 Gunakan client_aware_after_load 💥
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        # ... (Logika exclude tetap sama)
        Loader(path="assistant").load(
            log=False, exclude=_ast_exc, after_load=client_aware_after_load
        )

    # for addons
    if addons:
        # ... (Logika cloning/exclude tetap sama)
        # 💥 Gunakan client_aware_after_load 💥
        Loader(path="addons", key="Addons").load(
            func=load_addons,
            include=_in_only,
            exclude=_exclude,
            after_load=client_aware_after_load,
            load_all=True,
        )

    # ... (Logika Group Manager, PM Bot, dan VC Bot tetap sama)

