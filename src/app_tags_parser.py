# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile, fullmatch as re_fullmatch, sub as re_sub
from typing import List, Pattern, Tuple, Optional

# requirements
from iteration_utilities import unique_everseen

# internal
from app_gui_defines import ProcModule


DEFAULT_TAGS = ['sfw']

# language=PythonRegExp
TAG_CHAR = r'[a-zÀ-ʯ\d_+\-/!()*\'.]'
# language=PythonRegExp
META_CHAR = r'[a-z\d_]'
# language=PythonRegExp
META_COUNT_RX = r':(?:[<>]=?|=)?[a-z\d_]+?'
# language=PythonRegExp
META_COUNT_RN = r'(?:[<>]=?|=)[a-z\d_]+?'
# language=PythonRegExp
RE_ORGR_PART_RX = fr'{TAG_CHAR}+?(?:{META_COUNT_RX})?'
# language=PythonRegExp
RE_ORGR_PART_RN = fr'{TAG_CHAR}+?(?:{META_COUNT_RN})?'

# language=PythonRegExp
ANDGR_CHAR = r'[a-zÀ-ʯ\d_+\-/!()*\'.|?]'
# language=PythonRegExp
RE_ANDGR_PART_U = fr'{ANDGR_CHAR}+?'

re_plains = {
    ProcModule.PROC_RX: re_compile(fr'^-?{TAG_CHAR}+?$'),
    ProcModule.PROC_RN: re_compile(fr'^-?{TAG_CHAR}+?$'),
}
re_metas = {
    ProcModule.PROC_RX: re_compile(fr'^{META_CHAR}+?{META_COUNT_RX}$'),
    ProcModule.PROC_RN: re_compile(fr'^{META_CHAR}+?{META_COUNT_RN}$'),
}
re_orgrs_full = {
    ProcModule.PROC_RX: re_compile(fr'^\((?:{RE_ORGR_PART_RX})(?:~{RE_ORGR_PART_RX})+?\)$'),
    ProcModule.PROC_RN: re_compile(fr'^\((?:{RE_ORGR_PART_RN})(?:~{RE_ORGR_PART_RN})+?\)$'),
}
re_orgrs_full_s = {
    ProcModule.PROC_RX: re_compile(fr'^\( (?:{RE_ORGR_PART_RX})(?: ~ {RE_ORGR_PART_RX})+? \)$'),
    ProcModule.PROC_RN: re_compile(fr'^\( (?:{RE_ORGR_PART_RN})(?: ~ {RE_ORGR_PART_RN})+? \)$'),
}
re_andgr_full = re_compile(fr'^-\((?:{RE_ANDGR_PART_U})(?:,{RE_ANDGR_PART_U})+?\)$')

last_tags = ''
last_fulltags = None  # type: Optional[List[str]]


def reset_last_tags() -> None:
    global last_tags
    last_tags = ''


def re_plain() -> Pattern:
    return re_plains.get(ProcModule.CUR_PROC_MODULE)


def re_meta() -> Pattern:
    return re_metas.get(ProcModule.CUR_PROC_MODULE)


def re_orgr_full() -> Pattern:
    return re_orgrs_full.get(ProcModule.CUR_PROC_MODULE)


def re_orgr_full_s() -> Pattern:
    return re_orgrs_full_s.get(ProcModule.CUR_PROC_MODULE)


def split_or_group(gr: str) -> str:
    assert re_fullmatch(re_orgr_full(), gr)
    orgr_parts = gr[1:-1].split('~')
    for part in orgr_parts:
        assert not re_fullmatch(r'^-[^:]+:.+?$', part)  # negative sort tags
    return f'( {" ~ ".join(part for part in orgr_parts)} )'


def ret_tags(suc: bool, tag_list: List[str]) -> Tuple[bool, List[str]]:
    return suc, tag_list.copy()


def fail() -> Tuple[bool, List[str]]:
    return ret_tags(False, DEFAULT_TAGS)


def parse_tags(tags: str) -> Tuple[bool, List[str]]:
    global last_tags
    global last_fulltags

    if tags.find('  ') != -1:
        tags = re_sub(r'  +', ' ', tags)
    if len(tags) > 0 and tags[0] == ' ':
        tags = tags[1:]
    if len(tags) > 0 and tags[-1] == ' ':
        tags = tags[:-1]

    if last_tags == tags:
        if last_fulltags:
            return ret_tags(True, last_fulltags)
        return fail()

    last_tags = tags
    last_fulltags = None

    if len(tags) <= 0:
        return fail()

    fulltags = []  # type: List[str]
    for tag in unique_everseen(tags.split(' ')):  # type: str
        if ProcModule.is_rx() and tag.startswith('sort:'):
            return fail()
        if ProcModule.is_rn() and tag.startswith('order='):
            return fail()
        if tag[0] == '(' and re_fullmatch(re_orgr_full(), tag):
            try:
                tag = split_or_group(tag)
            except Exception:
                return fail()
        if not (
                re_fullmatch(re_orgr_full_s(), tag) or
                re_fullmatch(re_andgr_full, tag) or
                re_fullmatch(re_meta(), tag) or
                re_fullmatch(re_plain(), tag)
        ):
            return fail()
        fulltags.append(tag)

    last_fulltags = fulltags

    return ret_tags(True, fulltags)

#
#
#########################################
