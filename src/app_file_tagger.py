# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from os import path, rename as rename_file, listdir
from re import fullmatch as re_fullmatch, sub as re_sub
from typing import Tuple, Pattern, Dict, List

# internal
from app_defines import DEFAULT_ENCODING, FILE_NAME_FULL_MAX_LEN
from app_gui_defines import SLASH, UNDERSCORE
from app_tagger import append_filtered_tags
from app_utils import trim_undersores


def untag_files(files: Tuple[str]) -> int:
    untagged_count = 0
    try:
        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            base_path, full_name = tuple(full_path.rsplit(SLASH, 1))
            if not re_fullmatch(r'^(?:[a-z]{2}_)?(?:\d+?)[_].+?$', full_name):
                continue
            name, ext = path.splitext(full_name)
            untagged_name = re_sub(r'^([a-z]{2}_)?(\d+?)[_.].+?$', r'\1\2', name)
            new_name = f'{base_path}{SLASH}{untagged_name}{ext}'
            rename_file(full_path, new_name)
            untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files(files: Tuple[str], re_tags_to_process: Pattern, re_tags_to_exclude: Pattern) -> int:
    retagged_count = 0
    try:
        tagfiles_lines_full = []  # type: List[Tuple[str, str]]
        full_path = files[0].replace('\\', SLASH)
        base_path = full_path[:full_path.rfind(SLASH)]
        curdirfiles = list(listdir(base_path))
        for f in curdirfiles:
            if re_fullmatch(r'^[a-z]{2}_!tags_\d+?-\d+?\.txt$', f):
                with open(f'{base_path}{SLASH}{f}', 'rt', encoding=DEFAULT_ENCODING) as fo:
                    tagfiles_lines_full.extend({tuple(a.strip().split(': ', 1)) for a in fo.readlines() if len(a) > 1})

        tagdict = {v[0][3:]: v[1] for v in tagfiles_lines_full}  # type: Dict[str, str]

        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            base_path, full_name = tuple(full_path.rsplit(SLASH, 1))
            name, ext = path.splitext(full_name)
            maxlen = FILE_NAME_FULL_MAX_LEN - len(full_path)
            if not re_fullmatch(r'^(?:[a-z]{2}_)?(?:\d+?)[.].+?$', full_name):
                continue
            untagged_name_noext = re_sub(r'^([a-z]{2}_)?(\d+?)[_.].+?$', r'\1\2', name)
            try:
                tags = tagdict[name[3:] if name[0].isalpha() else name]
            except Exception:
                continue
            score_str, tags_rest = tuple(tags.split(' ', 1))
            add_str = append_filtered_tags(score_str, tags_rest, re_tags_to_process, re_tags_to_exclude)
            new_name = trim_undersores(f'{untagged_name_noext}{UNDERSCORE}{add_str if len(add_str) <= maxlen else add_str[:maxlen]}')
            new_name = f'{base_path}{SLASH}{new_name}{ext}'
            rename_file(full_path, new_name)
            retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
