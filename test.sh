#!/bin/sh
# this_file: test.sh
set -eu
cd "$(dirname "$0")"
uv run --no-project --with pytest python -m pytest -q tests "$@"
