#!/bin/sh
# this_file: src_docs/build.sh
set -eu
cd "$(dirname "$0")/.."
if test -z "${SOURCE_DATE_EPOCH:-}"; then
  SOURCE_DATE_EPOCH=$(git show -s --format=%ct HEAD)
fi
export SOURCE_DATE_EPOCH
python -c "from src_docs.build import ROOT, catalogue; catalogue(ROOT)"
properdocs build --strict --clean -f src_docs/mkdocs.yml
touch docs/.nojekyll
