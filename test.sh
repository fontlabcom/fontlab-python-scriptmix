#!/bin/sh
# this_file: test.sh
set -eu
cd "$(dirname "$0")"
# Supply a wheel/path or published requirement; never guess a development checkout.
: "${SCRIPTMIX_APP_REQUIREMENT:?Set SCRIPTMIX_APP_REQUIREMENT to an App wheel or fontlab-fontlabapp>=0.2.10}"
# Optional: space-separated extra requirements, e.g. a Fontport wheel or checkout
# for the feature source tests (fly.fp.feature_blocks).
extra=""
for requirement in ${SCRIPTMIX_EXTRA_REQUIREMENTS:-}; do
    extra="$extra --with $requirement"
done
# $extra is split on purpose: one --with flag per requirement.
# shellcheck disable=SC2086
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python "${SCRIPTMIX_PYTHON:-3.11}" --with pytest --with glyphslib \
    --with "$SCRIPTMIX_APP_REQUIREMENT" $extra python -m pytest -q tests "$@"
