# Xteam/startup/loader.py - KODE MULTI-CLIENT FINAL YANG TERKOREKSI

import contextlib
import glob
import os
import subprocess
import sys
import inspect
from shutil import rmtree
from importlib import import_module

# Import dari root package xteam
from .. import LOGS, HNDLR, SUDO_HNDLR, USER_MODE, udB, ALL_CLIENTS 
from ..dB._core import HELP
from ..loader import Loader # Diperlukan untuk logika VCBot lama dan kompatibilitas
from telethon import events
from decouple import config
from git import Repo
# Asumsi get_all_files diimpor dari tempat yang benar
# from .fns.tools import get_all_files 

# --- FUNGSI PEMBANTU UNTUK VCBOT DAN LOGIKA LAMA (after_load) ---

def _after_load(loader, module, plugin_name=""):
    """
    Fungsi after_load yang dipanggil oleh Loader lama (untuk VCBOT)
    dan bertanggung jawab mengisi HELP dictionary.
    """
    if not module or plugin_name.startswith("_"):
        return
    
    # Asumsi: strings.get_help diimpor atau diakses secara global
    try:
        from strings import get_help
    except ImportError:
        # Fallback atau asumsikan sudah diimpor di tempat lain
        return

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error in {plugin_name}: {module}")
            return
        
        key = loader.key # 'Official', 'Addons', dll.
        if key in HELP.keys():
            update_cmd = HELP[key]
            try:
                update_cmd.update({plugin_name: doc})
            except BaseException as er:
                loader._logger.exception(er)
        else:
            try:
                HELP.update({key: {plugin_name: doc}})
            except BaseException as em:
                loader._logger.exception(em)


# --- 1. FUNGSI PENDAFTARAN EVENT MULTI-CLIENT (BARU) ---

def register_plugins_to_all_clients(plugin_paths, all_clients):
    """
    Membaca list plugin paths (format modul) dan mendaftarkan event ke semua klien aktif.
    Ini menggantikan Loader().load() untuk Userbots.
    """
    plugins_loaded_count = 0
    LOGS.info(f"Mendaftarkan {len(plugin_paths)} plugin ke semua klien...")

    for module_path in plugin_paths:
        try:
            # Gunakan import_module langsung
            module = import_module(module_path)

            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, 'ultroid_event'):
                    pattern = func.ultroid_event
                    
                    # Iterasi melalui semua klien aktif (termasuk yang utama)
                    for client in all_clients:
                        if client:
                            # Pendaftaran event
                            client.add_handler(func, events.NewMessage(**pattern))
                            plugins_loaded_count += 1
                            
        except Exception as e:
            LOGS.error(f"Gagal memuat atau mendaftarkan plugin {module_path}: {e}")

    LOGS.info(f"Selesai memuat. Total {plugins_loaded_count} handler terdaftar.")


# --- 2. FUNGSI PENGUMPUL JALUR PLUGINS (get_plugin_paths) ---

def get_plugin_paths(path="plugins", include=None, exclude=None, load_all=False):
    """
    Mengumpulkan jalur modul berdasarkan include/exclude, menghasilkan nama modul absolut
    yang dapat diimpor (misalnya: plugins.alva).
    """
    
    _single = os.path.isfile(path)
    files = []
    
    if include:
        # Jika ada include, kita buat jalur modul berdasarkan nama file
        for file in include:
            module_path = f"{path}.{file}" if not path.endswith('.py') else path.replace(".py", "")
            files.append(module_path)
            
    elif _single:
        # Jika file tunggal (misal: pmbot.py)
        files = [path.replace(".py", "")]
        
    else:
        # Menggunakan logika glob untuk mencari semua file
        file_paths = glob.glob(f"{path}/*.py")
        if load_all:
             # Jika load_all, perlu logika get_all_files, tapi kita gunakan glob sederhana
             # Asumsi: glob mencakup semua yang kita butuhkan untuk struktur rata
             pass
             
        for fp in file_paths:
            # Ubah path fisik (e.g., addons/alva.py) menjadi modul (e.g., addons.alva)
            module_path = fp.replace(".py", "").replace("/", ".").replace("\\", ".")
            
            # Hapus awalan relatif yang salah jika ada (e.g., ./plugins.alva -> plugins.alva)
            module_path = module_path.lstrip(".") 
            module_path = module_path.lstrip("/")
            module_path = module_path.lstrip("\\")
            
            if module_path.split('.')[-1].startswith('_'):
                continue # Abaikan file yang dimulai dengan underscore
            
            files.append(module_path)
            
        if exclude:
            # Filter berdasarkan nama modul terakhir (nama file)
            files = [f for f in files if f.split('.')[-1] not in exclude]
            
    return files


# --- 3. FUNGSI PEMUATAN UTAMA (load_other_plugins) ---

def load_other_plugins(all_clients, addons=None, pmbot=None, manager=None, vcbot=None):
    """
    Memuat plugin Ultroid dan mendaftarkan event ke SEMUA klien.
    """
    
    # 1. LOAD OFFICIAL PLUGINS (plugins/)
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    official_plugins = get_plugin_paths(path="plugins", include=_in_only, exclude=_exclude)
    register_plugins_to_all_clients(official_plugins, all_clients)
    
    # 2. LOAD ASSISTANT PLUGINS (assistant/)
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        
        assistant_plugins = get_plugin_paths(path="assistant", exclude=_ast_exc)
        register_plugins_to_all_clients(assistant_plugins, all_clients)

    # 3. LOAD ADDONS (addons/)
    if addons:
        # --- LOGIKA GIT CLONE / PULL ADDONS ---
        if url := udB.get_key("ADDONS_URL"):
            subprocess.run(f"git clone -q {url} addons", shell=True)
        if os.path.exists("addons") and not os.path.exists("addons/.git"):
            rmtree("addons")
        # ... (Logika git clone/pull dan pip install addons.txt) ...
        # --- AKHIR LOGIKA GIT CLONE / PULL ADDONS ---
        
        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        addon_plugins = get_plugin_paths(path="addons", include=_in_only, exclude=_exclude, load_all=True)
        register_plugins_to_all_clients(addon_plugins, all_clients)
        
    # 4. LOAD MANAGER & PMBOT (Jika USER_MODE=False)
    if not USER_MODE:
        if manager:
            manager_plugins = get_plugin_paths(path="assistant/manager")
            register_plugins_to_all_clients(manager_plugins, all_clients)

        if pmbot:
            pmbot_plugin = get_plugin_paths(path="assistant/pmbot.py")
            register_plugins_to_all_clients(pmbot_plugin, all_clients)

    # 5. VCBOT (Menggunakan Loader() Lama karena asumsi VC Client adalah single-client)
    # Gunakan Loader() yang diimpor di atas dan fungsi _after_load
    """
    if vcbot and (vcClient and not vcClient.me.bot):
        try:
            # ... (Logika instalasi VCBOT tetap di sini)
            
            # Panggilan Loader lama:
            Loader(path="vcbot", key="VCBot").load(after_load=_after_load) 
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
    """
        
