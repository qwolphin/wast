#!/usr/bin/env bash

set -e -x

time traceback-with-variables render.py 

black dev/wast.py

python3 -m dev.wast
