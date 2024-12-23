# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from __future__ import annotations
from datetime import datetime
from enum import IntEnum, auto, unique


class Comment:
    """
    Comment structure (not saving all the info of course)
    """
    __slots__ = ('author', 'body')

    def __init__(self, author: str, body: str) -> None:
        self.author: str = author
        self.body: str = body

    def __str__(self) -> str:
        return f'{self.author}:\n{self.body}'

    def __repr__(self) -> str:
        return str(self)


class ItemInfo:
    """
    Used to store universal info for processed item
    """
    __slots__ = ('id', 'height', 'width', 'tags', 'ext', 'source', 'comments', 'score', 'has_children', 'parent_id')
    optional_slots = frozenset(__slots__[__slots__.index('source'):])

    def __init__(self) -> None:
        self.id: str = ''
        self.height: str = ''
        self.width: str = ''
        self.tags: str = ''
        self.ext: str = ''
        self.source: str = ''
        self.comments: list[Comment] = list()
        self.score: str = ''
        self.has_children: str = ''
        self.parent_id: str = ''

    def __lt__(self, other) -> bool:
        return int(self.id or 0) < int(other.id or 0)


class PageCheck:
    """
    PageCheck\n
    Used to store page items check info for binary page search subchecks\n
    first x ... x last
    """
    __slots__ = ('first', 'last')

    def __init__(self) -> None:
        self.first: bool = False
        self.last: bool = False

    def __str__(self) -> str:
        return f'{self.first} <--> {self.last}'

    def __repr__(self) -> str:
        return str(self)


# PyCharm bug PY-53388 (IDE thinks auto() needs an argument / Python 3.9.x)
# noinspection PyArgumentList
@unique
class DownloaderStates(IntEnum):
    IDLE = 0
    LAUNCHING = auto()
    SEARCHING = auto()
    SCANNING_PAGES1 = auto()
    SCANNING_PAGES2 = auto()
    FILTERING_ITEMS1 = auto()
    FILTERING_ITEMS2 = auto()
    FILTERING_ITEMS3 = auto()
    FILTERING_ITEMS4 = auto()
    DOWNLOADING = auto()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}.{self.name} ({self.value:d})'


PROGRESS_BAR_PCT = {
    DownloaderStates.SEARCHING: 0.005,
    DownloaderStates.SCANNING_PAGES1: 0.005,
    DownloaderStates.SCANNING_PAGES2: 0.005,
    DownloaderStates.FILTERING_ITEMS1: 0.005,
    DownloaderStates.FILTERING_ITEMS2: 0.005,
    DownloaderStates.FILTERING_ITEMS3: 0.005,
    DownloaderStates.FILTERING_ITEMS4: 0.005,
    DownloaderStates.DOWNLOADING: 0.965
}
assert sum(v for v in PROGRESS_BAR_PCT.values()) == 1.000


PROGRESS_BAR_MAX = 1000000000


def max_progress_value_for_state(state: DownloaderStates) -> float:
    return PROGRESS_BAR_MAX * PROGRESS_BAR_PCT.get(state, 1.0)


PROGRESS_VALUE_DOWNLOAD = max_progress_value_for_state(DownloaderStates.DOWNLOADING)
PROGRESS_VALUE_NO_DOWNLOAD = PROGRESS_BAR_MAX - PROGRESS_VALUE_DOWNLOAD


class DownloadModes:
    FULL = 'full'
    SKIP = 'skip'
    TOUCH = 'touch'


DMODE_DEFAULT = DownloadModes.FULL
DMODE_CHOICES = (DownloadModes.FULL, DownloadModes.SKIP, DownloadModes.TOUCH)

STATE_WORK_START = DownloaderStates.SEARCHING


STATUSBAR_INFO_MAP: dict[DownloaderStates, tuple[str, str | None, str | None, str | None]] = {
    DownloaderStates.IDLE: ('Ready', None, None, None),
    DownloaderStates.LAUNCHING: ('Launching...', None, None, None),
    DownloaderStates.SEARCHING: ('Searching...', None, None, None),
    DownloaderStates.SCANNING_PAGES1: ('Filtering pages (1/2)... ', 'total_pages', None, None),
    DownloaderStates.SCANNING_PAGES2: ('Filtering pages (2/2)... ', 'total_pages', None, None),
    DownloaderStates.FILTERING_ITEMS1: ('Filtering files (1/4)... ', 'total_count', None, None),
    DownloaderStates.FILTERING_ITEMS2: ('Filtering files (2/4)... ', 'total_count', None, None),
    DownloaderStates.FILTERING_ITEMS3: ('Filtering files (3/4)... ', 'total_count', None, None),
    DownloaderStates.FILTERING_ITEMS4: ('Filtering files (4/4)... ', 'total_count', None, None),
    DownloaderStates.DOWNLOADING: ('Downloading... ', 'processed_count', ' / ', 'total_count_all')
}

CONNECT_TIMEOUT_BASE = 10
CONNECT_RETRIES_BASE = 10
CONNECT_RETRIES_CHUNK = 5

THREADS_MAX_ITEMS = 8
DOWNLOAD_CHUNK_SIZE = 2097152  # 2 Mb
WRITE_CHUNK_SIZE = 524288  # 512 Kb

SITENAME_B_RX = 'aHR0cHM6Ly9hcGkucnVsZTM0Lnh4eC8='
SITENAME_B_RN = 'aHR0cHM6Ly9ydWxlMzRoZW50YWkubmV0Lw=='
SITENAME_B_RS = 'aHR0cHM6Ly9ydWxlMzQudXMv'
SITENAME_B_RP = 'aHR0cHM6Ly9ydWxlMzQucGFoZWFsLm5ldC8='
SITENAME_B_EN = 'aHR0cHM6Ly9lNjIxLm5ldC8='
SITENAME_B_XB = 'aHR0cHM6Ly94Ym9vcnUuY29tLw=='
MESSAGE_EMPTY_SEARCH_RESULT_RX = 'Tm9ib2R5IGhlcmUgYnV0IHVzIGNoaWNrZW5zIQ=='
MESSAGE_EMPTY_SEARCH_RESULT_RN = 'Tm8gaW1hZ2VzIHdlcmUgZm91bmQgdG8gbWF0Y2ggdGhlIHNlYXJjaCBjcml0ZXJpYQ=='
SOURCE_DEFAULT = 'Unknown'
FILE_NAME_FULL_MAX_LEN = 240
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Goanna/6.7 Firefox/102.0 PaleMoon/33.3.1'
DEFAULT_HEADERS = f'{{"User-Agent": "{USER_AGENT}"}}'
PROXY_DEFAULT_STR = '127.0.0.1:222'
UTF8 = 'utf-8'

MODULE_ABBR_RX = 'rx'
MODULE_ABBR_RN = 'rn'
MODULE_ABBR_RS = 'rs'
MODULE_ABBR_RP = 'rp'
MODULE_ABBR_EN = 'en'
MODULE_ABBR_XB = 'xb'
FILE_NAME_PREFIX_RX = f'{MODULE_ABBR_RX}_'
FILE_NAME_PREFIX_RN = f'{MODULE_ABBR_RN}_'
FILE_NAME_PREFIX_RS = f'{MODULE_ABBR_RS}_'
FILE_NAME_PREFIX_RP = f'{MODULE_ABBR_RP}_'
FILE_NAME_PREFIX_EN = f'{MODULE_ABBR_EN}_'
FILE_NAME_PREFIX_XB = f'{MODULE_ABBR_XB}_'
TAGS_CONCAT_CHAR_RX = '+'
TAGS_CONCAT_CHAR_RN = '+'
TAGS_CONCAT_CHAR_RS = '+'
TAGS_CONCAT_CHAR_RP = ' '
TAGS_CONCAT_CHAR_EN = '+'
TAGS_CONCAT_CHAR_XB = '+'
ID_VALUE_SEPARATOR_CHAR_RX = ':'
ID_VALUE_SEPARATOR_CHAR_RN = '='
ID_VALUE_SEPARATOR_CHAR_RS = ':'
ID_VALUE_SEPARATOR_CHAR_RP = '='
ID_VALUE_SEPARATOR_CHAR_EN = ':'
ID_VALUE_SEPARATOR_CHAR_XB = ':'
MODULE_CHOICES = (MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS, MODULE_ABBR_RP, MODULE_ABBR_EN, MODULE_ABBR_XB)

DATE_MIN_DEFAULT = '01-01-1970'
FMT_DATE = '%d-%m-%Y'
LAUCH_DATE = datetime.today().date()
DATE_MAX_DEFAULT = LAUCH_DATE.strftime(FMT_DATE)
ITEMS_PER_PAGE_RX = 1000  # fixed 42 for html, up to 1000 for dapi
ITEMS_PER_PAGE_RN = 63  # fixed 63
ITEMS_PER_PAGE_RS = 42  # fixed 42
ITEMS_PER_PAGE_RP = 100  # fixed 70 for html, up to 100 for api
ITEMS_PER_PAGE_EN = 320  # up to 320 for both html and api
ITEMS_PER_PAGE_XB = 1000  # fixed 42 for html, up to 1000 for dapi
TAG_AUTOCOMPLETE_LENGTH_MIN = 2
TAG_AUTOCOMPLETE_NUMBER_MAX = 7
TAG_LENGTH_MIN = 4
TAG_LENGTH_MAX_RX = 9
TAG_LENGTH_MAX_RN = 21
TAGS_STRING_LENGTH_MAX_RX = 3300  # '4000 after all special symbols encoded', longer tags string will always return empty result
TAGS_STRING_LENGTH_MAX_RN = 300  # real value is unknown, tested up to 2400 but longer strings take forever to process serverside
TAGS_STRING_LENGTH_MAX_RS = 7000  # real value is unknown, last tested: 6600
TAGS_STRING_LENGTH_MAX_RP = 300  # real value is unknown, has max tags limit
TAGS_STRING_LENGTH_MAX_EN = 3300  # real value is unknown, has max tags limit
TAGS_STRING_LENGTH_MAX_XB = 3300  # real value is unknown, assumed RX limits

ACTION_STORE_TRUE = 'store_true'
ACTION_APPEND = 'append'

PLATFORM_WINDOWS = 'win32'
PLATFORM_LINUX = 'linux'
# PLATFORM_DARWIN = 'darwin'  # Mac

SUPPORTED_PLATFORMS = {PLATFORM_WINDOWS, PLATFORM_LINUX}  # , PLATFORM_DARWIN

KNOWN_EXTENSIONS_VID = ('mp4', 'webm')
KNOWN_EXTENSIONS_IMG = ('swf', 'png', 'jpg', 'jpeg', 'gif')
KNOWN_EXTENSIONS = KNOWN_EXTENSIONS_VID + KNOWN_EXTENSIONS_IMG
KNOWN_EXTENSIONS_STR = ' '.join(f'*.{e}' for e in KNOWN_EXTENSIONS)

INT_BOUNDS_DEFAULT = (0, 0)

FILE_NAME_ALIASES = 'all_tag_aliases.json'


class ThreadInterruptException(Exception):
    pass


class Mem:
    KB: int = 1024
    MB: int = KB * 1024
    GB: int = MB * 1024


# PyCharm bug PY-53388 (IDE thinks auto() needs an argument / Python 3.9.x)
# noinspection PyArgumentList
class HtmlCacheMode(IntEnum):
    CACHE_BYTES = auto()
    CACHE_BS = auto()  # cache BeautifulSoup objects

#
#
#########################################
