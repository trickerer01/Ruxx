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
    UTF8, FILE_NAME_PREFIX_RX, FILE_NAME_PREFIX_RN, FILE_NAME_PREFIX_RS, FILE_NAME_PREFIX_RZ, FILE_NAME_PREFIX_RP, FILE_NAME_PREFIX_EN,
    ID_VALUE_SEPARATOR_CHAR_RX, ID_VALUE_SEPARATOR_CHAR_RN, ID_VALUE_SEPARATOR_CHAR_RS, ID_VALUE_SEPARATOR_CHAR_RZ,
    ID_VALUE_SEPARATOR_CHAR_RP, ID_VALUE_SEPARATOR_CHAR_EN,
)
from app_module import ProcModule

__all__ = ('prepare_tags_list',)

re_comments = re_compile(r'^(?:--|//|#).*?$')
re_separators = re_compile(r'(?:, *| +)')

idval_eq_separators = {
    ProcModule.RX: ID_VALUE_SEPARATOR_CHAR_RX,
    ProcModule.RN: ID_VALUE_SEPARATOR_CHAR_RN,
    ProcModule.RS: ID_VALUE_SEPARATOR_CHAR_RS,
    ProcModule.RZ: ID_VALUE_SEPARATOR_CHAR_RZ,
    ProcModule.RP: ID_VALUE_SEPARATOR_CHAR_RP,
    ProcModule.EN: ID_VALUE_SEPARATOR_CHAR_EN,
}
idstring_patterns = {
    ProcModule.RX: re_compile(fr'^(?:{FILE_NAME_PREFIX_RX}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RX}?)?\d+?)*$'),
    ProcModule.RN: re_compile(fr'^(?:{FILE_NAME_PREFIX_RN}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RN}?)?\d+?)*$'),
    ProcModule.RS: re_compile(fr'^(?:{FILE_NAME_PREFIX_RS}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RS}?)?\d+?)*$'),
    ProcModule.RZ: re_compile(fr'^(?:{FILE_NAME_PREFIX_RZ}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RZ}?)?\d+?)*$'),
    ProcModule.RP: re_compile(fr'^(?:{FILE_NAME_PREFIX_RP}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RP}?)?\d+?)*$'),
    ProcModule.EN: re_compile(fr'^(?:{FILE_NAME_PREFIX_EN}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_EN}?)?\d+?)*$'),
}
prefix_optional_patterns = {
    ProcModule.RX: re_compile(fr'{FILE_NAME_PREFIX_RX}?'),
    ProcModule.RN: re_compile(fr'{FILE_NAME_PREFIX_RN}?'),
    ProcModule.RS: re_compile(fr'{FILE_NAME_PREFIX_RS}?'),
    ProcModule.RZ: re_compile(fr'{FILE_NAME_PREFIX_RZ}?'),
    ProcModule.RP: re_compile(fr'{FILE_NAME_PREFIX_RP}?'),
    ProcModule.EN: re_compile(fr'{FILE_NAME_PREFIX_EN}?'),
}


def get_idval_eq_sep() -> str:
    return idval_eq_separators.get(ProcModule.value())


def get_r_idstring() -> Pattern:
    return idstring_patterns.get(ProcModule.value())


def get_r_prefix_optional() -> Pattern:
    return prefix_optional_patterns.get(ProcModule.value())


def id_list_from_string(id_str: str) -> List[str]:
    id_str = re_separators.sub(' ', id_str.strip())  # separators
    id_str = get_r_prefix_optional().sub('', id_str)  # prefix
    return id_str.strip().split(' ')


def parse_file(filepath: str) -> Tuple[bool, List[str]]:
    id_list = list()
    try:
        for line in open(filepath, 'rt', encoding=UTF8).readlines():
            line = line.strip(' \n\ufeff')
            if len(line) == 0 or re_comments.fullmatch(line):
                continue
            elif not get_r_idstring().fullmatch(line):
                raise IOError
            id_list.extend(id_list_from_string(line))
        return True, [f'id{get_idval_eq_sep()}{s}' for s in sorted(unique_everseen(id_list), key=lambda item: int(item))]
    except Exception:
        return False, id_list


def prepare_tags_list(filepath: str) -> Tuple[bool, str]:
    suc, id_list = parse_file(filepath)
    return suc, f'({"~".join(id_list)})'

#
#
#########################################
