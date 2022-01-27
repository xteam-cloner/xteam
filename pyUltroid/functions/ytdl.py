# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
import re
import time

from telethon import Button
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

from .. import LOGS, udB
from .helper import download_file, humanbytes, run_async, time_formatter
from .tools import async_searcher, set_attributes


async def ytdl_progress(k, start_time, event):
    if k["status"] == "error":
        return await event.edit("error")
    while k["status"] == "downloading":
        text = (
            f"`Downloading: {k['filename']}\n"
            + f"Total Size: {humanbytes(k['total_bytes'])}\n"
            + f"Downloaded: {humanbytes(k['downloaded_bytes'])}\n"
            + f"Speed: {humanbytes(k['speed'])}/s\n"
            + f"ETA: {time_formatter(k['eta']*1000)}`"
        )
        if round((time.time() - start_time) % 10.0) == 0:
            try:
                await event.edit(text)
            except Exception as ex:
                LOGS.error(f"ytdl_progress: {ex}")


def get_yt_link(query):
    search = VideosSearch(query, limit=1).result()
    return search["result"][0]["link"]


async def download_yt(event, link, ytd):
    reply_to = event.reply_to_msg_id or event
    info = await dler(event, link, ytd, download=True)
    if not info:
        return
    title = info["title"]
    id_ = info["id"]
    thumb = id_ + ".jpg"
    await download_file(f"https://i.ytimg.com/vi/{id_}/hqdefault.jpg", thumb)
    ext = "." + ytd["outtmpl"].split(".")[-1]
    if ext == ".m4a":
        ext = ".mp3"
    file = title + ext
    try:
        os.rename(id_ + ext, file)
    except FileNotFoundError:
        os.rename(id_ + ext * 2, file)
    attributes = await set_attributes(file)
    res, _ = await event.client.fast_uploader(
        file, show_progress=True, event=event, to_delete=True
    )
    caption = f"`{title}`\n\n`From YouTube`"
    await event.client.send_file(
        event.chat_id,
        file=res,
        caption=caption,
        attributes=attributes,
        supports_streaming=True,
        thumb=thumb,
        reply_to=reply_to,
    )
    os.remove(thumb)
    try:
        await event.delete()
    except BaseException:
        pass


# ---------------YouTube Downloader Inline---------------
# @New-Dev0 @buddhhu @1danish-00


def get_formats(type, id, data):
    if type == "audio":
        audio = []
        for _quality in ["64", "128", "256", "320"]:
            _audio = {}
            _audio.update(
                {
                    "ytid": id,
                    "type": "audio",
                    "id": _quality,
                    "quality": _quality + "KBPS",
                }
            )
            audio.append(_audio)
        return audio
    elif type == "video":
        video = []
        size = 0
        for vid in data["formats"]:
            if vid["format_id"] == "251":
                size += vid["filesize"] if vid.get("filesize") else 0
            if vid["vcodec"] is not "none":
                _id = int(vid["format_id"])
                _quality = str(vid["width"]) + "×" + str(vid["height"])
                _size = size + (vid["filesize"] if vid.get("filesize") else 0)
                _ext = "mkv" if vid["ext"] == "webm" else "mp4"
                if _size < 2147483648:  # Telegram's Limit of 2GB
                    _video = {}
                    _video.update(
                        {
                            "ytid": id,
                            "type": "video",
                            "id": str(_id) + "+251",
                            "quality": _quality,
                            "size": _size,
                            "ext": _ext,
                        }
                    )
                    video.append(_video)
        return video
    return []


def get_buttons(listt):
    id = listt[0]["ytid"]
    butts = [
        Button.inline(
            text=f"[{x['quality']}"
            + (f" {humanbytes(x['size'])}]" if x.get("size") else "]"),
            data=f"ytdownload:{x['type']}:{x['id']}:{x['ytid']}"
            + (f":{x['ext']}" if x.get("ext") else ""),
        )
        for x in listt
    ]
    buttons = list(zip(butts[::2], butts[1::2]))
    if len(butts) % 2 == 1:
        buttons.append((butts[-1],))
    buttons.append([Button.inline("« Back", f"ytdl_back:{id}")])
    return buttons


async def dler(event, url, opts: dict = {}, download=False):
    time.time()
    await event.edit("`Getting Data from YouTube..`")
    if "quiet" not in opts:
        opts["quiet"] = True
    opts["username"] = udB.get_key("YT_USERNAME")
    opts["password"] = udB.get_key("YT_PASSWORD")
    """
    if "progress_hooks" not in opts:
        opts["progress_hooks"] = [
            lambda k: asyncio.get_event_loop().create_task(
                ytdl_progress(k, start_time, event)
            )
        ]
    """
    if download:
        await ytdownload(url, opts)
    try:
        return YoutubeDL({}).extract_info(url=url, download=False)
    except Exception as e:
        await event.edit(f"{type(e)}: {e}")
        return


@run_async
def ytdownload(url, opts):
    try:
        YoutubeDL(opts).download([url])
    except Exception as ex:
        LOGS.error(ex)


async def get_videos_link(url):
    id_ = url[url.index("=") + 1 :]
    try:
        html = await async_searcher(url)
    except BaseException:
        return []
    pattern = re.compile(r"watch\?v=\S+?list=" + id_)
    v_ids = re.findall(pattern, html)
    links = []
    if v_ids:
        for z in v_ids:
            idd = re.search(r"=(.*)\\", str(z)).group(1)
            links.append(f"https://www.youtube.com/watch?v={idd}")
    return links
