# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from argparse import ArgumentParser, Namespace, ZERO_OR_MORE
from collections.abc import Sequence
from inspect import stack
from os import path

# internal
from app_defines import (
    MODULE_ABBR_RX, MODULE_CHOICES, DEFAULT_HEADERS, ACTION_STORE_TRUE, ACTION_APPEND, DMODE_DEFAULT, DMODE_CHOICES, THREADS_MAX_ITEMS,
)
from app_help import (
    HELP_ARG_HELP, HELP_ARG_VERSION, HELP_ARG_MODULE, HELP_ARG_DOWNLOAD_MODE, HELP_ARG_DOWNLOAD_LIMIT, HELP_ARG_SKIP_IMAGES,
    HELP_ARG_SKIP_VIDEOS, HELP_ARG_PREFER_LOWRES, HELP_ARG_MINDATE, HELP_ARG_MAXDATE, HELP_ARG_THREADS, HELP_ARG_PATH, HELP_ARG_PROXY,
    HELP_ARG_NOPROXY, HELP_ARG_PROXYNODOWN, HELP_ARG_HEADERS, HELP_ARG_COOKIES, HELP_ARG_PREFIX, HELP_ARG_DUMP_TAGS, HELP_ARG_DUMP_SOURCES,
    HELP_ARG_DUMP_COMMENTS, HELP_ARG_DUMP_PER_ITEM, HELP_ARG_APPEND_SOURCE_AND_TAGS, HELP_ARG_TAGS, HELP_ARG_WARN_NON_EMPTY_FOLDER,
    HELP_ARG_INCLUDE_PARCHI, HELP_ARG_CON_TIMEOUT, HELP_ARG_CON_RETRIES, HELP_ARG_GET_MAXID, HELP_ARG_CACHE_HTML_BLOAT, HELP_ARG_VERBOSE,
    HELP_ARG_PREFER_WEBM, HELP_ARG_PREFER_MP4, HELP_ARG_HEADER, HELP_ARG_COOKIE, HELP_ARG_MERGE_LISTS, HELP_ARG_REVERSE_DOWNLOAD_ORDER,
    HELP_ARG_API_KEY,
)
from app_revision import APP_NAME, APP_VERSION
from app_validators import (
    valid_thread_count, valid_date, valid_folder_path, valid_json, valid_kwarg, valid_proxy, valid_positive_int, valid_api_key
)

__all__ = ('prepare_arglist',)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    subs = parser.add_subparsers()
    par_main = subs.add_parser('cmd', description='Run using normal cmdline', add_help=False)
    par_main.add_argument('--help', action='help', help=HELP_ARG_HELP)
    par_main.add_argument('--version', action='version', help=HELP_ARG_VERSION, version=f'{APP_NAME} {APP_VERSION}')
    return par_main


def prepare_arglist(args: Sequence[str]) -> Namespace:
    parser = create_parser()
    parser.usage = f'{path.basename(stack()[2].filename)} [-module #module=rx] [options...] tags...'
    parser.add_argument('-module', default=MODULE_ABBR_RX, help=HELP_ARG_MODULE, choices=MODULE_CHOICES)
    ex1 = parser.add_mutually_exclusive_group(required=False)
    ex2 = parser.add_mutually_exclusive_group(required=False)
    ex3 = parser.add_mutually_exclusive_group(required=False)
    ex1.add_argument('-get_maxid', action=ACTION_STORE_TRUE, help=HELP_ARG_GET_MAXID)
    parser.add_argument('-include_parchi', action=ACTION_STORE_TRUE, help=HELP_ARG_INCLUDE_PARCHI)
    parser.add_argument('-skip_img', action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_IMAGES)
    parser.add_argument('-skip_vid', action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_VIDEOS)
    ex2.add_argument('-webm', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_WEBM)
    ex2.add_argument('-mp4', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_MP4)
    parser.add_argument('-lowres', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_LOWRES)
    parser.add_argument('-mindate', metavar='#DD-MM-YYYY', help=HELP_ARG_MINDATE, type=valid_date)
    parser.add_argument('-maxdate', metavar='#DD-MM-YYYY', help=HELP_ARG_MAXDATE, type=valid_date)
    parser.add_argument('-threads', metavar=f'1..{THREADS_MAX_ITEMS:d}', help=HELP_ARG_THREADS, type=valid_thread_count)
    parser.add_argument('-path', metavar='#PATH', default=valid_folder_path(path.curdir), help=HELP_ARG_PATH, type=valid_folder_path)
    parser.add_argument('-proxy', metavar='#type://[user:pass@]a.d.d.r:port', help=HELP_ARG_PROXY, type=valid_proxy)
    parser.add_argument('-noproxy', action=ACTION_STORE_TRUE, help=HELP_ARG_NOPROXY)
    parser.add_argument('-proxynodown', action=ACTION_STORE_TRUE, help=HELP_ARG_PROXYNODOWN)
    parser.add_argument('-timeout', metavar='#NUMBER', help=HELP_ARG_CON_TIMEOUT, type=valid_positive_int)
    parser.add_argument('-retries', metavar='#NUMBER', help=HELP_ARG_CON_RETRIES, type=valid_positive_int)
    parser.add_argument('-api_key', metavar='#KEY,USER_ID', help=HELP_ARG_API_KEY, type=valid_api_key)
    parser.add_argument('-headers', metavar='#JSON', help=HELP_ARG_HEADERS, type=valid_json, default=DEFAULT_HEADERS)
    parser.add_argument('-cookies', metavar='#JSON', help=HELP_ARG_COOKIES, type=valid_json)
    parser.add_argument('-header', metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_HEADER, type=valid_kwarg)
    parser.add_argument('-cookie', metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_COOKIE, type=valid_kwarg)
    parser.add_argument('-prefix', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFIX)
    parser.add_argument('-dump_tags', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_TAGS)
    parser.add_argument('-dump_sources', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_SOURCES)
    parser.add_argument('-dump_comments', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_COMMENTS)
    ex3.add_argument('-dump_per_item', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_PER_ITEM)
    ex3.add_argument('-merge_lists', action=ACTION_STORE_TRUE, help=HELP_ARG_MERGE_LISTS)
    parser.add_argument('-append_info', action=ACTION_STORE_TRUE, help=HELP_ARG_APPEND_SOURCE_AND_TAGS)
    parser.add_argument('-warn_nonempty', action=ACTION_STORE_TRUE, help=HELP_ARG_WARN_NON_EMPTY_FOLDER)
    parser.add_argument('-verbose', action=ACTION_STORE_TRUE, help=HELP_ARG_VERBOSE)
    parser.add_argument('-cache_html_bloat', action=ACTION_STORE_TRUE, help=HELP_ARG_CACHE_HTML_BLOAT)
    parser.add_argument('-dmode', default=DMODE_DEFAULT, help=HELP_ARG_DOWNLOAD_MODE, choices=DMODE_CHOICES)
    parser.add_argument('-dlimit', metavar='#NUMBER', default=0, help=HELP_ARG_DOWNLOAD_LIMIT, type=valid_positive_int)
    parser.add_argument('-reverse', action=ACTION_STORE_TRUE, help=HELP_ARG_REVERSE_DOWNLOAD_ORDER)
    parser.add_argument(dest='tags', nargs=ZERO_OR_MORE, help=HELP_ARG_TAGS)
    parsed, unks = parser.parse_known_args(args)
    parsed.tags.extend(unks)  # -tags will be placed here; shove them into parsed tags
    if (not parsed.get_maxid) and (not parsed.tags):
        parser.error('the following arguments are required: tags')
    return parsed

#
#
#########################################
