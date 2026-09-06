#!/usr/bin/env bash
# Judge sandbox izolyatsiyasi — CI da har PR da ishlaydi.
#
# Bu bake-off harness'ining IZOLYATSIYA qismini qayta ishlatadi: o'sha
# case'lar, o'sha moddiy tekshiruvlar. Alohida to'plam yozish ikkita
# haqiqat manbai yaratardi va ular vaqt bilan ajralib ketardi.
#
# CI da judge worker ko'tarilmagan bo'lsa — skanerlar o'tkazib yuboriladi,
# lekin STATIK tekshiruvlar baribir bajariladi.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

fail=0
note() { printf '  %s\n' "$1"; }
bad()  { printf '  ✗ %s\n' "$1"; fail=1; }
ok()   { printf '  ✓ %s\n' "$1"; }

echo "═══ 1. Judge host konfiguratsiyasi ═══"

# 06-architecture 🔒: judge host'da DB credential BO'LMASLIGI kerak.
# YAML tahlili orqali — matn qidirish izohdagi so'zga ham tushardi.
python3 tests/security/check_compose.py || fail=1

# Worker o'zi ham tekshirishi kerak — kod darajasidagi himoya
for f in services/judge-go/main.go services/judge-py/main.py; do
  if grep -q "DATABASE_URL" "$f"; then
    ok "$(basename "$(dirname "$f")") DATABASE_URL ni rad etadi"
  else
    bad "$(basename "$(dirname "$f")") DATABASE_URL tekshiruvi yo'q"
  fi
done

# Limitlar majburiy — fail closed
if grep -q "PreflightCgroup" services/judge-go/main.go; then
  ok "judge-go preflight bilan ishga tushadi"
else
  bad "judge-go da cgroup preflight yo'q"
fi

echo
echo "═══ 2. Ilova darajasidagi qoidalar ═══"

# Manba faqat egasiga — IDOR himoyasi
if grep -q "source_code" apps/api/judging/views.py \
   && grep -q "is_staff" apps/api/judging/views.py; then
  ok "attempt manbasi egalik bo'yicha filtrlanadi"
else
  bad "attempt manbasida egalik tekshiruvi topilmadi"
fi

# PAT hash bo'lib saqlanadi
if grep -q "sha256" apps/api/core/models.py; then
  ok "PAT SHA-256 hash bilan saqlanadi"
else
  bad "PAT hash'lanmayapti"
fi

# Rate limit sozlangan
if grep -q "DEFAULT_THROTTLE_RATES" apps/api/config/settings.py; then
  ok "rate limit sozlangan"
else
  bad "rate limit sozlanmagan"
fi

echo
echo "═══ 3. Sandbox escape sinovlari ═══"

if [ -z "${REDIS_URL:-}" ]; then
  note "REDIS_URL yo'q — judge ishlamayapti, dinamik sinovlar o'tkazib yuborildi"
  note "Ularni local ishga tushirish:"
  note "  docker compose up -d redis && docker run -d --privileged … rankwant/judge-go"
  note "  REDIS_URL=redis://localhost:6379/0 tests/security/run.sh"
else
  python3 services/bakeoff/harness/runner.py \
      --worker "${JUDGE_WORKER:-judge-go}" \
      --redis "$REDIS_URL" \
      --timeout "${JUDGE_TIMEOUT:-300}" \
    || bad "izolyatsiya sinovlari yiqildi"
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "XAVFSIZLIK TEKSHIRUVI YIQILDI"
  exit 1
fi
echo "Xavfsizlik tekshiruvi o'tdi"
