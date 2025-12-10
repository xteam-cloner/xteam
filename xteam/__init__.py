import os
import sys
import asyncio # WAJIB: Untuk menjalankan kode asinkron di top-level
import time
import telethonpatch

# --- Import Lokal (Asumsi) ---
from .version import __version__
from .configs import Var
from .startup import * # Mengandung LOGS, dll.
from .startup._database import UltroidDB
from .startup.BaseClient import UltroidClient
from .startup.connections import validate_session, vc_connection # Import fungsi VC yang sudah di-await
from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
from .version import ultroid_version
# -----------------------------

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"

# --- DEKLARASI GLOBAL ---
# Harus dideklarasikan di sini agar dapat diakses di top-level setelah asyncio.run() selesai
ultroid_bot = asst = udB = vcClient = None
start_time = 0.0

class ULTConfig:
    lang = "en"
    thumb = "resources/extras/8189450f-de7f-4582-ba94-f8ec2d928b31.jpeg"


if run_as_module:
    
    # --- FUNGSI STARTUP ASINKRON UTAMA ---
    async def initialize_ultroid():
        """
        Fungsi Asinkron yang menampung semua logika startup Ultroid, 
        memungkinkan penggunaan 'await'.
        """
        global ultroid_bot, asst, udB, vcClient, start_time
        
        start_time = time.time()
        
        if not os.path.exists("./plugins"):
            LOGS.error("'plugins' folder not found!\nMake sure that, you are on correct path.")
            sys.exit(1)

        _ult_cache = {}
        _ignore_eval = []

        udB = UltroidDB()
        update_envs()

        LOGS.info(f"Connecting to {udB.name}...")
        if udB.ping():
            LOGS.info(f"Connected to {udB.name} Successfully!")

        BOT_MODE = udB.get_key("BOTMODE")
        DUAL_MODE = udB.get_key("DUAL_MODE")
        USER_MODE = udB.get_key("USER_MODE")
        
        if USER_MODE:
            DUAL_MODE = False

        if BOT_MODE:
            if DUAL_MODE:
                udB.del_key("DUAL_MODE")
                DUAL_MODE = False
            ultroid_bot = None

            if not udB.get_key("BOT_TOKEN"):
                LOGS.critical('"BOT_TOKEN" not Found! Please add it, in order to use "BOTMODE"')
                sys.exit(1)
        else:
            ultroid_bot = UltroidClient(
                validate_session(Var.SESSION, LOGS),
                udB=udB,
                app_version=ultroid_version,
                device_model="xteam-urbot",
            )
            # Ini biasanya tidak diawaitkan karena berjalan di background
            ultroid_bot.run_in_loop(autobot())

        # Inisialisasi Asisten Bot
        if USER_MODE:
            asst = ultroid_bot
        else:
            client_id = os.environ.get("CLIENT_ID", "1")
            asst_session = f"asst{client_id}"
            asst = UltroidClient(asst_session, bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

        # Finalisasi Objek Klien
        if BOT_MODE:
            ultroid_bot = asst
            if udB.get_key("OWNER_ID"):
                try:
                    # Menggunakan 'await'
                    ultroid_bot.me = await ultroid_bot.get_entity(udB.get_key("OWNER_ID"))
                except Exception as er:
                    LOGS.exception(er)
        elif not asst.me.bot_inline_placeholder and asst._bot:
            # Menggunakan 'await'
            await enable_inline(ultroid_bot, asst.me.username)

        # --- PERBAIKAN KRITIS UNTUK KONEKSI VC ---
        # Baris yang sebelumnya memicu SyntaxError: 'await' outside function
        vcClient = await vc_connection(udB, ultroid_bot) 
        # ------------------------------------------

        _version_changes(udB)

        HNDLR = udB.get_key("HNDLR") or "."
        DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
        SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
        
        # Lanjutkan ke pemuatan plugin dan menjalankan klien utama.
        # Asumsi fungsi load_plugins/main_loop dipanggil di sini.
        # Contoh: await ultroid_bot.run_until_disconnected() 


    # --- PANGGILAN SINKRON UTAMA (TOP-LEVEL) ---
    try:
        # Menjalankan fungsi asinkron initialize_ultroid() di event loop utama
        LOGS.info("Starting Ultroid Core...")
        asyncio.run(initialize_ultroid()) 
        LOGS.info("Ultroid Core Shut Down.")
    except KeyboardInterrupt:
        LOGS.info("Ultroid Shutdown by user.")
    except Exception as e:
        LOGS.critical(f"Fatal error during Ultroid startup: {e}")
        LOGS.exception(e)
        sys.exit(1)

else:
    print("xteam 2022 © Xteam-Cloner")
    
    from logging import getLogger
    LOGS = getLogger("xteam")
    
    # Variabel tetap None jika tidak dijalankan sebagai module
    ultroid_bot = asst = udB = vcClient = None
  
