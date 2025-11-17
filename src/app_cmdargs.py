# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import os
from argparse import ZERO_OR_MORE, ArgumentParser, Namespace
from collections.abc import Sequence
from inspect import stack

from app_defines import (
    ACTION_APPEND,
    ACTION_STORE_TRUE,
    DEFAULT_HEADERS,
    DMODE_CHOICES,
    DMODE_DEFAULT,
    MODULE_ABBR_RX,
    MODULE_CHOICES,
    THREADS_MAX_ITEMS,
)
from app_gui_defines import (
    OPTION_CMD_APIKEY_CMD,
    OPTION_CMD_APPEND_SOURCE_AND_TAGS,
    OPTION_CMD_CACHE_PROCCED_HTML,
    OPTION_CMD_COOKIES_CMD,
    OPTION_CMD_DATEAFTER_CMD,
    OPTION_CMD_DATEBEFORE_CMD,
    OPTION_CMD_DOWNLIMIT_CMD,
    OPTION_CMD_DOWNLOAD_ORDER,
    OPTION_CMD_DOWNMODE_CMD,
    OPTION_CMD_FNAMEPREFIX,
    OPTION_CMD_GET_MAXID_CMD,
    OPTION_CMD_HEADERS_CMD,
    OPTION_CMD_HIDE_PERSONAL_INFO,
    OPTION_CMD_IGNORE_PROXY,
    OPTION_CMD_IMAGES,
    OPTION_CMD_INFO_SAVE_MODE,
    OPTION_CMD_MODULE_CMD,
    OPTION_CMD_PARCHI,
    OPTION_CMD_PATH_CMD,
    OPTION_CMD_PROXY_CMD,
    OPTION_CMD_PROXY_NO_DOWNLOAD,
    OPTION_CMD_RETRIES_CMD,
    OPTION_CMD_SAVE_COMMENTS,
    OPTION_CMD_SAVE_SOURCES,
    OPTION_CMD_SAVE_TAGS,
    OPTION_CMD_THREADING_CMD,
    OPTION_CMD_TIMEOUT_CMD,
    OPTION_CMD_VERBOSE,
    OPTION_CMD_VIDEOS,
    OPTION_CMD_WARN_NONEMPTY_DEST,
)
from app_help import (
    HELP_ARG_API_KEY,
    HELP_ARG_APPEND_SOURCE_AND_TAGS,
    HELP_ARG_CACHE_HTML_BLOAT,
    HELP_ARG_CON_RETRIES,
    HELP_ARG_CON_TIMEOUT,
    HELP_ARG_COOKIE,
    HELP_ARG_COOKIES,
    HELP_ARG_DOWNLOAD_LIMIT,
    HELP_ARG_DOWNLOAD_MODE,
    HELP_ARG_DUMP_COMMENTS,
    HELP_ARG_DUMP_PER_ITEM,
    HELP_ARG_DUMP_SOURCES,
    HELP_ARG_DUMP_TAGS,
    HELP_ARG_GET_MAXID,
    HELP_ARG_HEADER,
    HELP_ARG_HEADERS,
    HELP_ARG_HELP,
    HELP_ARG_HIDE_PERSONAL_INFO,
    HELP_ARG_INCLUDE_PARCHI,
    HELP_ARG_MAXDATE,
    HELP_ARG_MERGE_LISTS,
    HELP_ARG_MINDATE,
    HELP_ARG_MODULE,
    HELP_ARG_NOPROXY,
    HELP_ARG_PATH,
    HELP_ARG_PREFER_LOWRES,
    HELP_ARG_PREFER_MP4,
    HELP_ARG_PREFER_WEBM,
    HELP_ARG_PREFIX,
    HELP_ARG_PROXY,
    HELP_ARG_PROXYNODOWN,
    HELP_ARG_REVERSE_DOWNLOAD_ORDER,
    HELP_ARG_SKIP_IMAGES,
    HELP_ARG_SKIP_VIDEOS,
    HELP_ARG_TAGS,
    HELP_ARG_THREADS,
    HELP_ARG_VERBOSE,
    HELP_ARG_VERSION,
    HELP_ARG_WARN_NON_EMPTY_FOLDER,
)
from app_module import ProcModule
from app_revision import APP_NAME, APP_VERSION
from app_validators import (
    valid_api_key,
    valid_date,
    valid_folder_path,
    valid_json,
    valid_kwarg,
    valid_positive_int,
    valid_proxy,
    valid_thread_count,
)

__all__ = ('prepare_arglist',)

DEFAULT_PATH = valid_folder_path(os.path.curdir)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    subs = parser.add_subparsers()
    par_main = subs.add_parser('cmd', description='Run using normal cmdline', add_help=False)
    par_main.add_argument('--help', action='help', help=HELP_ARG_HELP)
    par_main.add_argument('--version', action='version', help=HELP_ARG_VERSION, version=f'{APP_NAME} {APP_VERSION}')
    return par_main


def prepare_arglist(args: Sequence[str]) -> Namespace:
    parser = create_parser()
    parser.usage = f'{os.path.basename(stack()[2].filename)} [-module #module={ProcModule.PROC_MODULE_NAME_DEFAULT}] [options...] tags...'
    parser.add_argument(OPTION_CMD_MODULE_CMD, default=MODULE_ABBR_RX, help=HELP_ARG_MODULE, choices=MODULE_CHOICES)
    ex1 = parser.add_mutually_exclusive_group(required=False)
    ex2 = parser.add_mutually_exclusive_group(required=False)
    ex3 = parser.add_mutually_exclusive_group(required=False)
    ex1.add_argument(OPTION_CMD_GET_MAXID_CMD, action=ACTION_STORE_TRUE, help=HELP_ARG_GET_MAXID)
    parser.add_argument(OPTION_CMD_HIDE_PERSONAL_INFO[True], action=ACTION_STORE_TRUE, help=HELP_ARG_HIDE_PERSONAL_INFO)
    parser.add_argument(OPTION_CMD_PARCHI[True], action=ACTION_STORE_TRUE, help=HELP_ARG_INCLUDE_PARCHI)
    parser.add_argument(OPTION_CMD_IMAGES[0], action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_IMAGES)
    parser.add_argument(OPTION_CMD_VIDEOS[0], action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_VIDEOS)
    ex2.add_argument(OPTION_CMD_VIDEOS[1], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_MP4)
    ex2.add_argument(OPTION_CMD_VIDEOS[2], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_WEBM)
    parser.add_argument(OPTION_CMD_IMAGES[1], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_LOWRES)
    parser.add_argument(OPTION_CMD_DATEAFTER_CMD, metavar='#DD-MM-YYYY', help=HELP_ARG_MINDATE, type=valid_date)
    parser.add_argument(OPTION_CMD_DATEBEFORE_CMD, metavar='#DD-MM-YYYY', help=HELP_ARG_MAXDATE, type=valid_date)
    parser.add_argument(OPTION_CMD_THREADING_CMD, metavar=f'1..{THREADS_MAX_ITEMS:d}', help=HELP_ARG_THREADS, type=valid_thread_count)
    parser.add_argument(OPTION_CMD_PATH_CMD, metavar='#PATH', default=DEFAULT_PATH, help=HELP_ARG_PATH, type=valid_folder_path)
    parser.add_argument(OPTION_CMD_PROXY_CMD, metavar='#type://[user:pass@]a.d.d.r:port', help=HELP_ARG_PROXY, type=valid_proxy)
    parser.add_argument(OPTION_CMD_IGNORE_PROXY[True], action=ACTION_STORE_TRUE, help=HELP_ARG_NOPROXY)
    parser.add_argument(OPTION_CMD_PROXY_NO_DOWNLOAD[True], action=ACTION_STORE_TRUE, help=HELP_ARG_PROXYNODOWN)
    parser.add_argument(OPTION_CMD_TIMEOUT_CMD, metavar='#NUMBER', help=HELP_ARG_CON_TIMEOUT, type=valid_positive_int)
    parser.add_argument(OPTION_CMD_RETRIES_CMD, metavar='#NUMBER', help=HELP_ARG_CON_RETRIES, type=valid_positive_int)
    parser.add_argument(OPTION_CMD_APIKEY_CMD, metavar='#KEY,USER_ID', help=HELP_ARG_API_KEY, type=valid_api_key)
    parser.add_argument(OPTION_CMD_HEADERS_CMD, metavar='#JSON', help=HELP_ARG_HEADERS, type=valid_json, default=DEFAULT_HEADERS)
    parser.add_argument(OPTION_CMD_COOKIES_CMD, metavar='#JSON', help=HELP_ARG_COOKIES, type=valid_json)
    parser.add_argument(OPTION_CMD_HEADERS_CMD[:-1], metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_HEADER, type=valid_kwarg)
    parser.add_argument(OPTION_CMD_COOKIES_CMD[:-1], metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_COOKIE, type=valid_kwarg)
    parser.add_argument(OPTION_CMD_FNAMEPREFIX[True], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFIX)
    parser.add_argument(OPTION_CMD_SAVE_TAGS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_TAGS)
    parser.add_argument(OPTION_CMD_SAVE_SOURCES[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_SOURCES)
    parser.add_argument(OPTION_CMD_SAVE_COMMENTS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_COMMENTS)
    ex3.add_argument(OPTION_CMD_INFO_SAVE_MODE[1], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_PER_ITEM)
    ex3.add_argument(OPTION_CMD_INFO_SAVE_MODE[2], action=ACTION_STORE_TRUE, help=HELP_ARG_MERGE_LISTS)
    parser.add_argument(OPTION_CMD_APPEND_SOURCE_AND_TAGS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_APPEND_SOURCE_AND_TAGS)
    parser.add_argument(OPTION_CMD_WARN_NONEMPTY_DEST[True], action=ACTION_STORE_TRUE, help=HELP_ARG_WARN_NON_EMPTY_FOLDER)
    parser.add_argument(OPTION_CMD_VERBOSE[True], action=ACTION_STORE_TRUE, help=HELP_ARG_VERBOSE)
    parser.add_argument(OPTION_CMD_CACHE_PROCCED_HTML[True], action=ACTION_STORE_TRUE, help=HELP_ARG_CACHE_HTML_BLOAT)
    parser.add_argument(OPTION_CMD_DOWNMODE_CMD, default=DMODE_DEFAULT, help=HELP_ARG_DOWNLOAD_MODE, choices=DMODE_CHOICES)
    parser.add_argument(OPTION_CMD_DOWNLIMIT_CMD, metavar='#NUMBER', default=0, help=HELP_ARG_DOWNLOAD_LIMIT, type=valid_positive_int)
    parser.add_argument(OPTION_CMD_DOWNLOAD_ORDER[True], action=ACTION_STORE_TRUE, help=HELP_ARG_REVERSE_DOWNLOAD_ORDER)
    parser.add_argument(dest='tags', nargs=ZERO_OR_MORE, help=HELP_ARG_TAGS)
    parsed, unks = parser.parse_known_args(args)
    parsed.tags.extend(unks)  # -tags will be placed here; shove them into parsed tags
    if not parsed.get_maxid and not parsed.tags:
        parser.error('the following arguments are required: tags')
    return parsed

#
#
#########################################
