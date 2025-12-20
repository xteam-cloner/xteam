# xteam-urbot 
# Copyright (C) 2021-2025 Xteam_clonet

from . import *
import os
import sys
import time
import asyncio 
import logging
from pytgcalls import PyTgCalls
from telethon import TelegramClient 
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.sessions import StringSession
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import xteam 
from .startup.connections import validate_session
from strings import get_string
from .fns.helper import bash, time_formatter, updater
from .startup.funcs import (
    WasItRestart,
    autopilot,
    customize,
    fetch_ann, 
    plug,
    ready,
    startup_stuff,
)
from .startup.loader import load_other_plugins 

LOGS = logging.getLogger(__name__)

def register_vc_handlers():
    """
    Mendaftarkan unified_update_handler ke instance PyTgCalls.
    """
    try:
        from xteam.handlers import unified_update_handler 
        if xteam.call_py:
            xteam.call_py.on_update()(unified_update_handler)
            LOGS.info("✅ PyTgCalls Event Handlers registered.")
    except ImportError:
        LOGS.error("Gagal mengimpor unified_update_handler.")
    except Exception as e:
        LOGS.error(f"Error saat registrasi handler: {e}")

async def main_async():
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        and await updater()
    ):
        await bash("bash installer.sh") 
        os.execl(sys.executable, sys.executable, "-m", "xteam")

    await startup_stuff()

    ultroid_bot.me.phone = None 

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    await autopilot()

    pmbot = udB.get_key("PMBOT")
    manager = udB.get_key("MANAGER")
    addons = udB.get_key("ADDONS") or Var.ADDONS
    vcbot_enabled = udB.get_key("VCBOT") or Var.VCBOT
    
    if HOSTED_ON == "okteto":
        vcbot_enabled = False

    call_py = None
    
    if vcbot_enabled:
        # --- LOGIKA MULTI SESSION START ---
        session_candidates = [
            udB.get_key("VC_SESSION") or Var.VC_SESSION,
            udB.get_key("VC_SESSION1") or getattr(Var, "VC_SESSION1", None),
            udB.get_key("VC_SESSION2") or getattr(Var, "VC_SESSION2", None),
            udB.get_key("VC_SESSION3") or getattr(Var, "VC_SESSION3", None)
        ]
        
        selected_session = None
        for sess in session_candidates:
            if sess:
                selected_session = sess
                break 

        session = None
        if selected_session:
            session = validate_session(selected_session)
            LOGS.info("✅ VCBOT Berhasil menemukan sesi yang tersedia.")
        elif HOSTED_ON == "heroku":
            LOGS.warning("VCBOT enabled tapi semua VC_SESSION kosong. VC Bot disabled.")
            vcbot_enabled = False
            call_py = None
        else:
            session = "xteam-vc-client"
            LOGS.info("VCBOT enabled tapi VC_SESSION kosong. Menggunakan sesi lokal.")

        if session:
            try:
                bot = TelegramClient(
                    session=session,
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    connection=ConnectionTcpAbridged,
                    auto_reconnect=True,
                    connection_retries=None,
                )
                
                await bot.start() 
                vc_me = await bot.get_me()
                full_name = vc_me.first_name
                if vc_me.last_name:
                    full_name += f" {vc_me.last_name}"
                LOGS.info(f"Assistans Start as {full_name}") 
                
                call_py = PyTgCalls(bot)
                await call_py.start()
                
                # Integrasi ke namespace global
                xteam.asst = bot 
                xteam.call_py = call_py
                
                # Registrasi handler untuk auto-skip/stream ended
                #register_vc_handlers()
                
            except (AuthKeyDuplicatedError, EOFError):
                LOGS.error("Sesi duplikat atau kadaluarsa. VC Bot dimatikan.")
                call_py = None
            except Exception as er:
                LOGS.error("Gagal memulai PyTgCalls Client.")
                LOGS.exception(er)
                call_py = None
        # --- LOGIKA MULTI SESSION END ---

    await load_other_plugins(
        addons=addons, 
        pmbot=pmbot, 
        manager=manager, 
        vcbot=call_py
    )

    suc_msg = """
            ----------------------------------------------------------------------
                xteam-urbot has been deployed! Visit @xteam_cloner for updates!!
            ----------------------------------------------------------------------
    """

    plugin_channels = udB.get_key("PLUGIN_CHANNEL")
    await customize()

    if plugin_channels:
        await plug(plugin_channels)

    if not udB.get_key("LOG_OFF"):
        await ready()

    await WasItRestart(udB)

    try:
        cleanup_cache()
    except:
        pass

    LOGS.info(f"Took {time_formatter((time.time() - start_time)*1000)} to start")
    LOGS.info(suc_msg)


if __name__ == "__main__":
    ultroid_bot.start() 
    ultroid_bot.loop.create_task(main_async()) 
    asst.run()
