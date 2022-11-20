#!/usr/bin/env bash

set -e -x

time traceback-with-variables render.py

cp template/* dev/

black dev/

python3 -m dev.wast
