#!/usr/bin/env bash

set -e -x

time traceback-with-variables render.py

cp template/* wast/

black wast/

python3 -c 'from wast import *'
