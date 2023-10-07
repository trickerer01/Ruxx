# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from app_revision import APP_NAME, APP_VERSION, APP_REV_DATE, __RUXX_DEBUG__

APP_AUTHOR_NICKNAME = 'trickerer'
APP_AUTHOR = f'Dmitriy \'{APP_AUTHOR_NICKNAME}\' Komardin'
APP_ADDRESS = f'github.com/{APP_AUTHOR_NICKNAME}01/{APP_NAME}'
APP_YEARS = '2020-2023'
APP_BUILD_TYPE_STR = 'Debug' if __RUXX_DEBUG__ else 'Release'

# cmdline args help messages
HELP_ARG_HELP = 'Print this message'
HELP_ARG_VERSION = 'Show program\'s version number and exit'
HELP_ARG_MODULE = 'Download module to use, default is \'rx\''
HELP_ARG_DOWNLOAD_MODE = '[Debug] Download mode (full, skip, touch), default is \'full\''
HELP_ARG_DOWNLOAD_LIMIT = '[Debug] Maximum number of files to download, default is \'0\''
HELP_ARG_SKIP_IMAGES = 'Skip all images'
HELP_ARG_SKIP_VIDEOS = 'Skip all videos'
HELP_ARG_INCLUDE_PARCHI = 'Include all parent posts and all child posts (recursive, downloads whole chain, no filters)'
HELP_ARG_GET_MAXID = 'Print maximum id (for module) and exit'
HELP_ARG_PREFER_WEBM = '[DEPRECATED] Prefer webm over mp4 when possible'
HELP_ARG_PREFER_LOWRES = 'Prefer low resolution images over the original'
HELP_ARG_MINDATE = 'Skip everything posted before this date, default is \'01-01-1970\''
HELP_ARG_MAXDATE = 'Skip everything posted after this date, default is \'<today>\''
HELP_ARG_THREADS = 'Maximum simultaneous downloads (affects page scans too), default is \'1\''
HELP_ARG_PATH = 'Full path to destination folder, default is \'<current folder>\''
HELP_ARG_PROXY = 'Proxy server address'
HELP_ARG_NOPROXY = 'Ignore proxy during this run'
HELP_ARG_PROXYNODOWN = 'Do not use proxy for downloads, only for search'
HELP_ARG_CON_TIMEOUT = 'Connection timeout (in seconds), default is \'10\''
HELP_ARG_CON_RETRIES = 'Connection retries is case of fail, default is \'10\''
HELP_ARG_HEADERS = 'Append additional headers: \'{"name": "value"}\''
HELP_ARG_COOKIES = 'Append additional cookies: \'{"name": "value"}\''
HELP_ARG_PREFIX = 'Name files using module prefix'
HELP_ARG_DUMP_TAGS = 'Save all tags to text file'
HELP_ARG_DUMP_SOURCES = 'Save all found source links to text file'
HELP_ARG_DUMP_COMMENTS = 'Save all found comments to text file'
HELP_ARG_APPEND_SOURCE_AND_TAGS = 'Append a shortened representation of major tags to file name'
HELP_ARG_WARN_NON_EMPTY_FOLDER = 'In GUI mode, warn if download folder is not empty'
HELP_ARG_TAGS = 'Tags to search for, requred'
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
ABOUT_MSG = f'{APP_NAME} version {APP_VERSION} ({APP_REV_DATE}) {APP_BUILD_TYPE_STR}\n© {APP_YEARS} {APP_AUTHOR}\n<{APP_ADDRESS}>'
# end help messages

#
#
#########################################
