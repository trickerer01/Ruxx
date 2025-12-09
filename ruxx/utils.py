# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import datetime
import math
import sys
from collections.abc import Iterable, MutableSequence
from tkinter import messagebox

from .defines import FMT_DATE, MIN_PYTHON_VERSION, MIN_PYTHON_VERSION_STR, SUBFOLDER_NAME_LEN_MAX, SUPPORTED_PLATFORMS
from .gui_defines import OPTION_CMD_PATH_CMD, OPTION_CMD_PROXY_CMD, SLASH, UNDERSCORE
from .rex import re_replace_symbols_sub, re_uscore_mult


def ensure_compatibility() -> None:
    assert sys.version_info >= MIN_PYTHON_VERSION, f'Minimum python version required is {MIN_PYTHON_VERSION_STR}!'
    assert sys.platform in SUPPORTED_PLATFORMS, f'Unsupported OS \'{sys.platform}\'!'


def assert_nonempty(container: Iterable[str], message='') -> Iterable[str]:
    try:
        next(iter(container))
        return container
    except StopIteration:
        assert False, message


# def is_sorted(c: Iterable) -> bool:
#     return all(a <= b for a, b in zip(c, c[1:]))


def find_first_not_of(s: str, chars: str) -> int:
    for i, c in enumerate(s):
        if c not in chars:
            return i
    return -1


def number_len_fmt(number: int) -> str:
    return f'0{math.ceil(math.log10(number + 1)):d}d'


def as_date(date_s: str) -> datetime.date:
    return datetime.datetime.strptime(date_s, FMT_DATE).date()


def confirm_yes_no(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg)


def normalize_path(basepath: str, append_slash=True) -> str:
    normalized_path = basepath.replace('\\', SLASH)
    if append_slash and len(normalized_path) != 0 and normalized_path[-1] != SLASH:
        normalized_path += SLASH
    return normalized_path


def trim_underscores(base_str: str) -> str:
    return re_uscore_mult.sub('_', base_str).strip('_')


def garble_text(base_str: str) -> str:
    return '*' * (1 + len(base_str) + sum(divmod(len(base_str), 3)))


def garble_argument_values(args_list: MutableSequence[str], *arg_extra_names: str) -> None:
    arguments_to_garble = (OPTION_CMD_PATH_CMD, OPTION_CMD_PROXY_CMD, *arg_extra_names)
    try:
        for arg_name in arguments_to_garble:
            try:
                idx = args_list.index(arg_name)
            except Exception:
                continue
            assert len(args_list) > idx + 1
            arg_value = args_list[idx + 1]
            if arg_value:
                args_list[idx + 1] = '<REDACTED>'  # garble_text(arg_value)
    except (ValueError, AssertionError):
        return


def format_score(score_str: str) -> str:
    score_str = score_str or '0'
    return f'({"" if score_str.startswith(("0", "-", "+", "u")) else "+"}{score_str})'


def make_subfolder_name(tags_str: str, task_num: int, tasks_count: int) -> str:
    max_tags_str_len = SUBFOLDER_NAME_LEN_MAX * 2
    lname = tags_str
    if len(lname) > max_tags_str_len:
        lname = f'{lname[:(max_tags_str_len + 1) // 2]}..{lname[-(max_tags_str_len + 1) // 2:]}'
    name = f'{task_num:{number_len_fmt(tasks_count)}}_{trim_underscores(re_replace_symbols_sub.sub(UNDERSCORE, lname))}'
    if len(name) > SUBFOLDER_NAME_LEN_MAX:
        name = name.replace('..', '')
        name = f'{name[:(SUBFOLDER_NAME_LEN_MAX - 2) // 2]}..{name[-(SUBFOLDER_NAME_LEN_MAX - 2) // 2:]}'
    return name

#
#
#########################################
