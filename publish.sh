#!/usr/bin/env bash
# this_file: publish.sh
#
# Publish this documentation repository. It ships no PyPI package: the site is
# served by GitHub Pages from main, so publishing is ./release.sh (rebuild,
# commit, tag, push), followed by a wait for the docs workflow on that commit.
#
# Usage: ./publish.sh            # patch bump (arguments go to ./release.sh)

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

./release.sh "$@"
SHA="$(git rev-parse HEAD)"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
run=""
for _ in $(seq 1 30); do
  run="$(gh run list -R "$REPO" --commit "$SHA" -L 5 --json databaseId -q '.[0].databaseId // empty')"
  [[ -n "$run" ]] && break
  sleep 2
done
if [[ -z "$run" ]]; then
  echo "error: no workflow run appeared for $SHA; see gh run list -R $REPO" >&2
  exit 1
fi
gh run watch "$run" -R "$REPO" --exit-status
echo "Published $(git describe --tags --exact-match HEAD) ($SHA)"
