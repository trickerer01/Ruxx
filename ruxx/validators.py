# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import datetime
import json
import pathlib
from abc import ABC, abstractmethod
from argparse import ArgumentError
from ipaddress import IPv4Address

from .defines import API_KEY_LEN_RX, DMODE_CHOICES, FMT_DATE, THREADS_MAX_ITEMS
from .gui_defines import (
    OPTION_VALUES_IMAGES,
    OPTION_VALUES_PARCHI,
    OPTION_VALUES_PROXYTYPE,
    OPTION_VALUES_THREADING,
    OPTION_VALUES_VIDEOS,
)
from .module import ProcModule

__all__ = (
    'APIKeyKeyValidator',
    'APIKeyUserIdValidator',
    'BoolStrValidator',
    'DateValidator',
    'DummyValidator',
    'FolderPathValidator',
    'ImagesCBValidator',
    'InfoSaveModeValidator',
    'JsonValidator',
    'ModuleValidator',
    'ParchiCBValidator',
    'ProxyTypeValidator',
    'ProxyValidator',
    'RetriesValidator',
    'ThreadsCBValidator',
    'TimeoutValidator',
    'Validator',
    'VideosCBValidator',
    'WindowPosValidator',
    'valid_api_key',
    'valid_date',
    'valid_download_mode',
    'valid_folder_path',
    'valid_json',
    'valid_kwarg',
    'valid_positive_int',
    'valid_proxy',
    'valid_thread_count',
    'valid_window_position',
)


def valid_proxy_type(ptype: str) -> str:
    try:
        assert ptype in OPTION_VALUES_PROXYTYPE
        return ptype
    except Exception:
        raise ArgumentError


def valid_proxy(prox: str, with_type=True) -> str:
    if len(prox) == 0:
        return prox
    try:
        from urllib import parse as url_parse
        if with_type is False:
            assert '://' not in prox
            url = url_parse.urlparse(f'{OPTION_VALUES_PROXYTYPE[0]}://{prox}')
        else:
            url = url_parse.urlparse(prox)
        _ = valid_proxy_type(url.scheme)
        _ = IPv4Address(url.hostname)
        assert 20 < url.port < 65535
        return prox
    except Exception:
        raise ArgumentError


def valid_date(date: str) -> str:
    try:
        _ = datetime.datetime.strptime(date, FMT_DATE)
        return date
    except Exception:
        raise ArgumentError


def valid_json(json_str: str) -> dict[str, str]:
    try:
        return json.loads(json_str.strip('\'"').replace('\\', ''))
    except Exception:
        raise ArgumentError


def valid_kwarg(kwarg: str) -> tuple[str, str]:
    try:
        k, v = tuple(kwarg.split('=', 1))
        return k, v
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
    return valid_positive_int(val, lb=1, ub=THREADS_MAX_ITEMS)


def valid_folder_path(pathstr: str) -> pathlib.Path:
    try:
        newpath = pathlib.Path(pathstr.strip('\'"')).resolve()
        assert newpath.parent.is_dir()
        return newpath
    except Exception:
        raise ArgumentError


def valid_download_mode(mode: str) -> str:
    try:
        assert mode in DMODE_CHOICES
        return mode
    except Exception:
        raise ArgumentError


def valid_window_position(val: str, tk) -> str:
    try:
        x, y = tuple(val.split('x', 1))
        assert 0 < int(x) + 25 < tk.winfo_screenwidth() and 0 < int(y) + 25 < tk.winfo_screenheight()
        return f'+{x}+{y}'
    except Exception:
        raise ArgumentError


def valid_api_key_key(key: str) -> str:
    try:
        if key:
            assert len(key) == API_KEY_LEN_RX
            assert key.isalnum()
        return key
    except Exception:
        raise ArgumentError


def valid_api_key_userid(user_id: str) -> str:
    try:
        if user_id:
            assert user_id.isnumeric()
        return user_id
    except Exception:
        raise ArgumentError


def valid_api_key(val: str) -> str:
    try:
        key, user_id = tuple(val.split(',', 1))
        _ = valid_api_key_key(key)
        _ = valid_api_key_userid(user_id)
        return f'{key},{user_id}'
    except Exception:
        raise ArgumentError


class Validator(ABC):
    tk = None

    @abstractmethod
    def __call__(self, val: int | str) -> bool: ...

    @abstractmethod
    def get_value_type(self) -> type: ...


class IntValidator(Validator):
    @abstractmethod
    def __call__(self, val: int) -> bool: ...

    def get_value_type(self) -> type:
        return int


class StrValidator(Validator):
    @abstractmethod
    def __call__(self, val: str) -> bool: ...

    def get_value_type(self) -> type:
        return str


class DummyValidator(IntValidator, StrValidator):
    def __call__(self, val: int | str) -> bool:
        return True

    def get_value_type(self) -> type:
        return str


class ModuleValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        return ProcModule.PROC_MODULE_MIN - 1 <= val <= ProcModule.PROC_MODULE_MAX - 1


class FolderPathValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_folder_path(val)
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
        return val in ('0', '1')


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


class InfoSaveModeValidator(IntValidator):
    def __call__(self, val: int) -> bool:
        try:
            _ = valid_positive_int(str(val), ub=2)
            return True
        except Exception:
            return False


class APIKeyKeyValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_api_key_key(val)
            return True
        except Exception:
            return False


class APIKeyUserIdValidator(StrValidator):
    def __call__(self, val: str) -> bool:
        try:
            _ = valid_api_key_userid(val)
            return True
        except Exception:
            return False

#
#
#########################################
