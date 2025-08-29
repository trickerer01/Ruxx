# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys
from collections.abc import Iterable
from datetime import datetime, date
from math import ceil, log10
from tkinter import messagebox

# internal
from app_defines import FMT_DATE, SUPPORTED_PLATFORMS, SUBFOLDER_NAME_LEN_MAX
from app_gui_defines import SLASH, UNDERSCORE
from app_re import re_uscore_mult, re_replace_symbols_sub


def ensure_compatibility() -> None:
    assert sys.version_info >= (3, 9), 'Minimum python version required is 3.9!'
    assert sys.platform in SUPPORTED_PLATFORMS, f'Unsupported OS \'{sys.platform}\'!'


def assert_nonempty(container: Iterable[str], message='') -> Iterable[str]:
    assert (not not container), message
    return container


# def is_sorted(c: Iterable) -> bool:
#     return all(a <= b for a, b in zip(c, c[1:]))


def find_first_not_of(s: str, chars: str) -> int:
    i = 0
    for c in s:
        if c not in chars:
            return i
        i += 1
    return -1


def number_len_fmt(number: int) -> str:
    return f'0{ceil(log10(number + 1)):d}d'


def as_date(date_s: str) -> date:
    return datetime.strptime(date_s, FMT_DATE).date()


def confirm_yes_no(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg)


def normalize_path(basepath: str, append_slash=True) -> str:
    normalized_path = basepath.replace('\\', SLASH)
    if append_slash and len(normalized_path) != 0 and normalized_path[-1] != SLASH:
        normalized_path += SLASH
    return normalized_path


def trim_underscores(base_str: str) -> str:
    return re_uscore_mult.sub('_', base_str).strip('_')


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
