# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import * 
import os
import sys
import time
import asyncio 
from pytgcalls import PyTgCalls

# --- Import yang diperlukan ---
# IMPOR VARIABEL GLOBAL VC CLIENTS DARI __init__.py
#from . import vcClient 
from .startup.connections import vc_connection
from .fns.helper import bash, time_formatter, updater
from .startup.funcs import (
    WasItRestart,
    autopilot,
    customize,
    plug,
    ready,
    startup_stuff,
)
from .startup.loader import load_other_plugins 
# --- Akhir Import ---

# *** PERBAIKAN KRITIS 1: Menggunakan async def main() ***
async def main():
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        # Mengganti run_in_loop() dengan await
        and await updater()
    ):
        await bash("bash installer.sh") 
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")

    # Mengganti run_in_loop() dengan await
    await startup_stuff()

    ultroid_bot.me.phone = None 

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    # Mengganti run_in_loop() dengan await
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

    # Inisialisasi Klien VC (Lokal)
    vcClient = None
    #_vcUserClient_local = None

    if vcbot_enabled:
        # Panggil koneksi: Menerima (PyTgCalls Client, Telethon User Client)
        vcClient = await vc_connection(udB, ultroid_bot) 
        
        # *** PERBAIKAN KRITIS 2: Menetapkan Nilai ke Global Client ***
        # Gunakan variabel global yang diimpor dari __init__.py
        #global vcClient
        # *************************************************************

    # load_other_plugins: Gunakan klien lokal sebagai argumen
    await load_other_plugins(
        addons=addons, 
        pmbot=pmbot, 
        manager=manager, 
        vcbot=vcClient # Teruskan klien Telethon VC
    )

    suc_msg = """
            ----------------------------------------------------------------------
                xteam-urbot has been deployed! Visit @xteam_cloner for updates!!
            ----------------------------------------------------------------------
    """

    # for channel plugins
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # Mengganti run_in_loop() dengan await
    await customize()

    # Load Addons from Plugin Channels.
    if plugin_channels:
        # Mengganti run_in_loop() dengan await
        await plug(plugin_channels)

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        # Mengganti run_in_loop() dengan await
        await ready()

    # Edit Restarting Message (if It's restarting)
    # Mengganti run_in_loop() dengan await
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
    # *** PERUBAHAN KRITIS 3: Entry Point yang Benar ***
    
    # 1. Start bot non-blocking (membuat event loop)
    ultroid_bot.start() 

    # 2. Jadwalkan coroutine main() ke event loop bot utama.
    ultroid_bot.loop.create_task(main()) 
    
    # 3. asst.run() menjaga loop tetap hidup (blocking call).
    asst.run()
        
