#!/usr/bin/env bash

cd "$(dirname "$0")"
git add . && git commit -m 'Updating wast' && git push

set -e
rsync -avh dev/ stable/ --delete
