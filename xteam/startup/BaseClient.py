# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import contextlib
import inspect
import sys
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

from ..configs import Var
from . import *


class UltroidClient(TelegramClient):
    def __init__(
        self,
        session,
        api_id=None,
        api_hash=None,
        bot_token=None,
        udB=None,
        logger: Logger = LOGS,
        log_attempt=True,
        exit_on_error=True,
        *args,
        **kwargs,
    ):
        self._cache = {}
        self._dialogs = []
        self._handle_error = exit_on_error
        self._log_at = log_attempt
        self.logger = logger
        self.udB = udB
        kwargs["api_id"] = api_id or Var.API_ID
        kwargs["api_hash"] = api_hash or Var.API_HASH
        kwargs["base_logger"] = TelethonLogger
        super().__init__(session, **kwargs)
        self.run_in_loop(self.start_client(bot_token=bot_token))
        self.dc_id = self.session.dc_id
        # self.call_py = PyTgCalls(self)  # PyTgCalls for Telethon, if needed later.

    def __repr__(self):
        return f"<Ultroid.Client :\n self: {self.full_name}\n bot: {self._bot}\n>"

    @property
    def __dict__(self):
        if self.me:
            return self.me.to_dict()

    async def start_client(self, **kwargs):
        """function to start client"""
        if self._log_at:
            self.logger.info("Trying to login.")
        try:
            await self.start(**kwargs)
        except ApiIdInvalidError:
            self.logger.critical("API ID and API_HASH combination does not match!")

            sys.exit()
        except (AuthKeyDuplicatedError, EOFError) as er:
            if self._handle_error:
                self.logger.critical("String session expired. Create new!")
                return sys.exit()
            self.logger.critical("String session expired.")
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            # AccessTokenError can only occur for Bot account
            # And at Early Process, Its saved in DB.
            self.udB.del_key("BOT_TOKEN")
            self.logger.critical(
                "Bot token is expired or invalid. Create new from @Botfather and add in BOT_TOKEN env variable!"
            )
            sys.exit()
        # Save some stuff for later use...
        self.me = await self.get_me()
        if self.me.bot:
            me = f"@{self.me.username}"
        else:
            setattr(self.me, "phone", None)
            me = self.full_name
        if self._log_at:
            self.logger.info(f"Logged in as {me}")
        self._bot = await self.is_bot()

    async def fast_uploader(self, file, **kwargs):
        """Upload files in a faster way"""

        import os
        from pathlib import Path

        start_time = time.time()
        path = Path(file)
        filename = kwargs.get("filename", path.name)
        # Set to True and pass event to show progress bar.
        show_progress = kwargs.get("show_progress", False)
        if show_progress:
            event = kwargs["event"]
        # Whether to use cached file for uploading or not
        use_cache = kwargs.get("use_cache", True)
        # Delete original file after uploading
        to_delete = kwargs.get("to_delete", False)
        message = kwargs.get("message", f"Uploading {filename}...")
        by_bot = self._bot
        size = os.path.getsize(file)
        # Don't show progress bar when file size is less than 5MB.
        if size < 5 * 2**20:
            show_progress = False
        if use_cache and self._cache and self._cache.get("upload_cache"):
            for files in self._cache["upload_cache"]:
                if (
                    files["size"] == size
                    and files["path"] == path
                    and files["name"] == filename
                    and files["by_bot"] == by_bot
                ):
                    if to_delete:
                        with contextlib.suppress(FileNotFoundError):
                            os.remove(file)
                    return files["raw_file"], time.time() - start_time
        from xteam.fns.FastTelethon import upload_file
        from xteam.fns.helper import progress

        raw_file = None
        while not raw_file:
            with open(file, "rb") as f:
                raw_file = await upload_file(
                    client=self,
                    file=f,
                    filename=filename,
                    progress_callback=(
                        lambda completed, total: self.loop.create_task(
                            progress(completed, total, event, start_time, message)
                        )
                    )
                    if show_progress
                    else None,
                )
        cache = {
            "by_bot": by_bot,
            "size": size,
            "path": path,
            "name": filename,
            "raw_file": raw_file,
        }
        if self._cache.get("upload_cache"):
            self._cache["upload_cache"].append(cache)
        else:
            self._cache.update({"upload_cache": [cache]})
        if to_delete:
            with contextlib.suppress(FileNotFoundError):
                os.remove(file)
        return raw_file, time.time() - start_time

    async def fast_downloader(self, file, **kwargs):
        """Download files in a faster way"""
        # Set to True and pass event to show progress bar.
        show_progress = kwargs.get("show_progress", False)
        filename = kwargs.get("filename", "")
        if show_progress:
            event = kwargs["event"]
        # Don't show progress bar when file size is less than 10MB.
        if file.size < 10 * 2**20:
            show_progress = False
        import mimetypes

        from telethon.tl.types import DocumentAttributeFilename

        from xteam.fns.FastTelethon import download_file
        from xteam.fns.helper import progress

        start_time = time.time()
        # Auto-generate Filename
        if not filename:
            try:
                if isinstance(file.attributes[-1], DocumentAttributeFilename):
                    filename = file.attributes[-1].file_name
            except IndexError:
                mimetype = file.mime_type
                filename = (
                    mimetype.split("/")[0]
                    + "-"
                    + str(round(start_time))
                    + mimetypes.guess_extension(mimetype)
                )
        message = kwargs.get("message", f"Downloading {filename}...")

        raw_file = None
        while not raw_file:
            with open(filename, "wb") as f:
                raw_file = await download_file(
                    client=self,
                    location=file,
                    out=f,
                    progress_callback=(
                        lambda completed, total: self.loop.create_task(
                            progress(completed, total, event, start_time, message)
                        )
                    )
                    if show_progress
                    else None,
                )
        return raw_file, time.time() - start_time

    def run_in_loop(self, function):
        """run inside asyncio loop"""
        return self.loop.run_until_complete(function)

    def run(self):
        """run asyncio loop"""
        self.run_until_disconnected()

    def add_handler(self, func, *args, **kwargs):
        """Add new event handler, ignoring if exists"""
        if func in [_[0] for _ in self.list_event_handlers()]:
            return
        self.add_event_handler(func, *args, **kwargs)

    @property
    def utils(self):
        return telethon_utils

    @property
    def full_name(self):
        """full name of Client"""
        return self.utils.get_display_name(self.me)

    @property
    def uid(self):
        """Client's user id"""
        return self.me.id

    def to_dict(self):
        return dict(inspect.getmembers(self))

    async def parse_id(self, text):
        with contextlib.suppress(ValueError):
            text = int(text)
        return await self.get_peer_id(text)


---

## Pyrogram Client

"""Here's the class for a Pyrogram client, separate from the `UltroidClient` (which is based on Telethon). This class uses `pyrogram.Client` and includes the `PyTgCalls` integration.
"""

from pyrogram import Client
from pytgcalls import PyTgCalls
from logging import Logger

from ..configs import Var # Assuming Var contains API_ID, API_HASH, etc.
from . import LOGS # Assuming LOGS is your logger instance


class PyrogramClient(Client):
    def __init__(
        self,
        name: str,
        api_id: int = None,
        api_hash: str = None,
        bot_token: str = None,
        logger: Logger = LOGS,
        log_attempt: bool = True,
        exit_on_error: bool = True,
        **kwargs,
    ):
        self.logger = logger
        self._log_at = log_attempt
        self._handle_error = exit_on_error
        super().__init__(
            name=name,
            api_id=api_id or Var.API_ID,
            api_hash=api_hash or Var.API_HASH,
            bot_token=bot_token,
            **kwargs,
        )
        self.call_py = PyTgCalls(self) # PyTgCalls integrated with Pyrogram

    async def start_client(self):
        """Function to start the Pyrogram client."""
        if self._log_at:
            self.logger.info("Trying to login with Pyrogram.")
        try:
            await self.start()
            self.me = await self.get_me()
            if self.me.is_bot:
                me = f"@{self.me.username}"
            else:
                me = f"{self.me.first_name} {self.me.last_name or ''}".strip()
            if self._log_at:
                self.logger.info(f"Logged in with Pyrogram as {me}")
            
            # Start PyTgCalls client
            await self.call_py.start()
            if self._log_at:
                self.logger.info("PyTgCalls client started for Pyrogram.")

        except Exception as e:
            self.logger.critical(f"Error starting Pyrogram client: {e}")
            if self._handle_error:
                sys.exit()

    async def stop_client(self):
        """Function to stop the Pyrogram client."""
        if self._log_at:
            self.logger.info("Stopping Pyrogram client.")
        await self.stop()
        if self._log_at:
            self.logger.info("Pyrogram client stopped.")
        
        # Stop PyTgCalls client
        await self.call_py.stop()
        if self._log_at:
            self.logger.info("PyTgCalls client stopped for Pyrogram.")

    @property
    def full_name(self):
        """Full name of the Pyrogram client."""
        if self.me:
            return f"{self.me.first_name} {self.me.last_name or ''}".strip()
        return "Not logged in"

    @property
    def uid(self):
        """Client's user ID for Pyrogram."""
        return self.me.id if self.me else None

    def run(self):
        """Run the Pyrogram client until disconnected."""
        # Pyrogram's Client.run() handles event loop.
        # This method is primarily for consistency with Telethon's run().
        # For actual usage, you'd typically call app.run() or app.start() and app.stop().
        self.run_until_disconnected() # This is a conceptual placeholder.
                                     # Pyrogram's run() method is blocking.
                                     # For async, use start() and stop() within your own event loop.

#PyTgCalls (Standalone for Pyrogram)
#This shows how PyTgCalls is initialized with a Pyrogram Client instance.
from pyrogram import Client
from pytgcalls import PyTgCalls

def initialize_pytgcalls_pyrogram(app: Client):
    """
    Initializes PyTgCalls with a given Pyrogram Client instance.

    Args:
        app: An instance of pyrogram.Client.

    Returns:
        An instance of PyTgCalls linked to the provided Pyrogram Client.
    """
    call_py = PyTgCalls(app)
    return call_py

#PyTgCalls (Standalone for Telethon)
#This shows how PyTgCalls is initialized with a Telethon TelegramClient instance.
from telethon import TelegramClient
from pytgcalls import PyTgCalls

def initialize_pytgcalls_telethon(client: TelegramClient):
    """
    Initializes PyTgCalls with a given Telethon TelegramClient instance.

    Args:
        client: An instance of telethon.TelegramClient.

    Returns:
        An instance of PyTgCalls linked to the provided Telethon Client.
    """
    call_py = PyTgCalls(client)
    return call_py
