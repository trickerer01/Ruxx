# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys

# internal
from app_gui import run_ruxx_gui

__all__ = ('run_gui',)


def run_gui() -> None:
    run_ruxx_gui()


if __name__ == '__main__':
    run_gui()
    sys.exit(0)

#
#
#########################################
