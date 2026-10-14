#!/bin/sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$project_root/scripts/corpus.py" verify
python3 -m unittest discover -s "$project_root/tests" -p 'test_*.py'
"${SBCL:-sbcl}" --noinform --no-sysinit --no-userinit --non-interactive \
  --load "$project_root/scripts/fresh-sbcl.lisp"
if [ -n "${TOPIC_MAPS_REPORT:-}" ]; then
  python3 "$project_root/scripts/check-report.py" "$TOPIC_MAPS_REPORT" --slice-1
  python3 "$project_root/scripts/check-semantics.py" "$TOPIC_MAPS_REPORT.semantics.json"
fi
