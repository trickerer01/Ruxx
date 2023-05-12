# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from os import path, rename as rename_file, listdir
from re import fullmatch
from typing import Tuple, Pattern, Dict

# internal
from app_defines import DEFAULT_ENCODING, FILE_NAME_FULL_MAX_LEN
from app_gui_defines import SLASH, UNDERSCORE
from app_tagger import append_filtered_tags
from app_utils import trim_undersores, normalize_path

__all__ = ('untag_files', 'retag_files')


def untag_files(files: Tuple[str]) -> int:
    untagged_count = 0
    try:
        for full_path in files:
            base_path, full_name = path.split(normalize_path(full_path, False))
            fname_match = fullmatch(r'^([a-z]{2}_)?(\d+?)[_.].+?$', full_name)
            if fname_match is None:
                continue
            _, ext = path.splitext(full_name)
            untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
            rename_file(full_path, f'{base_path}{SLASH}{untagged_name_noext}{ext}')
            untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files(files: Tuple[str], re_tags_to_process: Pattern, re_tags_to_exclude: Pattern) -> int:
    retagged_count = 0
    try:
        base_path = path.split(normalize_path(files[0], False))[0]
        tagdict = dict()  # type: Dict[str, str]
        for diritem in listdir(base_path):
            if path.splitext(diritem)[1] == '.txt':
                if fullmatch(r'^[a-z]{2}_!tags_\d+?-\d+?\.txt$', diritem) is not None:
                    with open(f'{base_path}{SLASH}{diritem}', 'rt', encoding=DEFAULT_ENCODING) as tags_file:
                        lines = tags_file.readlines()
                    for line in lines:
                        line = line.strip(' \n\ufeff')
                        if len(line) > 1:
                            parts = line.split(': ', 1)
                            tagdict[parts[0][3:]] = parts[1]

        assert len(tagdict) > 0

        for full_path in files:
            base_path, full_name = path.split(normalize_path(full_path, False))
            name, ext = path.splitext(full_name)
            tags = tagdict.get(name[3:] if name[0].isalpha() else name)
            if tags is None:
                continue
            fname_match = fullmatch(r'^([a-z]{2}_)?(\d+?)[.].+?$', full_name)
            if fname_match is None:
                continue
            maxlen = FILE_NAME_FULL_MAX_LEN - len(full_path)
            untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
            score_str, tags_rest = tuple(tags.split(' ', 1))
            add_str = append_filtered_tags(score_str, tags_rest, re_tags_to_process, re_tags_to_exclude)
            new_name = trim_undersores(f'{untagged_name_noext}{UNDERSCORE}{add_str if len(add_str) <= maxlen else add_str[:maxlen]}')
            rename_file(full_path, f'{base_path}{SLASH}{new_name}{ext}')
            retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
