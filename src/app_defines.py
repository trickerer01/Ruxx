# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# [1, 5, 9] slice notation
# print(list(range(10))[1:10:4])
# print(list(range(10))[-9:10:4])
# print(list(range(10))[1::4])

# def pow_b(n: int, p: int) -> int:
#     return n if (p == 1) else (n * pow_b(n, p - 1)) if (p & 1) else (pow_b(n * n, p // 2))

from enum import IntEnum, auto, unique
from typing import Dict, Tuple, Optional, Set, List


class Comment:
    """
    Comment structure (not saving all the info of course)
    """
    __slots__ = ('author', 'body')

    def __init__(self, author='', body='') -> None:
        self.author = author
        self.body = body

    def __str__(self) -> str:
        return f'{self.author}:\n{self.body}'

    def __repr__(self) -> str:
        return str(self)


class ItemInfo:
    """
    Used to store universal info for processed item
    """
    __slots__ = ('id', 'height', 'width', 'tags', 'ext', 'source', 'comments', 'score', 'has_children', 'parent_id')
    optional_slots = __slots__[__slots__.index('source'):]

    def __init__(self) -> None:
        self.id = ''
        self.height = ''
        self.width = ''
        self.tags = ''
        self.ext = ''
        self.source = ''
        self.comments = []  # type: List[Comment]
        self.score = ''
        self.has_children = ''
        self.parent_id = ''


class PageCheck:
    """
    PageCheck
    Used to store page items check info for binary page search subchecks
    first x ... x last
    """
    __slots__ = ('first', 'last')

    def __init__(self) -> None:
        self.first = False
        self.last = False


@unique
class DownloaderStates(IntEnum):
    STATE_IDLE = 0
    STATE_SEARCHING = auto()
    STATE_SCANNING_PAGES1 = auto()
    STATE_SCANNING_PAGES2 = auto()
    STATE_FILTERING_ITEMS1 = auto()
    STATE_FILTERING_ITEMS2 = auto()
    STATE_FILTERING_ITEMS3 = auto()
    STATE_FILTERING_ITEMS4 = auto()
    STATE_DOWNLOADING = auto()
    MAX_STATES = auto()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}.{self._name_} ({self.value:d})'


PROGRESS_BAR_PCT = {
    DownloaderStates.STATE_SEARCHING: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES1: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES2: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS1: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS2: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS3: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS4: 0.005,
    DownloaderStates.STATE_DOWNLOADING: 0.965
}
assert sum(v for v in PROGRESS_BAR_PCT.values()) == 1.000


PROGRESS_BAR_MAX = 1000000000


def max_progress_value_for_state(state: DownloaderStates) -> float:
    return PROGRESS_BAR_MAX * PROGRESS_BAR_PCT.get(state)


PROGRESS_VALUE_DOWNLOAD = max_progress_value_for_state(DownloaderStates.STATE_DOWNLOADING)
PROGRESS_VALUE_NO_DOWNLOAD = PROGRESS_BAR_MAX - PROGRESS_VALUE_DOWNLOAD


@unique
class DownloadModes(IntEnum):
    DOWNLOAD_FULL = 0
    DOWNLOAD_SKIP = auto()
    DOWNLOAD_TOUCH = auto()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}.{self._name_} ({self.value:d})'


DMODE_DEFAULT = DownloadModes.DOWNLOAD_FULL
DMODE_CHOICES = {dm.value for dm in DownloadModes.__members__.values()}  # type: Set[int]

STATE_WORK_START = DownloaderStates.STATE_SEARCHING


STATUSBAR_INFO_MAP = {
    DownloaderStates.STATE_IDLE: ('Ready', None, None, None),
    DownloaderStates.STATE_SEARCHING: ('Searching...', None, None, None),
    DownloaderStates.STATE_SCANNING_PAGES1: ('Filtering pages (1/2)... ', 'total_pages', None, None),
    DownloaderStates.STATE_SCANNING_PAGES2: ('Filtering pages (2/2)... ', 'total_pages', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS1: ('Filtering files (1/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS2: ('Filtering files (2/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS3: ('Filtering files (3/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS4: ('Filtering files (4/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_DOWNLOADING: ('Downloading... ', 'processed_count', ' / ', 'total_count_all')
}  # type: Dict[DownloaderStates, Tuple[str, Optional[str], Optional[str], Optional[str]]]


CONNECT_TIMEOUT_BASE = 10
CONNECT_RETRIES_PAGE = 10
CONNECT_RETRIES_ITEM = 10
CONNECT_RETRIES_CHUNK = 5

THREADS_MAX_ITEMS = 8
DOWNLOAD_CHUNK_SIZE = 2097152  # 2 Mb
WRITE_CHUNK_SIZE = 524288  # 512 Kb

SITENAME_B_RX = 'aHR0cHM6Ly9hcGkucnVsZTM0Lnh4eC8='
SITENAME_B_RN = 'aHR0cHM6Ly9ydWxlMzRoZW50YWkubmV0Lw=='
SITENAME_B_RS = 'aHR0cHM6Ly9ydWxlMzQudXMv'
MESSAGE_EMPTY_SEARCH_RESULT_RX = 'Tm9ib2R5IGhlcmUgYnV0IHVzIGNoaWNrZW5zIQ=='
MESSAGE_EMPTY_SEARCH_RESULT_RN = 'Tm8gaW1hZ2VzIHdlcmUgZm91bmQgdG8gbWF0Y2ggdGhlIHNlYXJjaCBjcml0ZXJpYQ=='
MESSAGE_EMPTY_SEARCH_RESULT_RS = MESSAGE_EMPTY_SEARCH_RESULT_RX
SOURCE_DEFAULT = 'Unknown'
FILE_NAME_FULL_MAX_LEN = 240
# USER_AGENT = 'Ruxx / 1.1'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Goanna/6.2 Firefox/102.0 PaleMoon/32.3.1'
DEFAULT_HEADERS = f'{{"User-Agent": "{USER_AGENT}"}}'
PROXY_DEFAULT_STR = '127.0.0.1:222'
ENCODING_UTF8 = 'utf-8'
DEFAULT_ENCODING = ENCODING_UTF8

MODULE_ABBR_RX = 'rx'
MODULE_ABBR_RN = 'rn'
MODULE_ABBR_RS = 'rs'
FILE_NAME_PREFIX_RX = f'{MODULE_ABBR_RX}_'
FILE_NAME_PREFIX_RN = f'{MODULE_ABBR_RN}_'
FILE_NAME_PREFIX_RS = f'{MODULE_ABBR_RS}_'
TAGS_CONCAT_CHAR_RX = '+'
TAGS_CONCAT_CHAR_RN = '+'
TAGS_CONCAT_CHAR_RS = '+'
ID_VALUE_SEPARATOR_CHAR_RX = ':'
ID_VALUE_SEPARATOR_CHAR_RN = '='
ID_VALUE_SEPARATOR_CHAR_RS = ':'
MODULE_CHOICES = (MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS)

DATE_MIN_DEFAULT = '01-01-1970'
FMT_DATE = '%d-%m-%Y'
ITEMS_PER_PAGE_RX = 1000  # fixed 42 for html, up to 1000 for dapi
ITEMS_PER_PAGE_RN = 63  # fixed 63
ITEMS_PER_PAGE_RS = 42  # fixed 42
TAG_LENGTH_MIN = 4
TAG_LENGTH_MAX_RX = 9
TAG_LENGTH_MAX_RN = 21
TAG_LENGTH_MAX_RS = 9
TAGS_STRING_LENGTH_MAX_RX = 3300  # longer tags string will always return empty result
TAGS_STRING_LENGTH_MAX_RN = 300  # tested up to 2400 but longer strings take forever to process serverside
TAGS_STRING_LENGTH_MAX_RS = 7000  # actual value is unknown, last tested: 6600

ACTION_STORE_TRUE = 'store_true'

PLATFORM_WINDOWS = 'win32'
PLATFORM_LINUX = 'linux'
# PLATFORM_DARWIN = 'darwin'  # Mac

SUPPORTED_PLATFORMS = {
    PLATFORM_WINDOWS,
    PLATFORM_LINUX,
    # PLATFORM_DARWIN
}

KNOWN_EXTENSIONS = ('mp4', 'webm', 'swf', 'png', 'jpg', 'jpeg', 'gif')
KNOWN_EXTENSIONS_STR = ' '.join(f'*.{e}' for e in KNOWN_EXTENSIONS)


class ThreadInterruptException(Exception):
    pass

#
#
#########################################
