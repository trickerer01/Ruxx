# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import re

from app_gui_defines import UNDERSCORE
from app_re import (
    re_meta_group,
    re_not_a_letter,
    re_numbered_or_counted_tag,
    re_replace_symbols,
    re_tags_exclude_major1,
    re_tags_exclude_major2,
)
from app_tagsdb import TAG_ALIASES
from app_utils import trim_underscores

__all__ = ('append_filtered_tags', 'no_validation_tag', 'normalize_wtag')


# unused
def no_validation_tag(tag: str) -> str:
    return tag[1:-1] if len(tag) > 2 and f'{tag[0]}{tag[-1]}' == '%%' else ''


# unused
def normalize_wtag(wtag: str) -> str:
    return wtag.replace('*', '.*').replace('?', '.')


def append_filtered_tags(base_string: str, tags_str: str, re_tags_to_process: re.Pattern, re_tags_to_exclude: re.Pattern) -> str:
    if not tags_str:
        return base_string

    tags_list = tags_str.split(' ')
    tags_toadd_list: list[str] = []

    for tag in tags_list:
        tag = tag.replace('-', '').replace('\'', '')
        if tag not in TAG_ALIASES and not re_tags_to_process.fullmatch(tag):
            continue

        # digital_media_(artwork)
        aser_valid = False
        if aser_match := re_meta_group.fullmatch(tag):
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
        if alias := TAG_ALIASES.get(tag):
            tag = alias

        if re_tags_to_exclude.fullmatch(tag):
            continue

        do_add = True
        if tags_toadd_list:
            nutag = re_not_a_letter.sub('', re_numbered_or_counted_tag.sub(r'\1', tag))
            # try and see
            # 1) if this tag can be consumed by existing tags
            # 2) if this tag can consume existing tags
            for i in reversed(range(len(tags_toadd_list))):
                t = re_numbered_or_counted_tag.sub(r'\1', tags_toadd_list[i].lower())
                nut = re_not_a_letter.sub('', t)
                if len(nut) >= len(nutag) and nutag in nut:
                    do_add = False
                    break
            if do_add:
                for i in reversed(range(len(tags_toadd_list))):
                    t = re_numbered_or_counted_tag.sub(r'\1', tags_toadd_list[i].lower())
                    nut = re_not_a_letter.sub('', t)
                    if 1 < len(nut) <= len(nutag) and nut in nutag:
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

#
#
#########################################
