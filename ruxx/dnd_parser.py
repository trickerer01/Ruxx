# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import base64
import pathlib
from collections.abc import Iterable
from enum import Flag

from yarl import URL

from .defines import (
    IDVAL_EQ_SEPARATORS,
    MODULE_ABBR_BB,
    MODULE_ABBR_EN,
    MODULE_ABBR_RN,
    MODULE_ABBR_RP,
    MODULE_ABBR_RS,
    MODULE_ABBR_RX,
    MODULE_ABBR_XB,
    SITENAME_B_BB,
    SITENAME_B_EN,
    SITENAME_B_RN,
    SITENAME_B_RP,
    SITENAME_B_RS,
    SITENAME_B_RX,
    SITENAME_B_XB,
    UTF8,
    Mem,
)
from .module import ProcModule
from .utils import normalize_host

__all__ = ('analyze_dnd_string',)

DND_FILE_MAXSIZE = 4 * Mem.KB
DND_FILE_EXTENSIONS = ('.txt', '.list', '.conf', '.c0nf')

URL_PARSING_TEMPLATES: dict[str, tuple[str, list[dict[str, str]]]] = {
    normalize_host(URL(base64.b64decode(SITENAME_B_RX).decode())).host: (
        MODULE_ABBR_RX,
        [
            {'page': 'post', 's': 'list', 'tags': '?'},
            {'page': 'post', 's': 'view', 'id': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_RN).decode())).host: (
        MODULE_ABBR_RN,
        [
            {'/': '', 'post': '', 'list': '', '': '?'},
            {'/': '', 'post': '', 'view': '', '': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_RS).decode())).host: (
        MODULE_ABBR_RS,
        [
            {'r': 'posts/index', 'q': '?'},
            {'r': 'posts/view', 'id': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_RP).decode())).host: (
        MODULE_ABBR_RP,
        [
            {'/': '', 'post': '', 'list': '', '': '?'},
            {'/': '', 'post': '', 'view': '', '': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_EN).decode())).host: (
        MODULE_ABBR_EN,
        [
            {'tags': '?'},
            {'/': '', 'posts': '', '': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_XB).decode())).host: (
        MODULE_ABBR_XB,
        [
            {'page': 'post', 's': 'list', 'tags': '?'},
            {'page': 'post', 's': 'view', 'id': '?'},
        ],
    ),
    normalize_host(URL(base64.b64decode(SITENAME_B_BB).decode())).host: (
        MODULE_ABBR_BB,
        [
            {'page': 'post', 's': 'list', 'tags': '?'},
            {'page': 'post', 's': 'view', 'id': '?'},
        ],
    ),
}


def _get_idval_eq_sep() -> str:
    return IDVAL_EQ_SEPARATORS[ProcModule.name()]


class DNDResultFlags(Flag):
    DND_FLAG_NONE = 0x00
    DND_FLAG_IS_URL = 0x01
    DND_FLAG_IS_FILE = 0x02
    DND_FLAG_ERR_INVALID_STRING = 0x04
    DND_FLAG_ERR_INVALID_URL = 0x08
    DND_FLAG_ERR_INVALID_FILE = 0x10

    DND_FLAG_ERR_INVALID_ALL = DND_FLAG_ERR_INVALID_STRING | DND_FLAG_ERR_INVALID_URL | DND_FLAG_ERR_INVALID_FILE


class DNDStringAnalysisResult:
    def __init__(self, dnd_string) -> None:
        self._original_string = dnd_string
        self._flags = DNDResultFlags.DND_FLAG_NONE
        self._file_path = pathlib.Path()
        self._tags: list[str] = []

    def has_flag(self, flags: DNDResultFlags) -> bool:
        return bool(self._flags & flags)

    def has_all_flags(self, flags: DNDResultFlags) -> bool:
        return (self._flags & flags) == flags

    def set_flag(self, flags: DNDResultFlags) -> None:
        self._flags |= flags

    def remove_flag(self, flags: DNDResultFlags) -> None:
        self._flags &= ~flags

    def is_empty(self) -> bool:
        return not bool(self._tags)

    def is_invalid(self) -> bool:
        return self.has_all_flags(DNDResultFlags.DND_FLAG_ERR_INVALID_ALL) or self.is_empty()

    def add_tags(self, tags: Iterable[str]) -> None:
        self._tags.extend(tags)

    @property
    def flags(self) -> DNDResultFlags:
        return DNDResultFlags(self._flags)

    @property
    def original_string(self) -> str:
        return self._original_string

    @property
    def file_path(self) -> pathlib.Path:
        return pathlib.Path(self._file_path)

    @property
    def tags(self) -> tuple[str]:
        return tuple(self._tags)


def analyze_dnd_string(dnd_string: str) -> DNDStringAnalysisResult:
    res = DNDStringAnalysisResult(dnd_string)

    # 1) URL
    if res.is_empty():
        try:
            url = URL(dnd_string)
            assert url.host in URL_PARSING_TEMPLATES
            url_query = url.query
            url_parts = url.parts
            module, parsing_templates = URL_PARSING_TEMPLATES[url.host]
            idvalsep = IDVAL_EQ_SEPARATORS[module]
            for t in parsing_templates:
                if url_query:
                    for k, v in url_query.items():
                        if k not in t or t[k] not in (v, '?'):
                            break
                        if t[k] == '?':
                            uvalues = [f'{k}{idvalsep}{_}' if k == 'id' else _ for _ in ' '.join(v.split('+')).split() if _]
                            res.add_tags(uvalues)
                if url_parts:
                    if len(t) > len(url_parts):
                        continue
                    for i, tk in enumerate(t):
                        upart: str = url_parts[i]
                        if tk and upart != tk:
                            break
                        if t[tk] == '?':
                            res.add_tags([f'id{idvalsep}{upart}' if upart.isnumeric() else upart.lower()])
            assert not res.is_empty()
        except Exception:
            res.set_flag(DNDResultFlags.DND_FLAG_ERR_INVALID_URL)

    # 2) File
    if res.is_empty():
        try:
            file_path = pathlib.Path(dnd_string)
            assert file_path != pathlib.Path() and file_path.suffix in DND_FILE_EXTENSIONS and file_path.is_file()
            file_stat = file_path.stat()
            assert file_stat.st_size <= DND_FILE_MAXSIZE
            with open(file_path, 'rt', encoding=UTF8) as dnd_file:
                dnd_file_string = dnd_file.read()
                fvalues = ' '.join(dnd_file_string.split('+')).split()
                res.add_tags(fvalues)
            assert not res.is_empty()
        except Exception:
            res.set_flag(DNDResultFlags.DND_FLAG_ERR_INVALID_FILE)

    # 3) Plain string
    if res.is_empty():
        try:
            assert not any(_ in dnd_string for _ in '/\\')
            svalues = ' '.join(dnd_string.split('+')).split()
            res.add_tags(svalues)
            assert not res.is_empty()
        except Exception:
            res.set_flag(DNDResultFlags.DND_FLAG_ERR_INVALID_STRING)

    return res

#
#
#########################################
