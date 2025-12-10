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

# --- BARIS BARU: Import yang diperlukan untuk Event Handling & VC ---
from telethon import events
from .startup.connections import vc_connection # Import vc_connection
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
# --- AKHIR BARIS BARU ---


# *** PERUBAHAN KRITIS: MENGGANTI async def main() dengan Event Handler ***
# Handler ini akan dipicu ketika bot menerima pesan pertamanya dari dirinya sendiri (saat online).
@ultroid_bot.on(events.NewMessage(func=lambda e: not e.is_group and e.is_private and e.is_self))
async def startup_tasks(event):
    
    # --- LOGIKA RUN ONCE (Wajib untuk Startup Handler) ---
    if hasattr(ultroid_bot, '_setup_done'):
        # Handler ini sudah dijalankan sebelumnya. Hentikan eksekusi.
        ultroid_bot.remove_event_handler(startup_tasks)
        return
    ultroid_bot._setup_done = True
    # --------------------------------------------------------

    # --- KODE LAMA DARI async def main() DIMULAI DI SINI ---

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        and ultroid_bot.run_in_loop(updater())
    ):
        ultroid_bot.run_in_loop(bash("bash installer.sh"))
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")

    ultroid_bot.run_in_loop(startup_stuff())

    # Diasumsikan ultroid_bot.me sudah tersedia di dalam event handler
    ultroid_bot.me.phone = None 

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    ultroid_bot.run_in_loop(autopilot())

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

    # *** PERBAIKAN VC CLIENT: Await Inisialisasi ***
    vcClient = None
    if vcbot_enabled:
        # Panggil fungsi async vc_connection dan TUNGGU hasilnya
        vcClient = await vc_connection(udB, ultroid_bot) 
        
    # *** PERBAIKAN LOADER: Await load_other_plugins ***
    await load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcClient)

    suc_msg = """
            ----------------------------------------------------------------------
                xteam-urbot has been deployed! Visit @xteam_cloner for updates!!
            ----------------------------------------------------------------------
    """

    # for channel plugins
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # Customize Ultroid Assistant...
    ultroid_bot.run_in_loop(customize())

    # Load Addons from Plugin Channels.
    if plugin_channels:
        ultroid_bot.run_in_loop(plug(plugin_channels))

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        ultroid_bot.run_in_loop(ready())

    # Edit Restarting Message (if It's restarting)
    ultroid_bot.run_in_loop(WasItRestart(udB))

    try:
        cleanup_cache()
    except BaseException:
        pass

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •ULTROID•"
    )
    LOGS.info(suc_msg)
    
    # --- KODE LAMA DARI async def main() BERAKHIR DI SINI ---


if __name__ == "__main__":
    # *** PERBAIKAN KRITIS: Entry Point File Sederhana ***
    # Ini untuk mengatasi TypeError. Bot akan memulai loop dan menjalankan handler di atas.
    
    ultroid_bot.run() # Memulai bot utama dan event loop-nya
    
    # asst.run() # Memulai bot asisten di loop yang sama atau loop terpisah
                 # (Biarkan ini jika diperlukan oleh framework)
    
