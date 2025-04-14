#!/bin/bash
set -e -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

rm -f /tmp/git-grok.log

test_names=()
for arg in "$@"; do
  test_names+=("-k" "${arg%.py}")
done

if ! python3 -B -m unittest discover -v "${test_names[@]}"; then
  echo
  cat /tmp/git-grok.log
  exit 1
fi
