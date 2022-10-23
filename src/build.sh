#!/usr/bin/env bash

MY_TMP='/tmp/wast_tmp_file'
rm "${MY_TMP}" > /dev/null || true

set -e -x

traceback-with-variables render.py > "${MY_TMP?}"

# runs only on success
cat "${MY_TMP?}" > dev/wast.py

black dev/wast.py

python3 -m dev.wast
