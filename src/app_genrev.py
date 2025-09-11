# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from datetime import datetime
from os import path

__all__ = ()

CWD = path.abspath(path.curdir).replace('\\', '/')
APP_REV_FILE_PATH = f'{CWD}/src/app_revision.py'
STR_APP_REVISION = 'APP_REVISION = \''
STR_APP_DATE = 'APP_REV_DATE = \''

UTF8 = 'utf-8'


def write_revision_date() -> None:
    with open(APP_REV_FILE_PATH, 'r+', encoding=UTF8) as f:
        lines = f.readlines()
        set_rev = set_date = False
        for idx, line in enumerate(lines):
            if line.startswith(STR_APP_REVISION):
                revision = line[line.find('\'') + 1:line.rfind('\'')]
                lines[idx] = f'{STR_APP_REVISION}{int(revision) + 1:d}\'\n'
                set_rev = True
            elif line.startswith(STR_APP_DATE):
                lines[idx] = f'{STR_APP_DATE}{datetime.today().strftime("%d %b %Y")}\'\n'
                set_date = True
            else:
                continue
            if set_rev is set_date is True:
                break
        f.flush()
        f.seek(0)
        f.truncate()
        f.writelines(lines)


if __name__ == '__main__':
    write_revision_date()

#
#
#########################################
