# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import abstractmethod
from datetime import datetime, date
from tkinter import messagebox
# from typing import Iterable
try:
    from typing import Protocol
except Exception:
    # noinspection PyUnresolvedReferences
    from typing_extensions import Protocol

# internal
from app_defines import FMT_DATE_DEFAULT
from app_gui_defines import SLASH, re_uscore_mult

__all__ = ('Protocol', 'Comparable', 'as_date', 'confirm_yes_no', 'normalize_path', 'trim_undersores', 'format_score', 'find_first_not_of')


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other) -> bool: ...

    @abstractmethod
    def __eq__(self, other) -> bool: ...


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
    return datetime.strptime(date_s, FMT_DATE_DEFAULT).date()


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
    score_str = score_str if score_str not in {'', None} else '0'
    return f'score({"" if score_str[0] in {"0", "-", "u"} else "+"}{score_str})'

#
#
#########################################
