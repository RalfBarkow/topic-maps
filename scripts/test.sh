#!/bin/sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$project_root/scripts/corpus.py" verify
python3 -m unittest discover -s "$project_root/tests" -p 'test_*.py'
"${SBCL:-sbcl}" --noinform --no-sysinit --no-userinit --non-interactive \
  --load "$project_root/scripts/fresh-sbcl.lisp"
python3 "$project_root/scripts/check-nfc.py"
if [ -n "${TOPIC_MAPS_REPORT:-}" ]; then
  python3 "$project_root/scripts/check-report.py" "$TOPIC_MAPS_REPORT" --slice-12a
  python3 "$project_root/scripts/check-semantics.py" "$TOPIC_MAPS_REPORT.semantics.json"
  python3 "$project_root/scripts/check-merging.py" "$TOPIC_MAPS_REPORT.merging.json"
  python3 "$project_root/scripts/check-associations.py" "$TOPIC_MAPS_REPORT.associations.json"
  python3 "$project_root/scripts/check-cxtm.py" "$TOPIC_MAPS_REPORT.cxtm.json" --slice-12a
  python3 "$project_root/scripts/check-occurrences.py" "$TOPIC_MAPS_REPORT.occurrences.json"
  python3 "$project_root/scripts/check-prefixes.py" "$TOPIC_MAPS_REPORT.prefixes.json"
  python3 "$project_root/scripts/check-integers.py" "$TOPIC_MAPS_REPORT.integers.json"
  python3 "$project_root/scripts/check-decimals.py" "$TOPIC_MAPS_REPORT.decimals.json"
  python3 "$project_root/scripts/check-dates.py" "$TOPIC_MAPS_REPORT.dates.json"
  python3 "$project_root/scripts/check-datetimes.py" "$TOPIC_MAPS_REPORT.datetimes.json"
  python3 "$project_root/scripts/check-timezones.py" "$TOPIC_MAPS_REPORT.timezones.json"
  python3 "$project_root/scripts/check-typed-names.py" "$TOPIC_MAPS_REPORT.typed-names.json"
fi
