import sys

from .ruxx import ruxx_main


def main(argv=None) -> None:
    sys.exit(ruxx_main(argv))


__all__ = ('main',)
