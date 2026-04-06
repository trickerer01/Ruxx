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

from .defines import FILE_NAME_FULL_MAX_LEN, ItemInfo
from .file_parser import prepare_item_infos_dict
from .rex import re_infolist_filename
from .tagger import append_filtered_tags
from .tagsdb import load_tag_aliases
from .utils import format_score, trim_underscores

__all__ = ('retag_files', 'untag_files')


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


def retag_files(files: Sequence[pathlib.Path], re_tags_to_process: re.Pattern, re_tags_to_exclude: re.Pattern) -> int:
    retagged_count = 0
    try:
        re_media_untagged_name = re.compile(r'^([a-z]{2}_)?(\d+).+?$')
        base_path = files[0].parent
        item_infos_all: dict[str, ItemInfo] = {}
        with os.scandir(base_path.as_posix()) as listing:
            for dentry in listing:
                if dentry.is_file() and re_infolist_filename.fullmatch(dentry.name):
                    suc, item_infos = prepare_item_infos_dict(pathlib.Path(dentry.path), '')
                    if suc:
                        item_infos_all.update(item_infos)
        assert len(item_infos_all) > 0
        load_tag_aliases()

        for fpath in files:
            name = fpath.with_suffix('').name
            fname_match = re_media_untagged_name.fullmatch(name)
            if not fname_match:
                continue
            item_info = item_infos_all.get(name[3:] if name[0].isalpha() else name)
            tags_str = item_info.tags if item_info else ''
            score_str = format_score(item_info.score) if item_info else ''
            if tags_str or score_str:
                maxlen = FILE_NAME_FULL_MAX_LEN - len(fpath.as_posix())
                name_notags_noext = f'{fname_match.group(1) or ""}{fname_match.group(2)}'
                add_str = append_filtered_tags(score_str, tags_str, re_tags_to_process, re_tags_to_exclude)
                new_name = trim_underscores(f'{name_notags_noext}_{add_str[:maxlen]}{fpath.suffix}')
                fpath.rename(base_path / new_name)
                retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
