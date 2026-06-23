#!/usr/bin/env sh
set -eu
SCOPE="${1:-user}"
python3 tools/install.py --scope "$SCOPE"
