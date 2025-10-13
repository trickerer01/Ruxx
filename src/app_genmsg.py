# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import sys
from subprocess import check_output

UTF8 = 'utf-8'


def write_commit_msg() -> None:
    msg_file_path = sys.argv[1]
    cur_rev = check_output(('grep.exe', 'src/app_revision.py', '-Po', '-e', r'(?<=APP_REVISION = .)([0-9]+)(?=.+)'),
                           ).decode(errors='replace').strip()
    assert cur_rev.isnumeric(), f'\'{cur_rev}\''
    with open(msg_file_path, 'r+', encoding=UTF8) as f:
        commit_msg = f.read()
        f.flush()
        f.seek(0)
        f.truncate()
        f.write(f'Rev {cur_rev}: {commit_msg}')


if __name__ == '__main__':
    write_commit_msg()

#
#
#########################################
