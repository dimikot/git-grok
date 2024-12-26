#!/bin/bash
set -e -o pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

rm -f /tmp/git-grok.log

if ! python3 -B -m unittest discover -v -k "${*:-*}"; then
  echo
  cat /tmp/git-grok.log
  exit 1
fi
