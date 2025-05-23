from xteam import udB
from xteam.startup import LOGS
from xteam.startup.funcs import _version_changes, update_envs
from .multi_db import _init_multi_dbs


def _handle_post_startup():
    update_envs()
    _version_changes(udB)
    _init_multi_dbs("MULTI_DB")
