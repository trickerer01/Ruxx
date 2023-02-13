# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from datetime import datetime, date
from platform import system as running_system
from re import sub as re_sub
from tkinter import messagebox

# internal
from app_defines import FMT_DATE_DEFAULT, PLATFORM_WINDOWS
from app_gui_defines import SLASH


def find_first_not_of(s: str, not_chars: str) -> int:
    for i, c in enumerate(s):  # type: int, str
        if c not in not_chars:
            return i
    return -1


def as_date(date_s: str) -> date:
    return datetime.strptime(date_s, FMT_DATE_DEFAULT).date()


def confirm_yes_no(title: str, msg: str) -> bool:
    return messagebox.askyesno(title, msg)


# unused
def endl() -> str:
    return '\r\n' if running_system() == PLATFORM_WINDOWS else '\n'


def trim_quotes_trailing_spaces(string: str) -> str:
    string = string.replace('"', '')
    while len(string) > 0 and string[0] == ' ':
        string = string[1:]
    while len(string) > 0 and string[-1] == ' ':
        string = string[:-1]

    return string


def normalize_path(basepath: str, append_slash=True) -> str:
    normalized_path = basepath.replace('\\', SLASH)
    if append_slash and len(normalized_path) != 0 and normalized_path[-1] != SLASH:
        normalized_path += SLASH
    return normalized_path


def trim_undersores(base_str: str) -> str:
    ret_str = re_sub(r'_{2,}', '_', base_str)
    if len(ret_str) != 0:
        if len(ret_str) >= 2 and ret_str[0] == '_' and ret_str[-1] == '_':
            ret_str = ret_str[1:-1]
        elif ret_str[-1] == '_':
            ret_str = ret_str[:-1]
        elif ret_str[0] == '_':
            ret_str = ret_str[1:]
    return ret_str


def format_score(score_str: str) -> str:
    score_str = score_str if score_str not in ['', None] else '0'
    return f'score({"" if score_str[0] in ["0", "-", "u"] else "+"}{score_str})'

#
#
#########################################
