#!/usr/bin/env bash
# this_file: release.sh
#
# Release this documentation repository: rebuild the site (./build.sh), then
# commit the regenerated output, bump the vX.Y.Z tag and push both with
# `uvx gitnextver`. GitHub Pages serves main, so the push is the deployment
# trigger; there is no PyPI upload. ./publish.sh runs this.
#
# Usage: ./release.sh            # patch bump (default)
#        ./release.sh minor      # or major

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

BUMP="${1:-patch}"
case "$BUMP" in patch | minor | major) ;; *)
  echo "error: bump must be patch, minor or major, not '$BUMP'" >&2; exit 1 ;;
esac

if git rev-parse -q --verify MERGE_HEAD >/dev/null || [[ -n "$(git diff --name-only --diff-filter=U)" ]]; then
  echo "error: a merge is in progress or files are unmerged; finish it first" >&2
  exit 1
fi
git symbolic-ref -q HEAD >/dev/null || { echo "error: HEAD is detached; check out a branch" >&2; exit 1; }

git fetch -q --tags origin
if git rev-parse -q --verify '@{u}' >/dev/null; then
  git merge -q --ff-only '@{u}' || { echo "error: the branch has diverged from its upstream; reconcile it first" >&2; exit 1; }
fi

./build.sh

match='v[0-9]*.[0-9]*.[0-9]*'
TAG="$(git describe --tags --exact-match --match "$match" HEAD 2>/dev/null || true)"
if [[ -n "$TAG" && -z "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "HEAD is already $TAG"
else
  # Push below, not inside gitnextver, so pre-push hooks show their output.
  args=(--pull=False --push=False --bump="$BUMP")
  if [[ -z "$(git status --porcelain --untracked-files=all)" ]]; then args+=(--commit=False); fi
  uvx gitnextver "${args[@]}"
  TAG="$(git describe --tags --exact-match --match "$match" HEAD 2>/dev/null || true)"
fi
if [[ ! "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "error: no vX.Y.Z tag on HEAD after gitnextver" >&2
  exit 1
fi

BRANCH="$(git symbolic-ref --short HEAD)"
remote_tag="$(git ls-remote origin "refs/tags/$TAG" | cut -f1)"
remote_head="$(git ls-remote origin "refs/heads/$BRANCH" | cut -f1)"
if [[ "$remote_tag" == "$(git rev-parse "refs/tags/$TAG")" && "$remote_head" == "$(git rev-parse HEAD)" ]]; then
  echo "origin already has $BRANCH and $TAG; nothing to push"
else
  echo "Pushing $TAG (pre-push hooks run now and may take a while)"
  git push --atomic origin "HEAD:refs/heads/$BRANCH" "refs/tags/$TAG"
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "error: tracked files changed after the release commit" >&2
  exit 1
fi
echo "Released $TAG"
