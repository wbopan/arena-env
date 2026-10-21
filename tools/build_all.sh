#!/bin/bash
# Build every task under $1 (default ~/arena/skillsbench) into local images
# arena-task/<name>:local, one at a time, logging to build/logs/<name>.log and
# a summary line per task in build/summary.tsv.
set -u
SRC=${1:-$HOME/arena/skillsbench}
ROOT=$HOME/arena
cd "$ROOT" || exit 1
. venv/bin/activate
DOCKER_ROOT=$(docker info --format "{{.DockerRootDir}}" 2>/dev/null || echo /)
mkdir -p build/logs
for d in "$SRC"/*/; do
  name=$(basename "$d")
  [ -f "$d/environment/Dockerfile" ] || continue
  if docker image inspect "arena-task/$name:local" >/dev/null 2>&1; then
    echo -e "$name\tcached" >> build/summary.tsv; continue
  fi
  while [ "$(df --output=avail -BG "$DOCKER_ROOT" | tail -1 | tr -dc 0-9)" -lt 12 ]; do echo "low disk, waiting" >> build/logs/disk.log; sleep 300; done
  t0=$(date +%s)
  extra=()
  [ -f "arena-env/notes/$name.md" ] && extra+=(--digest "arena-env/notes/$name.md")
  [ -f "arena-env/notes/$name.hint.md" ] && extra+=(--hint "arena-env/notes/$name.hint.md")
  if python arena-env/tools/build_task.py "$d" "build/$name" "${extra[@]}" > "build/logs/$name.log" 2>&1 \
     && DOCKER_BUILDKIT=1 timeout 2400 docker build --network=host --platform linux/amd64 -t "arena-task/$name:local" "build/$name" >> "build/logs/$name.log" 2>&1; then
    status=ok
  else
    status=fail
  fi
  size=$(docker image inspect "arena-task/$name:local" --format '{{.Size}}' 2>/dev/null || echo 0)
  echo -e "$name\t$status\t$(( $(date +%s) - t0 ))s\t$size\t$(grep -o 'warm-up verifier exit [0-9]*, reward.txt: [^ ]*' build/logs/$name.log | tail -1)" >> build/summary.tsv
  df -h "$DOCKER_ROOT" | tail -1 | awk '{print "disk", $4}' >> build/logs/disk.log
done
echo ALL_DONE >> build/summary.tsv
