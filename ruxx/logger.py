# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import time
from collections.abc import Callable
from locale import getpreferredencoding
from threading import Lock as ThreadLock

from .defines import UTF8
from .utils import find_first_not_of

__all__ = ('Logger', 'trace')


class Logger:
    print_lock: ThreadLock = ThreadLock()

    pending_strings: list[str] = []
    is_cmdline: bool = False
    is_disabled: bool = False
    append_to_window_proc: Callable[[str], None] | None = None

    @staticmethod
    def init(is_cmd: bool, is_disabled=False) -> None:
        Logger.is_cmdline = is_cmd
        Logger.is_disabled = is_disabled

    @staticmethod
    def _prepare(text: str) -> None:
        if Logger.is_cmdline:
            # need to circumvent non-unicode console errors
            try:
                print(text)
            except UnicodeError:
                try:
                    print(text.encode(UTF8, errors='backslashreplace').decode(getpreferredencoding(), errors='backslashreplace'))
                except Exception:
                    print('<Message was not logged due to UnicodeError>')
        else:
            assert Logger.append_to_window_proc, 'Logger window is uninitialized!'
            Logger.append_to_window_proc(f'{text}\n')

    @staticmethod
    def log(message: str, safe: bool, add_timestamp: bool) -> None:
        if Logger.is_disabled:
            return
        if not message:
            return

        if add_timestamp:
            non_n_idx = find_first_not_of(message, '\n')
            textparts = (message[:non_n_idx], message[non_n_idx:]) if non_n_idx != -1 else ('', message)
            message = f'{textparts[0]}[{time.strftime("%X", time.localtime())}] {textparts[1]}'

        if safe:
            with Logger.print_lock:
                Logger._prepare(message)
        else:
            Logger._prepare(message)

    @staticmethod
    def print_pending_strings(safe=False, timestamp=False) -> None:
        for ps in Logger.pending_strings:
            Logger.log(ps, safe, timestamp)
        Logger.pending_strings.clear()


def trace(message: str, safe=False, timestamp=False) -> None:
    Logger.log(message, safe, timestamp)

#
#
#########################################
