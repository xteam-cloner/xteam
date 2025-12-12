# Xteam/__main__.py - Ultroid UserBot Core
# Copyright (C) 2021-2025 TeamUltroid
#
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import *
import os
import sys
import time
import asyncio 

# Impor untuk PyTgCalls dan Telethon
from pytgcalls import PyTgCalls
from telethon import TelegramClient 
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError

# Impor namespace xteam (penting untuk mengekspos variabel global)
import xteam # Tambahkan impor eksplisit

# Asumsi impor utilitas VC, error, dan strings ada
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

# ⚠️ CATATAN: 'call_py' harus didefinisikan sebagai 'None' di xteam/__init__.py
# agar dapat diakses oleh modul lain.

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

    if (HOSTED_ON == "termux" or udB.get_key("LITE_DEPLOY")) and udB.get_key(
        "EXCLUDE_OFFICIAL"
    ) is None:
        _plugins = "autocorrect autopic audiotools compressor forcesubscribe fedutils gdrive glitch instagram nsfwfilter nightmode pdftools profanityfilter writer youtube"
        udB.set_key("EXCLUDE_OFFICIAL", _plugins)

    # 🛑 LOGIKA VC_CONNECTION (REVISI)
    
    # 1. Pastikan xteam.call_py diinisialisasi ke None
    call_py = None
    
    if vcbot_enabled:
        VC_SESSION = udB.get_key("VC_SESSION") or Var.VC_SESSION
        
        if VC_SESSION and VC_SESSION != Var.SESSION:
            LOGS.info("Starting up Telethon Client for VcClient (Inlined).")
            vc_client = None
            
            try:
                # 2. Buat Klien MTProto 
                vc_client = TelegramClient(
                    session=validate_session(VC_SESSION, _exit=False),
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH, 
                    system_version="UltroidVC"
                )
                await vc_client.start()
                vc_me = await vc_client.get_me()
                LOGS.info(f"VC Client login successful: @{vc_me.username} (ID: {vc_me.id})") 
                
                # 3. Buat instance PyTgCalls 
                call_py_instance = PyTgCalls(vc_client) 
                await call_py_instance.start()
                
                LOGS.info("PyTgCalls Client started successfully.")
                
                # 🛠️ PERBAIKAN KRITIS: Ekspos klien ke namespace global xteam
                call_py = call_py_instance
                
            except (AuthKeyDuplicatedError, EOFError):
                LOGS.info(get_string("py_c3"))
                udB.del_key("VC_SESSION")
                call_py = None # Pastikan tetap None jika gagal otentikasi
            except Exception as er:
                LOGS.info("While creating PyTgCalls Client for VC.")
                LOGS.exception(er)
                call_py = None # Pastikan tetap None jika ada error lain
        else:
            LOGS.info("VCBOT enabled but VC_SESSION missing or same as main session.")

    # 🛑 MELEWATKAN KLIEN KE LOADER PLUGIN
    # load_other_plugins akan mendapatkan objek PyTgCalls yang valid atau None.
    await load_other_plugins(
        addons=addons, 
        pmbot=pmbot, 
        manager=manager, 
        vcbot=call_py # Menggunakan klien yang sudah diekspos
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
    except BaseException:
        pass

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •ULTROID•"
    )
    LOGS.info(suc_msg)


if __name__ == "__main__":
    
    ultroid_bot.start() 

    ultroid_bot.loop.create_task(main_async()) 
    
    asst.run()
            
