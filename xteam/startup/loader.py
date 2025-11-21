import contextlib
import glob
import os
import sys
import inspect
from shutil import rmtree
from importlib import import_module
from decouple import config
from git import Repo 
from .. import LOGS, HNDLR, SUDO_HNDLR, USER_MODE, udB, ALL_CLIENTS 
from ..dB._core import HELP
from ..loader import Loader
from telethon import events 

# --- Fungsi Utility (_after_load dan get_plugin_paths) Tetap Sama ---

# ... (Pastikan _after_load dan get_plugin_paths dari jawaban sebelumnya ada di sini) ...

# --- Fungsi Pemuatan Utama yang Diperbaiki ---

def load_other_plugins(all_clients=None, addons=None, pmbot=None, manager=None, vcbot=None):
    """
    Memuat semua plugin (resmi, asisten, addon) menggunakan sistem Loader.
    Argumen 'all_clients' dipertahankan hanya untuk kompatibilitas dengan __main__.py, 
    tetapi tidak digunakan di dalam fungsi ini karena Loader yang menangani pendaftaran.
    """
    
    LOGS.info("Memulai proses pemuatan plugin...")

    # --- 1. Plugin Resmi (Official) ---
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    official_paths = get_plugin_paths(path="plugins", include=_in_only, exclude=_exclude)
    
    LOGS.info(f"Memuat {len(official_paths)} plugin resmi...")
    for path in official_paths:
        try:
            Loader(path=path, key="plugins").load(after_load=_after_load) 
        except Exception as e:
            LOGS.error(f"Gagal memuat plugin resmi {path}: {e}")

    # --- 2. Plugin Asisten (Assistant) ---
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        
        assistant_paths = get_plugin_paths(path="assistant", exclude=_ast_exc)
        
        LOGS.info(f"Memuat {len(assistant_paths)} plugin asisten...")
        for path in assistant_paths:
            try:
                Loader(path=path, key="assistant").load(after_load=_after_load)
            except Exception as e:
                LOGS.error(f"Gagal memuat plugin asisten {path}: {e}")

    # --- 3. Addons ---
    if addons:
        # Kloning Addons dengan aman menggunakan pustaka Git
        if url := udB.get_key("ADDONS_URL"):
            if os.path.exists("addons") and not os.path.exists("addons/.git"):
                rmtree("addons") 
            if not os.path.exists("addons"):
                LOGS.info(f"Mengkloning Addons dari {url}...")
                try:
                    Repo.clone_from(url, "addons", depth=1)
                    LOGS.info("Kloning Addons berhasil!")
                except Exception as e:
                    LOGS.error(f"Gagal mengkloning Addons dari {url}: {e}")
        
        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        addon_paths = get_plugin_paths(path="addons", include=_in_only, exclude=_exclude, load_all=True)
        
        LOGS.info(f"Memuat {len(addon_paths)} plugin addon...")
        for path in addon_paths:
            try:
                Loader(path=path, key="addons").load(after_load=_after_load)
            except Exception as e:
                LOGS.error(f"Gagal memuat plugin addon {path}: {e}")
        
    # --- 4. Manager & PMBot ---
    if not USER_MODE:
        if manager:
            manager_paths = get_plugin_paths(path="assistant/manager")
            LOGS.info(f"Memuat {len(manager_paths)} plugin manager...")
            for path in manager_paths:
                try:
                    Loader(path=path, key="manager").load(after_load=_after_load)
                except Exception as e:
                    LOGS.error(f"Gagal memuat plugin manager {path}: {e}")

        if pmbot:
            pmbot_path = "assistant.pmbot"
            LOGS.info(f"Memuat PMBot...")
            try:
                Loader(path=pmbot_path, key="pmbot").load(after_load=_after_load)
            except Exception as e:
                LOGS.error(f"Gagal memuat plugin pmbot {pmbot_path}: {e}")

    # ... (Blok VCBot yang di-komentar) ...

    LOGS.info("Semua proses pemuatan plugin selesai.")
    
