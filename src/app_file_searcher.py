# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import os
from contextlib import ExitStack, suppress
from threading import current_thread
from typing import BinaryIO, Literal

from app_defines import KNOWN_EXTENSIONS
from app_utils import normalize_path


def find_duplicated_files(dest_dict: dict[str, list[str]], basepath: str, scan_depth: int, keep: Literal['first', 'last']) -> None:
    class DFileInfo:
        def __init__(self, folder: str, name: str) -> None:
            self.folder: str = normalize_path(folder)
            self.name: str = name

        @property
        def fullpath(self) -> str:
            return f'{self.folder}{self.name}'

    try:
        found_filenames_dict: dict[str, list[str]] = {}
        base_path = normalize_path(basepath)
        read_buffer_size = 16 * 1024

        def scan_folder(base_folder: str, level: int) -> None:
            if os.path.isdir(base_folder):
                dentry: os.DirEntry
                for dentry in os.scandir(base_folder):
                    fullpath = f'{base_folder}{dentry.name}'
                    if dentry.is_dir():
                        fullpath = normalize_path(fullpath)
                        if level < scan_depth:
                            found_filenames_dict[fullpath] = []
                            with suppress(PermissionError):
                                scan_folder(fullpath, level + 1)
                    elif dentry.is_file():
                        ext = os.path.splitext(dentry.name)[1]
                        if ext[1:] in KNOWN_EXTENSIONS:
                            found_filenames_dict[base_folder].append(dentry.name)

        found_filenames_dict[base_path] = []
        scan_folder(base_path, 0)

        filepaths_all = set()
        for dirpath, filenames in found_filenames_dict.items():
            for filename in filenames:
                filepaths_all.add(f'{dirpath}{filename}')

        files_by_size: dict[int, list[DFileInfo]] = {}
        for filepath in filepaths_all:
            fsize = os.path.getsize(filepath)
            if fsize and fsize not in files_by_size:
                files_by_size[fsize] = []
            fsbase_folder, fname = os.path.split(filepath)
            files_by_size[fsize].append(DFileInfo(fsbase_folder, fname))
        for fsz in list(files_by_size.keys()):
            if fsz in files_by_size and len(files_by_size[fsz]) < 2:
                del files_by_size[fsz]

        for filesize, dinfos in files_by_size.items():
            files_list = sorted(dinfos, key=lambda x: x.name, reverse=True)
            with ExitStack() as ctx:
                open_files: list[BinaryIO] = [ctx.enter_context(open(f.fullpath, 'rb')) for f in files_list]
                open_fnames = [f.name for f in open_files]
                exacts = [open_files]
                fidx = 0  # container may get extended during iteration
                while fidx < len(exacts):
                    exacts_fi: list[BinaryIO] = exacts[fidx]
                    if fidx > 0:
                        for bf in exacts_fi:
                            bf.flush()
                            bf.seek(0)
                    while exacts_fi[0].tell() + 1 < filesize and len(exacts_fi) > 1:
                        rbyteslist = [bf.read(read_buffer_size) for bf in exacts_fi]
                        nexacts = [exacts_fi[ri] for ri in range(1, len(rbyteslist)) if rbyteslist[ri] != rbyteslist[0]]
                        for nex in nexacts:
                            exacts_fi.remove(nex)
                        if len(nexacts) > 1:
                            exacts.append(nexacts)
                    if len(exacts_fi) > 1:
                        if keep == 'first':
                            exacts_fi.sort(key=lambda x: x.name)
                        dfinfos = [files_list[open_fnames.index(exacts_fi[fli].name)] for fli in range(len(exacts_fi))]
                        dest_dict[dfinfos[0].fullpath] = [dfinfos[_].fullpath for _ in range(1, len(dfinfos))]
                    fidx += 1
    finally:
        if hasattr(current_thread(), 'killed'):
            current_thread().killed = True

#
#
#########################################
