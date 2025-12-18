# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import json
import os
import pathlib

from .defines import FILE_NAME_ALIASES, MODULE_CHOICES, TAG_AUTOCOMPLETE_LENGTH_MIN, TAG_AUTOCOMPLETE_NUMBER_MAX, UTF8
from .logger import trace
from .rex import re_wtag
from .utils import format_exception

__all__ = ('TAG_ALIASES', 'TagsDB', 'is_wtag', 'load_tag_aliases')

TAG_ALIASES: dict[str, str] = {}


class TagsDB:
    """TagsDB !Static!"""
    DB: dict[str, dict[str, int]] = {}
    DBFiles: dict[str, pathlib.Path] = {}
    AuxDB: dict[str, pathlib.Path] = {}
    AuxDBFiles: dict[str, pathlib.Path] = {}

    def __init__(self) -> None:
        raise RuntimeError(f'{self.__class__.__name__} class should never be instanced!')

    @staticmethod
    def try_locate_file_single(filename: str) -> None:
        if filename in TagsDB.AuxDBFiles:
            return
        acwd = pathlib.Path(os.getcwd()).resolve()
        afld = pathlib.Path(__file__).resolve().parent.parent
        if acwd.name == 'ruxx':
            acwd = acwd.parent
        if afld.name == 'ruxx':
            afld = afld.parent
        trace(f'cwd: \'{acwd}\'')
        trace(f'fld: \'{afld}\'')
        for basepath in (acwd, afld):
            for folder_path in (basepath, basepath / 'tags', basepath / '2tags'):
                pfilename = folder_path / filename
                trace(f'looking for {pfilename}...')
                if pfilename.is_file():
                    TagsDB.AuxDBFiles[filename] = pfilename
                    trace('...found')
                    break
            if filename in TagsDB.AuxDBFiles:
                break

    @staticmethod
    def try_set_basepath(basepath: pathlib.Path, *, traverse=True) -> int:
        def collect_taglist_names(fpath: pathlib.Path, paths_dict: dict[str, pathlib.Path]) -> None:
            for module in MODULE_CHOICES:
                taglist_path = fpath / f'{module}_tags.json'
                if taglist_path.is_file():
                    paths_dict[module] = taglist_path

        def collect_aux_file_names(fpath: pathlib.Path) -> None:
            tag_aliases_path = fpath / 'all_tag_aliases.json'
            if tag_aliases_path.is_file():
                TagsDB.AuxDBFiles[FILE_NAME_ALIASES] = tag_aliases_path

        folder = pathlib.Path(__file__).resolve().parent.parent
        TagsDB.clear()
        while not TagsDB.DBFiles:
            folder_up, tail = folder.parent, folder.name
            for folder_path in (basepath, basepath / 'tags', basepath / '2tags'):
                if folder_path.is_dir():
                    tlpaths: dict[str, pathlib.Path] = {}
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
        if filepath := TagsDB.AuxDBFiles.get(filename, pathlib.Path()):
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
            trace(format_exception('full'))
            trace(f'Error: Failed to load tag aliases from {TagsDB.AuxDBFiles.get(FILE_NAME_ALIASES, FILE_NAME_ALIASES)}')
            TAG_ALIASES.update({'': ''})

#
#
#########################################
