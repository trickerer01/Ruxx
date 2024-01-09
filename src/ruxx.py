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
from ruxx_cmd import run_cmd
from ruxx_gui import run_gui

__all__ = ()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        run_cmd(sys.argv[1:])
    else:
        run_gui()
    sys.exit(0)

#
#
#########################################
