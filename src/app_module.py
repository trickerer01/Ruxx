# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# internal
from app_defines import MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS, MODULE_ABBR_RZ, MODULE_ABBR_RP, MODULE_ABBR_EN


class ProcModule:
    RX = 1
    RN = 2
    RS = 3
    RZ = 4
    RP = 5
    EN = 6

    PROC_MODULE_DEFAULT = RX
    CUR_PROC_MODULE = PROC_MODULE_DEFAULT
    PROC_MODULE_MIN = RX
    PROC_MODULE_MAX = EN

    PROC_MODULES_BY_NAME = {
        MODULE_ABBR_RX: RX,
        MODULE_ABBR_RN: RN,
        MODULE_ABBR_RS: RS,
        MODULE_ABBR_RZ: RZ,
        MODULE_ABBR_RP: RP,
        MODULE_ABBR_EN: EN,
    }
    PROC_MODULES_NAMES_BY_ID = {
        RX: MODULE_ABBR_RX,
        RN: MODULE_ABBR_RN,
        RS: MODULE_ABBR_RS,
        RZ: MODULE_ABBR_RZ,
        RP: MODULE_ABBR_RP,
        EN: MODULE_ABBR_EN,
    }

    @staticmethod
    def set(dwnmodule: int) -> None:
        ProcModule.CUR_PROC_MODULE = dwnmodule

    @staticmethod
    def value() -> int:
        return ProcModule.CUR_PROC_MODULE

    @staticmethod
    def name() -> str:
        return ProcModule.PROC_MODULES_NAMES_BY_ID.get(ProcModule.value(), 'unk')

    @staticmethod
    def set_cur_module_by_name(name: str) -> None:
        ProcModule.set(ProcModule.PROC_MODULES_BY_NAME.get(name, ProcModule.RX))

    @staticmethod
    def is_rx() -> bool:
        return ProcModule.value() is ProcModule.RX

    @staticmethod
    def is_rn() -> bool:
        return ProcModule.value() is ProcModule.RN

    @staticmethod
    def is_rs() -> bool:
        return ProcModule.value() is ProcModule.RS

    @staticmethod
    def is_rz() -> bool:
        return ProcModule.value() is ProcModule.RZ

    @staticmethod
    def is_rp() -> bool:
        return ProcModule.value() is ProcModule.RP

    @staticmethod
    def is_en() -> bool:
        return ProcModule.value() is ProcModule.EN

#
#
#########################################
