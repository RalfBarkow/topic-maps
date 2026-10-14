#!/bin/sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$project_root/scripts/corpus.py" verify
python3 -m unittest discover -s "$project_root/tests" -p 'test_*.py'
"${SBCL:-sbcl}" --noinform --no-sysinit --no-userinit --non-interactive \
  --load "$project_root/scripts/fresh-sbcl.lisp"
python3 "$project_root/scripts/check-nfc.py"
if [ -n "${TOPIC_MAPS_REPORT:-}" ]; then
  python3 "$project_root/scripts/check-report.py" "$TOPIC_MAPS_REPORT" --slice-5
  python3 "$project_root/scripts/check-semantics.py" "$TOPIC_MAPS_REPORT.semantics.json"
  python3 "$project_root/scripts/check-merging.py" "$TOPIC_MAPS_REPORT.merging.json"
  python3 "$project_root/scripts/check-associations.py" "$TOPIC_MAPS_REPORT.associations.json"
  python3 "$project_root/scripts/check-cxtm.py" "$TOPIC_MAPS_REPORT.cxtm.json" --slice-5
  python3 "$project_root/scripts/check-occurrences.py" "$TOPIC_MAPS_REPORT.occurrences.json"
fi
