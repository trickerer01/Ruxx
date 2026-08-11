# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import pathlib
import re
from collections.abc import Iterable, Sequence

from .defines import FILE_NAME_FULL_MAX_LEN, MODULE_CHOICES, ItemInfo
from .tagger import append_filtered_tags, append_filtered_tags_by_type
from .tags import TagTypes
from .tagsdb import TagsDB, load_tag_aliases
from .utils import format_score, trim_underscores

__all__ = ('retag_files_any', 'retag_files_tagtype', 'untag_files')


def untag_files(files: Iterable[pathlib.Path]) -> int:
    untagged_count = 0
    try:
        re_media_tagged_name = re.compile(r'^([a-z]{2}_)?(\d+)[_.].+?$')
        for full_path in files:
            if fname_match := re_media_tagged_name.fullmatch(full_path.name):
                untagged_name_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                full_path.rename(full_path.parent / f'{untagged_name_noext}{full_path.suffix}')
                untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files_any(files: Sequence[pathlib.Path], infos: dict[str, ItemInfo], re_process: re.Pattern, re_exclude: re.Pattern) -> int:
    retagged_count = 0
    try:
        if not infos:
            return -1
        re_media_untagged_name = re.compile(r'^([a-z]{2}_)?(\d+).*?$')
        base_path = files[0].parent
        load_tag_aliases()
        for fpath in files:
            name = fpath.with_suffix('').name
            fname_match = re_media_untagged_name.fullmatch(name)
            if not fname_match:
                continue
            item_info = infos.get(name[3:] if name[0].isalpha() else name)
            tags_str = item_info.tags if item_info else ''
            score_str = format_score(item_info.score) if item_info else ''
            if tags_str or score_str:
                maxlen = FILE_NAME_FULL_MAX_LEN - len(fpath.as_posix())
                name_notags_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                add_str = append_filtered_tags(score_str, tags_str, re_process, re_exclude)
                new_name = trim_underscores(f'{name_notags_noext}_{add_str[:maxlen]}{fpath.suffix}')
                fpath.rename(base_path / new_name)
                retagged_count += 1
    except Exception:
        pass

    return retagged_count


def retag_files_tagtype(files: Sequence[pathlib.Path], infos: dict[str, ItemInfo], *tag_types: TagTypes) -> int:
    retagged_count = 0
    try:
        if not infos:
            return -1
        if TagsDB.is_empty():
            return -2
        re_media_untagged_name = re.compile(r'^([a-z]{2}_)?(\d+).*?$')
        base_path = files[0].parent
        for fpath in files:
            name = fpath.with_suffix('').name
            fname_match = re_media_untagged_name.fullmatch(name)
            if not fname_match:
                continue
            module = name[:2]
            if module not in MODULE_CHOICES:
                continue
            item_info = infos.get(name[3:] if name[0].isalpha() else name)
            tags_str = item_info.tags if item_info else ''
            score_str = format_score(item_info.score) if item_info else ''
            if tags_str or score_str:
                maxlen = FILE_NAME_FULL_MAX_LEN - len(fpath.as_posix())
                name_notags_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                add_str = append_filtered_tags_by_type(score_str, tags_str, module, *tag_types)
                new_name = trim_underscores(f'{name_notags_noext}_{add_str[:maxlen]}{fpath.suffix}')
                fpath.rename(base_path / new_name)
                retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
