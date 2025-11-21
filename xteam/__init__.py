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
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession
from telethon import TelegramClient
import contextlib
import inspect
import time
from logging import Logger
#...
from telethonpatch import TelegramClient
from telethon import utils as telethon_utils
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from pytgcalls import PyTgCalls
from .configs import Var # Tambahkan Var di sini jika belum ada

from .startup import *
from .startup._database import UltroidDB
from .startup.BaseClient import UltroidClient
from .startup.connections import validate_session, vc_connection
from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
from .version import ultroid_version
from telethon import __version__ as tver
    

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"


class ULTConfig:
    lang = "en"
    thumb = "resources/extras/8189450f-de7f-4582-ba94-f8ec2d928b31.jpeg"


if run_as_module:
    import time
    
    # ... [Import Lainnya yang Ada] ...

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
        if DUAL_MODE:
            udB.del_key("DUAL_MODE")
            DUAL_MODE = False
        ultroid_bot = None

        if not udB.get_key("BOT_TOKEN"):
            LOGS.critical(
                '"BOT_TOKEN" not Found! Please add it, in order to use "BOTMODE"'
            )

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

    # ==========================================================
    # ⚡️ MODIFIKASI MULTI-CLIENT: INISIALISASI & KOLEKSI ⚡️
    # ==========================================================

    ULTROID_CLIENTS = {}
    
    # Klien 1: Klien utama Ultroid yang sudah diinisialisasi
    if ultroid_bot:
        ULTROID_CLIENTS[1] = ultroid_bot

    def create_additional_client(session_string, client_id):
        """Membuat klien Telethon tambahan dari string session."""
        if not session_string:
            return None
        try:
            session = StringSession(str(session_string))
            client = UltroidClient( # Gunakan UltroidClient agar memiliki semua properti khusus
                session=session,
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                udB=udB, # Teruskan udB agar klien dapat mengakses database
                app_version=tver,
                device_model=f"xteam-urbot-{client_id}",
                log_attempt=False,
            )
            LOGS.info(f"Klien Tambahan {client_id} berhasil diinisialisasi.")
            return client
        except Exception as e:
            LOGS.error(f"Gagal menginisialisasi Klien Tambahan {client_id}: {e}")
            return None

    # Inisialisasi Klien Tambahan (STRING_2 hingga STRING_5)
    # Asumsi: STRING_2, STRING_3, dll. sudah dimuat ke Var dari Environment
    ULTROID_CLIENTS[2] = create_additional_client(getattr(Var, 'STRING_2', None), 2)
    ULTROID_CLIENTS[3] = create_additional_client(getattr(Var, 'STRING_3', None), 3)
    ULTROID_CLIENTS[4] = create_additional_client(getattr(Var, 'STRING_4', None), 4)
    ULTROID_CLIENTS[5] = create_additional_client(getattr(Var, 'STRING_5', None), 5)
    
    # Bersihkan klien yang gagal diinisialisasi
    ULTROID_CLIENTS = {k: v for k, v in ULTROID_CLIENTS.items() if v is not None}

    # Definisikan list global ALL_CLIENTS untuk digunakan oleh loader dan main loop
    ALL_CLIENTS = list(ULTROID_CLIENTS.values())

    # Jika klien utama (bot) digunakan di kode VC di bawah, gunakan klien 1
    bot = ULTROID_CLIENTS.get(1) 

    # ==========================================================
    # ⚡️ MODIFIKASI MULTI-CLIENT BERAKHIR ⚡️
    # ==========================================================

if BOT_MODE:
        ultroid_bot = asst
        if udB.get_key("OWNER_ID"):
            try:
                ultroid_bot.me = ultroid_bot.run_in_loop(
                    ultroid_bot.get_entity(udB.get_key("OWNER_ID"))
                )
            except Exception as er:
                LOGS.exception(er)
        elif not asst.me.bot_inline_placeholder and asst._bot:
            ultroid_bot.run_in_loop(enable_inline(ultroid_bot, asst.me.username))

vcClient = vc_connection(udB, ultroid_bot)
_version_changes(udB)
HNDLR = udB.get_key("HNDLR") or "."
DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
else:
print("xteam 2022 © teamx_cloner")
from logging import getLogger
LOGS = getLogger("xteam")
ultroid_bot = asst = udB = bot = call_py = vcClient = None
