# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from enum import IntEnum, unique, auto
from os import makedirs, path, rename, stat
from re import compile as re_compile
from typing import TypeVar, Collection, Iterable, Sequence

# internal
from app_defines import Mem
from app_gui_defines import SLASH
from app_utils import Comparable, normalize_path

__all__ = ('FileTypeFilter', 'sort_files_by_type', 'sort_files_by_size', 'sort_files_by_score')

CT = TypeVar('CT', bound=Comparable)


@unique
class FileTypeFilter(IntEnum):
    BY_VIDEO_AUDIO = 1
    BY_EXTENSION = auto()
    INVALID = auto()


def get_threshold_index(thresholds: Collection[CT], val: CT) -> int:
    for i, threshold in enumerate(thresholds):
        if val < threshold:
            return i
    return len(thresholds)  # folder names array size is len(thresholds) + 1


def move_file(old_fullpath: str, new_folder: str, file_name: str) -> None:
    if not path.isdir(new_folder):
        makedirs(new_folder)
    rename(old_fullpath, f'{new_folder}{file_name}')


def sort_files_by_type(files: Iterable[str], filter_type: FileTypeFilter) -> int:
    assert filter_type != FileTypeFilter.INVALID
    moved_count = 0
    for full_path in files:
        try:
            base_path, full_name = path.split(normalize_path(full_path, False))
            ext = path.splitext(full_name)[1][1:]
            if filter_type == FileTypeFilter.BY_EXTENSION:
                sub_name = 'jpg' if ext == 'jpeg' else ext
            else:
                sub_name = 'video' if ext in ('mp4', 'webm') else 'flash' if ext in ('swf',) else 'image'
            move_file(full_path, f'{base_path}{SLASH}{sub_name}{SLASH}', full_name)
            moved_count += 1
        except Exception:
            continue

    return moved_count


def sort_files_by_size(files: Sequence[str], thresholds_mb: Collection[float]) -> int:
    assert all(threshold_mb > 0.01 for threshold_mb in thresholds_mb)
    thresholds_mb = list(sorted(thresholds_mb))
    moved_count = 0
    try:
        base_path = path.split(normalize_path(files[0], False))[0]
        folder_names = [f'size({f"{th - 0.01:.2f}MB-"})' for th in thresholds_mb] + [f'size({f"{thresholds_mb[-1]:.2f}MB+"})']
        for full_path in files:
            try:
                file_size = stat(full_path).st_size
                full_name = path.split(full_path)[1]
                my_folder = folder_names[get_threshold_index(thresholds_mb, file_size / Mem.MB)]
                move_file(full_path, f'{base_path}{SLASH}{my_folder}{SLASH}', full_name)
                moved_count += 1
            except Exception:
                continue
    except Exception:
        pass

    return moved_count


def sort_files_by_score(files: Sequence[str], thresholds: Collection[int]) -> int:
    thresholds = list(sorted(thresholds))
    moved_count = 0
    try:
        base_path = path.split(normalize_path(files[0], False))[0]
        folder_names = [f'score({f"{th - 1:d}-"})' for th in thresholds] + [f'score({f"{thresholds[-1]:d}+"})']
        re_media_scored_name = re_compile(r'^(?:[a-z]{2}_)?(?:\d+?)_score\([-+]?(\d+)\).+?$')
        for full_path in files:
            try:
                full_name = path.split(full_path)[1]
                score = re_media_scored_name.fullmatch(full_name).group(1)
                my_folder = folder_names[get_threshold_index(thresholds, int(score))]
                move_file(full_path, f'{base_path}{SLASH}{my_folder}{SLASH}', full_name)
                moved_count += 1
            except Exception:
                continue
    except Exception:
        pass

    return moved_count

#
#
#########################################
