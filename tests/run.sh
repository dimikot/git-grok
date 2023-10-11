#!/bin/bash
cd $(dirname "${BASH_SOURCE[0]}")

python3 -B -m unittest discover -s . -p '*_test.py' $@
