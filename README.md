# xteam Library

Core library of [xteam Userbot](https://github.com/xteam-cloner/xteam-urbot), a python based telegram userbot.

[![CodeFactor](https://www.codefactor.io/repository/github/teamultroid/pyultroid/badge)](https://www.codefactor.io/repository/github/teamultroid/pyultroid)
[![PyPI - Version](https://img.shields.io/pypi/v/xteam?style=round)](https://pypi.org/project/xteam)    
[![PyPI - Downloads](https://img.shields.io/pypi/dm/xteam?label=DOWNLOADS&style=round)](https://pypi.org/project/xteam)    
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TeamUltroid/Ultroid/graphs/commit-activity)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/TeamUltroid/Ultroid)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

# Installation
```bash
pip3 install -U xteam
```

# Documentation 
[![Documentation](https://img.shields.io/badge/Documentation-Ultroid-blue)](http://ultroid.tech/)

# Usage
- Create folders named `plugins`, `addons`, `assistant` and `resources`.   
- Add your plugins in the `plugins` folder and others accordingly.   
- Create a `.env` file with following mandatory Environment Variables
   ```
   API_ID
   API_HASH
   SESSION
   REDIS_URI
   REDIS_PASSWORD
   ```
- Check
[`.env.sample`](https://github.com/TeamUltroid/Ultroid/blob/main/.env.sample) for more details.   
- Run `python3 -m xteam` to start the bot.   

## Creating plugins
 - ### To work everywhere

```python
@ultroid_cmd(
    pattern="start"
)   
async def _(e):   
    await e.eor("Ultroid Started!")   
```

- ### To work only in groups

```python
@ultroid_cmd(
    pattern="start",
    groups_only=True,
)   
async def _(e):   
    await eor(e, "Ultroid Started.")   
```

- ### Assistant Plugins 👇

```python
@asst_cmd("start")   
async def _(e):   
    await e.reply("Ultroid Started.")   
```

See more working plugins on [the offical repository](https://github.com/xteam-cloner/Userbotx)!

> Made with ♥️ by [@TeamX](https://t.me/xteam_cloner).    


# License
[![License](https://www.gnu.org/graphics/agplv3-155x51.png)](LICENSE)   
Userbot is licensed under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) v3 or later.

# Credits
* [![TeamX-Devs](https://img.shields.io/static/v1?label=TeamX&message=devs&color=critical)](https://t.me/UltroidDevs)
* [Lonami](https://github.com/Lonami) for [Telethon](https://github.com/LonamiWebs/Telethon)
