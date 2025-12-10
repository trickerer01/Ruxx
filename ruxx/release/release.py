# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import itertools
import os
import pathlib
import shutil
import sys
from subprocess import call as call_subprocess

from ruxx.defines import PLATFORM_WINDOWS
from ruxx.release.versioninfo import VERSIONINFO_FILE_PATH, generate_versioninfo
from ruxx.vcs.debug import __RUXX_DEBUG__
from ruxx.vcs.version import APP_NAME, APP_VERSION

__all__ = ('make_release',)

RUN_TESTS = not __RUXX_DEBUG__

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
BUILD_DIR = ROOT_DIR / 'build'
RELEASE_SRC_DIR = ROOT_DIR / 'dist'
RELEASE_DEST_DIR = ROOT_DIR / 'release'
RELEASE_FILENAME = f'{APP_NAME}{".exe" if sys.platform == PLATFORM_WINDOWS else ""}'
RELEASE_SRC = RELEASE_SRC_DIR / RELEASE_FILENAME
RELEASE_DEST = RELEASE_DEST_DIR / RELEASE_FILENAME
RELEASE_ICON_SIZE = 256

CLEANUP_FILES = (VERSIONINFO_FILE_PATH, ROOT_DIR / f'{APP_NAME}.spec')
CLEANUP_DIRS = (BUILD_DIR, RELEASE_SRC_DIR)

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
        if not RELEASE_SRC.is_file():
            raise FileNotFoundError('2')
    except FileNotFoundError:
        import traceback
        print(traceback.format_exc())
        return
    if RELEASE_DEST.is_file():
        os.remove(RELEASE_DEST)

    shutil.move(RELEASE_SRC, RELEASE_DEST_DIR)


def build_exe() -> None:
    call_subprocess((
        sys.executable, '-m', 'PyInstaller', ROOT_DIR.joinpath('ruxx/__main__.py').as_posix(),
        '--clean', '--log-level', 'DEBUG',
        '-F', '--noupx', '-c', '-y',
        '-n', APP_NAME,
        '-i', f'./images/8_{RELEASE_ICON_SIZE:d}.ico',
        *(itertools.chain.from_iterable(zip(('--exclude-module',) * len(MODULES_EXCLUDED), MODULES_EXCLUDED, strict=True))),
        '--version-file=version_info.txt',
    ))


def cleanup() -> None:
    def report_exc(*_) -> None:
        import traceback
        print(traceback.format_exc())
    for clean_item in CLEANUP_FILES:
        if clean_item.is_file():
            os.remove(clean_item)
    for clean_item in CLEANUP_DIRS:
        if clean_item.is_dir():
            shutil.rmtree(clean_item, onerror=report_exc)


def make_release() -> None:
    if RUN_TESTS is True:
        call_subprocess((
            sys.executable, '-m', 'unittest', ROOT_DIR.joinpath('ruxx/tests/tests.py').as_posix(),
        ))
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
