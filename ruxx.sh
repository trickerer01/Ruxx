#!/usr/bin/env sh
exec "${PYTHON:-python3}" -Werror -Xdev "$(dirname "$(realpath "$0")")/ruxx/__main__.py" "$@"
