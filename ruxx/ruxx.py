# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import sys
from collections.abc import Sequence

from .ruxx_cmd import run_cmd
from .ruxx_gui import run_gui

__all__ = ('ruxx_main',)


def ruxx_main(argv: Sequence[str]) -> None:
    if argv:
        run_cmd(argv)
    else:
        run_gui()


if __name__ == '__main__':
    ruxx_main(sys.argv[1:])
    sys.exit(0)

#
#
#########################################
