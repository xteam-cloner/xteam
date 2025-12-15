from typing import Union
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import VideoQuality, AudioQuality
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NoAudioSourceFound,
    NoVideoSourceFound,
)
# Exceptions yang tidak ada (ChatAdminRequired, ConnectionNotFound, TelegramServerError) telah dihapus dari import

from xteam import call_py as assistant_call


class XteamMusicBot:
    def __init__(self):
        self.active_calls = set()

    def create_media_stream(self, link: str, video: bool = False) -> MediaStream:
        if video:
            return MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
            )
        else:
            return MediaStream(
                media_path=link,
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
            )


    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ) -> None:

        stream = self.create_media_stream(link=link, video=bool(video))
        
        vc_client = assistant_call 

        try:
            await vc_client.play(chat_id, stream)

        except NoActiveGroupCall:
            # Menangkap NoActiveGroupCall (VC tidak aktif)
            raise Exception("Gagal bergabung. Obrolan Suara tidak aktif atau Asisten bukan admin.")

        except NoAudioSourceFound:
            raise Exception("Sumber audio tidak ditemukan.")

        except NoVideoSourceFound:
            raise Exception("Sumber video tidak ditemukan.")

        except Exception as e:
            # Blok ini menangkap semua error lainnya, termasuk:
            # - Error koneksi/server Telegram (ConnectionNotFound/TelegramServerError)
            # - Error izin admin (ChatAdminRequired dari klien dasar)
            # - Error lainnya dari PyTgCalls yang tidak didefinisikan di list exceptions.py Anda.
            raise Exception(
                f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄᴀʟʟ. Rᴇᴀsᴏɴ: {e}"
            )

        self.active_calls.add(chat_id)
        
