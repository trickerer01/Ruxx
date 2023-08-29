# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile
from typing import List, Tuple, Pattern

# requirements
from iteration_utilities import unique_everseen

# internal
from app_defines import (
    DEFAULT_ENCODING, FILE_NAME_PREFIX_RX, FILE_NAME_PREFIX_RN, FILE_NAME_PREFIX_RS,
    ID_VALUE_SEPARATOR_CHAR_RX, ID_VALUE_SEPARATOR_CHAR_RN, ID_VALUE_SEPARATOR_CHAR_RS,
)
from app_gui_defines import ProcModule

__all__ = ('prepare_tags_list',)

re_comments = re_compile(r'^(?:--|//|#).*?$')
re_separators = re_compile(r'(?:, *| +)')

prefixes = {
    ProcModule.PROC_RX: FILE_NAME_PREFIX_RX,
    ProcModule.PROC_RN: FILE_NAME_PREFIX_RN,
    ProcModule.PROC_RS: FILE_NAME_PREFIX_RS,
}
idval_eq_separators = {
    ProcModule.PROC_RX: ID_VALUE_SEPARATOR_CHAR_RX,
    ProcModule.PROC_RN: ID_VALUE_SEPARATOR_CHAR_RN,
    ProcModule.PROC_RS: ID_VALUE_SEPARATOR_CHAR_RS,
}
idstring_patterns = {
    ProcModule.PROC_RX: re_compile(r'^(?:rx_?)?\d+?(?:(?:, *?| +?)(?:rx_?)?\d+?)*$'),
    ProcModule.PROC_RN: re_compile(r'^(?:rn_?)?\d+?(?:(?:, *?| +?)(?:rn_?)?\d+?)*$'),
    ProcModule.PROC_RS: re_compile(r'^(?:rs_?)?\d+?(?:(?:, *?| +?)(?:rs_?)?\d+?)*$'),
}
prefix_optional_patterns = {
    ProcModule.PROC_RX: re_compile(fr'{prefixes.get(ProcModule.PROC_RX)}?'),
    ProcModule.PROC_RN: re_compile(fr'{prefixes.get(ProcModule.PROC_RN)}?'),
    ProcModule.PROC_RS: re_compile(fr'{prefixes.get(ProcModule.PROC_RS)}?'),
}


def get_idval_eq_sep() -> str:
    return idval_eq_separators.get(ProcModule.get())


def get_r_idstring() -> Pattern:
    return idstring_patterns.get(ProcModule.get())


def get_r_prefix_optional() -> Pattern:
    return prefix_optional_patterns.get(ProcModule.get())


def id_list_from_string(id_str: str) -> List[str]:
    id_str = re_separators.sub(' ', id_str.strip())  # separators
    id_str = get_r_prefix_optional().sub('', id_str)  # prefix
    return id_str.strip().split(' ')


def parse_file(filepath: str) -> Tuple[bool, List[str]]:
    id_list = list()  # type: List[str]
    try:
        for line in open(filepath, 'rt', encoding=DEFAULT_ENCODING).readlines():
            line = line.strip(' \n\ufeff')
            if len(line) == 0 or re_comments.fullmatch(line):
                continue
            elif not get_r_idstring().fullmatch(line):
                raise IOError
            id_list += id_list_from_string(line)
        return True, [f'id{get_idval_eq_sep()}{s}' for s in sorted(unique_everseen(id_list), key=lambda item: int(item))]
    except Exception:
        return False, id_list


def prepare_tags_list(filepath: str) -> Tuple[bool, str]:
    suc, id_list = parse_file(filepath)
    if suc is False or len(id_list) == 0:
        return False, ''

    return suc, f'({"~".join(id_list)})'

#
#
#########################################
