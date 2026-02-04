import asyncio
from telethon import functions, errors
from telethon.tl.functions.messages import ImportChatInviteRequest, ExportChatInviteRequest
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from xteam import bot
from xteam.configs import Var

ASSISTANT_ID = Var.ASSISTANT_ID

async def auto_delete(msg, delay=2):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

def AssistantAdd(mystic):
    async def wrapper(event):
        # Hanya jalankan di grup/channel
        if not event.is_group and not event.is_channel:
            return await mystic(event)

        # 1. Cek apakah Assistant sudah ada di dalam grup
        is_participant = False
        try:
            await event.client.get_permissions(event.chat_id, ASSISTANT_ID)
            is_participant = True
        except (errors.UserNotParticipantError, ValueError):
            is_participant = False
        except Exception:
            is_participant = False

        # 2. Jika belum ada, coba masukkan
        if not is_participant:
            try:
                # Ambil/Buat link invite
                invite = await event.client(ExportChatInviteRequest(event.chat_id))
                hash_code = invite.link.split('+')[-1] if '+' in invite.link else invite.link.split('/')[-1]
                
                # Gunakan bot client (Assistant) untuk bergabung
                try:
                    await bot(ImportChatInviteRequest(hash_code))
                    status = await event.reply("**ᴀssɪsᴛᴀɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴊᴏɪɴᴇᴅ!**")
                    asyncio.create_task(auto_delete(status, 5))
                except UserAlreadyParticipantError:
                    # Jika ternyata sudah di dalam, abaikan saja
                    pass
                
            except errors.ChatAdminRequiredError:
                error = await event.reply("❌ **ᴇʀʀᴏʀ**: Saya butuh hak admin (Add Users) untuk mengundang assistant!")
                asyncio.create_task(auto_delete(error, 10))
                return
            except Exception as e:
                error = await event.reply(f"❌ **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ**\n\n**ʀᴇᴀsᴏɴ**: `{e}`")
                asyncio.create_task(auto_delete(error, 10))
                return
                
        return await mystic(event)

    return wrapper
    
