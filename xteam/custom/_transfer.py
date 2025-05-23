# PyroGram Download and Upload.
# Written by @moiusrname for fast upload and downloads.
#
# Edited on 21-07-2022:
#  - created class pyroUL
#  - changed lots of helper functions.
#  - added pyroDL on 23-07-22
#  - fixed for 0.7: 06-09-22
#  - overhaul 0.7.1: 06-10-22

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = ("pyroUL", "pyroDL")

import asyncio
from time import time
from io import BytesIO
from random import choice, choices
from pathlib import Path
from mimetypes import guess_extension
from shlex import quote
from string import ascii_lowercase
# from mimetypes import guess_all_extensions

from pyrogram.errors import ChannelInvalid
from telethon.utils import get_display_name
from telethon.errors import (
    ChatForwardsRestrictedError,
    MessageNotModifiedError,
    MessageIdInvalidError,
)

from pyrog import app
from xteam.startup import LOGS
from xteam import ULTConfig, asst, udB, ultroid_bot
from xteam.exceptions import DownloadError, UploadError
from xteam.fns.helper import inline_mention
from .mediainfo import gen_mediainfo
from .functions import cleargif, run_async_task
from .commons import (
    asyncwrite,
    bash,
    check_filename,
    get_tg_filename,
    humanbytes,
    osremove,
    progress,
    time_formatter,
)

try:
    from music_tag import load_file
except ImportError:
    load_file = None

try:
    from PIL import Image
except ImportError:
    Image = None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DUMP_CHANNEL = udB.get_key("TAG_LOG")
PROGRESS_LOG = {}
LOGGER_MSG = "Uploading {} | Path: {} | DC: {} | Size: {}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Progress Bar
async def pyro_progress(
    current,
    total,
    message,
    edit_text,
    started_at,
    client=None,
    edit_delay=8,
):
    unique_id = str(message.chat_id) + "_" + str(message.id)
    if getattr(message, "is_cancelled", False) and client:
        LOGS.debug(
            f"Cancelling Transfer: {unique_id} | Progress: {humanbytes(current)} out of {humanbytes(total)}"
        )
        await client.stop_transmission()

    last_update = PROGRESS_LOG.get(unique_id)
    now = time()
    if last_update and current != total:
        if (now - last_update) < edit_delay:
            return

    diff = now - started_at
    percentage = current * 100 / total
    speed = current / diff
    time_to_completion = round((total - current) / speed) * 1000
    progress_bar = min(int(percentage // 5), 20)
    progress_str = "`[{0}{1}] {2}%`\n\n".format(
        "●" * progress_bar,
        "" * (20 - progress_bar),
        round(percentage, 2),
    )
    to_edit = f"✦ {edit_text} \n\n{progress_str}"
    to_edit += "`{0} of {1}`\n\n`✦ Speed: {2}/s`\n\n`✦ ETA: {3}`\n\n".format(
        humanbytes(current),
        humanbytes(total),
        humanbytes(speed),
        time_formatter(time_to_completion),
    )

    try:
        PROGRESS_LOG[unique_id] = now
        await message.edit(to_edit)
    except MessageNotModifiedError:
        pass
    except MessageIdInvalidError:
        setattr(message, "is_cancelled", True)


# default thumbnail
def default_thumb():
    cnfg = getattr(ULTConfig, "thumb", None)
    if cnfg and Path(cnfg).is_file():
        return cnfg
    return str(Path.cwd().joinpath("resources/extras/ultroid.jpg"))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class pyroDL:
    def __init__(self, event, source, show_progress=True):
        self.event = event
        self.source = source
        self.show_progress = show_progress

    def updateAttrs(self, kwargs):
        if self.event and self.show_progress:
            setattr(self.event, "is_cancelled", False)
        self.auto_edit = True
        self.delay = 8
        self._log = True
        self.schd_delete = any(kwargs.pop(i, 0) for i in ("schd_delete", "df"))
        self.relative_path = check_filename(
            Path("resources/downloads") / get_tg_filename(self.source)
        )
        self.filename = str(Path(self.relative_path).absolute())
        if self.show_progress:
            self.progress_text = f"`Downloading {self.relative_path}...`"
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def copy_msg(self):
        try:
            dump = udB.get_key("DUMP_CHANNEL")
            destination = dump if self.schd_delete and dump else DUMP_CHANNEL
            return await self.source.copy(
                destination,
                caption=f"#pyroDL\n\n{self.source.text}",
            )
        except ChatForwardsRestrictedError:
            raise
        except Exception:
            er = f"pyroDL: error while copying message to {destination}"
            LOGS.error(er, exc_info=True)
            raise DownloadError(er)

    def get_file_dc(self, file):
        if doc := getattr(file, "document", None):
            return doc.dc_id
        return 1

    async def handle_error(self, error):
        if "MessageIdInvalidError" in str(error):
            LOGS.debug(f"Stopped Downloading - {self.filename}")
        elif self.event and self.show_progress:
            try:
                msg = f"__**Error While Downloading :**__ \n>  `{self.relative_path}` \n>  `{error}`"
                await self.event.edit(msg)
            except Exception as exc:
                LOGS.exception(exc)

    async def get_message(self):
        try:
            chat = self.source.chat.username or self.source.chat_id
            msg = await self.client.get_messages(chat, self.source.id)
            if msg and not msg.empty:
                self.msg = msg
                self.is_copy = False
            else:
                raise ChannelInvalid
        except (ChannelInvalid, Exception):
            dump_msg = await self.copy_msg()
            self.is_copy = True
            await asyncio.sleep(0.6)
            self.msg = await self.client.get_messages(dump_msg.chat_id, dump_msg.id)

    async def download(self, **kwargs):
        try:
            self.dc = kwargs.pop("dc", self.get_file_dc(self.source))
            self.client = app(self.dc)
            self.updateAttrs(kwargs)
            await self.get_message()
            await self.tg_downloader()
            if self.event and getattr(self.event, "is_cancelled", False):
                raise DownloadError(
                    "MessageIdInvalidError: Event Message was deleted.."
                )
        except ChatForwardsRestrictedError:
            return await self.telethon_fast_downloader()
        except (DownloadError, Exception) as exc:
            await self.handle_error(exc)
        else:
            if self.auto_edit and self.show_progress:
                return await self.event.edit(
                    f"Successfully Downloaded \n`{self.relative_path}` \nin {self.dl_time}",
                )
            return self.filename
        finally:
            if self.event and self.show_progress:
                ids = str(self.event.chat_id) + "_" + str(self.event.id)
                PROGRESS_LOG.pop(ids, None)

    # fallback to here if forward is locked!
    async def telethon_fast_downloader(self):
        if file := getattr(self.source.media, "document", None):
            args = {
                "file": file,
                "filename": self.filename,
                "show_progress": self.show_progress,
            }
            if self.event and self.show_progress:
                progress_text = self.progress_text.replace("`", "")
                args["event"] = self.event
                args["message"] = progress_text
            dlx, dl_time = await self.event.client.fast_downloader(**args)
            dlx, self.dl_time = dlx.name, time_formatter(dl_time * 1000)
        else:
            args, s_time = None, time()
            if self.event and self.show_progress:
                progress_text = self.progress_text.replace("`", "")
                args = lambda d, t: asyncio.create_task(
                    progress(d, t, self.event, s_time, progress_text)
                )
            dlx = await self.event.client.download_media(
                self.source,
                self.filename,
                progress_callback=args,
            )
            self.dl_time = time_formatter((time() - s_time) * 1000)

        if self.auto_edit and self.show_progress:
            return await self.event.edit(
                f"Successfully Downloaded \n`{self.relative_path}` \nin {self.dl_time}",
            )
        return self.filename

    async def tg_downloader(self):
        args = {"message": self.msg, "file_name": self.filename}
        if self._log:
            LOGS.debug(f"Downloading | [DC {self.dc}] | {self.filename}")
        if self.show_progress:
            progress_args = (
                self.event,
                self.progress_text,
                time(),
                self.client,
                self.delay,
            )
            args["progress"] = pyro_progress
            args["progress_args"] = progress_args
        if self.schd_delete and self.is_copy:
            run_async_task(self.delTask, self.msg)

        try:
            stime = time()
            dlx = await self.client.download_media(**args)
            self.dl_time = time_formatter((time() - stime) * 1000)
        except Exception as exc:
            LOGS.exception("PyroDL Error!")
            raise DownloadError(exc)

    @staticmethod
    async def delTask(task):
        await asyncio.sleep(6)
        await task.delete()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class pyroUL:
    def __init__(self, event, _path, show_progress=True):
        self.event = event
        self.show_progress = show_progress
        self.path = self.list_files(_path)
        self.set_default_attributes()

    def list_files(self, path):
        if type(path) in (list, tuple):
            files = (Path(i).absolute() for i in path if Path(i).is_file())
        else:
            _path = Path(path)
            if not _path.exists():
                return f"Path doesn't exists: `{path}`"
            elif _path.is_file():
                files = (i.absolute() for i in (_path,))
            elif _path.is_dir():
                files = (i.absolute() for i in _path.rglob("*") if i.is_file())
            else:
                return "Unrecognised Path"
        if not (files := tuple(files)):
            return f"Path doesn't exists: `{path}`"
        self.total_files = len(files)
        return (i for i in files)

    def set_default_attributes(self):
        self.delete_file = False
        self.delete_thumb = True
        self.schd_delete = False
        self.auto_edit = True
        self.return_obj = False
        self.dc = 1
        self._log = True
        self.success = 0
        self.failed = 0
        self.silent = True
        self.skip_finalize = False
        self.force_document = False
        self.delay = 8  # progress edit delay

    async def upload(self, **kwargs):
        if type(self.path) == str:
            if self.event:
                await self.event.edit(self.path)
            return
        self.perma_attributes(kwargs)
        for count, file in enumerate(self.path, start=1):
            self.update_attributes(kwargs, file, count)
            try:
                await self.pre_upload()
                ulfunc = self.uploader_func()
                out = await ulfunc()
                await asyncio.sleep(0.6)
                self.post_upload()
                if self.event and getattr(self.event, "is_cancelled", False):
                    # Process Cancelled // Event message Deleted..
                    return LOGS.debug(f"Stopped Uploading - {str(self.file)}")
                if self.return_obj:
                    return out
                elif self.skip_finalize:
                    await asyncio.sleep(self.sleeptime)
                    continue
                await self.finalize(out)
                await self.handle_edits()
                await asyncio.sleep(self.sleeptime)
            except (UploadError, Exception) as exc:
                await self.handle_error(exc)
                await asyncio.sleep(self.sleeptime)
                continue
        await self.do_final_edit()

    def perma_attributes(self, kwargs):
        e = self.event
        self.reply_to = getattr(e, "reply_to_msg_id", e.id) if e else None
        self.copy_to = e.chat_id if e else DUMP_CHANNEL
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.pre_time = time()
        self.client = app(self.dc)
        self.schd_delete = any(kwargs.pop(i, 0) for i in ("schd_delete", "df"))
        self.delete_file = any(kwargs.pop(i, 0) for i in ("delete_file", "del"))
        if not hasattr(self, "chat_id"):
            dump = udB.get_key("DUMP_CHANNEL")
            self.chat_id = dump if self.schd_delete and dump else DUMP_CHANNEL

    def update_attributes(self, kwargs, file, count):
        self.file = file
        self.count = count
        try:
            self.relative_path = str(self.file.relative_to(Path.cwd()))
        except ValueError:
            self.relative_path = str(self.file)
        for k, v in kwargs.items():
            setattr(self, k, v)
        if self.event and self.show_progress:
            setattr(self.event, "is_cancelled", False)
            self.progress_text = (
                f"`{self.count}/{self.total_files} | Uploading {self.relative_path}..`"
            )

    async def pre_upload(self):
        self.start_time = time()
        pyroUL.size_checks(self.file)
        await self.get_metadata()
        self.handle_webm()
        self.set_captions(pre=True)

    def uploader_func(self):
        type = self.metadata.get("type")
        if self.force_document:
            return self.document_uploader
        elif type == "video":
            return self.video_uploader
        elif type == "audio":
            return self.audio_uploader
        elif type == "image":
            return self.image_uploader
        elif type == "gif":
            return self.animation_uploader
        elif type == "sticker":
            return self.sticker_uploader
        else:
            return self.document_uploader

    def post_upload(self):
        self.ul_time = time_formatter((time() - self.start_time) * 1000)
        self.cleanups()
        self.set_captions()
        if self.event and self.show_progress:
            ids = str(self.event.chat_id) + "_" + str(self.event.id)
            PROGRESS_LOG.pop(ids, None)

    async def finalize(self, out):
        try:
            client = self.event.client if self.event else ultroid_bot
            file = await client.get_messages(out.chat.id, ids=out.id)
            if not (file and file.media):
                raise UploadError("Uploaded Media not found...")
            copy = await file.copy(
                self.copy_to,
                caption=self.caption,
                silent=self.silent,
                reply_to=self.reply_to,
            )
            delattr(self, "caption")
            run_async_task(self.dump_stuff, out, copy)
        except Exception:
            er = f"Error while copying file from DUMP: {self.relative_path}"
            LOGS.exception(er)
            raise UploadError(er)

    async def handle_edits(self):
        self.success += 1
        await asyncio.sleep(0.6)
        if self.auto_edit and self.event:
            await self.event.edit(
                f"__**Successfully Uploaded!  ({self.count}/{self.total_files})**__ \n**>**  `{self.relative_path}`",
            )

    async def handle_error(self, error):
        self.failed += 1
        if self.event and self.show_progress:
            try:
                msg = f"__**Error While Uploading :**__ \n>  `{self.relative_path}` \n>  `{error}`"
                await self.event.edit(msg)
            except Exception as exc:
                LOGS.exception(exc)

    async def do_final_edit(self):
        if self.total_files > 1 and self.auto_edit and self.event:
            msg = f"__**Uploaded {self.success} files in {time_formatter((time() - self.pre_time) * 1000)}**__"
            if self.failed > 0:
                msg += f"\n\n**Got Error in {self.failed} files.**"
            await self.event.edit(msg)

    # Helper methods

    @staticmethod
    def size_checks(path):
        size = path.stat().st_size
        if size == 0:
            raise UploadError("File Size = 0 B ...")
        elif size > 2097152000:
            raise UploadError("File Size is Greater than 2GB..")

    async def get_metadata(self):
        self.metadata = await gen_mediainfo(str(self.file))
        type = self.metadata.get("type").lower()
        if type == "image":
            if self.file.stat().st_size > 3 * 1024 * 1024:
                self.metadata["type"] = "document"
                type = "document"
            exts = ".jpg .jpeg .exif .gif .bmp .png .webp .jpe .tiff".split()
            if not (self.file.suffix and self.file.suffix.lower() in exts):
                self.file = self.file.rename(self.file.with_suffix(".jpg")).absolute()
        if not (self.force_document or hasattr(self, "thumb")):
            self.thumb = None
            if type == "video":
                self.thumb = await gen_video_thumb(
                    str(self.file), self.metadata["duration"]
                )
            elif type == "audio":
                self.thumb = await gen_audio_thumb(str(self.file))
            elif type == "gif":
                self.thumb = await gen_video_thumb(str(self.file), -1, first_frame=True)

    @property
    def sleeptime(self):
        _ = self.total_files
        return 2 if _ in range(5) else (4 if _ < 25 else 8)

    def handle_webm(self):
        type = self.metadata.get("type")
        if type != "sticker" and self.file.suffix.lower() == ".webm":
            ext = "" if self.file.suffix.lower().endswith((".mkv", ".mp4")) else ".mkv"
            new_pth = check_filename(self.file.with_suffix(ext))
            self.file = self.file.rename(new_pth).absolute()

    def set_captions(self, pre=False):
        if pre:
            caption = getattr(self, "caption", None)
            self.pre_caption = caption if self.return_obj else None
            return
        if hasattr(self, "caption"):
            if cap := getattr(self, "caption"):
                self.caption = cap.replace("$$path", str(self.file)).replace(
                    "$$base", self.file.name
                )
        else:
            self.caption = "__**Uploaded in {0}** • ({1})__ \n**>**  `{2}`".format(
                self.ul_time,
                self.metadata["size"],
                self.relative_path,
            )

    def cleanups(self):
        if self.delete_file:
            osremove(self.file)
        if x := getattr(self, "thumb", None):
            if self.delete_thumb and "ultroid.jpg" not in x and x != ULTConfig.thumb:
                osremove(x)
        if hasattr(self, "thumb"):
            delattr(self, "thumb")

    async def dump_stuff(self, upl, copy):
        await cleargif(copy)
        await asyncio.sleep(2)
        if self.schd_delete:
            await upl.delete()
        elif not copy.sticker:
            dumpCaption = "#PyroUL ~ {0} \n\n•  Chat:  [{1}]({2}) \n•  User:  {3} - {4} \n•  Path:  `{5}`"
            sndr = copy.sender or await copy.get_sender()
            text = dumpCaption.format(
                f"{self.count}/{self.total_files}",
                get_display_name(copy.chat),
                copy.message_link,
                get_display_name(sndr),
                inline_mention(sndr, custom=sndr.id),
                str(self.file),
            )
            try:
                await upl.edit_caption(text)
            except Exception:
                LOGS.warning("Editing Dump Media. <(ignore)>", exc_info=True)

    # Uploader methods

    async def video_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "video": self.file,
            "caption": self.pre_caption,
            "thumb": self.thumb,
            "duration": self.metadata["duration"],
            "height": self.metadata["height"],
            "width": self.metadata["width"],
            "disable_notification": self.silent,
        }
        type = "Video"
        self._log_info(type)
        args = self._progress_args(args)
        try:
            return await self.client.send_video(**args)
        except Exception as exc:
            self._handle_upload_error(type, exc)

    async def audio_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "audio": self.file,
            "caption": self.pre_caption,
            "thumb": self.thumb,
            "duration": self.metadata["duration"],
            "title": self.metadata["title"],
            "performer": self.metadata["artist"],
            "disable_notification": self.silent,
        }
        type = "Audio"
        self._log_info(type)
        args = self._progress_args(args)
        try:
            return await self.client.send_audio(**args)
        except Exception as exc:
            self._handle_upload_error(type, exc)

    async def animation_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "animation": self.file,
            "caption": self.pre_caption,
            "thumb": self.thumb,
            "height": self.metadata["height"],
            "width": self.metadata["width"],
            "disable_notification": self.silent,
        }
        type = "Animation"
        self._log_info(type)
        try:
            return await self.client.send_animation(**args)
        except Exception as exc:
            self._handle_upload_error(type, exc)

    async def document_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "document": self.file,
            "caption": self.pre_caption,
            "thumb": self.thumb,
            "disable_notification": self.silent,
        }
        type = "Document"
        self._log_info(type)
        args = self._progress_args(args)
        try:
            return await self.client.send_document(**args)
        except Exception as exc:
            self._handle_upload_error(type, exc)

    async def image_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "photo": self.file,
            "caption": self.pre_caption,
            "disable_notification": self.silent,
        }
        try:
            return await self.client.send_photo(**args)
        except Exception as exc:
            self._handle_upload_error("Image", exc)

    async def sticker_uploader(self):
        args = {
            "chat_id": self.chat_id,
            "sticker": self.file,
            "disable_notification": self.silent,
        }
        try:
            return await self.client.send_sticker(**args)
        except Exception as exc:
            self._handle_upload_error("Sticker", exc)

    # Uploader helper methods.

    def _log_info(self, format):
        if self._log:
            LOGS.debug(
                LOGGER_MSG.format(
                    format, str(self.file), self.dc, self.metadata["size"]
                )
            )

    def _progress_args(self, args):
        if self.show_progress and self.event:
            progress_args = (
                self.event,
                self.progress_text,
                time(),
                self.client,
                self.delay,
            )
            args["progress"] = pyro_progress
            args["progress_args"] = progress_args
        return args

    def _handle_upload_error(self, type, error):
        LOGS.exception(f"{type} Uploader: {self.relative_path}")
        err = ", ".join(error.args) if error.args else "NoneType"
        raise UploadError(
            f"{error.__class__.__name__} while uploading {type}: `{err}`",
        )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def size_checks(path):
    if path.is_file():
        size = path.stat().st_size
        return size > 0 and size < 10 * 1024 * 1024


async def gen_video_thumb(path, duration, first_frame=False):
    if first_frame or duration < 6:
        dur = 1
    else:
        rnd_dur = choice((0.25, 0.33, 0.4, 0.45, 0.5, 0.55, 0.6, 0.66, 0.75))
        dur = int(duration * rnd_dur)
    rnds = "".join(choices(ascii_lowercase, k=8))
    thumb_path = Path(check_filename(f"resources/temp/{rnds}-{dur}.jpg")).absolute()
    await bash(
        f"ffmpeg -ss {dur} -i {quote(path)} -vframes 1 {quote(str(thumb_path))} -y"
    )
    return str(thumb_path) if size_checks(thumb_path) else default_thumb()


async def gen_audio_thumb(path):
    if not load_file:
        return default_thumb()

    rnds = "".join(choices(ascii_lowercase, k=8))
    thumb = Path(check_filename(f"resources/temp/{rnds}.jpg"))
    try:
        load = load_file(path)
        if not (album_art := load.get("artwork")):
            return LOGS.warning(f"no artwork found for: {path}")

        byt = BytesIO(album_art.values[0].data)
        if Image:
            img = Image.open(byt)
            img.save(thumb)
        else:
            await asyncwrite(thumb, byt, mode="wb+")
        return str(thumb) if size_checks(thumb) else default_thumb()
    except BaseException as exc:
        LOGS.error(exc)
        return default_thumb()
