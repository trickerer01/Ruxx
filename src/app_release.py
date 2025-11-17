# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import itertools
import os
import shutil
import sys
from subprocess import call as call_subprocess

from app_debug import __RUXX_DEBUG__
from app_defines import PLATFORM_LINUX, PLATFORM_WINDOWS
from app_revision import APP_NAME, APP_VERSION
from app_unittests import run_all_tests
from app_versioninfo import VERSIONINFO_FILE_PATH, generate_versioninfo

__all__ = ()

RUN_TESTS = not __RUXX_DEBUG__ and sys.platform == PLATFORM_LINUX

RELEASE_SRC_DIR = f'{os.path.curdir}/dist/'
RELEASE_DEST_DIR = f'{os.path.curdir}/release/'
RELEASE_FILENAME = f'{APP_NAME}{".exe" if sys.platform == PLATFORM_WINDOWS else ""}'
RELEASE_SRC = f'{RELEASE_SRC_DIR}{RELEASE_FILENAME}'
RELEASE_DEST = f'{RELEASE_DEST_DIR}{RELEASE_FILENAME}'
RELEASE_ICON_SIZE = 256

CLEANUP_FILES = (VERSIONINFO_FILE_PATH, f'{os.path.curdir}/{APP_NAME}.spec')
CLEANUP_DIRS = (f'{os.path.curdir}/build/', f'{os.path.curdir}/dist/')

MODULES_EXCLUDED = (
    'lxml',
    'lxml.etree',
    'lxml.isoschematron',
    'lxml.objectify',
    'asyncio',
    'readline',
    'org',
    'java',
    'java.lang',
    'difflib',
    'distutils',
    'distutils.util',
    'lib2to3',
    'sysconfig',
    'xml',
    'xml.etree.cElementTree',
    'pydoc',
    'aiofile',
    'aiohttp',
    'aiohttp-socks',
    'aiosignal',
    'backports.entry-points-selectable',
    'brotli',
    'colorama',
    'filelock',
    'flake8',
    'mccabe',
    'pycodestyle',
    'pyflakes',
    'ruff',
    'importlib-metadata',
    'zipp',
    'mutagen',
    'packaging',
    'pip',
    'pipdeptree',
    'psutil',
    'pycryptodomex',
    'pyinstaller',
    'altgraph',
    'pyinstaller-hooks-contrib',
    'pywin32-ctypes',
    'setuptools',
    'websockets',
)


def move_exe() -> None:
    try:
        if not os.path.isfile(RELEASE_SRC):
            raise FileNotFoundError('2')
    except FileNotFoundError:
        print(f'{sys.exc_info()[0]!s}: {sys.exc_info()[1]!s}')
        return
    if os.path.isfile(RELEASE_DEST):
        os.remove(RELEASE_DEST)

    shutil.move(RELEASE_SRC, RELEASE_DEST_DIR)


def build_exe() -> None:
    call_subprocess((
        sys.executable, '-m', 'PyInstaller', 'src/ruxx.py',
        '--clean', '--log-level', 'DEBUG',
        '-F', '--noupx', '-c', '-y',
        '-n', APP_NAME,
        '-i', f'./images/8_{RELEASE_ICON_SIZE:d}.ico',
        *(itertools.chain.from_iterable(zip(('--exclude-module',) * len(MODULES_EXCLUDED), MODULES_EXCLUDED, strict=True))),
        '--version-file=version_info.txt',
    ))


def cleanup() -> None:
    def report_exc(*_) -> None:
        print(f'{sys.exc_info()[0]!s}: {sys.exc_info()[1]!s}')
    for clean_item in CLEANUP_FILES:
        if os.path.isfile(clean_item):
            os.remove(clean_item)
    for clean_item in CLEANUP_DIRS:
        if os.path.isdir(clean_item):
            shutil.rmtree(clean_item, onerror=report_exc)


def make_release() -> None:
    if RUN_TESTS is True:
        run_all_tests()
    generate_versioninfo()
    build_exe()
    move_exe()
    cleanup()
    print(f'\n### Version: {APP_VERSION} ###')


if __name__ == '__main__':
    make_release()

#
#
#########################################
