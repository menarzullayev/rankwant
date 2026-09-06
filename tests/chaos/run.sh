#!/usr/bin/env bash
# Chaos / fault injection — test-strategy.md § 14.
#
# FAQAT staging'da. Har sinov: ma'lumot yo'qolmadimi, foydalanuvchi
# tushunarli xato ko'rdimi, tizim o'zi tiklandimi.
set -euo pipefail

: "${COMPOSE:=docker compose}"
: "${API:=http://localhost:8000/api/v1}"

if [ "${I_UNDERSTAND_THIS_IS_STAGING:-}" != "yes" ]; then
  echo "Bu skript servislarni ATAYLAB buzadi."
  echo "Staging'da ekanligingizni tasdiqlang:"
  echo "  I_UNDERSTAND_THIS_IS_STAGING=yes tests/chaos/run.sh"
  exit 1
fi

step() { printf '\n═══ %s ═══\n' "$1"; }
probe() { curl -s -o /dev/null -w '%{http_code}' "$API/health/" || echo "000"; }

step "1. Judge worker tekshiruv o'rtasida o'ldiriladi"
echo "Kutilgan: attempt yo'qolmaydi, qayta navbatga tushadi"
$COMPOSE kill -s KILL judge || true
sleep 5
$COMPOSE up -d judge
echo "  health: $(probe)"

step "2. Redis yiqiladi"
echo "Kutilgan: submit qabul qilinmaydi, LEKIN Attempt yozuvi saqlanadi"
$COMPOSE stop redis
echo "  health: $(probe)"
$COMPOSE start redis
sleep 5
echo "  tiklangach health: $(probe)"

step "3. Postgres yiqiladi"
echo "Kutilgan: toza 503, ma'lumot yo'qolmaydi"
$COMPOSE stop postgres
echo "  health: $(probe)"
$COMPOSE start postgres
sleep 8
echo "  tiklangach health: $(probe)"

step "4. DB kechikishi +5s"
echo "Kutilgan: so'rovlar sekinlashadi, lekin xato bermaydi"
echo "  (tc netem talab qiladi — qo'lda: tc qdisc add dev eth0 root netem delay 5000ms)"

echo
echo "Chaos sinovi tugadi. 10-operations § incident bo'yicha xulosa yozing."
