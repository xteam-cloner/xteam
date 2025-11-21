import contextlib
import glob
import os
from importlib import import_module
from logging import Logger

from . import LOGS # Asumsi impor Logger dan LOGS di sini
from .fns.tools import get_all_files # Asumsi impor get_all_files di sini


class Loader:
    def __init__(self, path="plugins", key="Official", logger: Logger = LOGS):
        self.path = path
        self.key = key
        self._logger = logger

    def load(
        self,
        log=True,
        func=import_module,
        include=None,
        exclude=None,
        after_load=None,
        load_all=False,
    ):
        # ... (Logika get_files) ...
        # Untuk tujuan perbaikan ini, mari fokus pada loop impor:
        files = [] # Asumsikan files diisi di sini

        for plugin in sorted(files):
            if func == import_module:
                plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
            try:
                modl = func(plugin)
            except ModuleNotFoundError as er:
                modl = None
                self._logger.error(f"{plugin}: '{er.name}' not installed!")
                continue # Melanjutkan ke plugin berikutnya
            except Exception as exc:
                modl = None
                self._logger.error(f"xteam - {self.key} - ERROR - {plugin}")
                self._logger.exception(exc)
                continue # Melanjutkan ke plugin berikutnya
            
            # --- KOREKSI LOGIKA BERIKUT DIMULAI DI SINI ---
            # Kode di bawah ini sebelumnya salah diindentasi, sekarang sudah benar:
            if log: # Pastikan ini di luar 'if _single' jika ingin mencatat semua yang berhasil dimuat
                self._logger.info(f"Successfully Loaded {plugin}!")
                
            if callable(after_load):
                if func == import_module:
                    plugin_name_for_cb = plugin.split(".")[-1]
                else:
                    plugin_name_for_cb = plugin
                after_load(self, modl, plugin_name=plugin_name_for_cb)
                
