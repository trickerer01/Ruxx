# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile, sub as re_sub, fullmatch as re_fullmatch
from typing import List, Tuple

# requirements
from iteration_utilities import unique_everseen

# internal
from app_defines import DEFAULT_ENCODING, FILE_NAME_PREFIX_RX, FILE_NAME_PREFIX_RN, ID_VALUE_SEPARATOR_CHAR_RX, ID_VALUE_SEPARATOR_CHAR_RN
from app_gui_defines import ProcModule

r_comments = re_compile(r'^(?:--|//|#).*?$')
r_idstring_rx = re_compile(r'^(?:(?:rx_?)?\d{1,8}(?:,(?: +?)?| +?))*?(?:rx_?)?\d{1,8} ?$')

prefixes = {
    ProcModule.PROC_RX: FILE_NAME_PREFIX_RX,
    ProcModule.PROC_RN: FILE_NAME_PREFIX_RN,
}
idval_eq_separators = {
    ProcModule.PROC_RX: ID_VALUE_SEPARATOR_CHAR_RX,
    ProcModule.PROC_RN: ID_VALUE_SEPARATOR_CHAR_RN,
}


def _get_prefix() -> str:
    return prefixes[ProcModule.get()]


def _get_idval_eq_sep() -> str:
    return idval_eq_separators[ProcModule.get()]


def _id_list_from_string(id_str: str) -> List[str]:
    id_str = re_sub(r'(?:, *| +)', ' ', id_str)  # separators
    id_str = re_sub(r'^ +', '', id_str)  # leading wspaces
    id_str = re_sub(r' +$', '', id_str)  # trailing wspaces
    id_str = re_sub(fr'{_get_prefix()}?', '', id_str)  # prefix
    return id_str.strip().split(' ')


def _parse_file(filepath: str) -> Tuple[bool, List[str]]:
    id_list = []  # type: List[str]
    try:
        for line in open(filepath, 'r', encoding=DEFAULT_ENCODING).readlines():
            if len(line.strip()) == 0 or re_fullmatch(r'^ +$', line) or re_fullmatch(r_comments, line):  # blank line, comments
                continue
            elif not re_fullmatch(r_idstring_rx, line):
                raise IOError
            id_list += _id_list_from_string(line)
        return True, [f'id{_get_idval_eq_sep()}{s}' for s in sorted(unique_everseen(id_list), key=lambda item: int(item))]
    # except (IOError, UnicodeError, ):
    #     return False, []
    except Exception:
        return False, []


def prepare_tags_list(filepath: str) -> Tuple[bool, str]:
    suc, id_list = _parse_file(filepath)
    if suc is False or len(id_list) == 0:
        return False, ''

    return suc, f'({"~".join(id_list)})'

#
#
#########################################
