# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys
from multiprocessing.dummy import current_process
from typing import List

# internal
from app_cmdargs import prepare_arglist
from app_downloaders import get_new_downloader
from app_logger import Logger
from app_module import ProcModule, PROC_MODULES_BY_ABBR
from app_utils import ensure_compatibility

__all__ = ('run_cmd',)


def run_cmd(args: List[str]) -> None:
    Logger.init(True)
    ensure_compatibility()
    current_process().killed = False
    arglist = prepare_arglist(args)
    ProcModule.set(PROC_MODULES_BY_ABBR[arglist.module])
    with get_new_downloader() as cdwn:
        cdwn.save_cmdline(args)
        if arglist.get_maxid:
            cdwn.launch_get_max_id(arglist)
        else:
            cdwn.launch_download(arglist)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        run_cmd(sys.argv[1:])
        sys.exit(0)
    else:
        print('ERROR: Ruxx cmd arguments required. To run GUI use ruxx_gui.py')
        sys.exit(-1)

#
#
#########################################
