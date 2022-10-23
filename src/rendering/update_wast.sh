#!/usr/bin/env bash

cd "$(dirname "$0")"
git add . && git commit -m 'Updating wast' && git push

set -e
mkdir tmp_wast_dir
cp -r dev/* tmp_wast_dir

mv tmp_wast_dir stable
