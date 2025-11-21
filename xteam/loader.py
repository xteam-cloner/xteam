# Xteam/startup/loader.py - KODE LENGKAP YANG BENAR

import importlib
import inspect
import os
from telethon import events
# Asumsikan LOGS sudah diimpor dari modul utama atau logging Ultroid

# --- Fungsi Pembantu untuk Mendapatkan Daftar File Plugin ---
# (Asumsikan fungsi ini sudah ada di loader Anda)
def get_plugin_files():
    """Mengumpulkan jalur file untuk semua plugin yang akan dimuat."""
    plugin_files = []
    # Logika untuk menelusuri folder 'plugins' dan mengumpulkan file .py
    for root, _, files in os.walk("./plugins"):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                # Ubah path menjadi format modul yang dapat diimpor (misalnya 'plugins.namafile')
                path = os.path.join(root, file).replace(os.path.sep, ".")[:-3]
                plugin_files.append(path)
    return plugin_files
# -----------------------------------------------------------------


# Fungsi Pemuatan Utama yang Telah Diubah
def load_other_plugins(all_clients, addons=None, pmbot=None, manager=None, vcbot=None):
    """
    Memuat plugin dari berbagai folder dan mendaftarkan handler pada SEMUA klien.
    
    :param all_clients: List dari semua objek UltroidClient/TelegramClient yang aktif.
    """
    
    LOGS.info("Memulai pemuatan plugin ke semua klien...")
    
    # Dapatkan daftar semua file plugin yang akan dimuat
    plugin_files = get_plugin_files()
    
    plugins_loaded_count = 0

    for module_path in plugin_files:
        try:
            # Impor modul plugin
            module = importlib.import_module(module_path)
            
            # Ekstraksi Event Handler (Telethon)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if hasattr(func, 'ultroid_event'):
                    # Handler ditemukan
                    pattern = func.ultroid_event
                    
                    # 💥 DAFTARKAN HANDLER UNTUK SETIAP KLIEN 💥
                    for client in all_clients:
                        if client: # Pastikan klien sudah terinisialisasi
                            # Gunakan add_handler yang disediakan oleh BaseClient.py
                            client.add_handler(func, events.NewMessage(**pattern))
                            
                    plugins_loaded_count += 1
                        
            # Ekstraksi Inline Query Handler (jika ada logika khusus Ultroid)
            # ... Anda juga harus mengulang di sini untuk mendaftarkan ke setiap klien
            
        except Exception as e:
            LOGS.error(f"Gagal memuat atau mendaftarkan plugin {module_path}: {e}")

    LOGS.info(f"Selesai memuat. Total {plugins_loaded_count} handler terdaftar pada semua klien.")


# --- Bagian Kode Tambahan yang Anda Berikan (Diperbaiki Indentasinya) ---
# Saya asumsikan ini adalah bagian dari kelas Loader yang mungkin sudah ada,
# atau ini adalah kode yang menyebabkan masalah indentasi. 
# Saya menempatkannya di luar fungsi agar sintaksnya valid di file Python.

# CATATAN: Blok di bawah ini memerlukan definisi kelas 'Loader' dan metode 'self._logger'
# yang mungkin berada di file 'xteam/loader.py' yang sebenarnya, tetapi saya hanya
# menyajikan ulang bagian kodenya dengan indentasi yang benar di sini:

"""
# Contoh bagaimana blok kode ini seharusnya berada di dalam sebuah metode kelas Loader:
# class Loader:
#     def some_method(self, files, func, import_module, after_load, _single, log, self.key):
#         for plugin in sorted(files):
#             if func == import_module:
#                 plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
#             try:
#                 modl = func(plugin)
#             except ModuleNotFoundError as er:
#                 modl = None
#                 self._logger.error(f"{plugin}: '{er.name}' not installed!")
#                 continue
#             except Exception as exc:
#                 modl = None
#                 self._logger.error(f"xteam - {self.key} - ERROR - {plugin}")
#                 self._logger.exception(exc)
#                 continue
#             if _single and log:
#                 self._logger.info(f"Successfully Loaded {plugin}!")
#             if callable(after_load):
#                 if func == import_module:
#                     plugin = plugin.split(".")[-1]
#                 after_load(self, modl, plugin_name=plugin)
"""
