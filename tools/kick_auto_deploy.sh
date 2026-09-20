#!/usr/bin/env bash
# Merge oxirida host watcher'ni darhol yurgizadi.
#
# Hosted `ubuntu-latest` da `schtasks` YO'Q — kick faqat shu mashinada.
# Darvoza baribir yashil main: watcher `deploy.sh` ni chaqiradi, u esa
# `check_deploy_gate.py` ni o'zi yuritadi. Docs/tools commitda
# `deploy_scope.py` bake ni o'tkazib yuboradi.
#
#   bash tools/kick_auto_deploy.sh
#   schtasks /run /tn "RankWant Auto Deploy"
set -uo pipefail

if ! command -v schtasks >/dev/null 2>&1; then
  printf 'schtasks yo'\''q — hosted CI kick qila olmaydi\n' >&2
  exit 2
fi

schtasks /run /tn "RankWant Auto Deploy"
