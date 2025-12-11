# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from argparse import ZERO_OR_MORE, ArgumentParser, Namespace

from .defines import (
    ACTION_APPEND,
    ACTION_STORE_TRUE,
    DEFAULT_HEADERS,
    DMODE_CHOICES,
    DMODE_DEFAULT,
    MODULE_ABBR_RX,
    MODULE_CHOICES,
    THREADS_MAX_ITEMS,
)
from .gui_defines import (
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
from .help import (
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
from .module import ProcModule
from .validators import (
    valid_api_key,
    valid_date,
    valid_folder_path,
    valid_json,
    valid_kwarg,
    valid_positive_int,
    valid_proxy,
    valid_thread_count,
)
from .vcs import APP_NAME, APP_VERSION

__all__ = ('prepare_arglist',)

MODULE = APP_NAME.replace('-', '_')
INDENT = ' ' * 7

PARSER_TITLE_NONE = ''
PARSER_TITLE_CMD = 'cmd'
PARSER_PARAM_PARSER_TYPE = 'zzzparser_type'
PARSER_PARAM_PARSER_TITLE = 'zzzparser_title'

PARSER_TITLE_NAMES_REMAP: dict[str, str] = {
}

DEFAULT_PATH = valid_folder_path('.')


def create_parsers() -> dict[str, ArgumentParser]:
    def create_parser(sub, name: str, description: str) -> ArgumentParser:
        if sub:
            parser: ArgumentParser = sub.add_parser(PARSER_TITLE_NAMES_REMAP.get(name, name), description=description, add_help=False)
            parser.set_defaults(**{PARSER_PARAM_PARSER_TITLE: name})
        else:
            parser = ArgumentParser(add_help=False, prog=MODULE)
        parser.set_defaults(**{PARSER_PARAM_PARSER_TYPE: parser})
        assert name not in parsers
        parsers[name] = parser
        return parser

    def create_subparser(parser: ArgumentParser, title: str, dest: str):
        return parser.add_subparsers(required=True, title=title, dest=dest, prog=MODULE)

    parsers: dict[str, ArgumentParser] = {}

    parser_main = create_parser(None, PARSER_TITLE_NONE, '')
    subs_main = create_subparser(parser_main, 'subcommands', 'subcommand_1')

    _ = create_parser(subs_main, PARSER_TITLE_CMD, '')
    return parsers


def add_common_args(par: ArgumentParser) -> None:
    op = par.add_argument_group(title='options')
    op.add_argument(OPTION_CMD_MODULE_CMD, default=MODULE_ABBR_RX, help=HELP_ARG_MODULE, choices=MODULE_CHOICES)
    op.add_argument(dest='tags', nargs=ZERO_OR_MORE, action='extend', help=HELP_ARG_TAGS)
    co = par.add_argument_group(title='connection options')
    co.add_argument(OPTION_CMD_PROXY_CMD, metavar='#type://[user:pass@]a.d.d.r:port', help=HELP_ARG_PROXY, type=valid_proxy)
    co.add_argument(OPTION_CMD_IGNORE_PROXY[True], action=ACTION_STORE_TRUE, help=HELP_ARG_NOPROXY)
    co.add_argument(OPTION_CMD_PROXY_NO_DOWNLOAD[True], action=ACTION_STORE_TRUE, help=HELP_ARG_PROXYNODOWN)
    co.add_argument(OPTION_CMD_TIMEOUT_CMD, metavar='#NUMBER', help=HELP_ARG_CON_TIMEOUT, type=valid_positive_int)
    co.add_argument(OPTION_CMD_RETRIES_CMD, metavar='#NUMBER', help=HELP_ARG_CON_RETRIES, type=valid_positive_int)
    co.add_argument(OPTION_CMD_HEADERS_CMD, metavar='#JSON', help=HELP_ARG_HEADERS, type=valid_json, default=DEFAULT_HEADERS)
    co.add_argument(OPTION_CMD_COOKIES_CMD, metavar='#JSON', help=HELP_ARG_COOKIES, type=valid_json)
    co.add_argument(OPTION_CMD_HEADERS_CMD[:-1], metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_HEADER, type=valid_kwarg)
    co.add_argument(OPTION_CMD_COOKIES_CMD[:-1], metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_COOKIE, type=valid_kwarg)
    co.add_argument(OPTION_CMD_CACHE_PROCCED_HTML[True], action=ACTION_STORE_TRUE, help=HELP_ARG_CACHE_HTML_BLOAT)
    au = par.add_argument_group(title='authentication options')
    au.add_argument(OPTION_CMD_APIKEY_CMD, metavar='#KEY,USER_ID', help=HELP_ARG_API_KEY, type=valid_api_key)
    do = par.add_argument_group(title='download options')
    do.add_argument(OPTION_CMD_PATH_CMD, metavar='#PATH', default=DEFAULT_PATH, help=HELP_ARG_PATH, type=valid_folder_path)
    do.add_argument(OPTION_CMD_PARCHI[True], action=ACTION_STORE_TRUE, help=HELP_ARG_INCLUDE_PARCHI)
    do.add_argument(OPTION_CMD_IMAGES[0], action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_IMAGES)
    do.add_argument(OPTION_CMD_VIDEOS[0], action=ACTION_STORE_TRUE, help=HELP_ARG_SKIP_VIDEOS)
    dom1 = do.add_mutually_exclusive_group(required=False)
    dom1.add_argument(OPTION_CMD_VIDEOS[1], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_MP4)
    dom1.add_argument(OPTION_CMD_VIDEOS[2], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_WEBM)
    do.add_argument(OPTION_CMD_IMAGES[1], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFER_LOWRES)
    do.add_argument(OPTION_CMD_THREADING_CMD, metavar=f'1..{THREADS_MAX_ITEMS:d}', help=HELP_ARG_THREADS, type=valid_thread_count)
    doex = par.add_argument_group(title='extra download options')
    doex.add_argument(OPTION_CMD_SAVE_TAGS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_TAGS)
    doex.add_argument(OPTION_CMD_SAVE_SOURCES[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_SOURCES)
    doex.add_argument(OPTION_CMD_SAVE_COMMENTS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_COMMENTS)
    doexm1 = doex.add_mutually_exclusive_group(required=False)
    doexm1.add_argument(OPTION_CMD_INFO_SAVE_MODE[1], action=ACTION_STORE_TRUE, help=HELP_ARG_DUMP_PER_ITEM)
    doexm1.add_argument(OPTION_CMD_INFO_SAVE_MODE[2], action=ACTION_STORE_TRUE, help=HELP_ARG_MERGE_LISTS)
    doex.add_argument(OPTION_CMD_DOWNLIMIT_CMD, metavar='#NUMBER', default=0, help=HELP_ARG_DOWNLOAD_LIMIT, type=valid_positive_int)
    doex.add_argument(OPTION_CMD_DOWNLOAD_ORDER[True], action=ACTION_STORE_TRUE, help=HELP_ARG_REVERSE_DOWNLOAD_ORDER)
    doex.add_argument(OPTION_CMD_DOWNMODE_CMD, default=DMODE_DEFAULT, help=HELP_ARG_DOWNLOAD_MODE, choices=DMODE_CHOICES)
    dofi = par.add_argument_group(title='filtering options')
    dofi.add_argument(OPTION_CMD_DATEAFTER_CMD, metavar='#DD-MM-YYYY', help=HELP_ARG_MINDATE, type=valid_date)
    dofi.add_argument(OPTION_CMD_DATEBEFORE_CMD, metavar='#DD-MM-YYYY', help=HELP_ARG_MAXDATE, type=valid_date)
    dona = par.add_argument_group(title='naming options')
    dona.add_argument(OPTION_CMD_FNAMEPREFIX[True], action=ACTION_STORE_TRUE, help=HELP_ARG_PREFIX)
    dona.add_argument(OPTION_CMD_APPEND_SOURCE_AND_TAGS[True], action=ACTION_STORE_TRUE, help=HELP_ARG_APPEND_SOURCE_AND_TAGS)
    lo = par.add_argument_group(title='logging options')
    lo.add_argument(OPTION_CMD_VERBOSE[True], action=ACTION_STORE_TRUE, help=HELP_ARG_VERBOSE)
    mi = par.add_argument_group(title='misc options')
    mi.add_argument(OPTION_CMD_WARN_NONEMPTY_DEST[True], action=ACTION_STORE_TRUE, help=HELP_ARG_WARN_NON_EMPTY_FOLDER)
    mi.add_argument(OPTION_CMD_HIDE_PERSONAL_INFO[True], action=ACTION_STORE_TRUE, help=HELP_ARG_HIDE_PERSONAL_INFO)
    ut = par.add_argument_group(title='utilities')
    ut.add_argument(OPTION_CMD_GET_MAXID_CMD, action=ACTION_STORE_TRUE, help=HELP_ARG_GET_MAXID)


def add_help(par: ArgumentParser, is_root: bool):
    mi = par.add_argument_group(title='misc')
    mi.add_argument('--help', action='help', help=HELP_ARG_HELP)
    if is_root:
        mi.add_argument('--version', action='version', help=HELP_ARG_VERSION, version=f'{APP_NAME} {APP_VERSION}')


def prepare_arglist(args: list[str] | tuple[str, ...]) -> Namespace:
    parsers = create_parsers()
    parser_root = parsers[PARSER_TITLE_NONE]
    pcmd = parsers[PARSER_TITLE_CMD]
    pcmd.usage = f'{MODULE} [-module #module={ProcModule.PROC_MODULE_NAME_DEFAULT}] [options...] tags...'

    [add_common_args(_) for _ in parsers.values()]
    [add_help(_, _ in (parser_root, pcmd)) for _ in parsers.values()]
    return execute_parser(pcmd, args)


def execute_parser(parser: ArgumentParser, args: list[str] | tuple[str, ...]) -> Namespace:
    try:
        assert args
        parsed = validate_parsed(parser, args)
        if not parsed.get_maxid and not parsed.tags:
            parser.error('the following arguments are required: tags')
        return parsed
    except Exception:
        from traceback import format_exc
        parser.error(format_exc())


def validate_parsed(parser: ArgumentParser, args: list[str] | tuple[str, ...]) -> Namespace:
    parsed, unks = parser.parse_known_args(args)
    parsed.tags.extend(unks)
    return parsed

#
#
#########################################
