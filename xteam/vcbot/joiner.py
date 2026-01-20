from typing import *
import random
from typing import Dict, List, Union

from xteam.configs import Var
from telethon import *
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotParticipantError
)
from telethon.tl.types import PeerChannel,InputChannel
from telethon.tl.functions.channels import *
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import telethon
from telethon.tl import functions
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import ExportChatInviteRequest

ASSISTANT_ID = Var.ASSISTANT_ID

def AssistantAdd(mystic):
    async def wrapper(event):
        # 1. Jika bukan di grup, langsung jalankan fungsi utama
        if not event.is_group:
            return await mystic(event)

        try:
            # 2. Cek apakah Assistant (Userbot) sudah ada di grup
            # Kita gunakan event.client (Bot Utama) untuk mengecek izin Assistant
            await event.client.get_permissions(event.chat_id, ASSISTANT_ID)
            
        except UserNotParticipantError:
            # 3. Jika Assistant tidak ada, buat link invite
            try:
                # Bot Utama membuat link
                invite_request = await event.client(ExportChatInviteRequest(event.chat_id))
                invite_link = invite_request.link
                
                # Bersihkan link untuk mendapatkan hash-nya
                invitelink = invite_link.replace("https://t.me/+", "").replace("https://t.me/joinchat/", "")
                
                # 4. Assistant (xteam.bot) bergabung menggunakan link tersebut
                await xteam.bot(ImportChatInviteRequest(invitelink))
                
                await event.reply("✅ **Assistant Berhasil Bergabung!**\nSekarang siap memutar musik.")
                
            except Exception as e:
                # Jika gagal (misal: Bot Utama bukan Admin atau tidak punya izin invite)
                await event.reply(
                    f"❌ **Assistant Gagal Bergabung**\n\n**Alasan**: `{e}`\n"
                    "**Solusi**: Pastikan Bot Utama adalah Admin dan punya izin 'Tambah Anggota'."
                )
                return
                
        # 5. Jalankan fungsi utama (mystic) setelah assistant dipastikan ada
        return await mystic(event)

    return wrapper
  
