import os

from telethon import TelegramClient, events
from telethon import sessions
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import logging
from pytgcalls import PyTgCalls
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)


from .configs import Var
BOT_USERNAME = Var.BOT_USERNAME
ASSISTANT_ID = Var.ASSISTANT_ID

bot = TelegramClient('Zaid', api_id=Var.API_ID, api_hash=Var.API_HASH)
Zaid = bot.start(bot_token=Var.BOT_TOKEN)
client = TelegramClient(sessions(Var.SESSION), Var.API_ID, Var.API_HASH)
call_py = PyTgCalls(client)
client.start()
call_py.start()
