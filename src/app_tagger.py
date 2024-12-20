# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
from collections.abc import Callable
from json import load as load_json
from os import path
from re import Pattern, compile as re_compile

# internal
from app_defines import MODULE_CHOICES, TAG_AUTOCOMPLETE_LENGTH_MIN, TAG_AUTOCOMPLETE_NUMBER_MAX, UTF8, FILE_NAME_ALIASES
from app_gui_defines import UNDERSCORE
from app_logger import trace
from app_re import re_replace_symbols, re_tags_exclude_major1, re_tags_exclude_major2, re_numbered_or_counted_tag
from app_utils import trim_undersores, normalize_path

__all__ = ('TagsDB', 'append_filtered_tags', 'is_wtag', 'normalize_wtag', 'no_validation_tag')

TAG_ALIASES: dict[str, str] = dict()

re_meta_group = re_compile(r'^([^(]+)\(([^)]+)\).*?$')
re_not_a_letter = re_compile(r'[^a-z]+')
re_wtag = re_compile(r'^(?:[^?*]*[?*]).*?$')


class TagsDB:
    DB: dict[str, dict[str, int]] = dict()
    DBFiles: dict[str, str] = dict()

    @staticmethod
    def try_locate_file_single(filename: str) -> str:
        basepath = normalize_path(path.abspath(f'{path.dirname(__file__)}/..'), False)
        for folder_path in (f'{basepath}/', f'{basepath}/tags/', f'{basepath}/2tags/'):
            pfilename = f'{folder_path}{filename}'
            if path.isfile(pfilename):
                return pfilename
        return filename

    @staticmethod
    def try_set_basepath(basepath: str, *, traverse=True) -> int:
        def collect_taglist_names(fpath: str, paths_dict: dict[str, str]) -> None:
            for module in MODULE_CHOICES:
                taglist_path = f'{fpath}{module}_tags.json'
                if path.isfile(taglist_path):
                    paths_dict[module] = taglist_path

        folder = normalize_path(basepath or path.abspath(f'{path.dirname(__file__)}/..'), False)
        TagsDB.clear()
        while not TagsDB.DBFiles:
            folder_up, tail = tuple(path.split(folder))
            for folder_path in (f'{folder}/', f'{folder}/tags/', f'{folder}/2tags/'):
                if path.isdir(folder_path):
                    tlpaths: dict[str, str] = dict()
                    collect_taglist_names(folder_path, tlpaths)
                    if tlpaths:
                        TagsDB.DBFiles.update(tlpaths)
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
        TagsDB.DB[module] = dict()
        try:
            with open(TagsDB.DBFiles.get(module, ''), 'rt', encoding=UTF8) as dbfile:
                lines = dbfile.readlines()
                for idx, line in enumerate(lines):
                    try:
                        kv_k, kv_v = tuple(line.strip(' ,"\n\ufeff').split('": "', 1))
                        ivalue = int(kv_v[:kv_v.find(' ')])
                        TagsDB.DB[module][kv_k] = ivalue
                    except Exception:
                        continue
        except FileNotFoundError:
            return

    @staticmethod
    def _get_tag_matches(module: str, value: str, pred: Callable[[str, str], bool], limit: int) -> list[tuple[str, int]]:
        arr = list(TagsDB.DB[module].keys())
        lb, ub = 0, len(arr)
        if not is_wtag(value):
            while lb < ub:
                mid = (lb + ub) // 2
                if arr[mid] < value:
                    lb = mid + 1
                else:
                    ub = mid
        ub = len(arr)
        gmatches: list[str] = list()
        while lb < ub:
            limit_reached = limit > 0 and len(gmatches) >= limit * 5
            if limit_reached or not pred(arr[lb], value):
                if limit_reached:
                    break
                else:
                    lb += 1
                    continue
            gmatches.append(arr[lb])
            lb += 1
        glist = [(g, TagsDB.DB[module][g]) for g in sorted(gmatches, reverse=True, key=lambda gmatch: TagsDB.DB[module][gmatch])]
        return glist[:limit] if limit > 0 else glist

    @staticmethod
    def autocomplete_tag(module: str, tag: str, *,
                         pred: Callable[[str, str], bool] = lambda x, y: x.startswith(y),
                         limit: int = None) -> list[tuple[str, int]]:
        matches = list()
        if len(tag) >= TAG_AUTOCOMPLETE_LENGTH_MIN or limit is None:
            limit = limit or TAG_AUTOCOMPLETE_NUMBER_MAX
            TagsDB._load(module)
            base_matches = TagsDB._get_tag_matches(module, tag, pred, limit)
            if limit > 0:
                matches.extend((mtag[len(tag):], count) for mtag, count in base_matches)
            else:
                matches.extend(base_matches)
        return matches


def no_validation_tag(tag: str) -> str:
    return tag[1:-1] if len(tag) > 2 and f'{tag[0]}{tag[-1]}' == '%%' else ''


def is_wtag(tag: str) -> bool:
    return not not re_wtag.fullmatch(tag)


def normalize_wtag(wtag: str) -> str:
    return wtag.replace('*', '.*').replace('?', '.')


def append_filtered_tags(base_string: str, tags_str: str, re_tags_to_process: Pattern, re_tags_to_exclude: Pattern) -> str:
    if len(tags_str) == 0:
        return base_string

    if not TAG_ALIASES:
        load_tag_aliases()

    tags_list = tags_str.split(' ')
    tags_toadd_list: list[str] = list()

    for tag in tags_list:
        tag = tag.replace('-', '').replace('\'', '')
        if TAG_ALIASES.get(tag) is None and re_tags_to_process.fullmatch(tag) is None:
            continue

        # digital_media_(artwork)
        aser_match = re_meta_group.fullmatch(tag)
        aser_valid = False
        if aser_match:
            major_skip_match1 = re_tags_exclude_major1.fullmatch(aser_match.group(1))
            major_skip_match2 = re_tags_exclude_major2.fullmatch(aser_match.group(2))
            if major_skip_match1 or major_skip_match2:
                continue
            stag = trim_undersores(aser_match.group(1))
            if len(stag) >= 14:
                continue
            tag = stag
            aser_valid = True

        tag = trim_undersores(tag)
        alias = TAG_ALIASES.get(tag)
        if alias:
            tag = alias

        if re_tags_to_exclude.fullmatch(tag):
            continue

        do_add = True
        if len(tags_toadd_list) > 0:
            nutag = re_not_a_letter.sub('', re_numbered_or_counted_tag.sub(r'\1', tag))
            # try and see
            # 1) if this tag can be consumed by existing tags
            # 2) if this tag can consume existing tags
            for i in reversed(range(len(tags_toadd_list))):
                t = re_numbered_or_counted_tag.sub(r'\1', tags_toadd_list[i].lower())
                nut = re_not_a_letter.sub('', t)
                if len(nut) >= len(nutag) and (nutag in nut):
                    do_add = False
                    break
            if do_add:
                for i in reversed(range(len(tags_toadd_list))):
                    t = re_numbered_or_counted_tag.sub(r'\1', tags_toadd_list[i].lower())
                    nut = re_not_a_letter.sub('', t)
                    if len(nutag) >= len(nut) and (nut in nutag):
                        if aser_valid is False and tags_toadd_list[i][0].isupper():
                            aser_valid = True
                        del tags_toadd_list[i]
        if do_add:
            if aser_valid:
                i: int
                c: str
                for i, c in enumerate(tag):
                    if (i == 0 or tag[i - 1] == UNDERSCORE) and c.isalpha():
                        tag = f'{tag[:i]}{c.upper()}{tag[i + 1:]}'
            tags_toadd_list.append(tag)

    return f'{base_string}{UNDERSCORE}{re_replace_symbols.sub(UNDERSCORE, UNDERSCORE.join(sorted(tags_toadd_list)))}'


def load_tag_aliases() -> None:
    file_location = TagsDB.try_locate_file_single(FILE_NAME_ALIASES)
    try:
        trace('Loading tag aliases...')
        with open(file_location, 'r', encoding=UTF8) as aliases_json_file:
            TAG_ALIASES.update(load_json(aliases_json_file))
    except Exception:
        trace(f'Error: Failed to load tag aliases from {file_location}')
        TAG_ALIASES.update({'': ''})

#
#
#########################################
