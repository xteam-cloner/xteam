from .. import run_as_module
import resources
from secrets import choice
import random
from secrets import choice
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterVoice
from telethon.tl.types import InputMessagesFilterPhotos
#from . import eor, ultroid_cmd, get_string, OWNER_NAME
from telethon import Button
if not run_as_module:
    from ..exceptions import RunningAsFunctionLibError

    raise RunningAsFunctionLibError(
        "You are running 'xteam' as a functions lib, not as run module. You can't access this folder.."
    )

from .. import *
from . import *
DEVLIST = [
    1434595544, # @xteam_clone
    719195224,  # @xditya
    1322549723,  # @danish_00
    1903729401,  # @its_buddhhu
    1303895686,  # @Sipak_OP
    611816596,  # @Arnab431
    1318486004,  # @sppidy
    803243487,  # @hellboi_atul
]

devs = [
    1434595544, # @xteam_clone
    719195224,  # @xditya
    1322549723,  # @danish_00
    1903729401,  # @its_buddhhu
    1303895686,  # @Sipak_OP
    611816596,  # @Arnab431
    1318486004,  # @sppidy
    803243487,  # @hellboi_atul
]


ULTROID_IMAGES = [
    f"https://graph.org/file/{_}.jpg"
    for _ in [
        "8d7b534e34e13316a7dd2"
        #"ec250c66268b62ee4ade6",
        #"3c25230ae30d246194eba",
        #"b01715a61b9e876c0d45d",
        #"4ceaf720a96a24527ecff",
        #"a96223b574f29f3f0d184",
        #"6e081d339a01cc6190393",
    ]
]

ALIVE_NAME = [
    "━━━━✿ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ᴀʟɪᴠᴇ ✿━━━"
]

ALIVE_TEXT = [
"❍❍❍❍❍❍❍❍❍❍❍❍❍❍❍❍"
]

PING_IMAGES = [f"/resources/extras/ping_pic.mp4"]

stickers = [
    "CAADAQADeAIAAm_BZBQh8owdViocCAI",
    "CAADAQADegIAAm_BZBQ6j8GpKtnrSgI",
    "CAADAQADfAIAAm_BZBQpqC84n9JNXgI",
    "CAADAQADfgIAAm_BZBSxLmTyuHvlzgI",
    "CAADAQADgAIAAm_BZBQ3TZaueMkS-gI",
    "CAADAQADggIAAm_BZBTPcbJMorVVsQI",
    "CAADAQADhAIAAm_BZBR3lnMZRdsYxAI",
    "CAADAQADhgIAAm_BZBQGQRx4iaM4pQI",
    "CAADAQADiAIAAm_BZBRRF-cjJi_QywI",
    "CAADAQADigIAAm_BZBQQJwfzkqLM0wI",
    "CAADAQADjAIAAm_BZBQSl5GSAT0viwI",
    "CAADAQADjgIAAm_BZBQ2xU688gfHhQI",
    "CAADAQADkAIAAm_BZBRGuPNgVvkoHQI",
    "CAADAQADpgIAAm_BZBQAAZr0SJ5EKtQC",
    "CAADAQADkgIAAm_BZBTvuxuayqvjhgI",
    "CAADAQADlAIAAm_BZBSMZdWN2Yew1AI",
    "CAADAQADlQIAAm_BZBRXyadiwWGNkwI",
    "CAADAQADmAIAAm_BZBQDoB15A1jS1AI",
    "CAADAQADmgIAAm_BZBTnOLQ8_d72vgI",
    "CAADAQADmwIAAm_BZBTve1kgdG0Y5gI",
    "CAADAQADnAIAAm_BZBQUMyFiylJSqQI",
    "CAADAQADnQIAAm_BZBSMAe2V4pwhNgI",
    "CAADAQADngIAAm_BZBQ06D92QL_vywI",
    "CAADAQADnwIAAm_BZBRw7UAbr6vtEgI",
    "CAADAQADoAIAAm_BZBRkv9DnGPXh_wI",
    "CAADAQADoQIAAm_BZBQwI2NgQdyKlwI",
    "CAADAQADogIAAm_BZBRPHJF3XChVLgI",
    "CAADAQADowIAAm_BZBThpas7rZD6DAI",
    "CAADAQADpAIAAm_BZBQcC2DpZcCw1wI",
    "CAADAQADpQIAAm_BZBQKruTcEU4ntwI",
]


#@call_back("asupan")
async def asupannya(event):
    try:
        asupannya = [
            asupan
            async for asupan in event.client.iter_messages(
                "@xcryasupan", filter=InputMessagesFilterVideo
            )
        ]
        await event.client.send_file(
            event.chat_id, file=choice(asupannya), reply_to=event.reply_to_msg_id
        )
        await xx.delete()
    except Exception:
        await xx.edit("**Tidak bisa menemukan video asupan.**")

QUOTES = [
"Nothing is impossible",
"Anyone can be anything",
"Take the risk or lose the chance",
"When there is a will, there is way",
"Do the best and let God do the rest",
"Good things take time",
"Don’t stop when you’re tired,stop when you’re done",
"Our life is very difficult,but there are millions of more difficult life out there",
"In life, there will be things that come up by itself, \nbut there will be things that also need to struggle to get it",
"Love comfort like sunshine after rain",
]
