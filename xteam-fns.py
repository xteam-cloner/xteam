import os
import shutil

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

long_description = "# xteam-fns"

name = "xteam-fns"
author = "TeamX"
author_email = "xteamji@gmail.com"
description = "Function based library for telegram telethon projects."
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

shutil.copy("xteam/_misc/_wrappers.py", "xteam/wrappers.py")
shutil.copy("xteam/startup/_database.py", "xteam/db.py")

setuptools.setup(
    name=name,
    version="1.0.1",
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    project_urls=project_urls,
    license=license_,
    packages=setuptools.find_packages(
        exclude=["xteam.dB", "xteam._misc", "xteam.startup"]
    ),
    install_requires=["telethon"],
    classifiers=classifiers,
    python_requires=">3.7, <3.14",
)

for file in ["wrappers", "db"]:
    os.remove(f"xteam/{file}.py")
