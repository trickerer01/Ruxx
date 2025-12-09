# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import sys

from .gui import run_ruxx_gui

__all__ = ('run_gui',)


def run_gui() -> None:
    run_ruxx_gui()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        run_gui()
        sys.exit(0)
    else:
        print('ERROR: Ruxx cmd arguments found. To run CMD use ruxx_cmd.py')
        sys.exit(-1)

#
#
#########################################
