# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys
from typing import List

# internal
from app_gui import run_ruxx, run_ruxx_gui

__all__ = ('run', 'run_gui')


def run(args: List[str]) -> None:
    run_ruxx(args)


def run_gui() -> None:
    run_ruxx_gui()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        run(sys.argv[1:])
    else:
        run_gui()
    sys.exit(0)

#
#
#########################################
