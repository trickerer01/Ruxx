# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# internal
from app_defines import MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS


class ProcModule(object):
    PROC_RX = 1
    PROC_RN = 2
    PROC_RS = 3

    PROC_MODULE_DEFAULT = PROC_RX
    CUR_PROC_MODULE = PROC_MODULE_DEFAULT
    PROC_MODULE_MIN = PROC_RX
    PROC_MODULE_MAX = PROC_RS

    PROC_MODULES_BY_NAME = {
        MODULE_ABBR_RX: PROC_RX,
        MODULE_ABBR_RN: PROC_RN,
        MODULE_ABBR_RS: PROC_RS,
    }
    PROC_MODULES_NAMES_BY_ID = {
        PROC_RX: MODULE_ABBR_RX,
        PROC_RN: MODULE_ABBR_RN,
        PROC_RS: MODULE_ABBR_RS,
    }

    @staticmethod
    def set(dwnmodule: int) -> None:
        ProcModule.CUR_PROC_MODULE = dwnmodule

    @staticmethod
    def get() -> int:
        return ProcModule.CUR_PROC_MODULE

    @staticmethod
    def get_cur_module_name() -> str:
        return ProcModule.PROC_MODULES_NAMES_BY_ID.get(ProcModule.get(), 'unk')

    @staticmethod
    def set_cur_module_by_name(name: str) -> None:
        ProcModule.CUR_PROC_MODULE = ProcModule.PROC_MODULES_BY_NAME.get(name, ProcModule.PROC_RX)

    @staticmethod
    def is_rx() -> bool:
        return ProcModule.get() is ProcModule.PROC_RX

    @staticmethod
    def is_rn() -> bool:
        return ProcModule.get() is ProcModule.PROC_RN

    @staticmethod
    def is_rs() -> bool:
        return ProcModule.get() is ProcModule.PROC_RS


PROC_MODULES_BY_ABBR = {
    MODULE_ABBR_RX: ProcModule.PROC_RX,
    MODULE_ABBR_RN: ProcModule.PROC_RN,
    MODULE_ABBR_RS: ProcModule.PROC_RS,
}

#
#
#########################################
