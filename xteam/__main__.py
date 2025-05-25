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
import os
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pytgcalls import PyTgCalls
from pytgcalls.types import InputAudioStream
from xteam.startup.BaseClient import PyrogramClient # Assuming this is your custom Pyrogram Client
from xteam.configs import Var # Assuming Var contains API_ID, API_HASH, BOT_TOKEN
from xteam import LOGS # Assuming LOGS is defined for logging

# Dictionary to store active group calls per chat ID
# This is crucial for managing multiple voice chats if needed
active_group_calls: dict[int, GroupCall] = {}

async def main_music_bot():
    # Initialize your Pyrogram Client
    # Ensure Var.BOT_TOKEN is correctly set for a bot
    app = PyrogramClient(
        name="Xteammusic", # Unique session name
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN, # Use BOT_TOKEN for a bot
        logger=LOGS,
        log_attempt=True,
        exit_on_error=True
    )

    # Initialize PyTgCalls with your Pyrogram Client
    # This automatically integrates PyTgCalls with your running Pyrogram client
    pytgcalls_client = PyTgCalls(app)

    # Start the Pyrogram client and PyTgCalls
    await asst.start()
    await app.start()
    await pytgcalls_client.start()
    LOGS.info("Pyrogram Client and PyTgCalls are now running!")

    # --- PyTgCalls Command Handlers ---

    @app.on_message(filters.command("joinvc") & filters.private)
    async def join_voice_chat(_, message: Message):
        if not message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            await message.reply("Please use this command in a group or channel with an active voice chat.")
            return

        chat_id = message.chat.id
        LOGS.info(f"Received /joinvc command in chat {chat_id}")

        if chat_id in active_group_calls:
            await message.reply("I am already in a voice chat in this group.")
            return

        try:
            # Check if the bot is an admin with 'manage_voice_chats' permission
            # This is crucial for a bot to join a voice chat
            # If it's a userbot, this permission check might not be strictly necessary
            # but it's good practice for any account joining a VC.
            member = await app.get_chat_member(chat_id, app.me.id)
            if not member.can_manage_voice_chats:
                await message.reply("I need `Manage Voice Chats` permission to join the voice chat.")
                return

            # Join the voice chat
            await pytgcalls_client.join_group_call(
                chat_id,
                InputAudioStream() # Join silently, or you can provide a default audio stream
            )
            # Store the group call instance
            active_group_calls[chat_id] = pytgcalls_client.get_active_group_call(chat_id)
            await message.reply(f"Successfully joined voice chat in chat `{chat_id}`.")
            LOGS.info(f"Successfully joined voice chat in {chat_id}")
        except Exception as e:
            await message.reply(f"Failed to join voice chat: {e}")
            LOGS.error(f"Failed to join voice chat: {e}")

    @app.on_message(filters.command("play") & filters.private)
    async def play_audio(_, message: Message):
        chat_id = message.chat.id

        if chat_id not in active_group_calls:
            await message.reply("I'm not in a voice chat in this group. Use /joinvc first.")
            return

        if not message.reply_to_message or not message.reply_to_message.audio:
            await message.reply("Reply to an audio file to play it.")
            return

        audio_file_path = None
        try:
            # Download the audio file from Telegram
            audio_file_path = await app.download_media(message.reply_to_message.audio)
            LOGS.info(f"Downloaded audio to: {audio_file_path}")

            # Stream the audio in the active voice chat
            await active_group_calls[chat_id].play(InputAudioStream(audio_file_path))

            await message.reply(f"Started playing audio in voice chat in chat `{chat_id}`.")
            LOGS.info(f"Started playing audio in voice chat in {chat_id}")
        except Exception as e:
            await message.reply(f"Failed to play audio: {e}")
            LOGS.error(f"Failed to play audio: {e}")
        finally:
            # Clean up the downloaded file
            if audio_file_path and os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                LOGS.info(f"Cleaned up audio file: {audio_file_path}")


    @app.on_message(filters.command("stopvc") & filters.private)
    async def stop_voice_chat(_, message: Message):
        chat_id = message.chat.id
        LOGS.info(f"Received /stopvc command in chat {chat_id}")

        if chat_id not in active_group_calls:
            await message.reply("I am not currently in a voice chat in this group.")
            return

        try:
            # End or leave the voice chat
            await pytgcalls_client.leave_group_call(chat_id)
            del active_group_calls[chat_id] # Remove from active calls
            await message.reply(f"Successfully left voice chat in chat `{chat_id}`.")
            LOGS.info(f"Successfully left voice chat in {chat_id}")
        except Exception as e:
            await message.reply(f"Failed to leave voice chat: {e}")
            LOGS.error(f"Failed to leave voice chat: {e}")

    # Keep the client running until termination (e.g., Ctrl+C)
    await app.idle()

    # Stop PyTgCalls and then the Pyrogram client
    await pytgcalls_client.stop()
    await app.stop()
    LOGS.info("Pyrogram Client and PyTgCalls have stopped.")

if __name__ == "__main__":
    # Ensure you have your environment variables for API_ID, API_HASH, and BOT_TOKEN set.
    # For example:
    # API_ID = 12345
    # API_HASH = "your_api_hash"
    # BOT_TOKEN = "your_bot_token"
    # Or define them in xteam/configs/Var.py
    asyncio.run(main_music_bot())
