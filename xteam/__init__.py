# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import sys
import telethonpatch
from .version import __version__

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"


class ULTConfig:
    lang = "en"
    thumb = "resources/extras/8189450f-de7f-4582-ba94-f8ec2d928b31.jpeg"


if run_as_module:
    import time
    import asyncio

    from typing import Optional
    from pytgcalls import PyTgCalls
    from telethon import TelegramClient
    
    from .configs import Var
    from .startup import *
    from .startup._database import UltroidDB
    from .startup.BaseClient import UltroidClient
    from .startup.connections import validate_session
    from .startup.funcs import _version_changes, autobot, enable_inline, update_envs
    from .version import ultroid_version

    import logging
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)

    if not os.path.exists("./plugins"):
        LOGS.error(
            "'plugins' folder not found!\nMake sure that, you are on correct path."
        )
        exit()

    start_time = time.time()
    _ult_cache = {}
    _ignore_eval = []
    
    call_py: Optional[PyTgCalls] = None
    bot : Optional[TelegramClient] = None

    udB = UltroidDB()
    update_envs()

    LOGS.info(f"Connecting to {udB.name}...")
    if udB.ping():
        LOGS.info(f"Connected to {udB.name} Successfully!")

    BOT_MODE = udB.get_key("BOTMODE")
    
    # Force DUAL_MODE to always be True
    DUAL_MODE = True
    USER_MODE = udB.get_key("USER_MODE")

    if BOT_MODE:
        ultroid_bot = None
        if not udB.get_key("BOT_TOKEN"):
            LOGS.critical('"BOT_TOKEN" not Found!')
            sys.exit()
    else:
        # HAPUS YANG LAMA, GANTI DENGAN INI:
        CURRENT_SESSION = os.environ.get("SESSION") or Var.SESSION
        client_id = os.environ.get("CLIENT_ID", "1")
        ultroid_bot = UltroidClient(
            validate_session(CURRENT_SESSION, LOGS),
            udB=udB,
            app_version=ultroid_version,
            session_name=f"ultroid{client_id}", 
            device_model=f"xteam-urbot{client_id}",
        )
        ultroid_bot.run_in_loop(autobot())
        

    if USER_MODE:
        asst = ultroid_bot
    else:
        client_id = os.environ.get("CLIENT_ID", "1")
        asst_session = f"asst{client_id}"
        asst = UltroidClient(asst_session, bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

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

    _version_changes(udB)

    HNDLR = udB.get_key("HNDLR") or "."
    DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
    SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
else:
    print("xteam 2022 © Xteam-Cloner")

    import logging
    from logging import getLogger

    LOGS = getLogger("xteam")
    
    logging.basicConfig(level=logging.DEBUG)
    LOGS.setLevel(logging.DEBUG)

    ultroid_bot = asst = udB = bot = call_py = None
    
