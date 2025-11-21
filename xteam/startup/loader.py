import contextlib
import glob
import os
import subprocess
import sys
import inspect
from shutil import rmtree
from importlib import import_module
from .. import LOGS, HNDLR, SUDO_HNDLR, USER_MODE, udB, ALL_CLIENTS 
from ..dB._core import HELP
from ..loader import Loader
from telethon import events
from decouple import config
from git import Repo
from .utils import load_addons

def _after_load(loader, module, plugin_name=""):
    if not module or plugin_name.startswith("_"):
        return
    try:
        from strings import get_help
    except ImportError:
        return

    if doc_ := get_help(plugin_name) or module.__doc__:
        try:
            doc = doc_.format(i=HNDLR)
        except Exception as er:
            loader._logger.exception(er)
            loader._logger.info(f"Error in {plugin_name}: {module}")
            return
        
        key = loader.key
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

def register_plugins_to_all_clients(plugin_paths, all_clients):
    plugins_loaded_count = 0
    LOGS.info(f"Mendaftarkan {len(plugin_paths)} plugin ke semua klien...")

    for module_path in plugin_paths:
        try:
            module = import_module(module_path)

            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, 'ultroid_event'):
                    pattern = func.ultroid_event
                    
                    for client in all_clients:
                        if client:
                            client.add_handler(func, events.NewMessage(**pattern))
                            plugins_loaded_count += 1
                            
        except Exception as e:
            LOGS.error(f"Gagal memuat atau mendaftarkan plugin {module_path}: {e}")

    LOGS.info(f"Selesai memuat. Total {plugins_loaded_count} handler terdaftar.")

def get_plugin_paths(path="plugins", include=None, exclude=None, load_all=False):
    _single = os.path.isfile(path)
    files = []
    
    if include:
        for file in include:
            module_path = f"{path}.{file}" if not path.endswith('.py') else path.replace(".py", "")
            files.append(module_path)
            
    elif _single:
        module_path = path.replace(os.path.sep, ".").replace(".py", "")
        files = [module_path]
        
    else:
        file_paths = glob.glob(f"{path}/*.py")
        if load_all:
             pass
             
        for fp in file_paths:
            module_path = fp.replace(".py", "").replace("/", ".").replace("\\", ".")
            module_path = module_path.lstrip(".") 
            module_path = module_path.lstrip("/")
            module_path = module_path.lstrip("\\")
            
            if module_path.split('.')[-1].startswith('_'):
                continue
            
            files.append(module_path)
            
        if exclude:
            files = [f for f in files if f.split('.')[-1] not in exclude]
            
    return files

def load_other_plugins(all_clients, addons=None, pmbot=None, manager=None, vcbot=None):
    _exclude = udB.get_key("EXCLUDE_OFFICIAL") or config("EXCLUDE_OFFICIAL", None)
    _exclude = _exclude.split() if _exclude else []
    _in_only = udB.get_key("INCLUDE_ONLY") or config("INCLUDE_ONLY", None)
    _in_only = _in_only.split() if _in_only else []
    
    official_plugins = get_plugin_paths(path="plugins", include=_in_only, exclude=_exclude)
    register_plugins_to_all_clients(official_plugins, all_clients)
    
    if not USER_MODE and not udB.get_key("DISABLE_AST_PLUGINS"):
        _ast_exc = ["pmbot"]
        if _in_only and "games" not in _in_only:
            _ast_exc.append("games")
        
        assistant_plugins = get_plugin_paths(path="assistant", exclude=_ast_exc)
        register_plugins_to_all_clients(assistant_plugins, all_clients)

    if addons:
        if url := udB.get_key("ADDONS_URL"):
            subprocess.run(f"git clone -q {url} addons", shell=True)
        if os.path.exists("addons") and not os.path.exists("addons/.git"):
            rmtree("addons")
        
        _exclude = udB.get_key("EXCLUDE_ADDONS")
        _exclude = _exclude.split() if _exclude else []
        _in_only = udB.get_key("INCLUDE_ADDONS")
        _in_only = _in_only.split() if _in_only else []

        addon_plugins = get_plugin_paths(path="addons", include=_in_only, exclude=_exclude, load_all=True)
        register_plugins_to_all_clients(addon_plugins, all_clients)
        
    if not USER_MODE:
        if manager:
            manager_plugins = get_plugin_paths(path="assistant/manager")
            register_plugins_to_all_clients(manager_plugins, all_clients)

        if pmbot:
            pmbot_plugin = get_plugin_paths(path="assistant/pmbot.py")
            register_plugins_to_all_clients(pmbot_plugin, all_clients)

    """
    if vcbot and (vcClient and not vcClient.me.bot):
        try:
            Loader(path="vcbot", key="VCBot").load(after_load=_after_load) 
        except ModuleNotFoundError:
            LOGS.error("'pytgcalls' not installed!\nSkipping loading of VCBOT.")
    """
        
