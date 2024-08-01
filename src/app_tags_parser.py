# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile
from typing import Optional, Pattern, Sequence, Tuple, List

# requirements
from iteration_utilities import unique_everseen

# internal
from app_module import ProcModule
from app_re import re_space_mult, re_favorited_by_tag, re_pool_tag

__all__ = ('reset_last_tags', 'parse_tags', 'convert_taglist')

DEFAULT_TAGS = ('sfw',)

# language=PythonRegExp
TAG_CHAR = r'[a-zÀ-ʯА-я\d_%+\-/!()*\'.]'
# language=PythonRegExp
META_CHAR = r'[a-z\d_\-.]'
# language=PythonRegExp
META_COUNT_RX = r':(?:(?:[<>]=?|=)?[a-z\d_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_COUNT_RN = r'(?:[<>]=?|=)[a-z\d_]+?'
# language=PythonRegExp
META_COUNT_RS = r':(?:(?:[<>]=?|=)?[a-z\d_]+?|[a-z\d_]+:[a-z\d_]+?)'
# language=PythonRegExp
META_COUNT_RZ = r':(?:[<>]=?)?[^:]+?'
# language=PythonRegExp
META_COUNT_RP = r'(?:[<>]=?|=)[a-z\d_]+?'
# language=PythonRegExp
META_SORT_RX = r'sort(?::[^:]+?){1,2}'
# language=PythonRegExp
META_SORT_RN = r'order=(?:id|score)_desc'
# language=PythonRegExp
META_SORT_RS = r'sort(?::[^:]+?){1,2}'
# language=PythonRegExp
META_SORT_RZ = r''
"""not supported"""
# language=PythonRegExp
META_SORT_RP = r'order=(?:id|score)_desc'
# language=PythonRegExp
META_FAV_RX = r'favorited_by:\d+?'
# language=PythonRegExp
META_FAV_RN = r'favorited_by=[^:=]+?'
# language=PythonRegExp
META_FAV_RS = r'favorited_by:\d+?'
# language=PythonRegExp
META_FAV_RZ = r'favorited_by:[^:]+?'
# language=PythonRegExp
META_FAV_RP = r'favorited_by=[^:=]+?'
# language=PythonRegExp
META_POOL_RX = r'pool:\d+?'
# language=PythonRegExp
META_POOL_RN = r''
"""not supported"""
# language=PythonRegExp
META_POOL_RS = r''
"""not supported"""
# language=PythonRegExp
META_POOL_RZ = r''
"""not supported"""
# language=PythonRegExp
META_POOL_RP = r''
"""not supported"""
# language=PythonRegExp
RE_ORGR_PART_RX = fr'{TAG_CHAR}+?(?:{META_COUNT_RX})?'
# language=PythonRegExp
RE_ORGR_PART_RN = fr'{TAG_CHAR}+?(?:{META_COUNT_RN})?'
# language=PythonRegExp
RE_ORGR_PART_RS = fr'{TAG_CHAR}+?(?:{META_COUNT_RS})?'
# language=PythonRegExp
RE_ORGR_PART_RZ = fr'{TAG_CHAR}+?'
# language=PythonRegExp
RE_ORGR_PART_RP = fr'{TAG_CHAR}+?(?:{META_COUNT_RP})?'

# language=PythonRegExp
ANDGR_CHAR = r'[a-zÀ-ʯА-я\d_+\-/!()*\'.|?]'
# language=PythonRegExp
RE_ANDGR_PART_U = fr'{ANDGR_CHAR}+?'

re_plains = {
    ProcModule.PROC_RX: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.PROC_RN: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.PROC_RS: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.PROC_RZ: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.PROC_RP: re_compile(fr'^-?{TAG_CHAR}+?$'),
}
re_metas = {
    ProcModule.PROC_RX: re_compile(fr'^{META_CHAR}+?{META_COUNT_RX}$'),
    ProcModule.PROC_RN: re_compile(fr'^{META_CHAR}+?{META_COUNT_RN}$'),
    ProcModule.PROC_RS: re_compile(fr'^{META_CHAR}+?{META_COUNT_RS}$'),
    ProcModule.PROC_RZ: re_compile(fr'^(?:id|favorited_by|score){META_COUNT_RZ}$'),
    ProcModule.PROC_RP: re_compile(fr'^{META_CHAR}+?{META_COUNT_RP}$'),
}
re_sorts = {
    ProcModule.PROC_RX: re_compile(fr'^{META_SORT_RX}$'),
    ProcModule.PROC_RN: re_compile(fr'^{META_SORT_RN}$'),
    ProcModule.PROC_RS: re_compile(fr'^{META_SORT_RS}$'),
    ProcModule.PROC_RZ: re_compile(fr'^{META_SORT_RZ}$'),
    ProcModule.PROC_RP: re_compile(fr'^{META_SORT_RP}$'),
}
re_favs = {
    ProcModule.PROC_RX: re_compile(fr'^{META_FAV_RX}$'),
    ProcModule.PROC_RN: re_compile(fr'^{META_FAV_RN}$'),
    ProcModule.PROC_RS: re_compile(fr'^{META_FAV_RS}$'),
    ProcModule.PROC_RZ: re_compile(fr'^{META_FAV_RZ}$'),
    ProcModule.PROC_RP: re_compile(fr'^{META_FAV_RP}$'),
}
re_pools = {
    ProcModule.PROC_RX: re_compile(fr'^{META_POOL_RX}$'),
    ProcModule.PROC_RN: re_compile(fr'^{META_POOL_RN}$'),
    ProcModule.PROC_RS: re_compile(fr'^{META_POOL_RS}$'),
    ProcModule.PROC_RZ: re_compile(fr'^{META_POOL_RZ}$'),
    ProcModule.PROC_RP: re_compile(fr'^{META_POOL_RP}$'),
}
re_orgrs_full = {
    ProcModule.PROC_RX: re_compile(fr'^\((?:{RE_ORGR_PART_RX})(?:~{RE_ORGR_PART_RX})+?\)$'),
    ProcModule.PROC_RN: re_compile(fr'^\((?:{RE_ORGR_PART_RN})(?:~{RE_ORGR_PART_RN})+?\)$'),
    ProcModule.PROC_RS: re_compile(fr'^\((?:{RE_ORGR_PART_RS})(?:~{RE_ORGR_PART_RS})+?\)$'),
    ProcModule.PROC_RZ: re_compile(fr'^\((?:{RE_ORGR_PART_RZ})(?:~{RE_ORGR_PART_RZ})+?\)$'),
    ProcModule.PROC_RP: re_compile(fr'^\((?:{RE_ORGR_PART_RP})(?:~{RE_ORGR_PART_RP})+?\)$'),
}
re_orgrs_full_s = {
    ProcModule.PROC_RX: re_compile(fr'^\( (?:{RE_ORGR_PART_RX})(?: ~ {RE_ORGR_PART_RX})+? \)$'),
    ProcModule.PROC_RN: re_compile(fr'^\( (?:{RE_ORGR_PART_RN})(?: ~ {RE_ORGR_PART_RN})+? \)$'),
    ProcModule.PROC_RS: re_compile(fr'^\( (?:{RE_ORGR_PART_RS})(?: ~ {RE_ORGR_PART_RS})+? \)$'),
    ProcModule.PROC_RZ: re_compile(fr'^\( (?:{RE_ORGR_PART_RZ})(?: ~ {RE_ORGR_PART_RZ})+? \)$'),
    ProcModule.PROC_RP: re_compile(fr'^\( (?:{RE_ORGR_PART_RP})(?: ~ {RE_ORGR_PART_RP})+? \)$'),
}
re_andgr_full = re_compile(fr'^-\((?:{RE_ANDGR_PART_U})(?:,{RE_ANDGR_PART_U})+?\)$')

re_negative_meta = re_compile(r'^-[^:]+:.+?$')

last_tags = ''
last_fulltags: Optional[Sequence[str]] = None


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


def convert_taglist(taglist: Sequence[str]) -> List[str]:
    parse_suc, parsed = parse_tags(' '.join(taglist))
    assert parse_suc, f'Invalid tags: {str(taglist)}'
    return [normalize_tag(tag) for tag in parsed]


def ret_tags(suc: bool, tag_list: Sequence[str]) -> Tuple[bool, Sequence[str]]:
    return suc, tag_list


def fail() -> Tuple[bool, Sequence[str]]:
    return ret_tags(False, DEFAULT_TAGS)


def parse_tags(tags: str) -> Tuple[bool, Sequence[str]]:
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
