# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import os
import sys
import telethonpatch
from .version import __version__
#from xteam.core.bot import ChampuBot
#from xteam.core.dir import dirr
#from xteam.core.git import git
#from xteam.core.userbot import Userbot
#from xteam.misc import dbb, heroku, sudo
#from .logging import LOGGER

# ... (awal file, semua impor, dan definisi class ULTConfig tetap sama) ...

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"

# 🛑 PENTING: Inisialisasi variabel global di sini sebelum blok IF/ELSE.
# Ini memastikan 'call_py' ada di namespace __init__.py sebelum diekspos
ultroid_bot = asst = udB = bot = call_py = vcClient = None 

class ULTConfig:
    lang = "en"
    thumb = "resources/extras/8189450f-de7f-4582-ba94-f8ec2d928b31.jpeg"
    

if run_as_module:
    import time

    from .configs import Var
    from .startup import *
    from .startup._database import UltroidDB
    from .startup.BaseClient import UltroidClient
    from .startup.connections import validate_session, vc_connection
    from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
    from .version import ultroid_version
    from telethon import __version__ as tver
    
    if not os.path.exists("./plugins"):
        LOGS.error(
            "'plugins' folder not found!\nMake sure that, you are on correct path."
        )
        exit()

    start_time = time.time()
    _ult_cache = {}
    _ignore_eval = []

    udB = UltroidDB()
    update_envs()
    #self.music = MusicModule(self)

    LOGS.info(f"Connecting to {udB.name}...")
    if udB.ping():
        LOGS.info(f"Connected to {udB.name} Successfully!")

    BOT_MODE = udB.get_key("BOTMODE")
    DUAL_MODE = udB.get_key("DUAL_MODE")
    VC_SESSION = udB.get_key("SESSION")
    
    USER_MODE = udB.get_key("USER_MODE")
    if USER_MODE:
        DUAL_MODE = False

    if BOT_MODE:
        # ... (Logika BOT_MODE tetap sama) ...
        ultroid_bot = None # Tetap None di BOT_MODE
        if not udB.get_key("BOT_TOKEN"):
            LOGS.critical('"BOT_TOKEN" not Found! ...')
            sys.exit()
    else:
        ultroid_bot = UltroidClient(
            validate_session(Var.SESSION, LOGS),
            udB=udB,
            app_version=tver,
            device_model="xteam-urbot",
        )
        ultroid_bot.run_in_loop(autobot())

    if USER_MODE:
        asst = ultroid_bot
    else:
        asst = UltroidClient("asst", bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

    # Klien bot VC (bot) tetap perlu didefinisikan sebelum PyTgCalls
    # --- Blok PyTgCalls ---
    try:
        # Asumsi Anda tetap ingin menggunakan session terpisah/khusus
        session = StringSession(str(Var.SESSION))
        bot= TelegramClient( # <-- 'bot' akan didefinisikan di sini
            session=session,
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            connection=ConnectionTcpAbridged,
            auto_reconnect=True,
            connection_retries=None,
        )
        bot.start()
        call_py = PyTgCalls(bot) # <-- 'call_py' akan didefinisikan di sini
        
        # PENTING: Start PyTgCalls secara asinkron setelah inisialisasi
        ultroid_bot.run_in_loop(call_py.start())
        LOGS.info("PyTgCalls berhasil diinisialisasi dan siap.")

    except Exception as e:
        # Jika gagal, pastikan bot dan call_py direset ke None di blok ini
        LOGS.error(f"STRING_SESSION_ERROR/PyTgCalls Gagal Inisialisasi - {e}")
        bot = None
        call_py = None
    # ----------------------

    # ... (Sisa kode tetap sama) ...
    
    vcClient = vc_connection(udB, ultroid_bot) # vcClient juga harus diinisialisasi
    _version_changes(udB)

    HNDLR = udB.get_key("HNDLR") or "."
    DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
    SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
    
# Jika bukan modul utama (misalnya diimpor oleh plugin)
else:
    print("xteam 2022 © teamx_cloner")

    from logging import getLogger

    LOGS = getLogger("xteam")
    
    # 🛑 PENTING: Semua variabel yang ingin diimpor harus diinisialisasi ke None di sini
    # Agar plugin tidak mendapatkan 'ImportError'
    ultroid_bot = asst = udB = bot = call_py = vcClient = None
