import re
import setuptools

requirements = [
    "telethon-patch",
    "aiofiles==24.1.0",
    "aiohttp==3.10.3",
    "asyncio==3.4.3",
    "httpx==0.25.0",
    "motor==3.6.0",
    "numpy==2.2.5",
    "pillow",
    "pydantic",
    "py-tgcalls==2.2.8",
    "python-dotenv==1.0.1",
    "python-decouple",
    "youtube-dl",
    "youtube-search==2.1.0",
    "kurigram",
    "ffmpeg",
    "python-dateutil",
    "deep-translator",
    "speedtest-cli",
    "python-telegram-bot",
    "emoji",
    "tqdm",
    "pyshorteners",
    "apscheduler",
    "bs4",
    "enhancer>=0.3.4",
    "gitpython",
    "google-api-python-client",
    "htmlwebshot",
    "lottie",
    "lxml",
    "numpy>=1.21.2",
    "oauth2client",
    "opencv-python-headless",
    "pillow>=9.0.0",
    "profanitydetector",
    "psutil",
    "pypdf2>=1.26.0",
    "pytz",
    "gtts",
    "qrcode",
    "requests",
    "tabulate",
    "telegraph",
    "tgcrypto",
    "youtube-search-python",
    "yt-dlp",
    "flask",
    "flask_restful",
    "wget",
    "catbox-uploader",
    "cloudscraper",
    "pymongo",
    "git+https://github.com/LonamiWebs/Telethon.git",
    "git+https://github.com/New-dev0/instagrapi.git@39df1b1#egg=instagrapi",
    "git+https://github.com/xteam-cloner/xteam.git",
    "git+https://github.com/buddhhu/img2html.git@c44170d#egg=img2html",
    "git+https://github.com/ufoptg/akipy.git",
    "git+https://github.com/xteam-cloner/pytgcalls.git"
]

with open("xteam/version.py", "rt", encoding="utf8") as x:
    version = re.search(r'__version__ = "(.*?)"', x.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

name = "xteam"
author = "TeamX"
author_email = "xteamji@gmail.com"
description = "A Secure and Powerful Python-Telethon Based Library For xteam Userbot."
license_ = "GNU AFFERO GENERAL PUBLIC LICENSE (v3)"
url = "https://github.com/xteam-cloner/xteam"
project_urls = {
    "Bug Tracker": "https://github.com/xteam-cloner/xteam/issues",
    "Documentation": "https://ultroid.tech",
    "Source Code": "https://github.com/xteam-cloner/xteam",
}
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    project_urls=project_urls,
    license=license_,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=classifiers,
    python_requires=">3.7, <3.14",
)
