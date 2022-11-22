#!/usr/bin/env bash

set -e -x

if [[ ! "${WAST_VERSION?}" =~ ([0-9]{1,3}\.){2}[0-9](\.post[0-9]{1,9})? ]]
then
    echo "${WAST_VERSION?} is not a valid package version"
    exit 1
fi

/app/build.sh

time sphinx-build -n -b html /app/docs /docs

time sphinx-build -n -b doctest /app/docs /docs
