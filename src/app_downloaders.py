# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# Downloader subclasses should be imported only to here
# From this module only import to highest level (app_unittests.py, app_gui.py, ruxx_cmd.py, ruxx_gui.py)
#

from app_download import Downloader
from app_download_rn import DownloaderRn
from app_download_rs import DownloaderRs
from app_download_rx import DownloaderRx
from app_download_rz import DownloaderRz
from app_module import ProcModule

__all__ = ('make_downloader', 'get_new_downloader')


DOWNLOADERS_BY_PROC_MODULE = {
    ProcModule.PROC_RX: DownloaderRx,
    ProcModule.PROC_RN: DownloaderRn,
    ProcModule.PROC_RS: DownloaderRs,
    ProcModule.PROC_RZ: DownloaderRz,
}


def make_downloader(proc_module: int, set_module=True) -> Downloader:  # TODO
    if set_module:
        ProcModule.set(proc_module)
    return DOWNLOADERS_BY_PROC_MODULE[proc_module]()


def get_new_downloader() -> Downloader:
    return make_downloader(ProcModule.CUR_PROC_MODULE, False)

#
#
#########################################
