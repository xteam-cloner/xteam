import contextlib
import glob
import os
import sys
import inspect
from shutil import rmtree
from importlib import import_module
from decouple import config
from git import Repo # Dipertahankan untuk kloning yang aman

# Asumsi: LOGS, HNDLR, SUDO_HNDLR, USER_MODE, udB, ALL_CLIENTS, HELP, Loader
from .. import LOGS, HNDLR, SUDO_HNDLR, USER_MODE, udB, ALL_CLIENTS 
from ..dB._core import HELP
from ..loader import Loader
from telethon import events # Dipertahankan untuk konteks, meskipun Loader yang menangani

# --- Fungsi Utility ---

def _after_load(loader, module, plugin_name=""):
    """
    Fungsi callback setelah modul plugin dimuat, bertanggung jawab memperbarui 
    dokumentasi Bantuan (HELP).
    """
    if not module or plugin_name.startswith("_"):
        return
    try:
        from strings import get_help
    except ImportError:
        # Jika 'strings' tidak tersedia, abaikan.
        return

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            # Menggunakan .format() untuk mengganti placeholder seperti {i}
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error formatting help doc in {plugin_name}: {er}")
            return
        
        key = loader.key # Kunci (e.g., "plugins", "assistant") dari Loader
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


def get_plugin_paths(path="plugins", include=None, exclude=None, load_all=False):
    """
    Mendapatkan path modul Python dari path folder/file yang diberikan.
    Contoh: 'plugins/spam.py' -> 'plugins.spam'
    """
    files = []
    
    if include:
        # Pemuatan berdasarkan daftar nama modul yang disertakan
        for file in include:
            # file: 'nama_plugin'
            module_path = f"{path}.{file}" if not file.endswith('.py') else file.replace(".py", "")
            files.append(module_path.replace(os.path.sep, "."))
            
    elif os.path.isfile(path):
        # Pemuatan file tunggal
        module_path = path.replace(os.path.sep, ".").replace(".py", "")
        files = [module_path]
        
    else:
        # Pemuatan folder
        file_paths = glob.glob(f"{path}/*.py")
             
        for fp in file_paths:
            # Konversi path file (e.g., 'plugins/spam.py') ke path modul (e.g., 'plugins.spam')
            module_path = fp.replace(".py", "").replace(os.path.sep, ".")
            module_path = module_path.lstrip(".") 
            
            # Lewati file dengan awalan underscore (file internal)
            if module_path.split('.')[-1].startswith('_'):
                continue
            
            files.append(module_path)
            
        if exclude:
            # Filter modul yang dikecualikan
            files = [f for f in files if f.split('.')[-1] not in exclude]
            
    return files


# --- Fungsi Pemuatan Utama ---

def load_other_plugins(all_clients=None, addons=None, pmbot=None, manager=None, vcbot=None):
    # Perhatikan: Argumen all_clients ditambahkan kembali dengan nilai default None, 
    # namun tidak digunakan karena pendaftaran kini diurus oleh Loader.
    
    LOGS.info("Memulai proses pemuatan plugin...")

    # --- 1. Plugin Resmi (Official) ---
    # ... (sisa isi fungsi tetap sama)

    # --- 1. Plugin Resmi (Official) ---
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    official_paths = get_plugin_paths(path="plugins", include=_in_only, exclude=_exclude)
    
    LOGS.info(f"Memuat {len(official_paths)} plugin resmi...")
    for path in official_paths:
        try:
            # Loader bertanggung jawab mengimpor dan mendaftarkan handler
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
                rmtree("addons") # Bersihkan folder jika ada sisa
            if not os.path.exists("addons"):
                LOGS.info(f"Mengkloning Addons dari {url}...")
                try:
                    # Menggunakan Repo.clone_from untuk keamanan
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

    # --- 5. VCBot ---
    """
    if vcbot and (vcClient and not vcClient.me.bot):
        try:
            Loader(path="vcbot", key="VCBot").load(after_load=_after_load) 
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
    """
    LOGS.info("Semua proses pemuatan plugin selesai.")

