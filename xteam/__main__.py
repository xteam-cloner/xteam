# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

from . import *

# *** PERUBAHAN 1: Impor Fungsi Asinkron VC ***
from .startup.connections import vc_connection 


# *** PERUBAHAN 2: Definisikan main sebagai async def ***
async def main():
    import os
    import sys
    import time

    from .fns.helper import bash, time_formatter, updater
    from .startup.funcs import (
        WasItRestart,
        autopilot,
        customize,
        plug,
        ready,
        startup_stuff,
    )
    # Asumsikan load_other_plugins di loader.py sudah diubah menjadi async def
    from .startup.loader import load_other_plugins 

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        AsyncIOScheduler = None

    # Option to Auto Update On Restarts..
    if (
        udB.get_key("UPDATE_ON_RESTART")
        and os.path.exists(".git")
        # Perlu menggunakan await di sini jika updater() adalah coroutine, 
        # tetapi kita akan pertahankan pola run_in_loop Ultroid
        and ultroid_bot.run_in_loop(updater())
    ):
        ultroid_bot.run_in_loop(bash("bash installer.sh"))

        os.execl(sys.executable, sys.executable, "-m", "pyUltroid")

    ultroid_bot.run_in_loop(startup_stuff())

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

    # *** PERUBAHAN 3: Inisialisasi dan Await Klien VC ***
    vcClient = None
    if vcbot_enabled:
        # Panggil fungsi async vc_connection dan TUNGGU hasilnya
        vcClient = await vc_connection(udB, ultroid_bot) 
        
    # *** PERUBAHAN 4: Await load_other_plugins dan Teruskan vcClient ***
    # vcClient adalah objek klien yang valid, bukan lagi boolean/string.
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


if __name__ == "__main__":
    # *** PERUBAHAN 5: Menjalankan Coroutine main() ***
    # Ini untuk mengatasi TypeError dan RuntimeWarning sebelumnya.
    # Kita menggunakan ultroid_bot.run() dan mengharapkan bot framework
    # akan menjalankan coroutine main() sebelum memulai loop.
    
    # Klien bot yang benar harus memulai loop, dan kita menyerahkan main() ke dalamnya.
    ultroid_bot.start()
    asst.run(main()) 


    # asst.run() # Baris ini mungkin tidak diperlukan atau harus disesuaikan, 
                # tergantung bagaimana framework Anda memulai dua klien.
                # Untuk saat ini, kita akan fokus pada bot utama.
  
