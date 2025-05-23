# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import contextlib
import inspect
import sys
import time
from logging import Logger
from pytgcalls import PyTgCalls
from telethonpatch import TelegramClient
from telethon import utils as telethon_utils
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from telethon.sessions import StringSession
from xteam.configs import Var
from . import *

# Import Pyrogram
from pyrogram import Client as PyrogramClient
from pyrogram.errors import (
    AccessTokenExpired as PyrogramAccessTokenExpiredError,
    AuthKeyUnregistered as PyrogramAuthKeyUnregisteredError,
    ApiIdInvalid as PyrogramApiIdInvalidError,
)
from pyrogram.raw.all import layer

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

        # Initialize Pyrogram and PyTgCalls clients
        self.pyrogram_client = UltroidPyrogramClient(
            session=session,
            api_id=api_id or Var.API_ID,
            api_hash=api_hash or Var.API_HASH,
            bot_token=bot_token,
            logger=logger,
            exit_on_error=exit_on_error,
        )
        self.pytgcalls_client = UltroidPyTgCallsClient(
            app=self.pyrogram_client,
            logger=logger,
        )
    
    def __repr__(self):
        return f"<Ultroid.Client :\n self: {self.full_name}\n bot: {self._bot}\n>"

    @property
    def __dict__(self):
        if self.me:
            return self.me.to_dict()

    async def start_client(self, **kwargs):
        """function to start client"""
        if self._log_at:
            self.logger.info("Trying to login (Telethon).")
        try:
            await self.start(**kwargs)
        except ApiIdInvalidError:
            self.logger.critical("Telethon: API ID and API_HASH combination does not match!")
            sys.exit()
        except (AuthKeyDuplicatedError, EOFError) as er:
            if self._handle_error:
                self.logger.critical("Telethon: String session expired. Create new!")
                return sys.exit()
            self.logger.critical("Telethon: String session expired.")
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            # AccessTokenError can only occur for Bot account
            # And at Early Process, Its saved in DB.
            self.udB.del_key("BOT_TOKEN")
            self.logger.critical(
                "Telethon: Bot token is expired or invalid. Create new from @Botfather and add in BOT_TOKEN env variable!"
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
            self.logger.info(f"Telethon: Logged in as {me}")
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
        if size < 5 * 2 ** 20:
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
        if file.size < 10 * 2 ** 20:
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
        # Start Pyrogram client before running Telethon's disconnected loop
        self.run_in_loop(self.pyrogram_client.start_client())
        self.run_until_disconnected()
        # Disconnect Pyrogram client when Telethon client disconnects
        self.run_in_loop(self.pyrogram_client.stop())


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

## UltroidPyrogramClient Class

#This class will handle your Pyrogram client's initialization and basic lifecycle.

#python
class UltroidPyrogramClient(PyrogramClient):
    def __init__(
        self,
        session: str,
        api_id: int,
        api_hash: str,
        bot_token: str = None,
        logger: Logger = LOGS,
        exit_on_error: bool = True,
        *args,
        **kwargs,
    ):
        name = "UltroidPyrogram"
        if bot_token:
            name = f"UltroidPyrogramBot:{bot_token.split(':')[0]}"

        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            session_string=session if not bot_token else None,
            bot_token=bot_token,
            in_memory=True,  # Use in-memory session for easier management
            *args,
            **kwargs,
        )
        self.logger = logger
        self._handle_error = exit_on_error
        self._bot = bool(bot_token)
        self.me = None # Will be set after successful login

    async def start_client(self):
        """Starts the Pyrogram client."""
        self.logger.info("Trying to login (Pyrogram).")
        try:
            await self.start()
            self.me = await self.get_me()
            if self.me.is_bot:
                self.logger.info(f"Pyrogram: Logged in as @{self.me.username}")
            else:
                self.logger.info(f"Pyrogram: Logged in as {self.me.first_name}")
        except PyrogramApiIdInvalidError:
            self.logger.critical("Pyrogram: API ID and API_HASH combination does not match!")
            sys.exit()
        except (PyrogramAccessTokenExpiredError, PyrogramAuthKeyUnregisteredError) as er:
            if self._handle_error:
                self.logger.critical("Pyrogram: Session expired. Create new!")
                sys.exit()
            self.logger.critical(f"Pyrogram: Session expired. Error: {er}")
        except Exception as e:
            self.logger.critical(f"Pyrogram: An unexpected error occurred during login: {e}")
            sys.exit()

    async def stop(self, *args, **kwargs):
        """Stops the Pyrogram client."""
        await super().stop(*args, **kwargs)
        self.logger.info("Pyrogram client stopped.")


class UltroidPyTgCallsClient(PyTgCalls):
    def __init__(
        self,
        app: UltroidPyrogramClient, # Pass the UltroidPyrogramClient instance
        logger: Logger = LOGS,
        *args,
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.logger = logger

    async def start_client(self):
        """Starts the PyTgCalls client."""
        self.logger.info("Trying to start PyTgCalls.")
        try:
            await self.start()
            self.logger.info("PyTgCalls started successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to start PyTgCalls: {e}")
            sys.exit()

    async def stop(self, *args, **kwargs):
        """Stops the PyTgCalls client."""
        await super().stop(*args, **kwargs)
        self.logger.info("PyTgCalls client stopped.")
