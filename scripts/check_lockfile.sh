#!/usr/bin/env bash
# Fails if requirements.lock is stale: re-runs the uv command recorded in the
# lockfile's header and compares the result with the committed lock.
set -eu

lock=requirements.lock
command=$(sed -n '2s/^#    //p' "$lock")
case "$command" in
  "uv pip compile "*" -o $lock") ;;
  *) echo "Unexpected command in $lock header: $command" >&2; exit 2 ;;
esac

fresh=$(mktemp)
trap 'rm -f "$fresh"' EXIT
# Same command, but written to a temp file so the committed lock isn't used
# as a source of version preferences.
eval "${command% -o "$lock"} --quiet -o \"\$fresh\""

if ! diff -u <(grep -v '^#' "$lock") <(grep -v '^#' "$fresh"); then
  echo "$lock is out of date. Regenerate it with the command in README.md." >&2
  exit 1
fi
echo "$lock is up to date."
