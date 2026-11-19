#!/bin/sh
cd "$(dirname "$0")"

run() {
  uv run -q --no-project --python 3.12 --with "voyager==$1" --with "numpy==$2" python repro.py "$3" index.voy
}

echo "=== save with voyager==2.0.6 numpy==1.26.4"
run 2.0.6 1.26.4 save
echo

for pair in "2.0.6 1.26.4" "2.0.5 2.2.3" "2.0.6 2.2.3" "2.0.6 2.2.6" "2.0.7 2.2.6" "2.2.3 2.2.3" "2.2.4 2.2.6"; do
  set -- $pair
  echo "=== load + query with voyager==$1 numpy==$2"
  run "$1" "$2" query
  echo
done
