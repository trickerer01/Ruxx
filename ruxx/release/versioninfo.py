# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import base64
import os

from ruxx.defines import UTF8
from ruxx.help import APP_ADDRESS, APP_AUTHOR_NICKNAME
from ruxx.version import APP_IS_BETA_TEXT, APP_NAME, APP_REVISION, APP_VER_MAJOR, APP_VER_SUB

APP_DOWNLOADER_TYPE = base64.b64decode('cnVsZTM0').decode()

APP_EMBED_VERSION = f'{APP_VER_MAJOR}.{APP_VER_SUB} r{APP_REVISION}{APP_IS_BETA_TEXT}'

APP_VERSION_INFO_FILENAME = 'version_info.txt'
VERSIONINFO_FILE_PATH = f'{os.path.curdir}/{APP_VERSION_INFO_FILENAME}'
APP_VERSION_INFO_CONTENT = (
    f'VSVersionInfo(\n'
    f'  ffi=FixedFileInfo(\n'
    f'    filevers=({APP_VER_MAJOR}, {APP_VER_SUB}, {APP_REVISION}, 0),\n'
    f'    prodvers=(1, 0, 0, 1),\n'
    f'    mask=0x3f,\n'
    f'    flags=0x0,\n'
    f'    OS=0x40004,\n'
    f'    fileType=0x1,\n'
    f'    subtype=0x0,\n'
    f'    date=(0, 0)\n'
    f'    ),\n'
    f'  kids=[\n'
    f'    StringFileInfo(\n'
    f'      [\n'
    f'      StringTable(\n'
    f'        u\'040904B0\',\n'
    f'        [StringStruct(u\'Comments\', u\'Advanced {APP_DOWNLOADER_TYPE} downloader\'),\n'
    f'        StringStruct(u\'FileDescription\', u\'{APP_NAME}\'),\n'
    f'        StringStruct(u\'FileVersion\', u\'{APP_EMBED_VERSION}\'),\n'
    f'        StringStruct(u\'OriginalFilename\', u\'{APP_NAME}.exe\'),\n'
    f'        StringStruct(u\'InternalName\', u\'{APP_NAME}\'),\n'
    f'        StringStruct(u\'LegalCopyright\', u\'{APP_AUTHOR_NICKNAME}@{APP_ADDRESS}\'),\n'
    f'        StringStruct(u\'ProductName\', u\'{APP_NAME}\'),\n'
    f'        StringStruct(u\'ProductVersion\', u\'{APP_EMBED_VERSION}\')])\n'
    f'      ]), \n'
    f'    VarFileInfo([VarStruct(u\'Translation\', [1033, 1200])])\n'
    f'  ]\n'
    f')\n'
)


def generate_versioninfo() -> None:
    with open(VERSIONINFO_FILE_PATH, 'wt', encoding=UTF8) as outfile:
        outfile.write(APP_VERSION_INFO_CONTENT)


if __name__ == '__main__':
    generate_versioninfo()

#
#
#########################################
