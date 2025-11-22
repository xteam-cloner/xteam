# Xteam/startup/loader.py - VERSI FINAL KOREKSI

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
from strings import get_help 
# PASTIKAN Anda juga mengimpor ALL_CLIENTS jika didefinisikan di file lain
# from .. import ALL_CLIENTS 


# --- FUNGSI HELPER ASLI UNTUK MENGELOLA DOKUMENTASI (HELP) ---
def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
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


# 👇 MODIFIKASI: FUNGSI UNTUK MENDAFTARKAN HANDLERS KE SEMUA KLIEN
def _register_handlers(loader, module, plugin_name="", all_clients=None, asst_bot=None):
    """
    Mendaftarkan handlers dari modul yang dimuat ke semua klien yang tersedia.
    """
    
    _after_load(loader, module, plugin_name) 

    # 2. Logika Pendaftaran Handler Utama (Userbot & Klien Tambahan)
    if hasattr(module, "HANDLER") and all_clients:
        handlers = getattr(module, "HANDLER")
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
        handlers = getattr(module, "ASST_HANDLER")
        for handler in handlers:
            try:
                asst_bot.add_handler(handler[0], handler[1])
            except Exception as e:
                loader._logger.error(f"Gagal mendaftarkan handler di klien Asisten: {plugin_name}")
                loader._logger.exception(e)


def load_other_plugins(all_clients=ALL_CLIENTS, addons=None, pmbot=None, manager=None, vcbot=None):
    
    def client_aware_after_load(loader, module, plugin_name=""):
        asst_client = pmbot or manager or vcbot 
        _register_handlers(
            loader, 
            module, 
            plugin_name, 
            all_clients=all_clients, 
            asst_bot=asst_client 
        )

    # for official
    # 🛑 PERBAIKAN: Definisi variabel _exclude dan _in_only yang hilang
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    # Gunakan client_aware_after_load untuk mendaftarkan handlers ke semua klien
    Loader().load(include=_in_only, exclude=_exclude, after_load=client_aware_after_load)

    # for assistant
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        
        # Gunakan client_aware_after_load
        Loader(path="assistant").load(
            log=False, exclude=_ast_exc, after_load=client_aware_after_load
        )

    # for addons
    if addons:
        # PENTING: Anda mungkin perlu mendefinisikan ulang _exclude dan _in_only 
        # di sini jika Anda ingin memuat addons secara spesifik
        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        # Gunakan client_aware_after_load
        Loader(path="addons", key="Addons").load(
            func=load_addons,
            include=_in_only,
            exclude=_exclude,
            after_load=client_aware_after_load,
            load_all=True,
        )

    # group manager
    if manager:
        Loader(path="assistant/manager", key="Group Manager").load()

    # chat via assistant
    if pmbot:
        Loader(path="assistant/pmbot.py").load_single(log=False)

    # vc bot (Biarkan logika ini tetap dikomentari atau sesuaikan)
    """if vcbot and not vcClient._bot:
        try:
            import pytgcalls
            if not os.path.isdir("vcbot/downloads"):
                os.mkdir("vcbot/downloads")
            Loader(path="vcbot", key="VCBot").load(after_load=_after_load)
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping load of VcBot.")
    """
                
