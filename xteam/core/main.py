import asyncio
import os
from telethon import TelegramClient, events # Import Telethon Client dan events
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from yt_dlp import YoutubeDL # Impor YoutubeDL

# Asumsi Var sudah diatur dan berisi API_ID, API_HASH, BOT_TOKEN
from xteam.configs import Var

# Ganti dengan ID chat Voice Call Anda (-100xxxxxxxxx)
# Untuk Telethon, ID channel/grup perlu diubah ke integer atau string yang dikenali Telethon
# Jika Anda mendapatkan ID dari bot seperti GetMyID_bot, pastikan itu numerik.
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -100123456789)) # Contoh, Ganti dengan ID channel/grup Anda!
# Anda bisa memindahkan ini ke Var.VC_CHAT_ID jika diinginkan

# --- Inisialisasi Client Telethon ---
# Bot token akan digunakan untuk login bot.
app = TelegramClient(
    "my_bot_session", # Nama sesi
    Var.API_ID,       # API ID dari xteam.configs.Var
    Var.API_HASH      # API Hash dari xteam.configs.Var
).start(bot_token=Var.BOT_TOKEN) # Mulai client sebagai bot dengan token

# --- Inisialisasi Client PyTgCalls ---
# PyTgCalls tetap menggunakan client Telegram (Telethon atau Pyrofork)
calls = PyTgCalls(app)

# --- Konfigurasi yt-dlp ---
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'quiet': True,
    'extract_flat': True,
    'skip_download': True,
    'force_generic_extractor': True,
    'geo_bypass': True,
}

# --- Fungsi untuk Mencari dan Mendapatkan URL Streaming ---
async def get_audio_stream_url(query: str):
    """
    Mencari video di YouTube dan mengembalikan URL streaming audio langsung.
    Menggunakan yt-dlp untuk mencari dan mengekstrak info.
    """
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info

            for format_entry in video_info['formats']: # Ubah 'format' menjadi 'format_entry' untuk menghindari konflik nama
                if format_entry.get('ext') in ['mp3', 'm4a', 'webm', 'ogg', 'aac'] and format_entry.get('acodec') != 'none':
                    return format_entry['url'], video_info.get('title', 'Unknown Title')

            return video_info['url'], video_info.get('title', 'Unknown Title')
        except Exception as e:
            print(f"Error saat mencari atau mendapatkan URL streaming: {e}")
            return None, None

# --- Handler Perintah /play ---
# @events.NewMessage(pattern='/play (.+)', forwards=False, outgoing=False, func=lambda e: e.is_group)
# ^ Contoh filter Telethon yang lebih kompleks.
# Untuk kesederhanaan, kita bisa cek di dalam fungsi.
@app.on(events.NewMessage(pattern='/play(?: (.+))?', forwards=False, outgoing=False))
async def play_command_handler(event):
    # Memastikan ini adalah pesan di grup
    if not event.is_group:
        await event.reply("Perintah ini hanya dapat digunakan di grup.")
        return

    # Mengambil query dari pesan
    query = event.pattern_match.group(1) # Mengambil group(1) dari pattern (.+)
    if not query and event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.text:
            query = reply_message.text

    if not query:
        await event.reply("Mohon berikan nama lagu atau URL YouTube setelah perintah /play atau balas pesan yang berisi nama lagu.")
        return

    await event.reply("Mencari dan memuat lagu... Mohon tunggu.")

    stream_url, title = await get_audio_stream_url(query)

    if not stream_url:
        await event.reply(f"Tidak dapat menemukan lagu untuk '{query}'.")
        return

    try:
        # Bergabung ke Voice Chat dan mulai memutar
        # Perhatikan bahwa event.chat_id atau CHAT_ID_FOR_VC bisa digunakan
        # event.chat_id akan mengambil ID grup saat ini.
        # CHAT_ID_FOR_VC adalah ID yang sudah Anda tentukan secara statis.
        # Saya akan gunakan CHAT_ID_FOR_VC untuk konsistensi dengan kode sebelumnya.
        await calls.join_group_call(
            LOG_CHANNEL,
            AudioPiped(
                stream_url,
                HighQualityAudio()
            )
        )
        # Mendapatkan username chat untuk link
        chat_entity = await event.get_chat()
        chat_username = chat_entity.username if chat_entity.username else "c" + str(abs(chat_entity.id))
        
        await event.reply(f"Memutar: **{title}**\n[🎶 Klik untuk bergabung ke Voice Chat](https://t.me/{chat_username}/?voicechat)")
    except Exception as e:
        error_message = f"Gagal memutar lagu: {e}"
        if "GROUPCALL_NOT_FOUND" in str(e) or "GROUPCALL_ID_INVALID" in str(e):
             error_message += "\nPeringatan: Voice Chat belum aktif atau ID salah. Pastikan Voice Chat sudah dimulai di grup/channel."
        elif "CHAT_ADMIN_REQUIRED" in str(e):
            error_message += "\nPeringatan: Bot tidak memiliki hak admin untuk mengelola Voice Chat. Berikan izin 'Mengelola Obrolan Suara'."
        await event.reply(error_message)

# --- Handler Perintah /stop ---
@app.on(events.NewMessage(pattern='/stop', forwards=False, outgoing=False))
async def stop_command_handler(event):
    if not event.is_group:
        await event.reply("Perintah ini hanya dapat digunakan di grup.")
        return
    try:
        await calls.stop_stream(CHAT_ID_FOR_VC)
        await event.reply("Pemutaran dihentikan.")
    except Exception as e:
        await event.reply(f"Gagal menghentikan pemutaran: {e}")

# --- Handler Perintah /pause ---
@app.on(events.NewMessage(pattern='/pause', forwards=False, outgoing=False))
async def pause_command_handler(event):
    if not event.is_group:
        await event.reply("Perintah ini hanya dapat digunakan di grup.")
        return
    try:
        await calls.pause_stream(LOG_CHANNEL)
        await event.reply("Musik dijeda.")
    except Exception as e:
        await event.reply(f"Gagal menjeda musik: {e}")

# --- Handler Perintah /resume ---
@app.on(events.NewMessage(pattern='/resume', forwards=False, outgoing=False))
async def resume_command_handler(event):
    if not event.is_group:
        await event.reply("Perintah ini hanya dapat digunakan di grup.")
        return
    try:
        await calls.resume_stream(LOG_CHANNEL)
        await event.reply("Musik dilanjutkan.")
    except Exception as e:
        await event.reply(f"Gagal melanjutkan musik: {e}")

# --- Fungsi Utama Asinkron ---
async def main():
    print("Memulai Client Telethon...")
    # Telethon client sudah dimulai di bagian inisialisasi .start(bot_token=Var.BOT_TOKEN)
    # await app.start() # Tidak perlu memanggil ini lagi
    print("Client Telethon terhubung!")

    print("Memulai Client PyTgCalls...")
    await calls.start()
    print("Client PyTgCalls terhubung!")

    print("\nBot musik siap! Kirim /play [nama lagu] di grup yang memiliki Voice Chat aktif.")
    print(f"Pastikan CHAT_ID_FOR_VC diatur ke ID Voice Chat yang benar: {CHAT_ID_FOR_VC}")
    print("Tekan Ctrl+C untuk keluar.")
    await idle() # Menjaga bot tetap berjalan dan mendengarkan event

    print("Mengakhiri koneksi PyTgCalls Client...")
    await calls.stop()
    print("PyTgCalls Client terputus.")

    print("Mengakhiri koneksi Telethon Client...")
    await app.run_until_disconnected() # Menunggu hingga client terputus
    # Atau jika Anda ingin berhenti secara eksplisit:
    # await app.disconnect()
    print("Telethon Client terputus.")

# --- Jalankan Fungsi Utama ---
if __name__ == "__main__":
    asyncio.run(main())
