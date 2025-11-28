# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import re

from iteration_utilities import unique_everseen

from app_defines import (
    FILE_NAME_PREFIX_BB,
    FILE_NAME_PREFIX_EN,
    FILE_NAME_PREFIX_RN,
    FILE_NAME_PREFIX_RP,
    FILE_NAME_PREFIX_RS,
    FILE_NAME_PREFIX_RX,
    FILE_NAME_PREFIX_XB,
    ID_VALUE_SEPARATOR_CHAR_BB,
    ID_VALUE_SEPARATOR_CHAR_EN,
    ID_VALUE_SEPARATOR_CHAR_RN,
    ID_VALUE_SEPARATOR_CHAR_RP,
    ID_VALUE_SEPARATOR_CHAR_RS,
    ID_VALUE_SEPARATOR_CHAR_RX,
    ID_VALUE_SEPARATOR_CHAR_XB,
    UTF8,
)
from app_module import ProcModule

__all__ = ('prepare_id_list', 'prepare_tag_lists')

re_comments = re.compile(r'^(?:--|//|#).*?$')
re_separators = re.compile(r'(?:, *| +)')

IDVAL_EQ_SEPARATORS = {
    ProcModule.RX: ID_VALUE_SEPARATOR_CHAR_RX,
    ProcModule.RN: ID_VALUE_SEPARATOR_CHAR_RN,
    ProcModule.RS: ID_VALUE_SEPARATOR_CHAR_RS,
    ProcModule.RP: ID_VALUE_SEPARATOR_CHAR_RP,
    ProcModule.EN: ID_VALUE_SEPARATOR_CHAR_EN,
    ProcModule.XB: ID_VALUE_SEPARATOR_CHAR_XB,
    ProcModule.BB: ID_VALUE_SEPARATOR_CHAR_BB,
}
IDSTRING_PATTERNS = {
    ProcModule.RX: re.compile(fr'^(?:{FILE_NAME_PREFIX_RX}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RX}?)?\d+?)*$'),
    ProcModule.RN: re.compile(fr'^(?:{FILE_NAME_PREFIX_RN}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RN}?)?\d+?)*$'),
    ProcModule.RS: re.compile(fr'^(?:{FILE_NAME_PREFIX_RS}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RS}?)?\d+?)*$'),
    ProcModule.RP: re.compile(fr'^(?:{FILE_NAME_PREFIX_RP}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_RP}?)?\d+?)*$'),
    ProcModule.EN: re.compile(fr'^(?:{FILE_NAME_PREFIX_EN}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_EN}?)?\d+?)*$'),
    ProcModule.XB: re.compile(fr'^(?:{FILE_NAME_PREFIX_XB}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_XB}?)?\d+?)*$'),
    ProcModule.BB: re.compile(fr'^(?:{FILE_NAME_PREFIX_BB}?)?\d+?(?:(?:, *?| +?)(?:{FILE_NAME_PREFIX_BB}?)?\d+?)*$'),
}
PREFIX_OPTIONAL_PATTERNS = {
    ProcModule.RX: re.compile(fr'{FILE_NAME_PREFIX_RX}?'),
    ProcModule.RN: re.compile(fr'{FILE_NAME_PREFIX_RN}?'),
    ProcModule.RS: re.compile(fr'{FILE_NAME_PREFIX_RS}?'),
    ProcModule.RP: re.compile(fr'{FILE_NAME_PREFIX_RP}?'),
    ProcModule.EN: re.compile(fr'{FILE_NAME_PREFIX_EN}?'),
    ProcModule.XB: re.compile(fr'{FILE_NAME_PREFIX_XB}?'),
    ProcModule.BB: re.compile(fr'{FILE_NAME_PREFIX_BB}?'),
}


def get_idval_eq_sep() -> str:
    return IDVAL_EQ_SEPARATORS[ProcModule.value()]


def get_r_idstring() -> re.Pattern:
    return IDSTRING_PATTERNS[ProcModule.value()]


def get_r_prefix_optional() -> re.Pattern:
    return PREFIX_OPTIONAL_PATTERNS[ProcModule.value()]


def id_list_from_string(id_str: str) -> list[str]:
    id_str = re_separators.sub(' ', id_str.strip())  # separators
    id_str = get_r_prefix_optional().sub('', id_str)  # prefix
    return id_str.strip().split(' ')


def parse_ids_file(filepath: str) -> tuple[bool, list[str]]:
    id_list: list[str] = []
    try:
        with open(filepath, 'rt', encoding=UTF8) as ifile:
            for line in ifile:
                line = line.strip(' \n\ufeff')
                if line and not re_comments.fullmatch(line):
                    assert get_r_idstring().fullmatch(line)
                    id_list.extend(id_list_from_string(line))
        return True, [f'id{get_idval_eq_sep()}{s}' for s in sorted(unique_everseen(id_list), key=int)]
    except Exception:
        return False, []


def prepare_id_list(filepath: str) -> tuple[bool, str]:
    suc, id_list = parse_ids_file(filepath)
    return suc, f'({"~".join(id_list)})'


def parse_tags_file(filepath: str) -> tuple[bool, list[str]]:
    tag_list: list[str] = []
    try:
        with open(filepath, 'rt', encoding=UTF8) as tfile:
            for line in tfile:
                line = line.strip(' \n\ufeff')
                if line and not re_comments.fullmatch(line):
                    tag_list.append(line)
        return True, list(unique_everseen(tag_list))
    except Exception:
        return False, tag_list


def prepare_tag_lists(filepath: str) -> tuple[bool, list[str]]:
    suc, tag_lists = parse_tags_file(filepath)
    return suc, tag_lists

#
#
#########################################
