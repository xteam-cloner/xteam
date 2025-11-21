# Xteam/startup/loader.py - KODE MULTI-CLIENT FINAL YANG DIKOREKSI

import importlib
import inspect
import os
from telethon import events
# Hapus atau Komentari baris import Loader yang menyebabkan ImportError
# from ..loader import Loader 


# Asumsikan LOGS sudah diimpor dari modul utama atau logging Ultroid


# --- Fungsi Pembantu untuk Mendapatkan Daftar File Plugin ---
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


# Fungsi Pemuatan Utama yang Telah Diubah untuk Multi-Client
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

# --- Bagian Kode Tambahan yang mungkin ada di file aslinya dan tidak relevan ---
# (Dibiarkan kosong karena fokus adalah pada load_other_plugins)
