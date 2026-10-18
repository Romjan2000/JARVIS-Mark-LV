#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python3 main.py || python main.py
