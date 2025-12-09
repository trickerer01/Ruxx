from .ruxx import ruxx_main


def main(argv=None) -> None:
    exit(ruxx_main(argv))


__all__ = ('main',)
