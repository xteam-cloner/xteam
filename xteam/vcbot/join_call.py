# File: xteam/vcbot.py (atau file core VC Anda)

from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputStream, InputAudioStream, InputVideoStream
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError 
# ... import lainnya

# ASUMSI: 'call_py' adalah instance dari PyTgCalls Anda.
# call_py = PyTgCalls(client_instance) 

async def join_call(chat_id: int, link: str, video: bool):
    """
    Menggabungkan panggilan suara/video grup.
    
    Args:
        chat_id: ID grup target.
        link: URL atau path file untuk streaming.
        video: True jika ini adalah streaming video, False untuk audio.
    """
    
    stream_type = StreamType.video if video else StreamType.audio
    
    # Menentukan jenis stream
    if video:
        stream = InputVideoStream(
            link,
            resolution=InputVideoStream.Resolution.HD_720, # Dapat disesuaikan
        )
    else:
        stream = InputAudioStream(link)

    # Menggunakan try-except untuk penanganan error join
    try:
        await call_py.join_group_call(
            chat_id,
            InputStream(
                stream,
                # Jika Anda ingin volume default 100
                audio_parameters=InputAudioStream.Config(volume=1.0) 
            ),
            stream_type=stream_type,
        )
    except NoActiveGroupCall:
        raise Exception("Tidak ada obrolan suara aktif di grup ini.")
    except AlreadyJoinedError:
        # Jika sudah bergabung, ganti saja streaming-nya (replace_stream)
        await call_py.change_stream(
            chat_id,
            InputStream(stream),
        )
    except Exception as e:
        # Menangani error umum lainnya
        raise Exception(f"Gagal bergabung: {e}")

# ... (fungsi helper lain seperti clear_queue, add_to_queue, dll.)
