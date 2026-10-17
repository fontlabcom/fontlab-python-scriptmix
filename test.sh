#!/bin/sh
# this_file: test.sh
set -eu
cd "$(dirname "$0")"
# Supply a wheel/path or published requirement; never guess a development checkout.
: "${SCRIPTMIX_APP_REQUIREMENT:?Set SCRIPTMIX_APP_REQUIREMENT to an updated App wheel (forthcoming 0.2.11), or a stable wheel plus SCRIPTMIX_APP_SOURCE}"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python 3.11 --with pytest \
    --with "$SCRIPTMIX_APP_REQUIREMENT" python -m pytest -q tests "$@"
