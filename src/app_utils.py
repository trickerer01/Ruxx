# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys
from abc import abstractmethod
from datetime import datetime, date
from tkinter import messagebox
from typing import Iterable, TypeVar, Protocol

# internal
from app_defines import FMT_DATE, SUPPORTED_PLATFORMS
from app_gui_defines import SLASH
from app_re import re_uscore_mult

T_N1 = TypeVar('T_N1')


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other) -> bool: ...

    @abstractmethod
    def __eq__(self, other) -> bool: ...


def ensure_compatibility() -> None:
    assert sys.version_info >= (3, 9), 'Minimum python version required is 3.9!'
    assert sys.platform in SUPPORTED_PLATFORMS, f'Unsupported OS \'{sys.platform}\'!'


def assert_nonempty(container: Iterable[T_N1], message='') -> Iterable[T_N1]:
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


def as_date(date_s: str) -> date:
    return datetime.strptime(date_s, FMT_DATE).date()


def confirm_yes_no(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg)


def normalize_path(basepath: str, append_slash=True) -> str:
    normalized_path = basepath.replace('\\', SLASH)
    if append_slash and len(normalized_path) != 0 and normalized_path[-1] != SLASH:
        normalized_path += SLASH
    return normalized_path


def trim_undersores(base_str: str) -> str:
    return re_uscore_mult.sub('_', base_str).strip('_')


def format_score(score_str: str) -> str:
    score_str = score_str or '0'
    return f'({"" if score_str.startswith(("0", "-", "+", "u")) else "+"}{score_str})'

#
#
#########################################
