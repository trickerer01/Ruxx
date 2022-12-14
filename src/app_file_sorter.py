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
from re import sub as re_sub
from typing import Tuple, List

# internal
from app_gui_defines import SLASH


@unique
class FileTypeFilter(IntEnum):
    BY_VIDEO_AUDIO = 1
    BY_EXTENSION = auto()
    FILTER_INVALID = auto()


def sort_files_by_type(files: Tuple[str], filter_type: FileTypeFilter) -> int:
    assert filter_type != FileTypeFilter.FILTER_INVALID

    moved_count = 0
    try:
        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            base_path, full_name = tuple(full_path.rsplit(SLASH, 1))
            _, ext = path.splitext(full_name)
            try:
                ext = ext[ext.find('.') + 1:]
                if filter_type == FileTypeFilter.BY_EXTENSION:
                    sub_name = 'jpg' if ext == 'jpeg' else ext
                else:
                    sub_name = 'video' if ext in ['mp4', 'webm'] else 'flash' if ext in ['swf'] else 'image'
                new_folder = f'{base_path}{SLASH}{sub_name}{SLASH}'
                new_path = f'{new_folder}{full_name}'
                if not path.isdir(new_folder):
                    makedirs(new_folder)
                rename(full_path, new_path)
                moved_count += 1
            except Exception:
                continue
    except Exception:
        pass

    return moved_count


def sort_files_by_size(files: Tuple[str], threshold_mb: float) -> int:
    assert threshold_mb > 0.01

    moved_count = 0
    try:
        full_path = files[0].replace('\\', SLASH)
        base_path = full_path[:full_path.rfind(SLASH)]
        new_folder_greater = f'size({threshold_mb:.2f}MB+)'
        new_folder_less = f'size({threshold_mb - 0.01:.2f}MB-)'
        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            full_name = full_path[full_path.rfind(SLASH) + 1:]
            try:
                file_size = stat(full_path).st_size
                my_folder = new_folder_greater if file_size / (1024.0 * 1024.0) >= threshold_mb else new_folder_less
                new_folder = f'{base_path}{SLASH}{my_folder}{SLASH}'
                new_path = f'{new_folder}{full_name}'
                if not path.isdir(new_folder):
                    makedirs(new_folder)
                rename(full_path, new_path)
                moved_count += 1
            except Exception:
                continue
    except Exception:
        pass

    return moved_count


def sort_files_by_score(files: Tuple[str], thresholds: List[int]) -> int:
    thresholds = list(reversed(sorted(thresholds)))
    moved_count = 0
    try:
        full_path = files[0].replace('\\', SLASH)
        base_path = full_path[:full_path.rfind(SLASH)]
        folder_names = [f'score({f"{thresholds[0]:d}+"})'] + [f'score({f"{th - 1:d}-"})' for i, th in enumerate(thresholds)]
        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            full_name = full_path[full_path.rfind(SLASH) + 1:]
            try:
                score = re_sub(r'^(?:[a-z]{2}_)?(?:\d+?)_score\([-+]?(\d+)\).+?$', r'\1', full_name)
                score = int(score)
                my_folder = folder_names[0]  # greatest
                for i, sc in enumerate(thresholds):
                    if score >= sc:
                        break
                    my_folder = folder_names[i + 1]
                new_folder = f'{base_path}{SLASH}{my_folder}{SLASH}'
                new_path = f'{new_folder}{full_name}'
                if not path.isdir(new_folder):
                    makedirs(new_folder)
                rename(full_path, new_path)
                moved_count += 1
            except Exception:
                continue
    except Exception:
        pass

    return moved_count

#
#
#########################################
