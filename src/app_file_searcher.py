# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from contextlib import ExitStack, suppress
from os import path, listdir
from threading import current_thread
from typing import Literal

from app_defines import KNOWN_EXTENSIONS
from app_utils import normalize_path


def find_duplicated_files(dest_dict: dict[str, list[str]], basepath: str, scan_depth: int, keep: Literal['first', 'last']) -> None:
    class DFileInfo:
        def __init__(self, folder: str, name: str, size: int) -> None:
            self.folder: str = normalize_path(folder)
            self.name: str = name
            self.size: int = size

        @property
        def fullpath(self) -> str:
            return f'{self.folder}{self.name}'

    try:
        found_filenames_dict: dict[str, list[str]] = dict()
        base_path = normalize_path(basepath)
        read_buffer_size = 16 * 1024

        def scan_folder(base_folder: str, level: int) -> None:
            if path.isdir(base_folder):
                for cname in listdir(base_folder):
                    fullpath = f'{base_folder}{cname}'
                    if path.isdir(fullpath):
                        fullpath = normalize_path(fullpath)
                        if level < scan_depth:
                            found_filenames_dict[fullpath] = list()
                            with suppress(PermissionError):
                                scan_folder(fullpath, level + 1)
                    elif path.isfile(fullpath):
                        ext = path.splitext(cname)[1]
                        if ext[1:] in KNOWN_EXTENSIONS:
                            found_filenames_dict[base_folder].append(cname)

        found_filenames_dict[base_path] = list()
        scan_folder(base_path, 0)

        filepaths_all = set()
        for dirpath in found_filenames_dict:
            for filename in found_filenames_dict[dirpath]:
                filepaths_all.add(f'{dirpath}{filename}')

        files_by_size: dict[int, list[DFileInfo]] = dict()
        for filepath in filepaths_all:
            fsize = path.getsize(filepath)
            if fsize and fsize not in files_by_size:
                files_by_size[fsize] = list()
            fsbase_folder, fname = path.split(filepath)
            files_by_size[fsize].append(DFileInfo(fsbase_folder, fname, fsize))
        for fsz in list(files_by_size.keys()).copy():
            if fsz in files_by_size and len(files_by_size[fsz]) < 2:
                del files_by_size[fsz]

        for filesize in files_by_size:
            files_list = sorted(files_by_size[filesize], key=lambda x: x.name, reverse=True)
            with ExitStack() as ctx:
                open_files = [ctx.enter_context(open(f.fullpath, 'rb')) for f in files_list]
                open_fnames = [f.name for f in open_files]
                exacts = [open_files]
                fidx = 0
                while fidx < len(exacts):
                    if fidx > 0:
                        for bf in exacts[fidx]:
                            bf.flush()
                            bf.seek(0)
                    while exacts[fidx][0].tell() + 1 < filesize and len(exacts[fidx]) > 1:
                        rbytes = [bf.read(read_buffer_size) for bf in exacts[fidx]]
                        nexacts = list(filter(None, [exacts[fidx][ri] for ri in range(1, len(rbytes)) if rbytes[ri] != rbytes[0]]))
                        for nex in nexacts:
                            exacts[fidx].remove(nex)
                        if len(nexacts) > 1:
                            exacts.append(nexacts)
                    if len(exacts[fidx]) > 1:
                        if keep == 'first':
                            exacts = [sorted(li, key=lambda x: x.name) for li in exacts]
                        dfinfos = [files_list[open_fnames.index(exacts[fidx][fli].name)] for fli in range(len(exacts[fidx]))]
                        dest_dict[dfinfos[0].fullpath] = [dfinfo.fullpath for dfinfo in dfinfos[1:]]
                    fidx += 1
    finally:
        if hasattr(current_thread(), 'killed'):
            current_thread().killed = True

#
#
#########################################
