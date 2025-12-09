# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from .debug import __RUXX_DEBUG__
from .version import APP_NAME, APP_REV_DATE, APP_VERSION

APP_AUTHOR_NICKNAME = 'trickerer'
APP_AUTHOR = f'Dmitriy \'{APP_AUTHOR_NICKNAME}\' Komardin'
APP_ADDRESS = f'github.com/{APP_AUTHOR_NICKNAME}01/{APP_NAME}'
APP_YEARS = '2020-2025'
APP_BUILD_TYPE_STR = 'Debug' if __RUXX_DEBUG__ else 'Release'

# cmdline args help messages
HELP_ARG_HELP = 'Print this message'
HELP_ARG_VERSION = 'Show program version string and exit'
HELP_ARG_MODULE = 'Download module to use, default is \'rx\''
HELP_ARG_DOWNLOAD_MODE = '[Debug] Download mode, default is \'full\''
HELP_ARG_DOWNLOAD_LIMIT = 'Maximum number of posts to download, default is \'0\' (disabled)'
HELP_ARG_REVERSE_DOWNLOAD_ORDER = 'Download in reverse order (highest id to lowest, unless changed by sort:X type tags)'
HELP_ARG_SKIP_IMAGES = 'Skip all images'
HELP_ARG_SKIP_VIDEOS = 'Skip all videos'
HELP_ARG_HIDE_PERSONAL_INFO = 'Mask API key, proxy and other sensitive info in logs'
HELP_ARG_INCLUDE_PARCHI = 'Include all parent posts and all child posts (recursive, downloads whole chain, no filters)'
HELP_ARG_GET_MAXID = 'Print maximum id (for module) and exit'
HELP_ARG_PREFER_WEBM = 'Prefer webm over mp4 when possible'
HELP_ARG_PREFER_MP4 = 'Prefer mp4 over webm when possible'
HELP_ARG_PREFER_LOWRES = 'Prefer low resolution images over the originals'
HELP_ARG_MINDATE = 'Skip everything posted before this date, default is \'01-01-1970\''
HELP_ARG_MAXDATE = 'Skip everything posted after this date, default is \'<today>\''
HELP_ARG_THREADS = 'Maximum simultaneous downloads (affects pages scan too), default is \'1\''
HELP_ARG_PATH = 'Full path to destination folder, default is \'<current folder>\''
HELP_ARG_PROXY = 'Proxy server address'
HELP_ARG_NOPROXY = 'Ignore proxy during this run'
HELP_ARG_PROXYNODOWN = 'Do not use proxy for downloads, only for search'
HELP_ARG_CON_TIMEOUT = 'Connection timeout (in seconds), default is \'10\''
HELP_ARG_CON_RETRIES = 'Connection retries count is case of fail, default is \'10\''
HELP_ARG_API_KEY = 'API authentication info'
HELP_ARG_HEADERS = 'Append additional headers: \'{"name1": "value1", "name2": "value2", etc.}\''
HELP_ARG_COOKIES = 'Append additional cookies: \'{"name1": "value1", "name2": "value2", etc.}\''
HELP_ARG_HEADER = 'Append additional header. May override -headers values. Example: user_agent=googlebot/1.1. Can be used multiple times'
HELP_ARG_COOKIE = 'Append additional cookie. May override -cookies values. Example: shm_user=user1. Can be used multiple times'
HELP_ARG_PREFIX = 'Use module prefix in file names'
HELP_ARG_DUMP_TAGS = 'Save all tags to text file'
HELP_ARG_DUMP_SOURCES = 'Save all found source links to text file'
HELP_ARG_DUMP_COMMENTS = 'Save all found comments to text file'
HELP_ARG_DUMP_PER_ITEM = 'Create tags/sources/comments files for each downloaded file'
HELP_ARG_MERGE_LISTS = 'Merge exising tags/sources/comments files(s) with saved info (only if saving is enabled)'
HELP_ARG_APPEND_SOURCE_AND_TAGS = 'Append a shortened representation of major tags to file name'
HELP_ARG_WARN_NON_EMPTY_FOLDER = 'In GUI mode, warn if download folder is not empty'
HELP_ARG_VERBOSE = 'Enable verbose logging'
HELP_ARG_CACHE_HTML_BLOAT = 'Cache processed HTML instead of raw bytes, can be faster but increases memory usage'
HELP_ARG_TAGS = 'Tags to search for, required'
# GUI help messages
HELP_TAGS_MSG_RX = (
    'Here is a quick list of supported tag patterns:\n\n'
    '\'tag1\'           \tplain text tag\n'
    '\'ta*\'            \ttag starting with \'ta\'\n'
    '\'t*1\'            \ttag starting with \'t\' and ending with \'1\'\n'
    '\'-tag1\'          \texclude tag \'tag1\'\n'
    '\'tag1 tag2\'      \ttag1 AND tag2\n'
    '\'(tag1~tag2)\'    \ttag1 OR tag2 (can be chained)\n'
    '\'-(tag1,tag2)\'   \tNOT BOTH tag1 AND tag2 (can be chained)\n'
    '\'tag:value\'      \tmeta tags (id:999999, score:>=1337, etc.)\n'
)
HELP_TAGS_MSG_RN = (
    'Here is a quick list of supported tag patterns:\n\n'
    '\'tag1\'           \tplain text tag\n'
    '\'ta*\'            \ttag starting with \'ta\'\n'
    '\'t*1\'            \ttag starting with \'t\' and ending with \'1\'\n'
    '\'-tag1\'          \texclude tag \'tag1\'\n'
    '\'tag1 tag2\'      \ttag1 AND tag2\n'
    '\'(tag1~tag2)\'    \ttag1 OR tag2 (can be chained)\n'
    '\'-(tag1,tag2)\'   \tNOT BOTH tag1 AND tag2 (can be chained)\n'
    '\'tag=value\'      \tmeta tags (id<999999, score>=1337, etc.)\n'
)
HELP_TAGS_MSG_RS = HELP_TAGS_MSG_RX
HELP_TAGS_MSG_RP = HELP_TAGS_MSG_RN
HELP_TAGS_MSG_EN = (
    'Here is a quick list of supported tag patterns:\n\n'
    '\'tag1\'           \tplain text tag\n'
    '\'ta*\'            \ttag starting with \'ta\'\n'
    '\'*ag1\'           \ttag ending with \'ag1\'\n'
    '\'t*1\'            \ttag starting with \'t\' and ending with \'1\'\n'
    '\'-tag1\'          \texclude tag \'tag1\'\n'
    '\'tag1 tag2\'      \ttag1 AND tag2\n'
    '\'(tag1~tag2)\'    \ttag1 OR tag2 (can be chained)\n'
    '\'-(tag1,tag2)\'   \tNOT BOTH tag1 AND tag2 (can be chained)\n'
    '\'tag:value\'      \tmeta tags (id:999999, score:>=1337, etc.)\n'
)
HELP_TAGS_MSG_XB = HELP_TAGS_MSG_RX
HELP_TAGS_MSG_BB = HELP_TAGS_MSG_RX
ABOUT_MSG = (f'{APP_NAME} version {APP_VERSION} ({APP_REV_DATE}) {APP_BUILD_TYPE_STR}\n'
             f'\N{copyright sign} {APP_YEARS} {APP_AUTHOR}\n<{APP_ADDRESS}>')
# end help messages

#
#
#########################################
