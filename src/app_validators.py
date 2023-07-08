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

# internal
from app_defines import FMT_DATE_DEFAULT, THREADS_MAX_ITEMS, DownloadModes
from app_gui_defines import (
    SLASH, ProcModule, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES, OPTION_VALUES_THREADING, OPTION_VALUES_DOWNORDER, OPTION_VALUES_PARCHI
)
from app_utils import Protocol, normalize_path

__all__ = (
    'valid_int', 'valid_thread_count', 'valid_date', 'valid_path', 'valid_json', 'valid_download_mode', 'valid_proxy', 'valid_positive_int',
    'StrValidator', 'IntValidator', 'ValidatorAlwaysTrue', 'ModuleValidator', 'VideosCBValidator', 'ImagesCBValidator', 'VALIDATORS_DICT',
    'ThreadsCBValidator', 'DownloadOrderCBValidator', 'PositiveIdValidator', 'IdValidator', 'JsonValidator', 'BoolStrValidator',
    'ProxyValidator', 'DateValidator', 'ParchiCBValidator',
)


def valid_proxy(prox: str) -> str:
    if len(prox) == 0:
        return prox
    try:
        pv, pp = tuple(prox.split(':', 1))
        pva, ppi = IPv4Address(pv), int(pp)
        assert 20 < ppi < 65535
        return f'{str(pva)}:{ppi:d}'
    except Exception:
        raise ArgumentError


def valid_date(date: str, rev=False) -> str:
    try:
        _ = datetime.strptime(date, '-'.join(reversed(FMT_DATE_DEFAULT.split('-'))) if rev else FMT_DATE_DEFAULT)
        return date
    except Exception:
        raise ArgumentError


def valid_json(json: str) -> dict:
    try:
        return json_loads(json.strip('\'"').replace('\\', ''))
    except Exception:
        raise ArgumentError


def valid_int(val: str) -> int:
    try:
        return int(val)
    except Exception:
        raise ArgumentError


def valid_positive_int(val: str) -> int:
    try:
        val = int(val)
        assert val >= 0
        return val
    except Exception:
        raise ArgumentError


def valid_thread_count(val: str) -> int:
    try:
        val = int(val)
        assert 1 <= val <= THREADS_MAX_ITEMS
        return val
    except Exception:
        raise ArgumentError


def valid_path(pathstr: str) -> str:
    try:
        newpath = normalize_path(path.abspath(pathstr.strip('\'"')))
        assert path.isdir(newpath[:(newpath.find(SLASH) + 1)])
        return newpath
    except Exception:
        raise ArgumentError


def valid_download_mode(mode: str) -> DownloadModes:
    try:
        return DownloadModes(int(mode))
    except Exception:
        raise ArgumentError


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


class ParchiCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_PARCHI) - 1


class ThreadsCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_THREADING) - 1


class DownloadOrderCBValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return 0 <= val <= len(OPTION_VALUES_DOWNORDER) - 1


class PositiveIdValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        return len(val) > 0 and not (len(val) > 1 and val[0] == '0') and all(c.isnumeric() for c in val)


class IdValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        return (len(val) > 0 and not (len(val) > 1 and (val[0] == '0' or val[0:2] == '-0')) and
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
        return len(val) == 1 and val[0] in ('0', '1')


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
