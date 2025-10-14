# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import json
import os
import re

# internal
from app_defines import FILE_NAME_ALIASES, MODULE_CHOICES, TAG_AUTOCOMPLETE_LENGTH_MIN, TAG_AUTOCOMPLETE_NUMBER_MAX, UTF8
from app_gui_defines import UNDERSCORE
from app_logger import trace
from app_re import re_numbered_or_counted_tag, re_replace_symbols, re_tags_exclude_major1, re_tags_exclude_major2
from app_utils import normalize_path, trim_underscores

__all__ = ('TagsDB', 'append_filtered_tags', 'is_wtag', 'load_tag_aliases', 'no_validation_tag', 'normalize_wtag')

TAG_ALIASES: dict[str, str] = {}

re_meta_group = re.compile(r'^([^(]+)\(([^)]+)\).*?$')
re_not_a_letter = re.compile(r'[^a-z]+')
re_wtag = re.compile(r'^(?:[^?*]*[?*]).*?$')


class TagsDB:
    DB: dict[str, dict[str, int]] = {}
    DBFiles: dict[str, str] = {}
    AuxDB: dict[str, dict[str, str]] = {}
    AuxDBFiles: dict[str, str] = {}

    @staticmethod
    def try_locate_file_single(filename: str) -> None:
        if filename in TagsDB.AuxDBFiles:
            return
        acwd = os.path.abspath(os.getcwd())
        afld = os.path.abspath(os.path.dirname(__file__))
        trace(f'cwd: \'{acwd}\'')
        trace(f'fld: \'{afld}\'')
        if os.path.basename(acwd) == 'src':
            acwd = os.path.abspath(f'{acwd}/..')
        if os.path.basename(afld) == 'src':
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
                lines = dbfile.readlines()
                for _idx, line in enumerate(lines):
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
        gmatches = list[str]()
        while lb < len(arr) and arr[lb].startswith(tag):
            gmatches.append(arr[lb])
            lb += 1
        glist = [(g, TagsDB.DB[module][g]) for g in sorted(gmatches, reverse=True, key=lambda gmatch: TagsDB.DB[module][gmatch])]
        return glist

    @staticmethod
    def autocomplete_tag(module: str, tag: str) -> list[tuple[str, int]]:
        matches = []
        if not is_wtag(tag) and len(tag) >= TAG_AUTOCOMPLETE_LENGTH_MIN:
            TagsDB._load(module)
            base_matches = TagsDB._get_tag_matches(module, tag)
            matches.extend((mtag[len(tag):], count) for mtag, count in base_matches[:TAG_AUTOCOMPLETE_NUMBER_MAX])
        return matches

    @staticmethod
    def load_aux_file(filename: str, dest: dict[str, str]) -> None:
        assert filename not in TagsDB.AuxDB
        filepath = TagsDB.AuxDBFiles.get(filename, '')
        with open(filepath, 'rt', encoding=UTF8) as auxfile:
            dest.update(json.load(auxfile))
            TagsDB.AuxDB[filename] = filepath


def no_validation_tag(tag: str) -> str:
    return tag[1:-1] if len(tag) > 2 and f'{tag[0]}{tag[-1]}' == '%%' else ''


def is_wtag(tag: str) -> bool:
    return bool(re_wtag.fullmatch(tag))


def normalize_wtag(wtag: str) -> str:
    return wtag.replace('*', '.*').replace('?', '.')


def append_filtered_tags(base_string: str, tags_str: str, re_tags_to_process: re.Pattern, re_tags_to_exclude: re.Pattern) -> str:
    if len(tags_str) == 0:
        return base_string

    tags_list = tags_str.split(' ')
    tags_toadd_list: list[str] = []

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
            stag = trim_underscores(aser_match.group(1))
            if len(stag) >= 14:
                continue
            tag = stag
            aser_valid = True

        tag = trim_underscores(tag)
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
                    if 1 < len(nut) <= len(nutag) and (nut in nutag):
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
    if TAG_ALIASES:
        return

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
