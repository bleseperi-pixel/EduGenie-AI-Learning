#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-lite.txt
[ -f .env ] || { cp .env.example .env; sed -i.bak 's/EXPLAIN_BACKEND=local/EXPLAIN_BACKEND=gemini/' .env && rm -f .env.bak; }
echo "Setup done. Put your GEMINI_API_KEY in .env, then run: ./run.sh"
