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

# Git Bash rewrites `/app/...` arguments into Windows paths before they reach
# `docker exec`, so every in-container read fails and the report goes red for
# the wrong reason (measured 2026-09-17 without it: "serializers.py konteynerda
# yo'q" and "417 fayl MAZMUNI farq qiladi"; with it: 4 files). Ignored elsewhere.
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

# `label_state SHA PATH...` — is an image built at commit SHA still current for
# the sources under PATH? Prints `same`, `current`, `stale` or `unknown`.
#
# web and judge images are built from one folder each (compose build context:
# apps/web, services/judge-go), so a label older than HEAD is still current when
# that folder has not changed since. Comparing with HEAD alone reported every
# docs-only commit as a stale image: the judge on 2026-09-17 (label 787eaa3), and
# the web right after #39, which touched no web file.
label_state() {
  local sha="$1" head
  shift
  head="$(git rev-parse HEAD 2>/dev/null)"
  if [ "$sha" = "$head" ]; then
    echo same
  elif ! git cat-file -e "${sha}^{commit}" 2>/dev/null; then
    echo unknown
  elif git diff --quiet "$sha" "$head" -- "$@"; then
    echo current
  else
    echo stale
  fi
}

# Entry point for tools/check_negative.py: one label decision, no docker.
if [ "${1:-}" = "--label-state" ]; then
  shift
  label_state "$@"
  exit 0
fi

# `build_label_state VALUE` — the `org.rankwant.built-at` label was passed
# through the build or not? Prints `ok` or `unlabeled`.
#
# Nega alohida tekshiruv: `img_time` (quyida) allaqachon image qurilgan
# vaqtni Docker metadatasidan (`.Created`) ko'rsatadi, ya'ni vaqtni
# yorliqdan takror chiqarish ortiqcha bo'lardi. Yorliqning YAGONA
# qo'shimcha ma'nosi shu: `.Created` HAR QANDAY build'da mavjud, yorliq esa
# faqat build argumentlari haqiqatan uzatilganda to'ladi. Demak
# `unknown` — argumentlar oqimi uzilganining isboti.
#
# O'lchandi 2026-09-18: `api`/`worker`/`beat`/`migrate` compose'ning QISQA
# shakli (`build: ./apps/api`) bilan qurilardi — u yerda `args` berishning
# iloji yo'q — va `org.rankwant.git-sha` ham, `built-at` ham `unknown`
# bo'lib qolgan edi. Ya'ni bu tekshiruv o'sha xatoni ushlaydi.
build_label_state() {
  case "${1:-}" in
    "" | "<no value>" | unknown) echo unlabeled ;;
    *) echo ok ;;
  esac
}

# Entry point for tools/check_negative.py: one decision, no docker.
if [ "${1:-}" = "--build-label-state" ]; then
  shift
  build_label_state "$@"
  exit 0
fi

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
#: `built-at` yorlig'i yo'q konteynerlar — DIAGNOSTIKA, exit'ga ta'sir
#: qilmaydi. Nega `stale` emas: yorliq hech qanday qarorga
#: ishlatilmaydi (`img_time` vaqtni Docker metadatasidan oladi), ya'ni
#: uning yo'qligi «kod eskirgan» degani EMAS. Lekin u build argumentlari
#: oqimi uzilganini ko'rsatadi — o'sha sozlama keyingi safar `git-sha` ni
#: ham bo'sh qoldirishi mumkin, shuning uchun ko'rinib turishi kerak.
unlabeled=0

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

# `check_build_label NAME IMAGE_REF` — `built-at` yorlig'i joyidami?
#
# Yorliq joyida bo'lsa JIM qoladi: vaqtni `img_time` allaqachon
# ko'rsatadi, ikkinchi marta chop etish shovqin bo'lardi. Faqat uzilganda
# qator chiqaradi — o'shanda gap «build argumentlari yetib kelmadi»,
# ya'ni keyingi safar `git-sha` ham bo'sh qolishi mumkin.
check_build_label() {
  local name="$1" image="$2" lab
  lab="$(docker inspect "$name" --format '{{index .Config.Labels "org.rankwant.built-at"}}' 2>/dev/null)"
  [ "$(build_label_state "$lab")" = "ok" ] && return
  printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$Y" 'TEKSHIRILMADI' "$N" \
    "$(img_time "$image")" "built-at yorlig'i yo'q — build argumentlari uzatilmagan"
  unlabeled=$((unlabeled + 1))
}

# `check_hash NAME SERVICE SRC_FILE CTR_FILE` — Python konteynerlari uchun.
# Manba fayl bilan konteyner ichidagi faylning sha256 si bir xil bo'lishi shart.
check_hash() {
  local name="$1" service="$2" src="$3" ctr="$4"
  local cshow shash chash
  cshow="$(img_time "rankwant-${service}:latest")"

  # ⚠️ `< /dev/null` SHART: `sha256sum` ishga tushishda stdin fd ni
  # sozlaydi (`_setmode`) va MSYS'da u YOPIQ bo'lsa yiqiladi:
  #   sha256sum: failed to set file descriptor text/binary mode: Bad file descriptor
  # Natija — BO'SH xesh, ya'ni yolg'on «ESKIRGAN» (o'lchandi 2026-09-19:
  # `0<&-` bilan api/worker/beat «serializers.py farq qiladi» dedi, holbuki
  # hash bir xil edi; `</dev/null` bilan «bir xil»). `2>/dev/null` xatoni
  # yashirgani uchun sabab ko'rinmaydi. Rejalashtirilgan vazifa (Task
  # Scheduler → `conhost --headless`) farzandga stdin bermaydi, ya'ni
  # skript QO'LDA to'g'ri, VAZIFADA yolg'on ishlaydi.
  shash="$(sha256sum "$src" < /dev/null 2>/dev/null | cut -d' ' -f1)"
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
# `py_inventory` — `.py` fayllar ro'yxati (nisbiy yo'l, tartiblangan).
# `host` yoki `container:<konteyner nomi>` qabul qiladi.
#
# ⚠️ Chiqarib tashlash SHART: `apps/api` ichida mahalliy `.venv/` bo'ladi
# (o'lchandi: `.venv/Lib/site-packages/_virtualenv.py`) va u konteynerda
# yo'q — filtrsiz skript HAR doim «eskirgan» derdi va tekshiruvni
# foydasiz qilardi. Shuning uchun `__pycache__`, nuqta bilan boshlanadigan
# har qanday katalog (`.venv`, `.mypy_cache`, …) va `node_modules` tashlanadi.
py_inventory() {
  if [ "$1" = "host" ]; then
    ( cd apps/api && find . -name '*.py' \
        -not -path '*/__pycache__/*' -not -path '*/.*/*' \
        -not -path '*/node_modules/*' | sort )
  else
    docker exec "${1#container:}" sh -c \
      "cd /app && find . -name '*.py' \
         -not -path '*/__pycache__/*' -not -path '*/.*/*' \
         -not -path '*/node_modules/*' | sort" 2>/dev/null
  fi
}

# `py_tree_hash TARGET` — butun `.py` daraxtining BITTA xeshi, `\r` siz.
#
# ⚠️ Nega `\r` olib tashlanadi: hash solishtirishdan ilgari ATAYLAB voz
# kechilgan edi, chunki Windows'da `git checkout` fayllarni CRLF ga
# o'giradi va sog'lom konteyner «ESKIRGAN» bo'lib ko'rinardi. Lekin
# hashesiz qolgan bo'shliq qimmatga tushdi — o'lchandi (2026-09-16):
# `arena/views.py` konteynerda va manbada HAR XIL edi
# (c385aecd… ↔ 1548467d…), skript esa «Hamma konteyner joriy kodda» dedi,
# chunki fayl RO'YXATI bir xil edi.
#
# Ya'ni ikki tomon ham `\r` siz xeshlanadi: qator oxiri farqi ko'rinmaydi
# (yolg'on signal yo'q), mazmun farqi esa KO'RINADI.
#
# ⚠️ Nega fayl-fayl emas, bitta xesh: o'lchandi — fayl boshiga alohida
# jarayon chaqirilsa uchta konteyner uchun **64 soniya** ketadi (330 fayl
# × 3 jarayon × 3 konteyner). Bu darvoza har deploy'da ishlaydi, ya'ni
# sekin bo'lishi mumkin emas. Fayl nomi faqat FARQ topilganda kerak —
# o'shanda `py_hashes` chaqiriladi.
py_tree_hash() {
  if [ "$1" = "host" ]; then
    ( cd apps/api && py_file_list | xargs -0 -r cat | tr -d '\r' | sha256sum | cut -d' ' -f1 )
  else
    docker exec -i "${1#container:}" sh -c '
      cd /app || exit 1
      find . -name "*.py" -not -path "*/__pycache__/*" -not -path "*/.*/*" \
        -not -path "*/node_modules/*" -print0 |
        sort -z | xargs -0 -r cat | tr -d "\r" | sha256sum | cut -d" " -f1' 2>/dev/null
  fi
}

# `py_file_list` — host tomonidagi NUL ajratilgan ro'yxat (tartiblangan).
py_file_list() {
  find . -name '*.py' -not -path '*/__pycache__/*' -not -path '*/.*/*' \
    -not -path '*/node_modules/*' -print0 | sort -z
}

# `py_hashes TARGET` — `hash  yo'l` juftliklari (faqat farqni aniqlash uchun).
# Skript BIR marta yoziladi va ikki tomonda stdin orqali bajariladi
# (`sh -s` / `docker exec -i … sh -s`) — shunda ichma-ich qo'shtirnoq
# qochirishdan qutulamiz, ya'ni ikkala tomon AYNAN bir xil kod yuradi.
PY_HASH_SCRIPT='
cd "$1" || exit 1
find . -name "*.py" \
  -not -path "*/__pycache__/*" -not -path "*/.*/*" \
  -not -path "*/node_modules/*" -print0 |
  sort -z |
  xargs -0 -r sh -c '"'"'
    for f in "$@"; do
      printf "%s  %s\n" "$(tr -d "\r" < "$f" | sha256sum | cut -d" " -f1)" "$f"
    done'"'"' _
'

py_hashes() {
  if [ "$1" = "host" ]; then
    printf '%s' "$PY_HASH_SCRIPT" | sh -s apps/api | sort
  else
    printf '%s' "$PY_HASH_SCRIPT" | docker exec -i "${1#container:}" sh -s /app 2>/dev/null | sort
  fi
}

# `check_inventory NAME` — konteynerda manbadagi fayllar TO'LIQ bormi.
#
# Nega kerak: `core/serializers.py` hash'i — eng sezgir nishon, lekin u
# YANGI ILOVANI ko'rsatmaydi. 2026-09-13 da aynan shunday bo'ldi:
# `updates` ilovasi manbada bor, konteynerda yo'q, `/updates/` esa 404 —
# skript baribir «hamma konteyner joriy kodda» derdi, chunki shartnoma
# fayli o'zgarmagan edi.
#
# Faqat RO'YXAT solishtiriladi, hash emas: hash qator oxiri (CRLF ↔ LF)
# farqidan yolg'on «ESKIRGAN» beradi — Windows'da `git checkout` fayllarni
# CRLF ga o'giradi (git shu haqda ogohlantiradi). Ro'yxat esa bunga
# berilmaydi va aynan kerakli narsani — fayl to'plamini — o'lchaydi.
#
# Farq bo'lmasa hech narsa chop etilmaydi: yuqoridagi `check_hash` qatori
# allaqachon «joyida» deb yozgan.
check_inventory() {
  local name="$1" service="$2"
  local host_list ctr_list missing extra note

  host_list="$(py_inventory host)"
  ctr_list="$(py_inventory "container:$name")"

  if [ -z "$ctr_list" ]; then
    printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$Y" 'TEKSHIRILMADI' "$N" '-' \
      "fayl ro'yxati o'qilmadi"
    stale=$((stale + 1))
    return
  fi

  missing="$(comm -23 <(printf '%s\n' "$host_list") <(printf '%s\n' "$ctr_list"))"
  extra="$(comm -13 <(printf '%s\n' "$host_list") <(printf '%s\n' "$ctr_list"))"

  if [ -n "$missing" ]; then
    note="$(printf '%s\n' "$missing" | grep -c .) fayl konteynerda yo'q — $(printf '%s\n' "$missing" | head -1)"
  elif [ -n "$extra" ]; then
    note="$(printf '%s\n' "$extra" | grep -c .) fayl konteynerda ortiqcha — $(printf '%s\n' "$extra" | head -1)"
  else
    # Ro'yxat bir xil — endi MAZMUN solishtiriladi. Busiz fayl ichidagi
    # o'zgarish ko'rinmaydi (2026-09-16 da aynan shunday bo'ldi).
    if [ "$(py_tree_hash host)" != "$(py_tree_hash "container:$name")" ]; then
      # Farq BOR — endi qaysi fayl ekani aniqlanadi (sekin yo'l, faqat shu
      # holatda ishlaydi; `HOST_HASHES` bir marta hisoblanadi).
      [ -n "${HOST_HASHES:-}" ] || HOST_HASHES="$(py_hashes host)"
      diff_list="$(comm -23 <(printf '%s\n' "$HOST_HASHES") \
        <(py_hashes "container:$name") | awk '{print $NF}')"
      n_diff="$(printf '%s\n' "$diff_list" | grep -c .)"
      note="$n_diff fayl MAZMUNI farq qiladi — $(printf '%s\n' "$diff_list" | head -1)"
    fi
  fi

  if [ -z "${note:-}" ]; then
    return
  fi

  # Image nomi = SERVIS nomi, konteyner nomi EMAS: `rankwant-api-1:latest`
  # degan image yo'q, `rankwant-api:latest` bor. `check_hash` ham shu
  # sababdan `$service` ni oladi.
  printf '%-22s %s%-15s%s %-22s %s\n' "$name" "$R" 'ESKIRGAN' "$N" \
    "$(img_time "rankwant-${service}:latest")" "$note"
  stale=$((stale + 1))
}

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
  check_inventory "$name" "$service"
  check_build_label "$name" "rankwant-${service}:latest"
done

# --- web (Next.js) ------------------------------------------------------
# `.next` chiqishi siqilgan va xeshlangan, shuning uchun fayl hash'i
# solishtirib bo'lmaydi. Buning o'rniga build vaqtida yozilgan yorliq
# (`org.rankwant.git-sha`, apps/web/Dockerfile) o'qiladi. Yorliq yo'q
# bo'lsa (eski image) ehtiyot chorasi sifatida route mavjudligi tekshiriladi.
# The label need not equal HEAD: it is current while apps/web is unchanged
# since that commit (label_state).
if docker inspect rankwant-web-1 >/dev/null 2>&1; then
  cshow="$(img_time rankwant-web:latest)"

  img_sha="$(docker inspect rankwant-web-1 --format '{{index .Config.Labels "org.rankwant.git-sha"}}' 2>/dev/null)"
  src_sha="$(git rev-parse HEAD 2>/dev/null)"

  if [ -n "$img_sha" ] && [ "$img_sha" != "<no value>" ] && [ "$img_sha" != "unknown" ]; then
    case "$(label_state "$img_sha" apps/web)" in
      same)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" "git-sha ${img_sha:0:7}" ;;
      current)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" \
          "git-sha ${img_sha:0:7}: undan beri apps/web o'zgarmagan" ;;
      unknown)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$Y" 'TEKSHIRILMADI' "$N" "$cshow" \
          "git-sha ${img_sha:0:7} bu klonda yo'q — git fetch, keyin qayta tekshiring"
        stale=$((stale + 1)) ;;
      *)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'ESKIRGAN' "$N" "$cshow" \
          "git-sha ${img_sha:0:7} dan beri apps/web o'zgargan (HEAD ${src_sha:0:7})"
        stale=$((stale + 1)) ;;
    esac
  elif docker exec rankwant-web-1 test -d /app/.next/server/app/login 2>/dev/null; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$G" 'joyida' "$N" "$cshow" '/login route bor (yorliqsiz image)'
  else
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-web-1' "$R" 'ESKIRGAN' "$N" "$cshow" '/login route yo`q'
    stale=$((stale + 1))
  fi
  check_build_label rankwant-web-1 rankwant-web:latest
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
#
# ⚠️ Fayl hash'i solishtirib bo'lmaydi: manbada `.go`, konteynerda esa
# kompilyatsiya qilingan binary. Ilgari bu qator «binary — hash manbada
# yo`q» deb yozardi, ya'ni judge eskiligi KO'RINMASDI — 2026-09-16 da
# tuzatilgan wall-kill kodi CI'da yashil bo'lib, produksiya esa eski
# binarni ishlatib turgan edi.
#
# Endi `apps/web` bilan bir xil naqsh: image'ga `org.rankwant.git-sha`
# yorlig'i yoziladi (`services/judge-go/Dockerfile`; qiymat `deploy.sh`
# dan `GIT_SHA` orqali keladi).
#
# ⚠️ Yorliq `unknown` bo'lsa — «tekshirilmadi» va `stale` oshadi: yorliqsiz
# build aynan eski build demakdir, uni «mos» deb o'qish yolg'on yashil.
if docker inspect rankwant-judge-1 >/dev/null 2>&1; then
  jshow="$(img_time rankwant-judge:latest)"
  jsha="$(docker inspect rankwant-judge-1 --format '{{index .Config.Labels "org.rankwant.git-sha"}}' 2>/dev/null)"
  src_sha="$(git rev-parse HEAD 2>/dev/null)"

  if [ -z "$jsha" ] || [ "$jsha" = "<no value>" ] || [ "$jsha" = "unknown" ]; then
    printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$Y" 'TEKSHIRILMADI' "$N" "$jshow" \
      "yorliq yo'q — binary hash'i solishtirilmaydi, qayta quring"
    stale=$((stale + 1))
  else
    # Same rule as web, see label_state at the top.
    case "$(label_state "$jsha" services/judge-go)" in
      same)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$G" 'joyida' "$N" "$jshow" \
          "yorliq HEAD bilan bir xil (${jsha:0:12})" ;;
      current)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$G" 'joyida' "$N" "$jshow" \
          "yorliq ${jsha:0:12}: undan beri services/judge-go o'zgarmagan" ;;
      unknown)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$Y" 'TEKSHIRILMADI' "$N" "$jshow" \
          "yorliq ${jsha:0:12} bu klonda yo'q — git fetch, keyin qayta tekshiring"
        stale=$((stale + 1)) ;;
      *)
        printf '%-22s %s%-15s%s %-22s %s\n' 'rankwant-judge-1' "$R" 'ESKIRGAN' "$N" "$jshow" \
          "yorliq ${jsha:0:12} dan beri services/judge-go o'zgargan (HEAD ${src_sha:0:12})"
        stale=$((stale + 1)) ;;
    esac
  fi
  check_build_label rankwant-judge-1 rankwant-judge:latest
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
if [ "$unlabeled" -gt 0 ]; then
  printf '%s%s konteynerda built-at yorlig'"'"'i yo'"'"'q — build argumentlari uzatilmagan.%s\n' \
    "$Y" "$unlabeled" "$N"
  printf 'Bu «eskirgan» degani emas (kod joyida), lekin o'"'"'sha sozlama `git-sha` ni ham\n'
  printf 'bo'"'"'sh qoldirishi mumkin. Sabab odatda bitta: servis compose'"'"'ning QISQA shakli\n'
  printf '(`build: ./apps/api`) bilan qurilgan — u yerda `args` berib bo'"'"'lmaydi.\n'
  printf 'Qayta qurish: tools/deploy.sh (u `BUILT_AT` ni o'"'"'zi uzatadi).\n'
fi

if [ "$stale" -gt 0 ] || [ "$envbad" -gt 0 ]; then
  exit 1
fi

printf '%sHamma konteyner joriy kodda.%s\n' "$G" "$N"
exit 0


