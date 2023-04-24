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

from enum import Enum, IntEnum, auto, unique
from typing import Dict, Tuple, Optional


class ItemInfo:
    """
    ItemInfo
    Used to store universal info for processed item
    """
    __slots__ = ('id', 'height', 'width', 'tags', 'ext', 'source', 'score')
    optional_slots = __slots__[__slots__.index('source'):]

    def __init__(self) -> None:
        self.id = ''
        self.height = ''
        self.width = ''
        self.tags = ''
        self.ext = ''
        self.source = ''
        self.score = ''


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
class PageFilterType(Enum):
    MODE_ID = 'id'
    MODE_DATE = 'date'


@unique
class DownloaderStates(IntEnum):
    STATE_IDLE = 0
    STATE_SCANNING_PAGES1 = auto()
    STATE_SCANNING_PAGES2 = auto()
    STATE_SCANNING_PAGES3 = auto()
    STATE_SCANNING_PAGES4 = auto()
    STATE_SCANNING_PAGES5 = auto()
    STATE_SCANNING_PAGES6 = auto()
    STATE_FILTERING_ITEMS1 = auto()
    STATE_FILTERING_ITEMS2 = auto()
    STATE_FILTERING_ITEMS3 = auto()
    STATE_FILTERING_ITEMS4 = auto()
    STATE_DOWNLOADING = auto()
    MAX_STATES = auto()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}.{self._name_} ({self.value:d})'


PROGRESS_BAR_PCT = {
    DownloaderStates.STATE_SCANNING_PAGES1: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES2: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES3: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES4: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES5: 0.005,
    DownloaderStates.STATE_SCANNING_PAGES6: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS1: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS2: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS3: 0.005,
    DownloaderStates.STATE_FILTERING_ITEMS4: 0.005,
    DownloaderStates.STATE_DOWNLOADING: 0.95
}


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
DMODE_CHOICES = {dm.value for dm in DownloadModes.__members__.values()}

STATE_WORK_START = DownloaderStates.STATE_SCANNING_PAGES1


STATUSBAR_INFO_MAP = {
    DownloaderStates.STATE_IDLE: ('Ready', None, None, None),
    DownloaderStates.STATE_SCANNING_PAGES1: ('Searching...', None, None, None),
    DownloaderStates.STATE_SCANNING_PAGES2: ('Filtering pages (1/4)... ', 'total_pages', None, None),
    DownloaderStates.STATE_SCANNING_PAGES3: ('Filtering pages (2/4)... ', 'total_pages', None, None),
    DownloaderStates.STATE_SCANNING_PAGES4: ('Filtering pages (3/4)... ', 'total_pages', None, None),
    DownloaderStates.STATE_SCANNING_PAGES5: ('Filtering pages (4/4)... ', 'total_pages', None, None),
    DownloaderStates.STATE_SCANNING_PAGES6: ('Preparing list... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS1: ('Filtering files (1/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS2: ('Filtering files (2/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS3: ('Filtering files (3/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_FILTERING_ITEMS4: ('Filtering files (4/4)... ', 'total_count', None, None),
    DownloaderStates.STATE_DOWNLOADING: ('Downloading... ', 'processed_count', ' / ', 'total_count')
}  # type: Dict[DownloaderStates, Tuple[str, Optional[str], Optional[str], Optional[str]]]


CONNECT_DELAY_PAGE = 10
CONNECT_RETRIES_PAGE = 10
CONNECT_DELAY_ITEM = 10
CONNECT_RETRIES_ITEM = 10
CONNECT_RETRIES_CHUNK = 3

THREADS_MAX_ITEMS = 8
DOWNLOAD_CHUNK_SIZE = 2097152  # 2 Mb
WRITE_CHUNK_SIZE = 524288  # 512 Kb
LINE_BREAKS_AT = 95

SITENAME_B_RX = 'aHR0cHM6Ly9hcGkucnVsZTM0Lnh4eC8='
SITENAME_B_RN = 'aHR0cHM6Ly9ydWxlMzRoZW50YWkubmV0Lw=='
MESSAGE_EMPTY_SEARCH_RESULT_RX = 'Tm9ib2R5IGhlcmUgYnV0IHVzIGNoaWNrZW5zIQ=='
MESSAGE_EMPTY_SEARCH_RESULT_RN = 'Tm8gaW1hZ2VzIHdlcmUgZm91bmQgdG8gbWF0Y2ggdGhlIHNlYXJjaCBjcml0ZXJpYQ=='
SOURCE_DEFAULT = 'Unknown'
FILE_NAME_FULL_MAX_LEN = 240
# USER_AGENT = 'Ruxx / 1.1'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686; rv:102.0) Gecko/20100101 Firefox/102.0'
DEFAULT_HEADERS = f'{{"user-agent": "{USER_AGENT}"}}'
PROXY_DEFAULT_STR = '127.0.0.1:222'
ENCODING_UTF8 = 'utf-8'
DEFAULT_ENCODING = ENCODING_UTF8

MODULE_ABBR_RX = 'rx'
MODULE_ABBR_RN = 'rn'
FILE_NAME_PREFIX_RX = f'{MODULE_ABBR_RX}_'
FILE_NAME_PREFIX_RN = f'{MODULE_ABBR_RN}_'
TAGS_CONCAT_CHAR_RX = '+'
TAGS_CONCAT_CHAR_RN = '+'
ID_VALUE_SEPARATOR_CHAR_RX = ':'
ID_VALUE_SEPARATOR_CHAR_RN = '='

DATE_MIN_DEFAULT = '1970-01-01'
# DATE_MAX_DEFAULT = '2100-01-01'
FMT_DATE_DEFAULT = '%Y-%m-%d'
ITEMS_PER_PAGE_RX = 1000  # fixed 42 for html, up to 1000 for dapi
ITEMS_PER_PAGE_RN = 63  # fixed 63
TAG_LENGTH_MIN = 4
TAG_LENGTH_MAX_RX = 9
TAG_LENGTH_MAX_RN = 21
TAGS_STRING_LENGTH_MAX_RX = 3300  # longer tags string will always return empty result
TAGS_STRING_LENGTH_MAX_RN = 300  # tested up to 2400 but longer strings take forever to process serverside
PROXY_HTTP = 'http://'
PROXY_SOCKS5 = 'socks5://'

ACTION_STORE_TRUE = 'store_true'

PLATFORM_WINDOWS = 'Windows'
PLATFORM_LINUX = 'Linux'
# PLATFORM_DARWIN = 'Darwin'  # Mac

SUPPORTED_PLATFORMS = [
    PLATFORM_WINDOWS,
    PLATFORM_LINUX,
    # PLATFORM_DARWIN
]

KNOWN_EXTENSIONS = {'mp4', 'webm', 'swf', 'png', 'jpg', 'jpeg', 'gif'}


class ThreadInterruptException(Exception):
    pass

#
#
#########################################
