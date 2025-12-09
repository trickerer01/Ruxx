# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# Downloader subclasses should be imported only to here
# From this module only import to top level (tests.py, gui.py, ruxx_cmd.py, ruxx_gui.py)
#

from .download import Downloader
from .download_bb import DownloaderBb
from .download_en import DownloaderEn
from .download_rn import DownloaderRn
from .download_rp import DownloaderRp
from .download_rs import DownloaderRs
from .download_rx import DownloaderRx
from .download_xb import DownloaderXb
from .module import ProcModule

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
