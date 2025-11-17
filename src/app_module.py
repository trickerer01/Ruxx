# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from typing import final

from app_defines import MODULE_ABBR_BB, MODULE_ABBR_EN, MODULE_ABBR_RN, MODULE_ABBR_RP, MODULE_ABBR_RS, MODULE_ABBR_RX, MODULE_ABBR_XB


@final
class ProcModule:
    RX: int = 1
    RN: int = 2
    RS: int = 3
    RP: int = 4
    EN: int = 5
    XB: int = 6
    BB: int = 7

    PROC_MODULES_BY_NAME: dict[str, int] = {
        MODULE_ABBR_RX: RX,
        MODULE_ABBR_RN: RN,
        MODULE_ABBR_RS: RS,
        MODULE_ABBR_RP: RP,
        MODULE_ABBR_EN: EN,
        MODULE_ABBR_XB: XB,
        MODULE_ABBR_BB: BB,
    }
    PROC_MODULES_NAMES_BY_ID: dict[int, str] = {
        RX: MODULE_ABBR_RX,
        RN: MODULE_ABBR_RN,
        RS: MODULE_ABBR_RS,
        RP: MODULE_ABBR_RP,
        EN: MODULE_ABBR_EN,
        XB: MODULE_ABBR_XB,
        BB: MODULE_ABBR_BB,
    }

    PROC_MODULE_DEFAULT: int = RX
    PROC_MODULE_NAME_DEFAULT: int = PROC_MODULES_NAMES_BY_ID[PROC_MODULE_DEFAULT]
    CUR_PROC_MODULE: int = PROC_MODULE_DEFAULT
    PROC_MODULE_MIN: int = RX
    PROC_MODULE_MAX: int = BB

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
    def is_rp() -> bool:
        return ProcModule.value() is ProcModule.RP

    @staticmethod
    def is_en() -> bool:
        return ProcModule.value() is ProcModule.EN

    @staticmethod
    def is_xb() -> bool:
        return ProcModule.value() is ProcModule.XB

    @staticmethod
    def is_bb() -> bool:
        return ProcModule.value() is ProcModule.BB

#
#
#########################################
