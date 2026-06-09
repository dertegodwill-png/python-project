#!/bin/sh
# Export Django data from SQLite to data.json (safe, human-readable)
# Usage: ./scripts/dumpdata.sh

python -u manage.py dumpdata --natural-primary --natural-foreign --indent 2 > data.json
ls -lh data.json
