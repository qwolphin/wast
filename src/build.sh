#!/usr/bin/env bash

set -e -x

time traceback-with-variables render.py

cp fragments/helpers.py dev/
cp fragments/utils.py dev/
cp fragments/common.py dev/
cp fragments/validators.py dev/
cp fragments/__init__.py dev/

black dev/

python3 -m dev.wast
