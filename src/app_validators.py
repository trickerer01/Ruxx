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
from app_defines import FMT_DATE, THREADS_MAX_ITEMS, DownloadModes
from app_gui_defines import (
    SLASH, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES, OPTION_VALUES_THREADING, OPTION_VALUES_PARCHI, OPTION_VALUES_PROXYTYPE,
)
from app_module import ProcModule
from app_utils import Protocol, normalize_path

__all__ = (
    'valid_thread_count', 'valid_date', 'valid_path', 'valid_json', 'valid_download_mode', 'valid_proxy', 'valid_positive_int',
    'valid_window_position', 'Validator', 'ValidatorAlwaysTrue', 'ModuleValidator', 'VideosCBValidator', 'ImagesCBValidator',
    'ThreadsCBValidator', 'JsonValidator', 'BoolStrValidator', 'ProxyValidator', 'ProxyTypeValidator', 'DateValidator',
    'ParchiCBValidator', 'TimeoutValidator', 'RetriesValidator', 'WindowPosValidator',
)


def valid_proxy_type(ptype: str) -> str:
    try:
        assert ptype in OPTION_VALUES_PROXYTYPE
        return ptype
    except Exception:
        raise ArgumentError


def valid_proxy(prox: str, check_type=True) -> str:
    if len(prox) == 0:
        return prox
    try:
        if check_type is True:
            from urllib.parse import urlparse
            url = urlparse(prox)
            pv, pp = tuple(url.netloc.split(':', 1))
            pt, pva, ppi = valid_proxy_type(url.scheme), IPv4Address(pv), int(pp)
            assert 20 < ppi < 65535
            return f'{pt}://{str(pva)}:{ppi:d}'

        pv, pp = tuple(prox.split(':', 1))
        pva, ppi = IPv4Address(pv), int(pp)
        assert 20 < ppi < 65535
        return f'{str(pva)}:{ppi:d}'
    except Exception:
        raise ArgumentError


def valid_date(date: str) -> str:
    try:
        _ = datetime.strptime(date, FMT_DATE)
        return date
    except Exception:
        raise ArgumentError


def valid_json(json: str) -> dict:
    try:
        return json_loads(json.strip('\'"').replace('\\', ''))
    except Exception:
        raise ArgumentError


def valid_positive_int(val: str, *, lb=0, ub=4294967295) -> int:
    try:
        val = int(val)
        assert lb <= val <= ub
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


def valid_window_position(val: str, tk) -> str:
    try:
        x, y = tuple(val.split('x', 1))
        assert 0 < int(x) + 25 < tk.winfo_screenwidth() and 0 < int(y) + 25 < tk.winfo_screenheight()
        return f'+{x}+{y}'
    except Exception:
        raise ArgumentError


class Validator(Protocol):
    tk = None

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


class DateValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_date(val)
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
            _ = valid_proxy(val, False)
            return True
        except Exception:
            return False


class ProxyTypeValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_proxy_type(val)
            return True
        except Exception:
            return False


class TimeoutValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_positive_int(val, lb=3, ub=300)
            return True
        except Exception:
            return False


class RetriesValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_positive_int(val, lb=5, ub=100)
            return True
        except Exception:
            return False


class WindowPosValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_window_position(val, self.tk)
            return True
        except Exception:
            return False

#
#
#########################################
