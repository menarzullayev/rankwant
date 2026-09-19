#!/usr/bin/env bash
# Cloudflare Workers route sozlamalari joyidami?
#
# Nega kerak: `rankwant.uz` oldida `rankwant-maintenance` Worker turadi
# (services/maintenance-worker). GET `/` dan tashqari HAR so'rovda
# ishlaydi, ya'ni bepul tarifning kuniga 100 000 so'rovi oddiy trafik
# bilan ham tugaydi. Bosh sahifa 2026-09-19 dan Worker'siz.
# 2026-09-13 da aynan shunday bo'ldi: 18:31 da 76%, 20:56 da 94%,
# 22:35 da esa limit tugadi.
#
# Limit tugaganda nima bo'lishi bitta maydonga bog'liq:
#
#   request_limit_fail_open = true  → so'rov origin'ga o'tadi, sayt ishlaydi
#   request_limit_fail_open = false → Cloudflare Error 1027, sayt YOPILADI
#
# Standart qiymat `false`. Ya'ni route qayta yaratilsa yoki yangi route
# qo'shilsa, himoya jimgina yo'qoladi va buni faqat keyingi limit
# tugaganda bilib qolamiz. Skript shuni oldini oladi.
#
# ⚠️ Maydon ochiq API hujjatida YO'Q. Lekin
# `GET /zones/{zone_id}/workers/routes` uni qaytaradi va
# `PUT .../routes/{route_id}` qabul qiladi (commit 74d3d55).
#
# ⚠️ Token haqida: wrangler OAuth tokenining muddati o'tgan bo'lishi mumkin
# (09-11 da olgan, ~24 soat yashaydi). Konfiguratsiyada `offline_access`
# scope bor, shuning uchun token brauzersiz yangilanadi.
#
# ⚠️ «token yo'q» bilan «octa sozlama noto'g'ri» NI AJRATING. Ikkalasi ham
# exit 1 bermasin: token yo'qligi — tekshiruv imkonsizligi (exit 2), va
# bu saytning holati haqida HECH NARSA aytmaydi.
#
# Ishlatish:  bash tools/check_workers.sh
# Chiqish:    0 — hamma route himoyalangan; 1 — himoya yo'q; 2 — o'lchab bo'lmadi.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

# ⚠️ Windows: `pwd` Git Bash'da `/c/Users/...` beradi, Windows Python esa uni
# `C:\c\Users\...` deb o'qiydi va faylni topmaydi. Shuning uchun skript yo'li
# `cygpath -w` bilan (bo'lsa) yoki qo'lda aylantiriladi.
PY_SCRIPT="$ROOT/tools/cf_route_audit.py"
if command -v cygpath > /dev/null 2>&1; then
  PY_SCRIPT="$(cygpath -w "$PY_SCRIPT")"
else
  case "$PY_SCRIPT" in
    /?/*) PY_SCRIPT="$(printf '%s' "$PY_SCRIPT" | sed 's|^/\([a-z]\)/|\1:/|')" ;;
  esac
fi

if [ -t 1 ]; then
  R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  R=''; G=''; Y=''; B=''; N=''
fi

# Interpretator NOMI emas, ISHLAYDIGANI tanlanadi — sabab
# `tools/pick-python.sh` da (Windows'da `python3` Store stub'iga tushadi).
# Ilgari bu yerda bitta mashinaga xos yo'l qotirilgan edi; u boshqa har
# qanday klonda ishlamasdi va zaxira yo'l ham o'sha stub'ni tanlardi.
if [ -z "${PY:-}" ]; then
  PY="$(bash "$ROOT/tools/pick-python.sh" || true)"
fi
if [ -z "$PY" ]; then
  printf '%sTekshiruv imkonsiz%s: ishlaydigan python topilmadi.\n' "$Y" "$N"
  exit 2
fi

printf '%sCloudflare Workers route holati%s\n\n' "$B" "$N"

out="$("$PY" "$PY_SCRIPT" 2>&1)"
rc=$?
if [ "$rc" = "2" ]; then
  printf '%sTekshiruv imkonsiz%s — sayt holati haqida xulosa YOQ.\n\n' "$Y" "$N"
  printf '%s\n' "$out"
  exit 2
fi

if [ "$rc" != "0" ]; then
  printf '%s\n' "$out"
  exit 2
fi

printf '%-15s %-32s %s\n' 'ZONA' 'PATTERN' 'FAIL OPEN'
printf '%s\n' '--------------------------------------------------------------------------'

unprotected=0
total=0
# ⚠️ `failopen` dan `\r` ni OLIB TASHLASH shart. Windows'da Python `print()`
# CRLF yozadi, `read` esa faqat `\n` ni ajratadi — natijada qiymat `True\r`
# bo'lib qoladi va `[ "$failopen" = "True" ]` HECH QACHON mos kelmaydi.
# Ya'ni himoyalangan route «himoyasiz» deb ko'rinadi. 2026-09-14 da
# o'lchandi: uchala route `True` edi, skript ikkitasini «YOQ» dedi.
while IFS=$'\t' read -r zone pattern failopen; do
  zone="${zone%$'\r'}"
  pattern="${pattern%$'\r'}"
  failopen="${failopen%$'\r'}"
  [ -z "$zone" ] && continue
  total=$((total + 1))
  if [ "$failopen" = "True" ]; then
    printf '%-15s %-32s %s\n' "$zone" "$pattern" "${G}ha${N}"
  else
    printf '%-15s %-32s %s\n' "$zone" "$pattern" "${R}YOQ${N}"
    unprotected=$((unprotected + 1))
  fi
done <<< "$out"

printf '\n'

if [ "$unprotected" -gt 0 ]; then
  printf '%sXATO%s: %s ta route himoyasiz. Limit tugasa sayt 1027 bilan yopiladi.\n\n' \
    "$R" "$N" "$unprotected"
  printf 'Tuzatish: PUT /zones/{zone_id}/workers/routes/{route_id} —\n'
  printf '%s\n' '  {"pattern": "<pattern>", "request_limit_fail_open": true}'
  exit 1
fi

printf '%sHamma %s route himoyalangan (fail open).%s\n' "$G" "$total" "$N"
exit 0
