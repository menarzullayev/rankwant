#!/usr/bin/env bash
# Deploy holati: ishlab turgan konteynerlar manba koddan ESKIMI?
#
# Nega kerak: `ci-local.sh` MANBA kodni sinaydi (vaqtinchalik konteynerda),
# lekin ishlab turgan `rankwant-web` / `rankwant-api` image'larini
# tekshirmaydi. Natijada CI to'liq yashil bo'lib, sayt eski kodni
# ko'rsatishi mumkin — 2026-09-13 da aynan shunday bo'ldi: web'da
# `/kirish` 404, API'da login «maydon to'ldirilmadi» bilan yiqilardi,
# holbuki barcha testlar o'tgan edi.
#
# Solishtirish SANAGA emas, KONTENTGA qarab ketadi. Sana bo'yicha
# solishtirish yaroqsiz: fayl tahrirlanmasa ham `touch` uni «yangi»
# qiladi (test tiklash, `git checkout`, muharrir saqlashi) va ishlab
# turgan kod aynan bir xil bo'lsa ham «eskirgan» degan yolg'on javob
# chiqadi.
#
# Python konteynerlari uchun konteyner ichidagi fayl hash'i manbaniki
# bilan solishtiriladi. Next.js `.next` chiqishi siqilgan, shuning
# uchun u yerda build yorlig'i (`org.rankwant.git-sha`) o'qiladi.
#
# ⚠️ IMAGE MA'LUMOTINI O'QISH — ikkita tuzoq (2026-09-13 da o'lchandi):
#
# 1. Image nomi `web` EMAS, `rankwant-web:latest`. `docker inspect web`
#    «no such object» beradi (bo'sh chiqish + exit 1). Compose faylida
#    servis `web` deb ataladi, lekin kelib chiqqan image `rankwant-web`;
#    `-p rankwant` bilan loyiha prefiksi qo'shiladi.
# 2. `date -u -d ""` — BO'SH argument bilan ham exit 0 qaytaradi va
#    jimgina «bugun 00:00» ni chop etadi. Ya'ni `... || fallback`
#    shaklidagi zaxira shoxobcha HECH QACHON ishlamaydi. Shuning uchun
#    qiymat avval bo'shligiga tekshiriladi, keyin formatlanadi.
#
# Ishlatish:  bash tools/check_deploy.sh
# Chiqish:    0 — hammasi joyida; 1 — eskirgan konteyner bor.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

if [ -t 1 ]; then
  R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  R=''; G=''; Y=''; B=''; N=''
fi

PROJECT=rankwant
stale=0
missing=0

printf '%sDeploy holati%s (project: %s)\n\n' "$B" "$N" "$PROJECT"
printf '%-22s %-15s %-22s %s\n' 'KONTEYNER' 'HOLAT' 'IMAGE SANASI' 'IZOH'
printf '%s\n' '----------------------------------------------------------------------------------------'

# `img_time IMAGE_REF` — image qurilgan vaqtni `YYYY-MM-DD HH:MM UTC` da.
# Bo'sh qiymat «o'qilmadi» deb ochiq ko'rsatiladi (jimgina 00:00 emas).
img_time() {
  local iso
  iso="$(docker image inspect "$1" --format '{{.Created}}' 2>/dev/null)"
  if [ -z "$iso" ]; then
    printf 'o`qilmadi'
    return
  fi
  date -u -d "$iso" '+%Y-%m-%d %H:%M UTC' 2>/dev/null || printf '%s' "${iso%%T*}"
}

# `check_hash NAME SERVICE SRC_FILE CTR_FILE` — Python konteynerlari uchun.
# Manba fayl bilan konteyner ichidagi faylning sha256 si bir xil bo'lishi shart.
check_hash() {
  local name="$1" service="$2" src="$3" ctr="$4"
  local cshow shash chash
  cshow="$(img_time "rankwant-${service}:latest")"

  shash="$(sha256sum "$src" 2>/dev/null | cut -d' ' -f1)"
  chash="$(docker exec "$name" sha256sum "$ctr" 2>/dev/null | cut -d' ' -f1)"

  if [ -z "$chash" ]; then
    printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$Y" 'TEKSHIRILMADI' "$N" "$cshow" "${ctr##*/} konteynerda yo'q"
    stale=$((stale + 1))
  elif [ "$shash" != "$chash" ]; then
    printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$R" 'ESKIRGAN' "$N" "$cshow" "${ctr##*/} farq qiladi"
    stale=$((stale + 1))
  else
    printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$G" 'joyida' "$N" "$cshow" "${ctr##*/} bir xil"
  fi
}

# --- Python konteynerlari ------------------------------------------------
# Ular `apps/api` dan quriladi; `core/serializers.py` — kirish
# shartnomasi yashaydigan fayl, ya'ni eng sezgir nishon.
for entry in \
  "rankwant-api-1|api" \
  "rankwant-worker-1|worker" \
  "rankwant-beat-1|beat"
do
  IFS='|' read -r name service <<<"$entry"
  if ! docker inspect "$name" >/dev/null 2>&1; then
    printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$Y" "YO'Q" "$N" '-' '-'
    missing=$((missing + 1)); continue
  fi
  check_hash "$name" "$service" "apps/api/core/serializers.py" "/app/core/serializers.py"
done

# --- web (Next.js) ------------------------------------------------------
# `.next` chiqishi siqilgan va xeshlangan, shuning uchun fayl hash'i
# solishtirib bo'lmaydi. Buning o'rniga build vaqtida yozilgan yorliq
# (`org.rankwant.git-sha`, apps/web/Dockerfile) o'qiladi: u manba
# commit'i bilan bir xil bo'lishi shart. Yorliq yo'q bo'lsa (eski image)
# ehtiyot chorasi sifatida route mavjudligi tekshiriladi.
if docker inspect rankwant-web-1 >/dev/null 2>&1; then
  cshow="$(img_time rankwant-web:latest)"

  img_sha="$(docker inspect rankwant-web-1 --format '{{index .Config.Labels "org.rankwant.git-sha"}}' 2>/dev/null)"
  src_sha="$(git rev-parse HEAD 2>/dev/null)"

  if [ -n "$img_sha" ] && [ "$img_sha" != "<no value>" ] && [ "$img_sha" != "unknown" ]; then
    if [ "$img_sha" = "$src_sha" ]; then
      printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" "git-sha ${img_sha:0:7}"
    else
      printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'ESKIRGAN' "$N" "$cshow" "git-sha ${img_sha:0:7} != ${src_sha:0:7}"
      stale=$((stale + 1))
    fi
  elif docker exec rankwant-web-1 test -d /app/.next/server/app/kirish 2>/dev/null; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" '/kirish route bor (yorliqsiz image)'
  else
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'ESKIRGAN' "$N" "$cshow" '/kirish route yo`q'
    stale=$((stale + 1))
  fi
else
  printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$Y" "YO'Q" "$N" '-' '-'
  missing=$((missing + 1))
fi

# --- judge (Go, kompilyatsiya qilingan binary) --------------------------
if docker inspect rankwant-judge-1 >/dev/null 2>&1; then
  cshow="$(img_time rankwant-judge:latest)"
  printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$G" 'ishlayapti' "$N" "$cshow" 'binary — hash manbada yo`q'
else
  printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$Y" "YO'Q" "$N" '-' '-'
  missing=$((missing + 1))
fi

printf '\n'
if [ "$missing" -gt 0 ]; then
  printf '%s%s konteyner ishlamayapti.%s\n' "$Y" "$missing" "$N"
fi
if [ "$stale" -gt 0 ]; then
  printf '%s%s konteyner eskirgan — ishlab turgan kod manbadan farq qiladi.%s\n' "$R" "$stale" "$N"
  printf 'Yangilash:\n'
  printf '  docker compose -p %s --env-file .env.public \\\n' "$PROJECT"
  printf '    -f docker-compose.yml -f docker-compose.public.yml build <servis> && \\\n'
  printf '  docker compose -p %s --env-file .env.public \\\n' "$PROJECT"
  printf '    -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps <servis>\n'
  exit 1
fi

printf '%sHamma konteyner joriy kodda.%s\n' "$G" "$N"
exit 0


