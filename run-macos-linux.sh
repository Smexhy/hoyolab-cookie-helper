#!/bin/sh
set -eu

cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1 || \
    ! python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    echo "Python 3.9 or newer was not found."
    echo "macOS: https://www.python.org/downloads/macos/"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv"
    exit 1
fi

if [ ! -x .venv/bin/python ]; then
    echo "Preparing the helper..."
    python3 -m venv .venv || {
        echo "Could not create the virtual environment."
        echo "On Ubuntu/Debian, run: sudo apt install python3-venv"
        exit 1
    }
fi

echo "Installing the pinned dependency..."
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt

if [ "${1:-}" = "--test" ]; then
    exec .venv/bin/python -m unittest discover -s tests
fi

exec .venv/bin/python get_cookie.py
