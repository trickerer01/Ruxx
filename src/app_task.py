# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile
from typing import Tuple, List, Pattern, Optional, Iterable

# internal
from app_defines import (
    TAGS_STRING_LENGTH_MAX_RX, TAGS_STRING_LENGTH_MAX_RN, TAGS_STRING_LENGTH_MAX_RS, TAGS_STRING_LENGTH_MAX_RZ, TAGS_STRING_LENGTH_MAX_RP,
)
from app_module import ProcModule
from app_network import thread_exit
from app_logger import trace

__all__ = ('split_tags_into_tasks', 'extract_neg_and_groups')

re_negative_and_group = re_compile(r'^-\(([^,]+(?:,[^,]+)+)\)$')


def split_tags_into_tasks(tag_groups_arr: Iterable[str], cc: str, sc: str, split_always: bool) -> List[str]:
    """
    Converts natively not processible tags into processible tags combinations\n
    Ex. ['(+a+~+b+)', '(+c+~+d+)', 'x', '-y'] => ['a+c+x+-y', 'a+d+x+-y', 'b+c+x+-y', 'b+d+x+-y']\n
    :param tag_groups_arr: list of tags ex. ['a', 'b', '(+c+~+d+)']
    :param cc: tags concatenation char (ex. 'a+b' => cc = '+')
    :param sc: meta tag type-value separator char (ex. 'id:123' => sc = ':')
    :param split_always: unconditionally separate all 'or' groups
    :return: list of fully formed tags directly injectable into request query template, len is up to max_or_group_len**2
    """
    new_tags_str_arr: List[str] = list()
    or_tags_to_append: List[List[str]] = list()
    has_negative = False
    for g_tags in tag_groups_arr:
        splitted = False
        add_list: List[str] = g_tags[2:-2].split('+~+') if len(g_tags) >= len('(+_+~+_+)') else list()
        if len(add_list) > 1:
            do_split = split_always
            for add_s in add_list:
                add_s_negative = add_s.startswith('-')
                add_s_meta = sc in add_s
                if add_s_negative is True or split_always is True or add_s_meta is True:
                    assert (add_s_negative & add_s_meta) is False  # see app_tags_parser.py::split_or_group(str)
                    do_split = True
                    has_negative |= add_s_negative
            if do_split:
                splitted = True
                or_tags_to_append.append(add_list)
        if not splitted:
            new_tags_str_arr.append(g_tags)
    if len(or_tags_to_append) > 0:
        if has_negative and len(new_tags_str_arr) == 0:
            thread_exit('Error: -tag in \'or\' group found, but no +tags! Cannot search by only -tags', -701)
        tags_multi_list = [f'{cc.join(new_tags_str_arr)}' if len(new_tags_str_arr) > 0 else '']
        for or_tags_list in reversed(or_tags_to_append):
            toapp = list()
            for or_tag in or_tags_list:
                for tags_string in tags_multi_list:
                    toapp.append(f'{or_tag}{f"{cc}{tags_string}" if len(tags_string) > 0 else ""}')
            tags_multi_list = toapp
        contains_msg = 'meta/negative tag(s) in ' if not split_always else ''
        trace(f'\nWarning (W1): {contains_msg}{len(or_tags_to_append):d} \'or\' group(s) found. '
              f'Splitting into {len(tags_multi_list):d} tasks.')
        return tags_multi_list
    return [cc.join(tag_groups_arr)]


def extract_neg_and_groups(tags_str: str, split_always: bool) -> Tuple[List[str], List[List[Pattern[str]]]]:
    """
    Separates tags string into fully formed tags and negative tag patterns\n
    Ex. 'a b (+c+~+d+) -(ff,gg)' => (['a', 'b' , '(+c+~+d+)'], [[re_compile(r'^ff$'), re_compile(r'^gg$')]])\n
    :param tags_str: provided string of tags separated by space
    :param split_always: unconditionally separate all 'or' groups
    :return: 1) list of fully-formed tags without negative groups, 2) list of zero or more tag pattern lists
    """
    def form_plist(neg_tags_group: str) -> Optional[List[Pattern]]:
        def esc(s: str) -> str:
            for c in '.[]()-+':
                s = s.replace(c, f'\\{c}')
            return s.replace('?', '.').replace('*', '.*')
        ngr = re_negative_and_group.fullmatch(neg_tags_group)
        return [re_compile(rf'^{esc(s)}$') for s in ngr.group(1).split(',')] if ngr else None

    parsed = list()
    tags_list = tags_str.split(' ')
    tgi: int
    for tgi in reversed(range(len(tags_list))):
        tag_group = tags_list[tgi]
        if len(tag_group) < len('-(a,b)') or tag_group[0:2] != '-(':
            continue
        plist = form_plist(tag_group)
        if plist:
            parsed.append(plist)
            del tags_list[tgi]

    total_len = len(tags_list) - 1  # concat chars count
    for t in tags_list:  # + length of each tag
        total_len += max(len(ogt) for ogt in t.split('+~+')) if split_always and t.startswith('(+') else len(t)
    max_string_lengths = {
        ProcModule.PROC_RX: TAGS_STRING_LENGTH_MAX_RX,
        ProcModule.PROC_RN: TAGS_STRING_LENGTH_MAX_RN,
        ProcModule.PROC_RS: TAGS_STRING_LENGTH_MAX_RS,
        ProcModule.PROC_RZ: TAGS_STRING_LENGTH_MAX_RZ,
        ProcModule.PROC_RP: TAGS_STRING_LENGTH_MAX_RP,
    }
    max_neg_tagss = {
        ProcModule.PROC_RX: (0, False),
        ProcModule.PROC_RN: (0, False),
        ProcModule.PROC_RS: (0, False),
        ProcModule.PROC_RZ: (3, True),
        ProcModule.PROC_RP: (3, False),
    }
    max_tags_neg, max_is_separate = max_neg_tagss[ProcModule.get()]
    neg_tags_list_all = list(filter(lambda x: x.startswith('-'), tags_list))
    max_tags = max(0, max_tags_neg - (0 if max_is_separate else (len(tags_list) - len(neg_tags_list_all))) if max_tags_neg else 10**9)
    max_string_len = max_string_lengths[ProcModule.get()]
    if total_len > max_string_len or len(neg_tags_list_all) > max_tags:
        trace('Warning (W3): total tags length exceeds acceptable limit, trying to extract negative tags into negative group...')
        neg_tags_list = list()
        # first pass: wildcarded negative tags - chance to ruin alias is lower (rx)
        # second pass: any negative tags
        for wildcardpass in (True, False):
            ti: int
            for ti in reversed(range(len(neg_tags_list_all))):
                if total_len <= max_string_len and len(neg_tags_list_all) <= max_tags:
                    break
                ntag = neg_tags_list_all[ti]
                if wildcardpass is True and ntag.rfind('*') == -1:
                    continue
                neg_tags_list.append(ntag[1:])
                total_len -= len(ntag) + 1
                del neg_tags_list_all[ti]
                del tags_list[tags_list.index(ntag)]
        if total_len > max_string_len or len(neg_tags_list_all) > max_tags:
            thread_exit('Fatal: extracting negative tags doesn\'t reduce total tags length enough! Aborting...', -609)
        assert len(neg_tags_list) > 0
        extracted_neg_group_str = f'-(*,{"|".join(reversed(neg_tags_list))})'
        trace(f'Info: extractd negative group: {extracted_neg_group_str}')
        plist = form_plist(extracted_neg_group_str)
        assert plist is not None
        parsed.append(plist)

    return tags_list, parsed

#
#
#########################################
