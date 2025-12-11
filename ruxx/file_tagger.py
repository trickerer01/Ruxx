# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import os
import pathlib
import re
from collections.abc import Iterable, Sequence

from .defines import FILE_NAME_FULL_MAX_LEN, UTF8
from .gui_defines import UNDERSCORE
from .tagger import append_filtered_tags
from .tagsdb import load_tag_aliases
from .utils import trim_underscores

__all__ = ('retag_files', 'untag_files')


def untag_files(files: Iterable[pathlib.Path]) -> int:
    untagged_count = 0
    try:
        re_media_tagged_name = re.compile(r'^([a-z]{2}_)?(\d+?)[_.].+?$')
        for full_path in files:
            if fname_match := re_media_tagged_name.fullmatch(full_path.name):
                untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                full_path.rename(full_path.parent / f'{untagged_name_noext}{full_path.suffix}')
                untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files(files: Sequence[pathlib.Path], re_tags_to_process: re.Pattern, re_tags_to_exclude: re.Pattern) -> int:
    retagged_count = 0
    try:
        re_media_untagged_name = re.compile(r'^([a-z]{2}_)?(\d+?)[.].+?$')
        re_tagsfile_name = re.compile(r'^[a-z]{2}_!tags_\d+?-\d+?\.txt$')
        base_path = files[0].parent
        tagdict: dict[str, str] = {}
        with os.scandir(base_path.as_posix()) as listing:
            for dentry in listing:
                if dentry.is_file():
                    if os.path.splitext(dentry.name)[1] == '.txt':
                        if re_tagsfile_name.fullmatch(dentry.name):
                            with open(base_path / dentry.name, 'rt', encoding=UTF8) as tags_file:
                                for line in tags_file:
                                    line = line.strip(' \n\ufeff')
                                    if len(line) > 1:
                                        parts = line.split(': ', 1)
                                        tagdict[parts[0][3:]] = parts[1]

        assert len(tagdict) > 0
        load_tag_aliases()

        for full_path in files:
            name = full_path.with_suffix('').name
            tags = tagdict.get(name[3:] if name[0].isalpha() else name)
            if fname_match := re_media_untagged_name.fullmatch(full_path.name) if tags else None:
                maxlen = FILE_NAME_FULL_MAX_LEN - len(full_path.as_posix())
                untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                score_str, tags_rest = tuple(tags.split(' ', 1))
                add_str = append_filtered_tags(score_str, tags_rest, re_tags_to_process, re_tags_to_exclude)
                new_name = trim_underscores(f'{untagged_name_noext}{UNDERSCORE}{add_str if len(add_str) <= maxlen else add_str[:maxlen]}')
                full_path.rename(base_path / f'{new_name}{full_path.suffix}')
                retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
