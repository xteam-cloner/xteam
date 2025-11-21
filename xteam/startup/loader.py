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
def _register_handlers(loader, module, plugin_name="", all_clients=None, asst_bot=None):
    """
    Mendaftarkan handlers dari modul yang dimuat ke semua klien yang tersedia.
    """
    
    # 1. Panggil fungsi asli untuk mengelola dokumentasi HELP
    _after_load(loader, module, plugin_name) 

    # 2. Logika Pendaftaran Handler Utama (Userbot & Klien Tambahan)
    if hasattr(module, "HANDLER") and all_clients:
        handlers = getattr(module, "HANDLER")
        # Iterasi SEMUA klien Userbot (Userbot Utama & Akun Kedua)
        for client in all_clients:
            if client:
                for handler in handlers:
                    try:
                        # Asumsi handler adalah tuple/list: (fungsi, event)
                        client.add_handler(handler[0], handler[1])
                    except Exception as e:
                        loader._logger.error(f"Gagal mendaftarkan handler di klien Userbot: {plugin_name}")
                        loader._logger.exception(e)
    
    # 3. Logika Pendaftaran Handler Bot Asisten (jika diperlukan)
    if asst_bot and hasattr(module, "ASST_HANDLER"):
        handlers = getattr(module, "ASST_HANDLER")
        for handler in handlers:
            try:
                asst_bot.add_handler(handler[0], handler[1])
            except Exception as e:
                loader._logger.error(f"Gagal mendaftarkan handler di klien Asisten: {plugin_name}")
                loader._logger.exception(e)


def load_other_plugins(all_clients=ALL_CLIENTS, addons=None, pmbot=None, manager=None, vcbot=None):
    
    # Buat fungsi helper untuk after_load yang membawa semua klien
    # Karena load() hanya menerima satu argumen func, kita bungkus logicnya di lambda.
    def client_aware_after_load(loader, module, plugin_name=""):
        # Kita asumsikan 'asst' adalah objek bot yang valid jika pmbot/manager/vcbot diaktifkan
        asst_client = pmbot or manager or vcbot # Coba tebak objek Bot Asisten
        _register_handlers(
            loader, 
            module, 
            plugin_name, 
            all_clients=all_clients, 
            asst_bot=asst_client # Teruskan objek Bot Asisten
        )

    # for official
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    # 💥 MODIFIKASI: Gunakan client_aware_after_load untuk mendaftarkan handlers ke semua klien
    Loader().load(include=_in_only, exclude=_exclude, after_load=client_aware_after_load)

    # for assistant
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        
        # 💥 MODIFIKASI: Gunakan client_aware_after_load
        Loader(path="assistant").load(
            log=False, exclude=_ast_exc, after_load=client_aware_after_load
        )

    # for addons (Hanya menampilkan bagian pemanggilan load yang dimodifikasi)
    if addons:
        # ... (Kode untuk cloning/pull addons tetap sama)
        
        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        # 💥 MODIFIKASI: Gunakan client_aware_after_load
        Loader(path="addons", key="Addons").load(
            func=load_addons,
            include=_in_only,
            exclude=_exclude,
            after_load=client_aware_after_load,
            load_all=True,
        )

    if not USER_MODE:
        # group manager
        if manager:
            # Karena ini adalah bot manager, Anda mungkin harus memastikan
            # bahwa file di assistant/manager secara eksplisit menggunakan
            # objek 'manager' untuk add_handler di dalamnya, BUKAN melalui after_load.
            Loader(path="assistant/manager", key="Group Manager").load()

        # chat via assistant
        if pmbot:
            # Sama seperti manager, logika pendaftaran handler ada di pmbot.py
            Loader(path="assistant/pmbot.py").load(log=False)

    
# vc bot (Tetap tidak dimodifikasi karena logikanya dikomentari)
    """if vcbot and (vcClient and not vcClient.me.bot):
        try:
            # ... (Logika VC Bot)
            try:
                # ...
                Loader(path="vcbot", key="VCBot").load(after_load=_after_load)
            except FileNotFoundError as e:
                LOGS.error(f"{e} Skipping VCBot Installation.")
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
"""
    
