import sys

if not __package__ and not getattr(sys, 'frozen', False):
    import os.path
    path = os.path.abspath(__file__)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(path))))

import ruxx.release

if __name__ == '__main__':
    ruxx.release.main(sys.argv[1:])
