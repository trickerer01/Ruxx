# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import sys

from ruxx_cmd import run_cmd
from ruxx_gui import run_gui

__all__ = ()


def main() -> None:
    if len(sys.argv) >= 2:
        run_cmd(sys.argv[1:])
    else:
        run_gui()


if __name__ == '__main__':
    main()
    sys.exit(0)

#
#
#########################################
