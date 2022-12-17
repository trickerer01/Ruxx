# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import fullmatch as re_fullmatch, compile as re_compile
from typing import Tuple, List, Pattern, Optional

# internal
from app_defines import TAGS_STRING_LENGTH_MAX_RX
from app_gui_defines import ProcModule
from app_network import thread_exit
from app_logger import trace


def split_tags_into_tasks(tag_groups_arr: List[str], cc: str, sc: str, can_have_or_groups: bool, split_always: bool) -> List[str]:
    if can_have_or_groups:
        # rx: (+id:2+~+id:3+)
        # rn: (+id=2+~+id=3+)
        # meta_or_group_re = re_compile(
        #     fr'^\(\+([^{sc}~+]+(?:{sc}[^{sc}~+]+)?(?:\+~\+[^{sc}~+]+(?:{sc}[^{sc}~+]+)?)*)\+\)$')
        new_tags_str_arr = []  # type: List[str]
        or_tags_to_append = []  # type: List[str]
        has_negative = False
        for g_tags in tag_groups_arr:
            splitted = False
            add_list = g_tags[2:-2].split('+~+') if len(g_tags) >= len('(+_+~+_+)') else []  # type: List[str]
            if len(add_list) > 1:
                do_split = split_always
                for add_s in add_list:
                    add_s_negative = add_s.startswith('-')
                    add_s_meta = add_s.find(sc) != -1
                    if add_s_negative is True or split_always is True or add_s_meta is True:
                        assert add_s_negative & add_s_meta is False  # see app_tags_parser.py::split_or_group(str)
                        if len(or_tags_to_append) > 0:
                            containment_msg = '' if split_always else ' containing sort/negative tag(s)'
                            thread_exit(f'Error: Can\'t handle more than one \'or\' group{containment_msg}. NYI!', -703)
                        do_split = True
                        has_negative |= add_s_negative
                if do_split:
                    splitted = True
                    or_tags_to_append += add_list
            if not splitted:
                new_tags_str_arr.append(g_tags)
        if len(or_tags_to_append) > 0:
            if has_negative and len(new_tags_str_arr) == 0:
                thread_exit('Error: -tag in \'or\' group found, but no +tags! Cannot search by only -tags', -701)
            trace(f'\nWarning (W1): sort/negative tag(s) in \'or\' group found. Splitting into {len(or_tags_to_append):d} tasks.')
            new_base_tags_str = f'{cc}{cc.join(new_tags_str_arr)}' if len(new_tags_str_arr) > 0 else ''
            return [f'{or_tag}{new_base_tags_str}' for or_tag in or_tags_to_append]
    return [cc.join(tag_groups_arr)]


def extract_neg_and_groups(tags_str: str) -> Tuple[List[str], List[List[Pattern[str]]]]:
    def esc(s: str) -> str:
        for c in '.[]()-+':
            s = s.replace(c, f'\\{c}')
        return s.replace('?', '.').replace('*', '.*')

    def form_plist(neg_tags_group: str) -> Optional[List[Pattern]]:
        ngr = re_fullmatch(r'^-\(([^,]+(?:,[^,]+)+)\)$', neg_tags_group)
        return [re_compile(rf'^{esc(s)}$') for s in ngr.group(1).split(',')] if ngr else None

    parsed = []
    tags_list = tags_str.split(' ')
    for tgi in reversed(range(len(tags_list))):  # type: int
        tag_group = tags_list[tgi]
        if len(tag_group) < len('-(a,b)') or tag_group[0:2] != '-(':
            continue
        plist = form_plist(tag_group)
        if plist:
            parsed.append(plist)
            del tags_list[tgi]
    if ProcModule.is_rx():
        total_len = sum(len(t) for t in tags_list) + len(tags_list) - 1
        if total_len > TAGS_STRING_LENGTH_MAX_RX:
            trace('Warning (W2): total tags length exceeds acceptable limit, trying to extract negative tags into negative group...')
            neg_tags_list = []  # type: List[str]
            # first pass: wildcarded negative tags - chance to ruin alias is lower
            # second pass: any negative tags
            for wildcardpass in [True, False]:
                for ti in reversed(range(len(tags_list))):  # type: int
                    if total_len <= TAGS_STRING_LENGTH_MAX_RX:
                        break
                    ntag = tags_list[ti]
                    if wildcardpass is True and ntag.rfind('*') == -1:
                        continue
                    if ntag.startswith('-'):
                        neg_tags_list.append(ntag[1:])
                        total_len -= len(ntag) + 1
                        del tags_list[ti]
            if total_len > TAGS_STRING_LENGTH_MAX_RX:
                thread_exit('Fatal: extracting negative tags doesn\'t reduce total tags length enough! '
                            'Search result will be empty! Aborting...', -609)
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
