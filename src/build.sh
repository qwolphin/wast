#!/usr/bin/env bash

set -e -x

traceback-with-variables render.py > dev/wast.py && black dev/wast.py && python3 -m dev.wast
