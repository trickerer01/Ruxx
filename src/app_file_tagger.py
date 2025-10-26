# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import os
import re
from collections.abc import Iterable, Sequence

# internal
from app_defines import FILE_NAME_FULL_MAX_LEN, UTF8
from app_gui_defines import SLASH, UNDERSCORE
from app_tagger import append_filtered_tags, load_tag_aliases
from app_utils import normalize_path, trim_underscores

__all__ = ('retag_files', 'untag_files')


def untag_files(files: Iterable[str]) -> int:
    untagged_count = 0
    try:
        re_media_tagged_name = re.compile(r'^([a-z]{2}_)?(\d+?)[_.].+?$')
        for full_path in files:
            base_path, full_name = os.path.split(normalize_path(full_path, False))
            fname_match = re_media_tagged_name.fullmatch(full_name)
            if fname_match is None:
                continue
            _, ext = os.path.splitext(full_name)
            untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
            os.rename(full_path, f'{base_path}{SLASH}{untagged_name_noext}{ext}')
            untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files(files: Sequence[str], re_tags_to_process: re.Pattern, re_tags_to_exclude: re.Pattern) -> int:
    retagged_count = 0
    try:
        re_media_untagged_name = re.compile(r'^([a-z]{2}_)?(\d+?)[.].+?$')
        re_tagsfile_name = re.compile(r'^[a-z]{2}_!tags_\d+?-\d+?\.txt$')
        base_path = os.path.split(normalize_path(files[0], False))[0]
        tagdict = dict[str, str]()
        dentry: os.DirEntry
        for dentry in os.scandir(base_path):
            if not dentry.is_file():
                continue
            if os.path.splitext(dentry.name)[1] == '.txt':
                if re_tagsfile_name.fullmatch(dentry.name) is not None:
                    with open(f'{base_path}{SLASH}{dentry.name}', 'rt', encoding=UTF8) as tags_file:
                        for line in tags_file:
                            line = line.strip(' \n\ufeff')
                            if len(line) > 1:
                                parts = line.split(': ', 1)
                                tagdict[parts[0][3:]] = parts[1]

        assert len(tagdict) > 0

        load_tag_aliases()

        for full_path in files:
            base_path, full_name = os.path.split(normalize_path(full_path, False))
            name, ext = os.path.splitext(full_name)
            tags = tagdict.get(name[3:] if name[0].isalpha() else name)
            if tags is None:
                continue
            fname_match = re_media_untagged_name.fullmatch(full_name)
            if fname_match is None:
                continue
            maxlen = FILE_NAME_FULL_MAX_LEN - len(full_path)
            untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
            score_str, tags_rest = tuple(tags.split(' ', 1))
            add_str = append_filtered_tags(score_str, tags_rest, re_tags_to_process, re_tags_to_exclude)
            new_name = trim_underscores(f'{untagged_name_noext}{UNDERSCORE}{add_str if len(add_str) <= maxlen else add_str[:maxlen]}')
            os.rename(full_path, f'{base_path}{SLASH}{new_name}{ext}')
            retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
