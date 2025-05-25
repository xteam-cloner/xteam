# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

from . import *


def main():
    import os
    import sys
    import time

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

        os.execl(sys.executable, sys.executable, "-m", "xteam")

    ultroid_bot.run_in_loop(startup_stuff())

    ultroid_bot.me.phone = None

    if not ultroid_bot.me.bot:
        udB.set_key("OWNER_ID", ultroid_bot.uid)

    LOGS.info("Initialising...")

    ultroid_bot.run_in_loop(autopilot())

    pmbot = udB.get_key("PMBOT")
    manager = udB.get_key("MANAGER")
    addons = udB.get_key("ADDONS") or Var.ADDONS
    vcbot = udB.get_key("VCBOT") or Var.VCBOT
    if HOSTED_ON == "okteto":
        vcbot = False

    if (HOSTED_ON == "termux" or udB.get_key("LITE_DEPLOY")) and udB.get_key(
        "EXCLUDE_OFFICIAL"
    ) is None:
        _plugins = "autocorrect autopic audiotools compressor forcesubscribe fedutils gdrive glitch instagram nsfwfilter nightmode pdftools profanityfilter writer youtube"
        udB.set_key("EXCLUDE_OFFICIAL", _plugins)

    load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcbot)

    suc_msg = """
            ----------------------------------------------------------------------
                xteam-urbot has been deployed! @xteam_cloner for updates!!
            ----------------------------------------------------------------------
    """

    # for channel plugins
    plugin_channels = udB.get_key("PLUGIN_CHANNEL")

    # Customize Ultroid Assistant...
    #ultroid_bot.run_in_loop(customize())

    # Load Addons from Plugin Channels.
    if plugin_channels:
        ultroid_bot.run_in_loop(plug(plugin_channels))

    # Send/Ignore Deploy Message..
    if not udB.get_key("LOG_OFF"):
        ultroid_bot.run_in_loop(ready())

    # TODO: Announcement API IS DOWN
    # if AsyncIOScheduler:
    #     scheduler = AsyncIOScheduler()
    #     scheduler.add_job(fetch_ann, "interval", minutes=12 * 60)
    #     scheduler.start()

    # Edit Restarting Message (if It's restarting)
    ultroid_bot.run_in_loop(WasItRestart(udB))

    try:
        cleanup_cache()
    except BaseException:
        pass

    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •xteam-urbot•"
    )
    LOGS.info(suc_msg)

import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from xteam.startup.BaseClient import PyrogramClient # Asumsi lokasi file Anda
from xteam.configs import Var # Asumsi Var berisi API_ID, API_HASH

# Asumsi LOGS sudah didefinisikan di xteam/__init__.py
from xteam import LOGS

async def main():
    # Inisialisasi klien Pyrogram Anda
    # Ganti 'my_account_session' dengan nama sesi yang sesuai untuk userbot Anda
    # Atau jika ini bot, gunakan token bot Anda (Var.BOT_TOKEN)
    app = PyrogramClient(
        name="Xteammusic", # Nama sesi unik
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN, # Uncomment ini jika Anda menggunakan bot token
        logger=LOGS,
        log_attempt=True,
        exit_on_error=True
    )

    # Memulai klien (dan juga PyTgCalls di dalamnya)
    await app.start_client()
    LOGS.info("Pyrogram Client and PyTgCalls are now running!")

    # --- Contoh Penggunaan PyTgCalls ---

    # Listener untuk perintah /joinvc
    @app.on_message(filters.command("joinvc") & filters.private)
    async def join_voice_chat(_, message: Message):
        chat_id = message.chat.id
        LOGS.info(f"Received /joinvc command in chat {chat_id}")
        
        # Contoh: mencoba bergabung ke obrolan suara di grup atau saluran
        # Anda perlu mendapatkan ID grup/saluran yang memiliki obrolan suara aktif
        # Untuk tujuan contoh, kita akan bergabung ke obrolan suara di chat_id ini
        # Jika ini adalah userbot, Anda bisa bergabung ke VC di grup/saluran
        # Jika ini bot, bot harus admin dengan hak kelola obrolan suara
        
        # Dapatkan peer (chat) dari ID pesan
        target_chat_id = message.chat.id # Atau ID grup/saluran tertentu
        
        try:
            # Bergabung ke obrolan suara
            await app.call_py.join_group_call(
                target_chat_id,
                # Sebagai contoh, kita akan memutar 'input.raw' atau audio dummy
                # Anda perlu menyediakan sumber audio yang valid
                # Misalnya, dari file audio lokal, atau URL stream
                # Lihat dokumentasi PyTgCalls untuk detail lebih lanjut tentang `InputAudioStream`
                # Untuk tes awal, kita bisa bergabung tanpa memutar apa pun jika tidak ada file
                # Anda bisa mengganti ini dengan audio stream sebenarnya
                # Contoh: AudioInputFromFile("path/to/your/audio.raw")
            )
            await message.reply(f"Berhasil bergabung ke obrolan suara di chat `{target_chat_id}`.")
            LOGS.info(f"Successfully joined voice chat in {target_chat_id}")
        except Exception as e:
            await message.reply(f"Gagal bergabung ke obrolan suara: {e}")
            LOGS.error(f"Failed to join voice chat: {e}")

    # Listener untuk perintah /play
    @app.on_message(filters.command("play") & filters.private)
    async def play_audio(_, message: Message):
        chat_id = message.chat.id
        if not message.reply_to_message or not message.reply_to_message.audio:
            await message.reply("Balas ke file audio untuk memutar.")
            return

        audio_file = message.reply_to_message.audio
        # Mendapatkan file audio dari Telegram
        downloaded_file = await app.download_media(audio_file)
        
        try:
            # Memutar audio di obrolan suara aktif
            await app.call_py.stream(
                chat_id, # ID chat di mana obrolan suara aktif
                downloaded_file # Path ke file audio yang diunduh
            )
            await message.reply(f"Mulai memutar audio di obrolan suara di chat `{chat_id}`.")
            LOGS.info(f"Started playing audio in voice chat in {chat_id}")
        except Exception as e:
            await message.reply(f"Gagal memutar audio: {e}")
            LOGS.error(f"Failed to play audio: {e}")
        finally:
            # Hapus file setelah digunakan
            import os
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)

    # Listener untuk perintah /stopvc
    @app.on_message(filters.command("stopvc") & filters.private)
    async def stop_voice_chat(_, message: Message):
        chat_id = message.chat.id
        LOGS.info(f"Received /stopvc command in chat {chat_id}")
        try:
            # Mengakhiri atau meninggalkan obrolan suara
            await app.call_py.leave_group_call(chat_id)
            await message.reply(f"Berhasil meninggalkan obrolan suara di chat `{chat_id}`.")
            LOGS.info(f"Successfully left voice chat in {chat_id}")
        except Exception as e:
            await message.reply(f"Gagal meninggalkan obrolan suara: {e}")
            LOGS.error(f"Failed to leave voice chat: {e}")

    # Menunggu klien untuk berhenti (misalnya, jika ada Ctrl+C)
    # Ini adalah cara Pyrogram agar bot tetap berjalan
    await app.idle()

    # Menghentikan klien (dan juga PyTgCalls di dalamnya) saat idle selesai
    await app.stop_client()
    LOGS.info("Pyrogram Client and PyTgCalls have stopped.")

if __name__ == "__main__":
    asyncio.run(main())
    

if __name__ == "__main__":
    main()

    asst.run()
