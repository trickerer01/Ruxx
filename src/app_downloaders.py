# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# Downloader subclasses should be imported only to here
# From this module only import to top level (app_unittests.py, app_gui.py, ruxx_cmd.py, ruxx_gui.py)
#

# internal
from app_download import Downloader
from app_download_bb import DownloaderBb
from app_download_en import DownloaderEn
from app_download_rn import DownloaderRn
from app_download_rp import DownloaderRp
from app_download_rs import DownloaderRs
from app_download_rx import DownloaderRx
from app_download_xb import DownloaderXb
from app_module import ProcModule

__all__ = ('get_new_downloader',)


DOWNLOADERS_BY_PROC_MODULE = {
    ProcModule.RX: DownloaderRx,
    ProcModule.RN: DownloaderRn,
    ProcModule.RS: DownloaderRs,
    ProcModule.RP: DownloaderRp,
    ProcModule.EN: DownloaderEn,
    ProcModule.XB: DownloaderXb,
    ProcModule.BB: DownloaderBb,
}


def make_downloader(proc_module: int) -> Downloader:
    ProcModule.set(proc_module)
    return DOWNLOADERS_BY_PROC_MODULE[proc_module]()


def get_new_downloader() -> Downloader:
    return make_downloader(ProcModule.CUR_PROC_MODULE)

#
#
#########################################
