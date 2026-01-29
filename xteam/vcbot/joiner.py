import random
import asyncio
from typing import *
from typing import Dict, List, Union
from xteam import bot
from xteam.configs import Var
from telethon import *
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotParticipantError
)
from telethon.tl.types import PeerChannel, InputChannel
from telethon.tl.functions.channels import *
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import telethon
from telethon.tl import functions
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, ExportChatInviteRequest

ASSISTANT_ID = Var.ASSISTANT_ID

async def auto_delete(msg, delay=2):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

def AssistantAdd(mystic):
    async def wrapper(event):
        if not event.is_group:
            return await mystic(event)

        try:
            await event.client.get_entity(ASSISTANT_ID)
        except Exception:
            try:
                await event.client(functions.users.GetFullUserRequest(id=ASSISTANT_ID))
            except Exception:
                pass 

        try:
            await event.client.get_permissions(event.chat_id, ASSISTANT_ID)
            
        except (UserNotParticipantError, ValueError):
            try:
                invite_request = await event.client(ExportChatInviteRequest(event.chat_id))
                invite_link = invite_request.link
                invitelink = invite_link.replace("https://t.me/+", "").replace("https://t.me/joinchat/", "")
                
                await bot(ImportChatInviteRequest(invitelink))
                
                status = await event.reply("**ᴀssɪsᴛᴀɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴊᴏɪɴᴇᴅ!**")
                asyncio.create_task(auto_delete(status, 5))
                
            except Exception as e:
                error = await event.reply(f"❌ **ᴀssɪsᴛᴀɴᴛ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ**\n\n**ʀᴇᴀsᴏɴ**: `{e}`")
                asyncio.create_task(auto_delete(error, 10))
                return
                
        return await mystic(event)

    return wrapper
    
