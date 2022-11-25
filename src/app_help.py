# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from app_revision import APP_NAME, APP_VERSION, APP_REV_DATE, __RUXX_DEBUG__

APP_AUTHOR = 'Dmitriy \'trickerer\' Komardin'
APP_YEARS = '2020-2022'
APP_BUILD_TYPE_STR = 'Debug' if __RUXX_DEBUG__ else 'Release'


# cmdline args help messages
HELP_ARG_MODULE = 'download module to use (rx, rn, etc.)'
HELP_ARG_DOWNLOAD_MODE = 'download mode (full, skip, touch)'
HELP_ARG_REVERSE = 'download in reverse order (oldest first)'
HELP_ARG_SKIP_IMAGES = 'skip all images'
HELP_ARG_SKIP_VIDEOS = 'skip all videos'
HELP_ARG_PREFER_WEBM = 'prefer webm over mp4 (when possible)'
HELP_ARG_PREFER_LOWRES = 'prefer low resolution pictures over the original'
HELP_ARG_LOWER_BOUND = 'skip everything below this id'
HELP_ARG_UPPER_BOUND = 'skip everything above this id'
HELP_ARG_MINDATE = 'skip everything posted before this date'
HELP_ARG_MAXDATE = 'skip everything posted after this date'
HELP_ARG_JOBS = 'maximum simultaneous downloads (affects page scans too)'
HELP_ARG_PATH = 'full path to the destination folder, default is current location'
HELP_ARG_PROXY = 'proxy server address'
HELP_ARG_NOPROXY = 'ignore proxy during this run'
HELP_ARG_PROXYNODOWN = 'do not use proxy for downloads, only for search'
HELP_ARG_PROXYSOCKS = 'use SOCKS5 proxy instead of http'
HELP_ARG_HEADERS = 'append additional headers: \'{"name": "value"}\''
HELP_ARG_COOKIES = 'append additional cookies: \'{"name": "value"}\''
HELP_ARG_PREFIX = 'name files using module prefix'
HELP_ARG_DUMP_TAGS = 'save all tags to a text file before downloading'
HELP_ARG_DUMP_SOURCES = 'save all found source links to a text file'
HELP_ARG_APPEND_SOURCE_AND_TAGS = 'append a shortened representation of sources and tags to file name'
HELP_ARG_WARN_NON_EMPTY_FOLDER = 'in GUI mode, warn if download folder is not empty'
HELP_ARG_TAGS = 'tags to search for'
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
    '\'tag:value\'      \tsort tags (id:999999, score:>=1337, etc.)\n'
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
    '\'tag=value\'      \tsort tags (id<999999, score>=1337, etc.)\n'
)
ABOUT_MSG = (
    f'{APP_NAME} version {APP_VERSION} ({APP_REV_DATE}) {APP_BUILD_TYPE_STR}\n'
    f'© {APP_YEARS} {APP_AUTHOR} <https://github.com/trickerer01>'
)
# end help messages

#
#
#########################################
