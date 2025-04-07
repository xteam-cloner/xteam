# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

"""
Exceptions which can be raised by py-Ultroid Itself.
"""


class xteamError(Exception):
    ...


class DependencyMissingError(ImportError):
    ...


class RunningAsFunctionLibError(xteamError):
    ...
