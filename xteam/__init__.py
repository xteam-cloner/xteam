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

from telethonpatch import TelegramClient
from telethon import utils as telethon_utils
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from pytgcalls import PyTgCalls
#from xteam.core.bot import ChampuBot
#from xteam.core.dir import dirr
#from xteam.core.git import git
#from xteam.core.userbot import Userbot
#from xteam.misc import dbb, heroku, sudo
#from .logging import LOGGER

run_as_module = __package__ in sys.argv or sys.argv[0] == "-m"


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
    VC_SESSION = udB.get_key("VC_SESSION")
    
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
            app_version=ultroid_version,
            device_model="xteam-urbot",
        )
        ultroid_bot.run_in_loop(autobot())

    if USER_MODE:
        asst = ultroid_bot
    else:
        asst = UltroidClient("asst", bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

    if VC_SESSION:
        # Assuming Var.SESSION is a valid string session
        session = StringSession(str(Var.SESSION))
        try:
            bot = TelegramClient(
                session=session,
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                connection=ConnectionTcpAbridged,
                auto_reconnect=True,
                connection_retries=None,
            )
            bot.start()
            call_py = PyTgCalls(bot) # <--- call_py is defined here
        except Exception as e:
            print(f"STRING_SESSION_ERROR - {e}")
            sys.exit()
            
    
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
