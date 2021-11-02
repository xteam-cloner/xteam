# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import inspect
import re
import sys
from io import BytesIO
from pathlib import Path
from time import gmtime, strftime
from traceback import format_exc

from telethon import Button
from telethon import __version__ as telever
from telethon import events
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserIsBotError,
)
from telethon.utils import get_display_name

from .. import DUAL_HNDLR, DUAL_MODE, HNDLR, LOGS, SUDO_HNDLR, asst, udB, ultroid_bot
from ..dB import DEVLIST
from ..dB._core import LIST, LOADED
from ..dB.sudos import is_fullsudo
from ..functions.admins import admin_check
from ..functions.helper import bash
from ..functions.helper import time_formatter as tf
from ..version import __version__ as pyver
from ..version import ultroid_version as ult_ver
from . import owner_and_sudos, should_allow_sudo, sudoers
from ._wrappers import eod

hndlr = "\\" + HNDLR
MANAGER = udB.get("MANAGER")
TAKE_EDITS = udB.get("TAKE_EDITS")
black_list_chats = eval(udB.get("BLACKLIST_CHATS"))
allow_sudo = should_allow_sudo()


def compile_pattern(data, hndlr):
    if hndlr == " ":  # No handler feature
        return re.compile("^" + data.replace("^", "").replace(".", ""))
    return (
        re.compile(hndlr + data.replace("^", "").replace(".", ""))
        if data.startswith("^")
        else re.compile(hndlr + data)
    )


# decorator

# Inspiration of ultroid_cmd decor is from RaphielGang/Telegram-Paperlane
# https://github.com/RaphielGang/Telegram-Paperplane/blob/625875a9ecdfd267a53067b3c1580000f5006973/userbot/events.py#L22


def ultroid_cmd(allow_sudo=allow_sudo, **args):
    # With time and addition of Stuff
    # Decorator has turned lengthy and non attractive.
    # Todo : Make it better..
    args["func"] = lambda e: not e.via_bot_id
    file_test = Path(inspect.stack()[1].filename)
    pattern = args.get("pattern", None)
    black_chats = args.get("chats", None)
    groups_only = args.get("groups_only", False)
    admins_only = args.get("admins_only", False)
    fullsudo = args.get("fullsudo", False)
    type_ = args.get("type", ["official"])
    only_devs = args.get("only_devs", False)
    allow_pm = args.get("allow_pm", False)
    args.get("allow_all", False)
    if isinstance(type_, str):
        type_ = [type_]
    if "official" in type_ and DUAL_MODE:
        type_.append("dualmode")

    args["forwards"] = False
    if pattern:
        args["pattern"] = compile_pattern(pattern, hndlr)
        reg = re.compile("(.*)")
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = (
                    cmd.group(1)
                    .replace("$", "")
                    .replace("?(.*)", "")
                    .replace("(.*)", "")
                    .replace("(?: |)", "")
                    .replace("| ", "")
                    .replace("( |)", "")
                    .replace("?((.|//)*)", "")
                    .replace("?P<shortname>\\w+", "")
                )
            except BaseException:
                pass
            try:
                LIST[file_test].append(cmd)
            except BaseException:
                LIST.update({file_test: [cmd]})
        except BaseException:
            pass

    args["blacklist_chats"] = True
    if len(black_list_chats) > 0:
        args["chats"] = black_list_chats
    if black_chats is not None:
        if len(black_chats) == 0:
            args["chats"] = []
        else:
            args["chats"] = black_chats

    for i in [
        "admins_only",
        "groups_only",
        "type",
        "fullsudo",
        "only_devs",
        "allow_pm",
        "allow_all",
    ]:
        if i in args:
            del args[i]

    def decorator(func):
        def doit(mode):
            async def wrapper(ult):
                chat = ult.chat
                if mode in ["dualmode", "official", "sudo"]:
                    if not ult.out and fullsudo and not is_fullsudo(ult.sender_id):
                        return await eod(ult, "`Full Sudo User Required...`", time=15)
                    if hasattr(chat, "title"):
                        if (
                            "#noub" in chat.title.lower()
                            and not (chat.admin_rights or chat.creator)
                            and not (ult.sender_id in DEVLIST)
                        ):
                            return
                    if admins_only:
                        if ult.is_private:
                            return await eod(ult, "`Use this in group/channel.`")
                        if not (chat.admin_rights or chat.creator):
                            return await eod(ult, "`I am not an admin.`")
                elif mode == "manager":
                    if not allow_pm and ult.is_private:
                        return
                    elif not (await admin_check(ult)):
                        return
                if only_devs and not udB.get("I_DEV"):
                    return await eod(
                        ult,
                        f"**⚠️ Developer Restricted!**\nIf you know what this does, and want to proceed, use\n`{HNDLR}setdb I_DEV True`.\n\nThis Might Be Dangerous.",
                        time=10,
                    )
                if groups_only and ult.is_private:
                    return await eod(ult, "`Use this in Group/Channel.`")
                try:
                    await func(ult)
                except FloodWaitError as fwerr:
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        f"`FloodWaitError:\n{str(fwerr)}\n\nSleeping for {tf((fwerr.seconds + 10)*1000)}`",
                    )
                    await ultroid_bot.disconnect()
                    await asyncio.sleep(fwerr.seconds + 10)
                    await ultroid_bot.connect()
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        "`Bot is working again`",
                    )
                    return
                except ChatSendInlineForbiddenError:
                    return await eod(ult, "`Inline Locked In This Chat.`")
                except (ChatSendMediaForbiddenError, ChatSendStickersForbiddenError):
                    return await eod(
                        ult, "`Sending media or sticker is not allowed in this chat.`"
                    )
                except (BotMethodInvalidError, UserIsBotError) as boterror:
                    return await eod(ult, str(boterror))
                except (
                    MessageIdInvalidError,
                    MessageNotModifiedError,
                    MessageDeleteForbiddenError,
                ):
                    pass
                except AuthKeyDuplicatedError as er:
                    LOGS.exception(er)
                    await asst.send_message(
                        int(udB.get("LOG_CHANNEL")),
                        "Session String expired, create new session from 👇",
                        buttons=[
                            Button.url("Bot", "t.me/SessionGeneratorBot?start="),
                            Button.url(
                                "Repl",
                                "https://replit.com/@TeamUltroid/UltroidStringSession",
                            ),
                        ],
                    )
                    exit()
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    LOGS.exception(e)
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    naam = get_display_name(chat)
                    ftext = "**Ultroid Client Error:** `Forward this to` @UltroidSupport\n\n"
                    ftext += "**Py-Ultroid Version:** `" + str(pyver)
                    ftext += "`\n**Ultroid Version:** `" + str(ult_ver)
                    ftext += "`\n**Telethon Version:** `" + str(telever) + "`\n\n"
                    ftext += "--------START ULTROID CRASH LOG--------"
                    ftext += "\n**Date:** `" + date
                    ftext += "`\n**Group:** `" + str(ult.chat_id) + "` " + str(naam)
                    ftext += "\n**Sender ID:** `" + str(ult.sender_id)
                    ftext += "`\n**Replied:** `" + str(ult.is_reply)
                    ftext += "`\n\n**Event Trigger:**`\n"
                    ftext += str(ult.text)
                    ftext += "`\n\n**Traceback info:**`\n"
                    ftext += str(format_exc())
                    ftext += "`\n\n**Error text:**`\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "`\n\n--------END ULTROID CRASH LOG--------"
                    ftext += "\n\n\n**Last 5 commits:**`\n"

                    stdout, stderr = await bash('git log --pretty=format:"%an: %s" -5')
                    result = str(stdout.strip()) + str(stderr.strip())

                    ftext += result + "`"

                    if len(ftext) > 4096:
                        with BytesIO(ftext.encode()) as file:
                            file.name = "logs.txt"
                            await asst.send_file(
                                int(udB["LOG_CHANNEL"]),
                                file,
                                caption="**Ultroid Client Error:** `Forward this to` @UltroidSupport\n\n",
                            )
                    else:
                        await asst.send_message(
                            int(udB["LOG_CHANNEL"]),
                            ftext,
                        )

            return wrapper

        if "official" in type_:
            args["outgoing"] = True
            cm = doit("official")
            ultroid_bot.add_event_handler(cm, events.NewMessage(**args))
            if "addons/" in str(file_test):
                if LOADED.get(file_test.stem):
                    LOADED[file_test.stem].append(cm)
                else:
                    LOADED.update({file_test.stem: [cm]})

            if TAKE_EDITS:
                args["func"] = (
                    lambda x: not (x.is_channel and x.chat.broadcast)
                    and not x.via_bot_id
                )
                ultroid_bot.add_event_handler(
                    doit("official"),
                    events.MessageEdited(**args),
                )
                args["func"] = lambda e: not e.fwd_from and not e.via_bot_id

            if allow_sudo and sudoers():
                args["outgoing"] = False
                args["from_users"] = sudoers
                args["pattern"] = compile_pattern(pattern, "\\" + SUDO_HNDLR)
                cm = doit("sudo")
                ultroid_bot.add_event_handler(cm, events.NewMessage(**args))
                if "addons/" in str(file_test):
                    if LOADED.get(file_test.stem):
                        LOADED[file_test.stem].append(cm)
                    else:
                        LOADED.update({file_test.stem: [cm]})
                del args["from_users"]
            del args["outgoing"]
        if "assistant" in type_:
            args["pattern"] = compile_pattern(pattern, "/")
            cm = doit("assistant")
            asst.add_event_handler(cm, events.NewMessage(**args))
            if "addons/" in str(file_test):
                if LOADED.get(file_test.stem):
                    LOADED[file_test.stem].append(cm)
                else:
                    LOADED.update({file_test.stem: [cm]})
        if MANAGER and "manager" in type_:
            args["pattern"] = compile_pattern(pattern, "/")
            asst.add_event_handler(doit("manager"), events.NewMessage(**args))

        if "dualmode" in type_:
            if not (("manager" in type_) and (DUAL_HNDLR == "/")) and not (
                ("assistant" in type_) and (DUAL_HNDLR == "/")
            ):
                args["from_users"] = owner_and_sudos
                args["pattern"] = compile_pattern(pattern, "\\" + DUAL_HNDLR)
                asst.add_event_handler(doit("dualmode"), events.NewMessage(**args))

    return decorator
