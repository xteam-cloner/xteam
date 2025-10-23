# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/xteam/blob/main/LICENSE>.

import base64
import ipaddress
import struct
import sys

from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.sessions.string import _STRUCT_PREFORMAT, CURRENT_VERSION, StringSession

from xteam.configs import Var
from . import *
from .BaseClient import UltroidClient

_PYRO_FORM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}

# https://github.com/pyrogram/pyrogram/blob/master/docs/source/faq/what-are-the-ip-addresses-of-telegram-data-centers.rst

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def validate_session(session, logger=LOGS, _exit=True):
    from strings import get_string

    if session:
        # Telethon Session
        if session.startswith(CURRENT_VERSION):
            if len(session.strip()) != 353:
                logger.exception(get_string("py_c1"))
                sys.exit()
            return StringSession(session)

        # Pyrogram Session
        elif len(session) in _PYRO_FORM.keys():
            data_ = struct.unpack(
                _PYRO_FORM[len(session)],
                base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
            )
            if len(session) in [351, 356]:
                auth_id = 2
            else:
                auth_id = 3
            dc_id, auth_key = data_[0], data_[auth_id]
            return StringSession(
                CURRENT_VERSION
                + base64.urlsafe_b64encode(
                    struct.pack(
                        _STRUCT_PREFORMAT.format(4),
                        dc_id,
                        ipaddress.ip_address(DC_IPV4[dc_id]).packed,
                        443,
                        auth_key,
                    )
                ).decode("ascii")
            )
        else:
            logger.exception(get_string("py_c1"))
            if _exit:
                sys.exit()
    logger.exception(get_string("py_c2"))
    if _exit:
        sys.exit()


"""def vc_connection(udB, ultroid_bot):
    from strings import get_string
    #from pytgcalls import PyTgCalls

    VC_SESSION = Var.VC_SESSION or udB.get_key("VC_SESSION")
    if VC_SESSION and VC_SESSION != Var.SESSION:
        LOGS.info("Starting up VcClient.")
        try:
            vc_client = UltroidClient(
                validate_session(VC_SESSION, _exit=False),
                log_attempt=False,
                exit_on_error=False,
            )
            try:
                PyTgCalls(vc_client)
                LOGS.info("PyTgCalls client initiated for VC.")
                return vc_client
            except Exception as e:
                LOGS.error(f"Failed to initialize PyTgCalls for VC: {e}")
                return ultroid_bot # Fallback to the main bot if PyTgCalls fails
        except (AuthKeyDuplicatedError, EOFError):
            LOGS.info(get_string("py_c3"))
            udB.del_key("VC_SESSION")
        except Exception as er:
            LOGS.info("While creating Client for VC.")
            LOGS.exception(er)
    return ultroid_bot
"""

def vc_connection(udB, ultroid_bot):
    # Imports are assumed to be available or managed by the surrounding module
    from strings import get_string
    # The 'PyTgCalls' import is typically done outside the function or within a try block 
    # to handle its potential absence, but it's used inside the function logic here.
    # from pytgcalls import PyTgCalls # Re-enable if it's not imported globally

    # 1. Retrieve VC Session
    VC_SESSION = Var.VC_SESSION or udB.get_key("VC_SESSION")

    # 2. Check if a separate VC session exists and is different
    if VC_SESSION and VC_SESSION != Var.SESSION:
        LOGS.info("Starting up VcClient.")
        try:
            # 3. Create the VC client
            vc_client = UltroidClient(
                validate_session(VC_SESSION, _exit=False),
                log_attempt=False,
                exit_on_error=False,
            )
            try:
                # Import PyTgCalls inside the function if it's not global
                from pytgcalls import PyTgCalls 
                # 4. Initialize PyTgCalls for Voice Chats
                PyTgCalls(vc_client)
                LOGS.info("PyTgCalls client initiated for VC.")
                # 5. Success: Return the dedicated VC client
                return vc_client
            except Exception as e:
                # 6. Fallback if PyTgCalls fails
                LOGS.error(f"Failed to initialize PyTgCalls for VC: {e}")
                return ultroid_bot  # Fallback to the main bot

        except (AuthKeyDuplicatedError, EOFError):
            # 7. Handle bad session keys
            LOGS.info(get_string("py_c3"))
            udB.del_key("VC_SESSION")
        except Exception as er:
            # 8. Handle general client creation errors
            LOGS.info("While creating Client for VC.")
            LOGS.exception(er)

    # 9. Final Fallback: Return the main bot if no VC session was set,
    # or if any fatal error prevented the VC client from being created.
    return ultroid_bot
