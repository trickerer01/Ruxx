# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import re
from collections.abc import Iterable

# internal
from app_debug import __RUXX_DEBUG__
from app_defines import (
    TAGS_STRING_LENGTH_MAX_BB,
    TAGS_STRING_LENGTH_MAX_EN,
    TAGS_STRING_LENGTH_MAX_RN,
    TAGS_STRING_LENGTH_MAX_RP,
    TAGS_STRING_LENGTH_MAX_RS,
    TAGS_STRING_LENGTH_MAX_RX,
    TAGS_STRING_LENGTH_MAX_XB,
)
from app_logger import trace
from app_module import ProcModule
from app_network import thread_exit

__all__ = ('extract_neg_and_groups', 'split_tags_into_tasks')

MAX_STRING_LENGTHS = {
    ProcModule.RX: TAGS_STRING_LENGTH_MAX_RX,
    ProcModule.RN: TAGS_STRING_LENGTH_MAX_RN,
    ProcModule.RS: TAGS_STRING_LENGTH_MAX_RS,
    ProcModule.RP: TAGS_STRING_LENGTH_MAX_RP,
    ProcModule.EN: TAGS_STRING_LENGTH_MAX_EN,
    ProcModule.XB: TAGS_STRING_LENGTH_MAX_XB,
    ProcModule.BB: TAGS_STRING_LENGTH_MAX_BB,
}
MAX_NEGATIVE_TAGS = {
    ProcModule.RX: (0, False),
    ProcModule.RN: (0, False),
    ProcModule.RS: (0, False),
    ProcModule.RP: (3, False),
    ProcModule.EN: (40, False),
    ProcModule.XB: (0, False),
    ProcModule.BB: (0, False),
}
MAX_WILDCARDS = {
    ProcModule.RX: 0,
    ProcModule.RN: 0,
    ProcModule.RS: 0,
    ProcModule.RP: 0,
    ProcModule.EN: 1,
    ProcModule.XB: 0,
    ProcModule.BB: 0,
}
re_negative_and_group = re.compile(r'^-\(([^,]+(?:,[^,]+)+)\)$')


def split_tags_into_tasks(tag_groups_arr: Iterable[str], cc: str, sc: str, split_always: bool) -> list[str]:
    """
    Converts natively not processible tags into processible tags combinations\n
    Ex. ['(+a+~+b+)', '(+c+~+d+)', 'x', '-y'] => ['a+c+x+-y', 'a+d+x+-y', 'b+c+x+-y', 'b+d+x+-y']\n
    :param tag_groups_arr: list of tags ex. ['a', 'b', '(+c+~+d+)']
    :param cc: tags concatenation char (ex. 'a+b' => cc = '+')
    :param sc: meta tag type-value separator char (ex. 'id:123' => sc = ':')
    :param split_always: unconditionally separate all 'or' groups
    :return: list of fully formed tags directly injectable into request query template, len is up to max_or_group_len**2
    """
    new_tags_str_arr: list[str] = []
    or_tags_to_append: list[list[str]] = []
    has_negative = False
    for g_tags in tag_groups_arr:
        splitted = False
        add_list: list[str] = g_tags[2:-2].split('+~+') if len(g_tags) >= len('(+_+~+_+)') else []
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
            toapp: list[str] = []
            for or_tag in or_tags_list:
                for tags_string in tags_multi_list:
                    toapp.append(f'{or_tag}{f"{cc}{tags_string}" if len(tags_string) > 0 else ""}')
            tags_multi_list = toapp
        contains_msg = 'meta/negative tag(s) in ' if not split_always else ''
        trace(f'\nWarning (W1): {contains_msg}{len(or_tags_to_append):d} \'or\' group(s) found. '
              f'Splitting into {len(tags_multi_list):d} tasks.')
        return tags_multi_list
    return [cc.join(tag_groups_arr)]


def extract_neg_and_groups(tags_str: str, split_always: bool) -> tuple[list[str], list[list[re.Pattern[str]]]]:
    """
    Separates tags string into fully formed tags and negative tag patterns\n
    Ex. 'a b (+c+~+d+) -(ff,gg)' => (['a', 'b' , '(+c+~+d+)'], [[re.compile(r'^ff$'), re.compile(r'^gg$')]])\n
    :param tags_str: provided string of tags separated by space
    :param split_always: unconditionally separate all 'or' groups
    :return: 1) list of fully-formed tags without negative groups, 2) list of zero or more tag pattern lists
    """
    def form_plist(neg_tags_group: str) -> list[re.Pattern] | None:
        def esc(s: str) -> str:
            for c in '.[]()-+':
                s = s.replace(c, f'\\{c}')
            return s.replace('?', '.').replace('*', '.*')
        ngr = re_negative_and_group.fullmatch(neg_tags_group)
        return [re.compile(rf'^{esc(s)}$') for s in ngr.group(1).split(',')] if ngr else None

    parsed: list[list[re.Pattern]] = []
    tags_list = tags_str.split(' ')
    tgi: int
    for tgi in reversed(range(len(tags_list))):
        tag_group = tags_list[tgi]
        if len(tag_group) < len('-(a,b)') or not tag_group.startswith('-('):
            continue
        if plist := form_plist(tag_group):
            parsed.append(plist)
            del tags_list[tgi]

    total_len = len(tags_list) - 1  # concat chars count
    for t in tags_list:  # + length of each tag
        total_len += max(len(ogt) for ogt in t.split('+~+')) if split_always and t.startswith('(+') else len(t)

    max_tags_all, max_is_separate = MAX_NEGATIVE_TAGS[ProcModule.value()]
    max_wtags_all = MAX_WILDCARDS[ProcModule.value()]
    max_string_len = MAX_STRING_LENGTHS[ProcModule.value()]
    neg_tags_list_all = list(filter(lambda x: x.startswith('-'), tags_list))
    w_tags_list_all = list(filter(lambda x: '*' in x, tags_list))
    max_ntags = max(0, max_tags_all - (0 if max_is_separate else (len(tags_list) - len(neg_tags_list_all))) if max_tags_all else 10**9)
    max_wtags = max_wtags_all or 10**9

    def tags_fixed() -> None:
        return total_len <= max_string_len and len(neg_tags_list_all) <= max_ntags and len(w_tags_list_all) <= max_wtags

    neg_tags_list: list[str] = []
    if not tags_fixed():
        trace('Warning (W3): either total tags length, maximum negative tags count or maximum wildcarded tags count '
              'exceeds acceptable limit, trying to extract negative tags into negative group...')
        # first pass: wildcarded negative tags - chance to ruin alias is lower (rx)
        # second pass: any negative tags
        for wildcardpass in (True, False):
            ti: int
            for ti in reversed(range(len(neg_tags_list_all))):
                if tags_fixed():
                    break
                ntag = neg_tags_list_all[ti]
                if wildcardpass is True and ntag.rfind('*') == -1:
                    continue
                neg_tags_list.append(ntag[1:])
                total_len -= len(ntag) + 1
                del neg_tags_list_all[ti]
                del tags_list[tags_list.index(ntag)]
                if wildcardpass is True and ntag in w_tags_list_all:
                    del w_tags_list_all[w_tags_list_all.index(ntag)]
        if not tags_fixed():
            thread_exit('Fatal: extracting negative tags doesn\'t reduce total tags length enough! Aborting...', -609)
        assert len(neg_tags_list) > 0, 'No negative tags extracted!'
        extracted_neg_group_str = f'-(*,{"|".join(reversed(neg_tags_list))})'
        trace(f'Info: extracted negative group: {extracted_neg_group_str}')
        plist = form_plist(extracted_neg_group_str)
        assert plist is not None
        parsed.append(plist)
    if 0 < max_tags_all < len(tags_list) - (len(neg_tags_list_all) if max_is_separate else 0):
        thread_exit(f'Fatal: max tags exceeded for {ProcModule.name().upper()} '
                    f'({len(tags_list):d} > {max_tags_all:d}), final tags: \'{" ".join(tags_list)}\'')

    if __RUXX_DEBUG__ and len(neg_tags_list) > 0:
        trace(f'Resulting args: {" ".join(tags_list)}')

    return tags_list, parsed

#
#
#########################################
