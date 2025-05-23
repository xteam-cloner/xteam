# better mediainfo! - by @moiusrname (dot arc)

__all__ = ("gen_mediainfo",)

import asyncio
from pathlib import Path, PurePath
from re import findall
from shlex import quote
from shutil import which

from xteam.fns.helper import humanbytes
from xteam.startup import HOSTED_ON, LOGS

try:
    from pymediainfo import MediaInfo
except ImportError:
    LOGS.warning("'pymediainfo' not Installed. Some Plugins might NOT work.")
    MediaInfo = None


class TGMediaInfo:
    __slots__ = ("path", "obj", "general_track", "track")

    def __init__(self, path):
        self.path = path
        self.obj = MediaInfo.parse(
            self.path,
            library_file="/data/data/com.termux/files/usr/bin/mediainfo"
            if HOSTED_ON == "termux"
            else None,
        )
        self.general_track = self.obj.general_tracks[0]

    async def run(self):
        out = {}
        out["size"] = humanbytes(Path(self.path).stat().st_size)
        _ext = self._getter(self.general_track, "file_extension", False)
        if _ext and _ext.lower() in ("tgs", "webp"):
            out["type"] = "sticker"
            return out

        minfo = {}
        if data := self.obj.video_tracks:
            self.track = data[0]
            minfo = await self.video_info()
        elif data := self.obj.audio_tracks:
            self.track = data[0]
            minfo = await self.audio_info()
        elif data := self.obj.image_tracks:
            self.track = data[0]
            minfo = await self.image_info()
        else:
            out["type"] = "document"
        return out | minfo

    @staticmethod
    async def execute(cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            executable=which("bash"),
        )
        stdout, stderr = await process.communicate()
        stderr = stderr.decode(errors="replace").strip()
        stdout = stdout.decode(errors="replace").strip()
        return process, stdout, stderr

    @staticmethod
    def check_output(data):
        try:
            chk = findall(r"[\d\.]+", data)
            return next(filter(bool, chk))
        except StopIteration:
            return

    # audio stream helper
    @staticmethod
    def _get_audio_metadata(data):
        result = {"title": "Unknown Track", "artist": "Unknown Artist"}
        _items = {
            "title": ("title", "track_name", "file_name_extension"),
            "artist": ("performer", "album"),
        }
        for key, vars in _items.items():
            for attr in vars:
                if value := TGMediaInfo._getter(data, attr, False):
                    result.update({key: value})
                    break
        return tuple(result.values())

    # alternate method for getting frame count from video stream
    @staticmethod
    async def _get_frame_count(file):
        cmd = f"ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=nb_read_packets -of default=noprint_wrappers=1 {quote(file)}"
        # -count_frames ~ slow
        try:
            res, output, err = await TGMediaInfo.execute(cmd)
            if res.returncode == 0 and (frames := TGMediaInfo.check_output(output)):
                return int(frames)
        except Exception as err:
            LOGS.exception(f"Error in getting frame count via ffprobe: {file} | {err}")

    # alternate method for getting bitrate from video stream
    @staticmethod
    async def _get_bitrate(file):
        cmd = f"ffprobe -hide_banner -v error -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1 {quote(file)}"
        try:
            res, output, err = await TGMediaInfo.execute(cmd)
            if res.returncode == 0 and (bit_rate := TGMediaInfo.check_output(output)):
                return int(bit_rate)
        except Exception as err:
            LOGS.exception(f"Error in getting bitrate via ffprobe: {file} | {err}")

    # alternate method for getting duration from video or audio stream
    @staticmethod
    async def _get_duration(file):
        cmd = f"ffprobe -hide_banner -v error -show_entries format=duration -of default=noprint_wrappers=1 {quote(file)}"
        try:
            res, output, err = await TGMediaInfo.execute(cmd)
            if res.returncode == 0 and (duration := TGMediaInfo.check_output(output)):
                return round(float(duration))
        except Exception as err:
            LOGS.exception(f"Error in getting duration via ffprobe: {file} | {err}")
            return 0

    @staticmethod
    def _getter(data, attr, to_int=True):
        def _conv_to_int(n):
            try:
                return round(float(n)) if n else 0
            except ValueError:
                return 0

        out = getattr(data, attr, 0)
        if to_int and type(out) != int:
            out = _conv_to_int(out)
        return out

    # video stream helper.
    async def _video_stream_helper(self, data):
        # webm sticker
        if (
            self.general_track.format.lower() == "webm"
            and data.get("duration") <= 3
            and data.get("width") == 512
        ):
            data["type"] = "sticker"

        # recheck frame count
        if not data.get("frames"):
            if frames := await self._get_frame_count(self.path):
                data["frames"] = frames

        # recheck bitrate
        if not data.get("bitrate"):
            if b_rate := await self._get_bitrate(self.path):
                data["bitrate"] = b_rate

        # gif check
        format = self._getter(self.track, "format", False)
        if format and format.lower() == "gif":
            data["type"] = "gif"
        return data

    # video stream
    async def video_info(self):
        _dur = round(self._getter(self.track, "duration") / 1000)
        duration = _dur or await self._get_duration(self.path)
        out = {
            "type": "video",
            "duration": duration,
            "has_audio": bool(self.obj.audio_tracks),
            "width": self._getter(self.track, "width"),
            "height": self._getter(self.track, "height"),
            "bitrate": self._getter(self.track, "bit_rate"),
            "frames": self._getter(self.track, "frame_count"),
        }
        return await self._video_stream_helper(out)

    # image stream
    async def image_info(self):
        out = {
            "type": "image",
            "width": self._getter(self.track, "width"),
            "height": self._getter(self.track, "height"),
        }
        format = self._getter(self.track, "format", False)
        if format and format.lower() == "gif":
            return await self.video_info()
        return out

    # audio stream
    async def audio_info(self):
        _dur = round(self._getter(self.general_track, "duration") / 1000)
        duration = _dur or await self._get_duration(self.path)
        title, artist = self._get_audio_metadata(self.general_track)
        return {
            "type": "audio",
            "duration": duration,
            "title": title,
            "artist": artist,
            "performer": artist,
        }


async def gen_mediainfo(path):
    if not MediaInfo:
        return {}
    _mediainfo = TGMediaInfo(path=str(path) if isinstance(path, PurePath) else path)
    return await _mediainfo.run()
