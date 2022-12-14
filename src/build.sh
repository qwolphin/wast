#!/usr/bin/env bash

set -e -x

cd /app

mkdir -p wast

if [[ ! "${WAST_VERSION?}" =~ ([0-9]{1,3}\.){2}[0-9](\.post[0-9]{1,9})? ]]
then
    echo "${WAST_VERSION?} is not a valid package version"
    exit 1
fi

time traceback-with-variables render.py

cp template/* wast/

black wast/

python3 -c 'from wast import *'
