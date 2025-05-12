# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
from collections.abc import Sequence
from re import Pattern, compile as re_compile

# requirements
from iteration_utilities import unique_everseen

# internal
from app_module import ProcModule
from app_re import re_space_mult, re_favorited_by_tag, re_pool_tag

__all__ = ('reset_last_tags', 'parse_tags', 'convert_taglist')

DEFAULT_TAGS = ('sfw',)

# language=PythonRegExp
TAG_CHAR = r'[a-zÀ-ʯА-яぁ-㋾･-ﾟ一-鿿\d_%+\-/!()*\'.]'
# language=PythonRegExp
META_CHAR = r'[a-z\d_\-.]'
# language=PythonRegExp
META_COUNT_RX = r':(?:(?:[<>]=?|=)?[a-z\d\-_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_COUNT_RN = r'(?:[<>]=?|=)[a-z\d\-_]+?'
# language=PythonRegExp
META_COUNT_RS = r':(?:(?:[<>]=?|=)?[a-z\d\-_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_COUNT_RP = r'(?:[<>]=?|=)[a-z\d\-_]+?'
# language=PythonRegExp
META_COUNT_EN = r':(?:[<>]=?|!)?[a-z\d\-_.]+?'
# language=PythonRegExp
META_COUNT_XB = r':(?:(?:[<>]=?|=)?[a-z\d\-_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_COUNT_BB = r':(?:(?:[<>]=?|=)?[a-z\d\-_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_SORT_RX = r'sort(?::[^:]+?){1,2}'
# language=PythonRegExp
META_SORT_RN = r'order=(?:id|score)_desc'
# language=PythonRegExp
META_SORT_RS = r'sort(?::[^:]+?){1,2}'
"""not supported"""
# language=PythonRegExp
META_SORT_RP = r'order=(?:id|score)_desc'
# language=PythonRegExp
META_SORT_EN = r'order:[^:]+(?:_(?:a|de)sc)?'
# language=PythonRegExp
META_SORT_XB = r'sort(?::[^:]+?){1,2}'
# language=PythonRegExp
META_SORT_BB = r'sort(?::[^:]+?){1,2}'
# language=PythonRegExp
META_FAV_RX = r'favorited_by:\d+?'
# language=PythonRegExp
META_FAV_RN = r'favorited_by=[^:=]+?'
# language=PythonRegExp
META_FAV_RS = r'favorited_by:\d+?'
# language=PythonRegExp
META_FAV_RP = r'favorited_by=[^:=]+?'
# language=PythonRegExp
META_FAV_EN = r'favorited_by:(?:!\d+?|[^!][^:]+?)'
# language=PythonRegExp
META_FAV_XB = r'favorited_by:\d+?'
# language=PythonRegExp
META_FAV_BB = r'favorited_by:\d+?'
# language=PythonRegExp
META_POOL_RX = r'pool:\d+?'
# language=PythonRegExp
META_POOL_RN = r''
"""not supported"""
# language=PythonRegExp
META_POOL_RS = r''
"""not supported"""
# language=PythonRegExp
META_POOL_RP = r''
"""not supported"""
# language=PythonRegExp
META_POOL_EN = r'(?:pool|set):[^:]+?'
# language=PythonRegExp
META_POOL_XB = r'pool:\d+?'
# language=PythonRegExp
META_POOL_BB = r'pool:\d+?'
# language=PythonRegExp
RE_ORGR_PART_RX = fr'{TAG_CHAR}+?(?:{META_COUNT_RX})?'
# language=PythonRegExp
RE_ORGR_PART_RN = fr'{TAG_CHAR}+?(?:{META_COUNT_RN})?'
# language=PythonRegExp
RE_ORGR_PART_RS = fr'{TAG_CHAR}+?(?:{META_COUNT_RS})?'
# language=PythonRegExp
RE_ORGR_PART_RP = fr'{TAG_CHAR}+?(?:{META_COUNT_RP})?'
# language=PythonRegExp
RE_ORGR_PART_EN = fr'{TAG_CHAR}+?(?:{META_COUNT_EN})?'
# language=PythonRegExp
RE_ORGR_PART_XB = fr'{TAG_CHAR}+?(?:{META_COUNT_XB})?'
# language=PythonRegExp
RE_ORGR_PART_BB = fr'{TAG_CHAR}+?(?:{META_COUNT_XB})?'

# language=PythonRegExp
ANDGR_CHAR = r'[a-zÀ-ʯА-я\d_+\-/!()*\'.|?]'
# language=PythonRegExp
RE_ANDGR_PART_U = fr'{ANDGR_CHAR}+?'

re_plains = {
    ProcModule.RX: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.RN: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.RS: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.RP: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.EN: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.XB: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.BB: re_compile(fr'^-?{TAG_CHAR}+?$'),
}
re_metas = {
    ProcModule.RX: re_compile(fr'^{META_CHAR}+?{META_COUNT_RX}$'),
    ProcModule.RN: re_compile(fr'^{META_CHAR}+?{META_COUNT_RN}$'),
    ProcModule.RS: re_compile(fr'^{META_CHAR}+?{META_COUNT_RS}$'),
    ProcModule.RP: re_compile(fr'^{META_CHAR}+?{META_COUNT_RP}$'),
    ProcModule.EN: re_compile(fr'^{META_CHAR}+?{META_COUNT_EN}$'),
    ProcModule.XB: re_compile(fr'^{META_CHAR}+?{META_COUNT_XB}$'),
    ProcModule.BB: re_compile(fr'^{META_CHAR}+?{META_COUNT_BB}$'),
}
re_sorts = {
    ProcModule.RX: re_compile(fr'^{META_SORT_RX}$'),
    ProcModule.RN: re_compile(fr'^{META_SORT_RN}$'),
    ProcModule.RS: re_compile(fr'^{META_SORT_RS}$'),
    ProcModule.RP: re_compile(fr'^{META_SORT_RP}$'),
    ProcModule.EN: re_compile(fr'^{META_SORT_EN}$'),
    ProcModule.XB: re_compile(fr'^{META_SORT_XB}$'),
    ProcModule.BB: re_compile(fr'^{META_SORT_BB}$'),
}
re_favs = {
    ProcModule.RX: re_compile(fr'^{META_FAV_RX}$'),
    ProcModule.RN: re_compile(fr'^{META_FAV_RN}$'),
    ProcModule.RS: re_compile(fr'^{META_FAV_RS}$'),
    ProcModule.RP: re_compile(fr'^{META_FAV_RP}$'),
    ProcModule.EN: re_compile(fr'^{META_FAV_EN}$'),
    ProcModule.XB: re_compile(fr'^{META_FAV_XB}$'),
    ProcModule.BB: re_compile(fr'^{META_FAV_BB}$'),
}
re_pools = {
    ProcModule.RX: re_compile(fr'^{META_POOL_RX}$'),
    ProcModule.RN: re_compile(fr'^{META_POOL_RN}$'),
    ProcModule.RS: re_compile(fr'^{META_POOL_RS}$'),
    ProcModule.RP: re_compile(fr'^{META_POOL_RP}$'),
    ProcModule.EN: re_compile(fr'^{META_POOL_EN}$'),
    ProcModule.XB: re_compile(fr'^{META_POOL_XB}$'),
    ProcModule.BB: re_compile(fr'^{META_POOL_BB}$'),
}
re_orgrs_full = {
    ProcModule.RX: re_compile(fr'^\((?:{RE_ORGR_PART_RX})(?:~{RE_ORGR_PART_RX})+?\)$'),
    ProcModule.RN: re_compile(fr'^\((?:{RE_ORGR_PART_RN})(?:~{RE_ORGR_PART_RN})+?\)$'),
    ProcModule.RS: re_compile(fr'^\((?:{RE_ORGR_PART_RS})(?:~{RE_ORGR_PART_RS})+?\)$'),
    ProcModule.RP: re_compile(fr'^\((?:{RE_ORGR_PART_RP})(?:~{RE_ORGR_PART_RP})+?\)$'),
    ProcModule.EN: re_compile(fr'^\((?:{RE_ORGR_PART_EN})(?:~{RE_ORGR_PART_EN})+?\)$'),
    ProcModule.XB: re_compile(fr'^\((?:{RE_ORGR_PART_XB})(?:~{RE_ORGR_PART_XB})+?\)$'),
    ProcModule.BB: re_compile(fr'^\((?:{RE_ORGR_PART_BB})(?:~{RE_ORGR_PART_BB})+?\)$'),
}
re_orgrs_full_s = {
    ProcModule.RX: re_compile(fr'^\( (?:{RE_ORGR_PART_RX})(?: ~ {RE_ORGR_PART_RX})+? \)$'),
    ProcModule.RN: re_compile(fr'^\( (?:{RE_ORGR_PART_RN})(?: ~ {RE_ORGR_PART_RN})+? \)$'),
    ProcModule.RS: re_compile(fr'^\( (?:{RE_ORGR_PART_RS})(?: ~ {RE_ORGR_PART_RS})+? \)$'),
    ProcModule.RP: re_compile(fr'^\( (?:{RE_ORGR_PART_RP})(?: ~ {RE_ORGR_PART_RP})+? \)$'),
    ProcModule.EN: re_compile(fr'^\( (?:{RE_ORGR_PART_EN})(?: ~ {RE_ORGR_PART_EN})+? \)$'),
    ProcModule.XB: re_compile(fr'^\( (?:{RE_ORGR_PART_XB})(?: ~ {RE_ORGR_PART_XB})+? \)$'),
    ProcModule.BB: re_compile(fr'^\( (?:{RE_ORGR_PART_BB})(?: ~ {RE_ORGR_PART_BB})+? \)$'),
}
re_andgr_full = re_compile(fr'^-\((?:{RE_ANDGR_PART_U})(?:,{RE_ANDGR_PART_U})+?\)$')

re_negative_meta = re_compile(r'^-[^:]+:.+?$')

last_tags = ''
last_fulltags: Sequence[str] | None = None


def reset_last_tags() -> None:
    global last_tags
    last_tags = ''


def re_plain() -> Pattern:
    return re_plains.get(ProcModule.CUR_PROC_MODULE)


def re_meta() -> Pattern:
    return re_metas.get(ProcModule.CUR_PROC_MODULE)


def re_sort() -> Pattern:
    return re_sorts.get(ProcModule.CUR_PROC_MODULE)


def re_fav() -> Pattern:
    return re_favs.get(ProcModule.CUR_PROC_MODULE)


def re_pool() -> Pattern:
    return re_pools.get(ProcModule.CUR_PROC_MODULE)


def re_orgr_full() -> Pattern:
    return re_orgrs_full.get(ProcModule.CUR_PROC_MODULE)


def re_orgr_full_s() -> Pattern:
    return re_orgrs_full_s.get(ProcModule.CUR_PROC_MODULE)


def split_or_group(gr: str) -> str:
    assert re_orgr_full().fullmatch(gr)
    orgr_parts = gr[1:-1].split('~')
    for part in orgr_parts:
        assert not re_negative_meta.fullmatch(part)  # negative meta tags
    return f'( {" ~ ".join(part for part in orgr_parts)} )'


def normalize_tag(tag: str) -> str:
    return tag.replace('+', '%2b').replace(' ', '+')


def convert_taglist(taglist: Sequence[str]) -> list[str]:
    parse_suc, parsed = parse_tags(' '.join(taglist))
    assert parse_suc, f'Invalid tags: {str(taglist)}'
    return [normalize_tag(tag) for tag in parsed]


def ret_tags(suc: bool, tag_list: Sequence[str]) -> tuple[bool, Sequence[str]]:
    return suc, tag_list


def fail() -> tuple[bool, Sequence[str]]:
    return ret_tags(False, DEFAULT_TAGS)


def parse_tags(tags: str) -> tuple[bool, Sequence[str]]:
    global last_tags
    global last_fulltags

    if '  ' in tags:
        tags = re_space_mult.sub(' ', tags)
    tags = tags.strip()

    if last_tags == tags:
        if last_fulltags:
            return ret_tags(True, last_fulltags)
        return fail()

    last_tags = tags
    last_fulltags = None

    if not tags:
        return fail()

    fulltags = list()
    sort_tags_count = 0
    custom_tags_count = 0
    tag: str
    for tag in unique_everseen(tags.split(' ')):
        if tag.startswith('(') and re_orgr_full().fullmatch(tag):
            try:
                tag = split_or_group(tag)
            except Exception:
                return fail()
        elif re_favorited_by_tag.fullmatch(tag):
            if re_fav().fullmatch(tag):
                custom_tags_count += 1
            else:
                return fail()
        elif re_pool_tag.fullmatch(tag):
            if re_pool().fullmatch(tag):
                custom_tags_count += 1
            else:
                return fail()
        elif re_sort().fullmatch(tag):
            sort_tags_count += 1
        if not (re_orgr_full_s().fullmatch(tag) or re_andgr_full.fullmatch(tag) or re_meta().fullmatch(tag) or re_plain().fullmatch(tag)):
            return fail()
        fulltags.append(tag)

    if len(fulltags) <= sort_tags_count > 0 or custom_tags_count > 1:
        return fail()

    last_fulltags = tuple(fulltags)

    return ret_tags(True, last_fulltags)

#
#
#########################################
