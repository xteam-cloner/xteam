import logging
from xteam import call_py, bot as client
# Hapus impor yang sudah tidak dipakai (seperti skip_current_song)

logger = logging.getLogger(__name__)

# Jika file ini tadinya punya fungsi lain, biarkan saja.
# Tapi pastikan bagian @call_py.on_update() SUDAH TIDAK ADA di sini.

# Contoh jika Anda ingin menyisakan log saja:
@call_py.on_update()
async def log_updates(client, update):
    # Ini hanya untuk memantau log, tidak menjalankan logika skip
    logger.debug(f"Update diterima: {type(update).__name__}")
    
