# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from argparse import ArgumentParser, Namespace, ONE_OR_MORE
from os import path
from typing import Sequence

# internal
from app_defines import MODULE_ABBR_RX, MODULE_ABBR_RN, DEFAULT_HEADERS, ACTION_STORE_TRUE, DMODE_DEFAULT, DMODE_CHOICES
from app_help import (
    HELP_ARG_MODULE, HELP_ARG_DOWNLOAD_MODE, HELP_ARG_DOWNLOAD_LIMIT, HELP_ARG_SKIP_IMAGES, HELP_ARG_SKIP_VIDEOS,
    HELP_ARG_PREFER_WEBM, HELP_ARG_PREFER_LOWRES, HELP_ARG_MINDATE, HELP_ARG_MAXDATE,
    HELP_ARG_THREADS, HELP_ARG_PATH, HELP_ARG_PROXY, HELP_ARG_NOPROXY, HELP_ARG_PROXYNODOWN, HELP_ARG_HEADERS,
    HELP_ARG_COOKIES, HELP_ARG_PREFIX, HELP_ARG_DUMP_TAGS, HELP_ARG_DUMP_SOURCES, HELP_ARG_APPEND_SOURCE_AND_TAGS, HELP_ARG_TAGS,
    HELP_ARG_WARN_NON_EMPTY_FOLDER, HELP_ARG_INCLUDE_PARCHI, HELP_ARG_TIMEOUT,
)
from app_validators import valid_thread_count, valid_date, valid_path, valid_json, valid_download_mode, valid_proxy, valid_positive_int

__all__ = ('prepare_arglist',)

DMODES_STR = str(DMODE_CHOICES).replace(' ', '')


def prepare_arglist(args: Sequence[str]) -> Namespace:
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--help', action='help')
    parser.add_argument('-module', default=MODULE_ABBR_RX, help=HELP_ARG_MODULE, choices=(MODULE_ABBR_RX, MODULE_ABBR_RN))
    parser.add_argument('-include_parchi', action=ACTION_STORE_TRUE, help=HELP_ARG_INCLUDE_PARCHI)
    parser.add_argument('-skip_img', action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_IMAGES)
    parser.add_argument('-skip_vid', action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_VIDEOS)
    parser.add_argument('-webm', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_WEBM)
    parser.add_argument('-lowres', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_LOWRES)
    parser.add_argument('-mindate', metavar='#DD-MM-YYYY', help=HELP_ARG_MINDATE, type=valid_date)
    parser.add_argument('-maxdate', metavar='#DD-MM-YYYY', help=HELP_ARG_MAXDATE, type=valid_date)
    parser.add_argument('-threads', metavar='1..8', help=HELP_ARG_THREADS, type=valid_thread_count)
    parser.add_argument('-path', metavar='#PATH', default=valid_path(path.curdir), help=HELP_ARG_PATH, type=valid_path)
    parser.add_argument('-proxy', metavar='#type://a.d.d.r:port', help=HELP_ARG_PROXY, type=valid_proxy)
    parser.add_argument('-noproxy', action=ACTION_STORE_TRUE, help=HELP_ARG_NOPROXY)
    parser.add_argument('-proxynodown', action=ACTION_STORE_TRUE, help=HELP_ARG_PROXYNODOWN)
    parser.add_argument('-timeout', metavar='#NUMBER', help=HELP_ARG_TIMEOUT, type=valid_positive_int)
    parser.add_argument('-headers', metavar='#JSON', help=HELP_ARG_HEADERS, type=valid_json, default=DEFAULT_HEADERS)
    parser.add_argument('-cookies', metavar='#JSON', help=HELP_ARG_COOKIES, type=valid_json)
    parser.add_argument('-prefix', action=ACTION_STORE_TRUE, help=HELP_ARG_PREFIX)
    parser.add_argument('-dump_tags', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_TAGS)
    parser.add_argument('-dump_sources', action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_SOURCES)
    parser.add_argument('-append_info', action=ACTION_STORE_TRUE, help=HELP_ARG_APPEND_SOURCE_AND_TAGS)
    parser.add_argument('-warn_nonempty', action=ACTION_STORE_TRUE, help=HELP_ARG_WARN_NON_EMPTY_FOLDER)
    parser.add_argument('-dmode', metavar=DMODES_STR, default=DMODE_DEFAULT.value, help=HELP_ARG_DOWNLOAD_MODE, type=valid_download_mode)
    parser.add_argument('-dlimit', metavar='#NUMBER', default=0, help=HELP_ARG_DOWNLOAD_LIMIT, type=valid_positive_int)
    parser.add_argument(dest='tags', nargs=ONE_OR_MORE, help=HELP_ARG_TAGS)

    parsed, unks = parser.parse_known_args(args)
    parsed.tags += unks  # -tags will be placed here; shove them into parsed tags
    return parsed

#
#
#########################################
