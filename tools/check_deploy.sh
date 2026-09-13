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
#: Kod joyida bo'lib, muhit bo'sh qolgan holatlar soni (pastga qarang).
envbad=0

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
  elif docker exec rankwant-web-1 test -d /app/.next/server/app/login 2>/dev/null; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" '/login route bor (yorliqsiz image)'
  else
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'ESKIRGAN' "$N" "$cshow" '/login route yo`q'
    stale=$((stale + 1))
  fi
else
  printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$Y" "YO'Q" "$N" '-' '-'
  missing=$((missing + 1))
fi

# --- Majburiy env o'zgaruvchilari ---------------------------------------
# Uchinchi xato sinfi: konteyner TO'G'RI kodda ishlaydi, lekin MUHIT
# noto'g'ri. Yuqoridagi ikki tekshiruv buni ko'rmaydi — hash bir xil,
# git-sha bir xil, konteyner `Up`. 2026-09-13 da aynan shunday bo'ldi:
#
#   docker compose ... up -d            # --env-file .env.public YO'Q
#
# Natijada `${DJANGO_ALLOWED_HOSTS}` bo'sh qoldi → `ALLOWED_HOSTS = []`
# → Django `DEBUG=False` bilan HAR so'rovni 400 bilan rad etdi →
# web SSR 400 ni ko'tarib 500 berdi → sayt butunlay ishlamadi.
#
# `Up` ko'rinishi yolg'on edi: konteyner tirik, ilova esa javob bera
# olmaydi. Shuning uchun qiymat BO'SHLIGI tekshiriladi, mavjudligi emas.
#
# ⚠️ `docker compose exec` bu yerda ishlatilmaydi: u `-p`/`--env-file`
# kontekstini talab qiladi va konteyner qayta ko'tarilganda nom
# o'zgarishi mumkin. `docker inspect .Config.Env` — eng past daraja,
# noto'g'ri compose chaqiruvini ham ko'rsatadi.
env_check() {
  local name="$1" var="$2" why="$3"
  local line val note

  if ! docker inspect "$name" >/dev/null 2>&1; then
    return   # yo'qligi yuqoridagi tsikllarda aytilgan
  fi

  # `VAR=qiymat` ko'rinishidagi yozuv. Bo'sh qiymat ham shu naqshga
  # tushadi (`VAR=`), ya'ni `grep -q` bilan bo'shni ajratib bo'lmaydi.
  line="$(docker inspect "$name" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null \
          | grep "^${var}=" || true)"
  val="${line#*=}"

  # Apostrof ichida apostrof yozib bo'lmaydi, shuning uchun yorliq
  # oldindan yasaladi — aks holda qavs `(` shell uchun sintaksis xatosi.
  if [ -z "$line" ]; then
    note="$var yo'q"
  elif [ -z "$val" ]; then
    note="$var bo'sh — $why"
  else
    return
  fi

  printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$R" 'MUHIT' "$N" '-' "$note"
  envbad=$((envbad + 1))
}

#: `web` SSR qaysi API manziliga murojaat qiladi. Bo'sh bo'lsa `undefined`
#: ga aylanadi va barcha SSR so'rovlari yiqiladi. Blok oxirida tekshiriladi.
env_check rankwant-api-1 DJANGO_ALLOWED_HOSTS "Django hamma so'rovni 400 qiladi"
env_check rankwant-api-1 DJANGO_SECRET_KEY "sessiya/token imzosi ishlamaydi"
env_check rankwant-api-1 CORS_ALLOWED_ORIGINS "brauzer so'rovlari bloklanadi"
env_check rankwant-api-1 CSRF_TRUSTED_ORIGINS "POST formalar rad etiladi"
env_check rankwant-worker-1 DJANGO_SECRET_KEY "sessiya/token imzosi ishlamaydi"
env_check rankwant-beat-1 DJANGO_SECRET_KEY "sessiya/token imzosi ishlamaydi"
env_check rankwant-web-1 API_BASE_INTERNAL "SSR API manzili yo'q"

#: `web` SSR qaysi API manziliga murojaat qiladi.
#
# ⚠️ `NEXT_PUBLIC_*` BUILT vaqtida bundle'ga singib ketadi, ya'ni
# konteynerning ISHLAB TURGAN env'i uni ko'rsatmaydi. Aynan shu tuzoq
# 2026-09-13 da ikkinchi marta urdi:
#
#   docker compose ... build web     # --env-file .env.public YO'Q
#
# Dockerfile'dagi zaxira qiymat (`http://localhost:8000/api/v1`) bundle'ga
# tushdi va HAR foydalanuvchining brauzeri O'Z kompyuteridagi
# `localhost:8000` ga murojaat qildi → `TypeError: Failed to fetch`.
# Konteyner env'i (`http://api:8000`) to'g'ri bo'lib turardi, ya'ni
# `env_check` yolg'iz buni KO'RMAYDI.
#
# Shuning uchun bundle'ning O'ZIDAN o'qiladi. `localhost` — har doim xato:
# brauzer uchun u foydalanuvchining mashinasi, server emas.
if docker inspect rankwant-web-1 >/dev/null 2>&1; then
  baked="$(docker exec rankwant-web-1 sh -c \
    'grep -rhoE "https?://[a-zA-Z0-9.:_-]+/api/v1" /app/.next/static 2>/dev/null | sort -u' \
    2>/dev/null || true)"

  if [ -z "$baked" ]; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$Y" 'TEKSHIRILMADI' "$N" '-' \
      "bundle'da API manzili topilmadi"
  elif printf '%s\n' "$baked" | grep -q '//localhost\|//127\.0\.0\.1'; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'BUILD XATO' "$N" '-' \
      "bundle'da ${baked%%$'\n'*} — brauzer o'ziga murojaat qiladi"
    envbad=$((envbad + 1))
  else
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" '-' \
      "bundle API: $(printf '%s' "$baked" | head -1)"
  fi
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
if [ "$envbad" -gt 0 ]; then
  printf '%s%s ta konteynerda majburiy muhit o'"'"'zgaruvchisi bo'"'"'sh.%s\n' "$R" "$envbad" "$N"
  printf 'Sabab deyarli har doim bitta: `docker compose` `--env-file .env.public`\n'
  printf 'BERMASDAN chaqirilgan. Kod to'"'"'g'"'"'ri, konteyner `Up`, lekin ilova javob\n'
  printf 'bera olmaydi. To'"'"'g'"'"'ri shakl:\n\n'
  printf '  docker compose -p %s --env-file .env.public \\\n' "$PROJECT"
  printf '    -f docker-compose.yml -f docker-compose.public.yml up -d\n\n'
  printf 'Yoki qayta ko'"'"'tarish uchun loyiha mexanizmi: tools/handoff.ps1 in\n'
fi
if [ "$stale" -gt 0 ]; then
  printf '%s%s konteyner eskirgan — ishlab turgan kod manbadan farq qiladi.%s\n' "$R" "$stale" "$N"
  printf 'Yangilash:\n'
  printf '  docker compose -p %s --env-file .env.public \\\n' "$PROJECT"
  printf '    -f docker-compose.yml -f docker-compose.public.yml build <servis> && \\\n'
  printf '  docker compose -p %s --env-file .env.public \\\n' "$PROJECT"
  printf '    -f docker-compose.yml -f docker-compose.public.yml up -d --no-deps <servis>\n'
fi

if [ "$stale" -gt 0 ] || [ "$envbad" -gt 0 ]; then
  exit 1
fi

printf '%sHamma konteyner joriy kodda.%s\n' "$G" "$N"
exit 0


