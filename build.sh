#!/usr/bin/env bash
# this_file: build.sh
set -euo pipefail
cd "$(dirname "$0")"
for argument in "$@"; do
  if [[ "$argument" == "--offline" ]]; then export UV_OFFLINE=true; fi
done
uv venv --allow-existing --python 3.13 .docs-venv
uv pip install --python .docs-venv/bin/python --require-hashes -r src_docs/requirements.txt
export PATH="$PWD/.docs-venv/bin:$PATH"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git show -s --format=%ct HEAD)}"
python -m src_docs.build "$@"
touch docs/.nojekyll
