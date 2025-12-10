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
import asyncio # Wajib untuk loop.create_task()

# --- Import yang diperlukan ---
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

# *** PERBAIKAN KRITIS 1: Mengganti run_in_loop() dengan await ***
async def main():
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        # GANTI ultroid_bot.run_in_loop(updater()) MENJADI await updater()
        and await updater()
    ):
        # GANTI ultroid_bot.run_in_loop(bash("...")) MENJADI await bash("...")
        await bash("bash installer.sh") 
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")

    # GANTI ultroid_bot.run_in_loop(startup_stuff()) MENJADI await startup_stuff()
    await startup_stuff()

    ultroid_bot.me.phone = None 

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    # GANTI ultroid_bot.run_in_loop(autopilot()) MENJADI await autopilot()
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

    # Inisialisasi Klien VC (Sudah menggunakan await)
    vcClient = None
    if vcbot_enabled:
        vcClient = await vc_connection(udB, ultroid_bot) 
        
    # load_other_plugins (Sudah menggunakan await)
    await load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcClient)

    suc_msg = """
            ----------------------------------------------------------------------
                xteam-urbot has been deployed! Visit @xteam_cloner for updates!!
            ----------------------------------------------------------------------
    """

    # for channel plugins
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # GANTI ultroid_bot.run_in_loop(customize()) MENJADI await customize()
    await customize()

    # Load Addons from Plugin Channels.
    if plugin_channels:
        # GANTI ultroid_bot.run_in_loop(plug(...)) MENJADI await plug(...)
        await plug(plugin_channels)

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        # GANTI ultroid_bot.run_in_loop(ready()) MENJADI await ready()
        await ready()

    # Edit Restarting Message (if It's restarting)
    # GANTI ultroid_bot.run_in_loop(WasItRestart(udB)) MENJADI await WasItRestart(udB)
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
    # *** PERUBAHAN KRITIS 2: Entry Point yang Benar ***
    
    # 1. Start bot non-blocking (membuat event loop)
    ultroid_bot.start() 

    # 2. Jadwalkan coroutine main() ke event loop bot utama.
    # Ini memastikan main() berjalan di event loop yang sudah aktif.
    ultroid_bot.loop.create_task(main()) 
    
    # 3. asst.run() menjaga loop tetap hidup.
    asst.run() 
