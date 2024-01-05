# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
# From this file only import to highest level (app_gui.py, ruxx.py, ruxx_gui.py)
#

from app_defines import MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS
from app_download_rn import DownloaderRn
from app_download_rs import DownloaderRs
from app_download_rx import DownloaderRx
from app_module import ProcModule

DOWNLOADERS_BY_PROC_MODULE = {
    ProcModule.PROC_RX: DownloaderRx,
    ProcModule.PROC_RN: DownloaderRn,
    ProcModule.PROC_RS: DownloaderRs,
}
PROC_MODULES_BY_ABBR = {
    MODULE_ABBR_RX: ProcModule.PROC_RX,
    MODULE_ABBR_RN: ProcModule.PROC_RN,
    MODULE_ABBR_RS: ProcModule.PROC_RS,
}

#
#
#########################################
