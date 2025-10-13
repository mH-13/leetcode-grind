#!/bin/bash
# Quick daily problem wizard launcher
# Usage: ./daily.sh

cd "$(dirname "$0")"
python3 scripts/daily.py
