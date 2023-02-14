# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import abstractmethod
from argparse import ArgumentError
from datetime import datetime
from ipaddress import IPv4Address
from json import loads as json_loads
from os import path
from typing import Union
try:
    from typing import Protocol
except Exception:
    # noinspection PyUnresolvedReferences
    from typing_extensions import Protocol

# internal
from app_defines import FMT_DATE_DEFAULT, THREADS_MAX_ITEMS, DownloadModes
from app_gui_defines import (
    SLASH, ProcModule, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES, OPTION_VALUES_THREADING, OPTION_VALUES_DOWNORDER
)
from app_utils import normalize_path


def unquote(string: str) -> str:
    try:
        while True:
            found = False
            if len(string) > 1 and string[0] in ['\'', '"']:
                string = string[1:]
                found = True
            if len(string) > 1 and string[-1] in ['\'', '"']:
                string = string[:-1]
                found = True
            if not found:
                break
        return string
    except Exception:
        raise ValueError


def valid_proxy(prox: str) -> str:
    try:
        pv, pp = tuple(prox.split(':', 1))
        pva = IPv4Address(pv)
        ppi = int(pp)
        assert 20 < ppi < 65535
    except Exception:
        raise ArgumentError

    return f'{str(pva)}:{ppi:d}'


def valid_date(date: str, rev=False) -> str:
    try:
        _ = datetime.strptime(date, '-'.join(reversed(FMT_DATE_DEFAULT.split('-'))) if rev else FMT_DATE_DEFAULT)
    except Exception:
        raise ArgumentError

    return date


def valid_json(json: str) -> dict:
    try:
        val = json_loads(unquote(json).replace('\\', ''))
    except Exception:
        raise ArgumentError

    return val


def valid_int(val: str) -> int:
    try:
        val = int(val)
    except Exception:
        raise ArgumentError

    return val


def valid_positive_int(val: str) -> int:
    try:
        val = int(val)
        assert val >= 0
    except Exception:
        raise ArgumentError

    return val


def valid_thread_count(val: str) -> int:
    try:
        val = int(val)
        if val < 1 or val > THREADS_MAX_ITEMS:
            raise ValueError
    except Exception:
        raise ArgumentError

    return val


def valid_path(pathstr: str) -> str:
    try:
        newpath = normalize_path(unquote(pathstr))
        if not path.isdir(newpath[:(newpath.find(SLASH) + 1)]):
            raise ValueError
    except Exception:
        raise ArgumentError

    return newpath


def valid_download_mode(mode: str) -> DownloadModes:
    try:
        dwnmode = DownloadModes(int(mode))
    except Exception:
        raise ArgumentError

    return dwnmode


class Validator(Protocol):
    @abstractmethod
    def __call__(self, val: Union[int, str]) -> bool:
        ...

    @abstractmethod
    def get_value_type(self) -> type:
        ...


class IntValidator(Validator):
    @abstractmethod
    def __call__(self, val: int) -> bool:
        ...

    def get_value_type(self) -> type:
        return int


class StrValidator(Validator):
    @abstractmethod
    def __call__(self, val: str) -> bool:
        ...

    def get_value_type(self) -> type:
        return str


class ValidatorAlwaysTrue(IntValidator, StrValidator):
    def __call__(self, val: Union[int, str]) -> bool:
        return True

    def get_value_type(self) -> type:
        return str


class ModuleValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return ProcModule.PROC_MODULE_MIN - 1 <= val <= ProcModule.PROC_MODULE_MAX - 1


class PathValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_path(val)
            return True
        except Exception:
            return False


class VideosCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_VIDEOS) - 1


class ImagesCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_IMAGES) - 1


class ThreadsCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_THREADING) - 1


class DownloadOrderCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_DOWNORDER) - 1


class PositiveIdValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        return len(val) > 0 and val[0] != '0' and int(val) > 0 and all(c.isnumeric() for c in val)


class IdValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        return (len(val) > 0 and val[val.find('-') + 1] != '0' and int(val) != 0 and
                all(c.isnumeric() or (i == 0 and c == '-') for i, c in enumerate(val)))


class DateValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_date(val, True)
            return True
        except Exception:
            return False


class JsonValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_json(val)
            return True
        except Exception:
            return False


class BoolStrValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        return len(val) == 1 and val[0] in ['0', '1']


class ProxyValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_proxy(val)
            return True
        except Exception:
            return False


VALIDATORS_DICT = {
    int: IntValidator,
    str: StrValidator,
}

#
#
#########################################
