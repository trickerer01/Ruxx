import sys

from .release import make_release


def main(*_) -> None:
    sys.exit(make_release())


__all__ = ('main',)
