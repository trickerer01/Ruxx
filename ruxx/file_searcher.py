# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import os
import pathlib
from contextlib import ExitStack, suppress
from threading import current_thread
from typing import BinaryIO, Literal

from .defines import KNOWN_EXTENSIONS, Mem

READ_BUFFER_SIZE_BASE = 4 * Mem.KB
READ_BUFFER_SIZE_MAX = 256 * Mem.KB
EXTENSIONS_SET = set(KNOWN_EXTENSIONS)


def find_duplicated_files(dest_dict: dict[str, list[pathlib.Path]], basepath: pathlib.Path, scan_depth: int, keep: Literal['first', 'last'],
                          ) -> None:
    try:
        found_files_dict: dict[int, list[os.DirEntry]] = {}

        def scan_folder(base_folder: pathlib.Path, level: int) -> None:
            if base_folder.is_dir():
                with os.scandir(base_folder.as_posix()) as listing:
                    for dentry in listing:
                        if dentry.is_dir():
                            if level < scan_depth:
                                with suppress(PermissionError):
                                    scan_folder(base_folder / dentry.name, level + 1)
                        elif dentry.is_file():
                            ext = os.path.splitext(dentry.name)[1]
                            if ext[1:] in EXTENSIONS_SET:
                                if fsize := dentry.stat().st_size:
                                    if fsize not in found_files_dict:
                                        found_files_dict[fsize] = []
                                    found_files_dict[fsize].append(dentry)

        scan_folder(basepath, 0)
        for fsz in list(found_files_dict.keys()):
            if len(found_files_dict[fsz]) < 2:
                del found_files_dict[fsz]

        for filesize, dentries in found_files_dict.items():
            files_list = sorted(dentries, key=lambda x: x.name, reverse=True)
            with ExitStack() as ctx:
                open_files: list[BinaryIO] = [ctx.enter_context(open(f.path, 'rb')) for f in files_list]
                open_fnames = [f.name for f in open_files]
                exacts = [open_files]
                fidx = 0  # container may get extended during iteration
                while fidx < len(exacts):
                    exacts_fi: list[BinaryIO] = exacts[fidx]
                    if fidx > 0:
                        for bf in exacts_fi:
                            bf.flush()
                            bf.seek(0)
                    read_buffer_size = READ_BUFFER_SIZE_BASE
                    while exacts_fi[0].tell() + 1 < filesize and len(exacts_fi) > 1:
                        rbyteslist = [bf.read(read_buffer_size) for bf in exacts_fi]
                        read_buffer_size = min(read_buffer_size * 2, READ_BUFFER_SIZE_MAX)
                        nexacts = [exacts_fi[ri] for ri in range(1, len(rbyteslist)) if rbyteslist[ri] != rbyteslist[0]]
                        for nex in nexacts:
                            exacts_fi.remove(nex)
                        if len(nexacts) > 1:
                            exacts.append(nexacts)
                    if len(exacts_fi) > 1:
                        if keep == 'first':
                            exacts_fi.sort(key=lambda x: x.name)
                        dfinfos = [files_list[open_fnames.index(exacts_fi[fli].name)] for fli in range(len(exacts_fi))]
                        dest_dict[dfinfos[0].path] = [pathlib.Path(dfinfos[_].path) for _ in range(1, len(dfinfos))]
                    fidx += 1
    finally:
        if hasattr(current_thread(), 'killed'):
            current_thread().killed = True

#
#
#########################################
