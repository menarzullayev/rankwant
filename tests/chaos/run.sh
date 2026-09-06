#!/usr/bin/env bash
# Chaos / fault injection — test-strategy.md § 14.
#
# Har sinov uchta savolga javob beradi: ma'lumot yo'qolmadimi,
# foydalanuvchi tushunarli xato ko'rdimi, tizim o'zi tiklandimi.
#
# Ishlatish (o'z compose stack'iga qarshi):
#   COMPOSE="docker compose -f docker-compose.yml -f docker-compose.ci.yml" \
#   I_UNDERSTAND_THIS_IS_STAGING=yes tests/chaos/run.sh

set -euo pipefail

: "${COMPOSE:=docker compose}"
: "${API:=http://localhost:8000/api/v1}"

if [ "${I_UNDERSTAND_THIS_IS_STAGING:-}" != "yes" ]; then
  echo "Bu skript servislarni ATAYLAB buzadi."
  echo "Staging yoki o'z local stack'ingizda ekanligingizni tasdiqlang:"
  echo "  I_UNDERSTAND_THIS_IS_STAGING=yes tests/chaos/run.sh"
  exit 1
fi

fail=0
step() { printf '\n═══ %s ═══\n' "$1"; }
ok()   { printf '  ✓ %s\n' "$1"; }
bad()  { printf '  ✗ %s\n' "$1"; fail=1; }

# Probe api konteyner ICHIDAN ishlaydi: host portlari e'lon qilinmagan
# bo'lishi mumkin, va api tirik turganda bog'liqlik yiqilishi aynan shu
# yerdan ko'rinadi.
probe() {
  $COMPOSE exec -T api python -c "
import urllib.request, urllib.error
try:
    print(urllib.request.urlopen('$API/health/', timeout=5).status)
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print('000')" 2>/dev/null | tr -d '\r' || echo "000"
}

expect() {  # expect <kutilgan> <olingan> <izoh>
  if [ "$2" = "$1" ]; then ok "$3 ($2)"; else bad "$3 — kutilgan $1, olingan $2"; fi
}

attempts() {
  $COMPOSE exec -T api python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from judging.models import Attempt
print(Attempt.objects.count())" 2>/dev/null | tr -d '\r' || echo "-1"
}

step "0. Boshlang'ich holat"
expect 200 "$(probe)" "health sog'lom"
before=$(attempts)
echo "  attempt soni: $before"

step "1. Judge worker o'ldiriladi"
echo "Kutilgan: API ishlashda davom etadi, attempt yozuvlari yo'qolmaydi"
$COMPOSE kill -s KILL judge >/dev/null 2>&1 || true
expect 200 "$(probe)" "judge'siz ham API sog'lom"
expect "$before" "$(attempts)" "attempt yozuvlari joyida"
$COMPOSE up -d judge >/dev/null 2>&1
sleep 5
ok "judge qayta ko'tarildi"

step "2. Redis yiqiladi"
echo "Kutilgan: health degraded (503), Attempt yozuvlari saqlanadi"
$COMPOSE stop redis >/dev/null 2>&1
expect 503 "$(probe)" "health bog'liqlik yo'qligini ko'rsatadi"
expect "$before" "$(attempts)" "ma'lumot yo'qolmadi"
$COMPOSE start redis >/dev/null 2>&1
sleep 6
expect 200 "$(probe)" "redis qaytgach tizim o'zi tiklandi"

step "3. Postgres yiqiladi"
echo "Kutilgan: toza 503, ma'lumot yo'qolmaydi"
$COMPOSE stop postgres >/dev/null 2>&1
expect 503 "$(probe)" "health DB yo'qligini ko'rsatadi"
$COMPOSE start postgres >/dev/null 2>&1
sleep 12
expect 200 "$(probe)" "postgres qaytgach tizim o'zi tiklandi"
expect "$before" "$(attempts)" "ma'lumot yo'qolmadi"

step "4. DB kechikishi +5s"
echo "  tc netem talab qiladi — hozircha qo'lda:"
echo "  tc qdisc add dev eth0 root netem delay 5000ms"

echo
if [ "$fail" -ne 0 ]; then
  echo "CHAOS SINOVI YIQILDI"
  exit 1
fi
echo "Chaos sinovi o'tdi — 10-operations § incident bo'yicha xulosa yozing."
