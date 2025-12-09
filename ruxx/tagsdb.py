# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import json
import os

from .defines import FILE_NAME_ALIASES, MODULE_CHOICES, TAG_AUTOCOMPLETE_LENGTH_MIN, TAG_AUTOCOMPLETE_NUMBER_MAX, UTF8
from .logger import trace
from .rex import re_wtag
from .utils import normalize_path

__all__ = ('TAG_ALIASES', 'TagsDB', 'is_wtag', 'load_tag_aliases')

TAG_ALIASES: dict[str, str] = {}


class TagsDB:
    """TagsDB !Static!"""
    DB: dict[str, dict[str, int]] = {}
    DBFiles: dict[str, str] = {}
    AuxDB: dict[str, dict[str, str]] = {}
    AuxDBFiles: dict[str, str] = {}

    def __init__(self) -> None:
        raise RuntimeError(f'{self.__class__.__name__} class should never be instanced!')

    @staticmethod
    def try_locate_file_single(filename: str) -> None:
        if filename in TagsDB.AuxDBFiles:
            return
        acwd = os.path.abspath(os.getcwd())
        afld = os.path.abspath(os.path.dirname(__file__))
        trace(f'cwd: \'{acwd}\'')
        trace(f'fld: \'{afld}\'')
        if os.path.basename(acwd) == 'ruxx':
            acwd = os.path.abspath(f'{acwd}/..')
        if os.path.basename(afld) == 'ruxx':
            afld = os.path.abspath(f'{afld}/..')
        basepath1 = normalize_path(acwd, False)
        basepath2 = normalize_path(afld, False)
        for basepath in (basepath1, basepath2):
            for folder_path in (f'{basepath}/', f'{basepath}/tags/', f'{basepath}/2tags/'):
                pfilename = f'{folder_path}{filename}'
                trace(f'looking for {pfilename}...')
                if os.path.isfile(pfilename):
                    TagsDB.AuxDBFiles[filename] = pfilename
                    trace('...found')
                    break
            if filename in TagsDB.AuxDBFiles:
                break

    @staticmethod
    def try_set_basepath(basepath: str, *, traverse=True) -> int:
        def collect_taglist_names(fpath: str, paths_dict: dict[str, str]) -> None:
            for module in MODULE_CHOICES:
                taglist_path = f'{fpath}{module}_tags.json'
                if os.path.isfile(taglist_path):
                    paths_dict[module] = taglist_path

        def collect_aux_file_names(fpath: str) -> None:
            tag_aliases_path = f'{fpath}all_tag_aliases.json'
            if os.path.isfile(tag_aliases_path):
                TagsDB.AuxDBFiles[FILE_NAME_ALIASES] = tag_aliases_path

        folder = normalize_path(basepath or os.path.abspath(f'{os.path.dirname(__file__)}/..'), False)
        TagsDB.clear()
        while not TagsDB.DBFiles:
            folder_up, tail = tuple(os.path.split(folder))
            for folder_path in (f'{folder}/', f'{folder}/tags/', f'{folder}/2tags/'):
                if os.path.isdir(folder_path):
                    tlpaths: dict[str, str] = {}
                    collect_taglist_names(folder_path, tlpaths)
                    if tlpaths:
                        TagsDB.DBFiles.update(tlpaths)
                    collect_aux_file_names(folder_path)
            if not tail or not traverse:
                break
            folder = folder_up
        return len(TagsDB.DBFiles)

    @staticmethod
    def clear() -> None:
        TagsDB.DB.clear()
        TagsDB.DBFiles.clear()

    @staticmethod
    def empty() -> bool:
        return not TagsDB.DBFiles

    @staticmethod
    def _load(module: str) -> None:
        if module in TagsDB.DB:
            return
        TagsDB.DB[module] = {}
        try:
            with open(TagsDB.DBFiles.get(module, ''), 'rt', encoding=UTF8) as dbfile:
                for line in dbfile:
                    try:
                        kv_k, kv_v = tuple(line.strip(' ,"\n\ufeff').split('": "', 1))
                        ivalue = int(kv_v[:kv_v.find(' ')])
                        TagsDB.DB[module][kv_k] = ivalue
                    except Exception:
                        continue
        except FileNotFoundError:
            return

    @staticmethod
    def _get_tag_matches(module: str, tag: str) -> list[tuple[str, int]]:
        arr = list(TagsDB.DB[module].keys())
        lb, ub = 0, len(arr) - 1
        while lb < ub:
            mid = lb + (ub - lb) // 2
            if arr[mid] < tag:
                lb = mid + 1
            else:
                ub = mid
        gmatches: list[str] = []
        while lb < len(arr) and arr[lb].startswith(tag):
            gmatches.append(arr[lb])
            lb += 1
        glist = [(g, TagsDB.DB[module][g]) for g in sorted(gmatches, reverse=True, key=lambda gmatch: TagsDB.DB[module][gmatch])]
        return glist

    @staticmethod
    def autocomplete_tag(module: str, tag: str) -> list[tuple[str, int]]:
        matches: list[tuple[str, int]] = []
        if not is_wtag(tag) and len(tag) >= TAG_AUTOCOMPLETE_LENGTH_MIN:
            TagsDB._load(module)
            base_matches = TagsDB._get_tag_matches(module, tag)
            matches.extend((mtag[len(tag):], count) for mtag, count in base_matches[:TAG_AUTOCOMPLETE_NUMBER_MAX])
        return matches

    @staticmethod
    def load_aux_file(filename: str, dest: dict[str, str]) -> None:
        assert filename not in TagsDB.AuxDB
        if filepath := TagsDB.AuxDBFiles.get(filename, ''):
            with open(filepath, 'rt', encoding=UTF8) as auxfile:
                dest.update(json.load(auxfile))
                TagsDB.AuxDB[filename] = filepath


def is_wtag(tag: str) -> bool:
    return bool(re_wtag.fullmatch(tag))


def load_tag_aliases() -> None:
    if not TAG_ALIASES:
        try:
            trace('Loading tag aliases...')
            TagsDB.try_locate_file_single(FILE_NAME_ALIASES)
            TagsDB.load_aux_file(FILE_NAME_ALIASES, TAG_ALIASES)
        except Exception:
            trace(f'Error: Failed to load tag aliases from {TagsDB.AuxDBFiles.get(FILE_NAME_ALIASES, FILE_NAME_ALIASES)}')
            TAG_ALIASES.update({'': ''})

#
#
#########################################
