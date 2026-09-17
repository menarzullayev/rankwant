#!/usr/bin/env bash
# CI haqiqatan ishlayaptimi?
#
# Nega kerak: `gh run list` da `queued` va `startup_failure` IKKALASI ham
# "hali natija yo'q" bo'lib ko'rinadi, lekin sabablari butunlay boshqa:
#
#   queued          → ishlaydigan runner yo'q. Workflow TO'G'RI, lekin
#                     hech kim uni olmayapti. Tuzatish: runner.
#   startup_failure → workflow fayli yoki ruxsati xato. Runner bor-yo'qligi
#                     ahamiyatsiz — run UMUMAN boshlanmaydi (0 job).
#                     Tuzatish: YAML / `permissions:`.
#
# Ikkalasini aralashtirsangiz noto'g'ri joyni tuzatasiz: runner qaytarib,
# ruxsat xatosini och qoldirasiz yoki aksincha.
#
# ⚠️ 2026-09-13: shu ikki holat bir vaqtda uchradi — runner oflayn edi
# (hammasi `queued`) va `deploy.yml` da `pull-requests: read` yo'q edi
# (Deploy `startup_failure`). Faqat bittasini ko'rish oson edi.
#
# Ishlatish:  bash tools/check_ci.sh [--limit N]
# Chiqish:    0 — runner tirik, run'lar haqiqiy natija beryapti
#             1 — MUAMMO (runner oflayn yoki startup_failure)
#             2 — O'LCHAB BO'LMADI (`gh` yo'q / auth yo'q). Bu "yaxshi"
#                 EMAS: chiqish 2 saytning holati haqida HECH NARSA
#                 demaydi, shuning uchun uni yashil deb o'qib bo'lmaydi.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

if [ -t 1 ]; then
  R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  R=''; G=''; Y=''; B=''; N=''
fi

limit=8
while [ $# -gt 0 ]; do
  case "$1" in
    --limit) limit="${2:-8}"; shift 2 ;;
    -h|--help) sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf "Noma'lum argument: %s\n" "$1" >&2; exit 2 ;;
  esac
done

# ── O'qish qatlami ──────────────────────────────────────────────────────
# Test hook: stub berilganda tarmoqqa UMUMAN chiqilmaydi. Stub — `jq`
# chiqishining o'zi (quyidagi naqshlar), ya'ni parslash kodi ikkala
# yo'lda ham bir xil ishlaydi.
runners_raw=""
runs_raw=""

if [ -n "${CI_RUNNERS_STUB:-}" ]; then
  runners_raw="$(printf '%b\n' "$CI_RUNNERS_STUB")"
else
  if ! command -v gh >/dev/null 2>&1; then
    printf "%s✗ \`gh\` topilmadi — CI holatini o'qib bo'lmadi.%s\n" "$R" "$N" >&2
    exit 2
  fi
  if ! runners_raw="$(gh api repos/{owner}/{repo}/actions/runners \
        --jq '.runners[] | "\(.name)|\(.os)|\(.status)"' 2>&1)"; then
    printf "%s✗ Runner ro'yxatini o'qib bo'lmadi.%s\n" "$R" "$N" >&2
    printf '  %s\n' "${runners_raw%%$'\n'*}" >&2
    printf '  `gh auth status` bilan tekshiring.\n' >&2
    exit 2
  fi
fi

# jq ifodasi ALOHIDA o'zgaruvchida. `"$( … --jq "…\"…\"" …)"` ko'rinishida
# qo'shtirnoq ichida qo'shtirnoq uch pog'ona bo'lib qoladi va bash uni
# noto'g'ri o'qiydi: `unexpected EOF while looking for matching '"'`.
# Bitta qo'shtirnoqli satr muammoni butunlay yo'q qiladi.
JQ_RUNS='.[] | "\(.workflowName)|\(.status)|\(.conclusion)|\(.headSha[0:7])|\(.createdAt)"'

if [ -n "${CI_RUNS_STUB:-}" ]; then
  runs_raw="$(printf '%b\n' "$CI_RUNS_STUB")"
else
  if ! runs_raw="$(gh run list --limit "$limit" \
        --json workflowName,status,conclusion,headSha,createdAt,event \
        --jq "$JQ_RUNS" 2>&1)"; then
    printf "%s✗ Run ro'yxatini o'qib bo'lmadi.%s\n" "$R" "$N" >&2
    printf '  %s\n' "${runs_raw%%$'\n'*}" >&2
    exit 2
  fi
fi

# ── 1. Runnerlar ────────────────────────────────────────────────────────
# Runner oflayn bo'lsa qolgan hamma narsa ma'nosiz: run'lar navbatda
# turadi va hech qachon boshlamaydi. Shuning uchun BIRINCHI shu.
online=0
total=0
printf '%sRunnerlar%s\n' "$B" "$N"
printf '%-26s %-10s %s\n' 'NOM' 'OS' 'HOLAT'
printf '%s\n' '--------------------------------------------------------'

if [ -z "$runners_raw" ]; then
  printf '%s%-26s%s %s\n' "$Y" "(ro'yxat bo'sh)" "$N" "runner ro'yxatdan o'tmagan"
fi

while IFS='|' read -r rname ros rstatus; do
  rname="${rname%$'\r'}"; ros="${ros%$'\r'}"; rstatus="${rstatus%$'\r'}"
  [ -z "$rname" ] && continue
  total=$((total + 1))
  if [ "$rstatus" = "online" ]; then
    online=$((online + 1))
    printf '%-26s %-10s %s%s%s\n' "$rname" "$ros" "$G" "online" "$N"
  else
    printf '%-26s %-10s %s%s%s\n' "$rname" "$ros" "$R" "$rstatus" "$N"
  fi
done <<< "$runners_raw"

if [ "$total" -eq 0 ]; then
  printf '%s%-26s%s %s\n' "$R" "0 runner" "$N" "ro'yxatdan o'tgan runner YO'Q"
fi

# ── 2. Runlar ───────────────────────────────────────────────────────────
# `startup_failure` — boshqa sinf: u runner holatidan MUSTAQIL.
printf '\n%sOxirgi %s run%s\n' "$B" "$limit" "$N"
printf '%-14s %-11s %-18s %-8s %s\n' 'WORKFLOW' 'STATUS' 'CONCLUSION' 'SHA' 'YOSHI'
printf '%s\n' '---------------------------------------------------------------------'

startup_fail=0
queued=0
completed=0
shown=0
stuck=0
now_epoch="$(date -u +%s)"

# Qotib qolgan run chegarasi. O'lchandi (2026-09-16): job 22 daqiqa
# `in progress` bo'lib turdi, runner esa `online, busy=False` edi —
# GitHub job'ni boshlangan deb hisoblaydi, uni bajaradigan
# `Runner.Worker` esa yo'q (assignment eskirgan). `timeout-minutes`
# buni TUTMAYDI: u BAJARILAYOTGAN qadamga qo'llanadi, navbatga emas.
# Oddiy job 1-3 daqiqada tugaydi, shuning uchun 15 daqiqa — aniq signal.
STUCK_SECONDS="${CI_STUCK_SECONDS:-900}"

while IFS='|' read -r wname wstatus wconcl wsha wcreated; do
  wname="${wname%$'\r'}"; wstatus="${wstatus%$'\r'}"; wconcl="${wconcl%$'\r'}"
  wsha="${wsha%$'\r'}"; wcreated="${wcreated%$'\r'}"
  [ -z "$wname" ] && continue
  shown=$((shown + 1))
  d=""   # oldingi iteratsiyadan qolmasin

  # Yoshi — `queued` ning halol sababini ajratadi: bir necha soniya
  # navbat normal, bir necha SOAT navbat = runner yo'q.
  age='-'
  if [ -n "$wcreated" ]; then
    ep="$(date -u -d "$wcreated" +%s 2>/dev/null || true)"
    # ⚠️ `date -u -d ""` BO'SH argument bilan ham exit 0 qaytaradi va
    # jimgina hozirgi vaqtni beradi — shuning uchun avval bo'shligi
    # tekshiriladi (tools/check_deploy.sh dagi bir xil tuzoq).
    if [ -n "$ep" ]; then
      d=$((now_epoch - ep))
      # ⚠️ `$(((d % 3600) / 60))` — uchta ochilgan qavs. Bittasi
      # tushib qolsa bash `))` ni butun fayl bo'ylab qidiradi va
      # «unexpected EOF» beradi, xato esa butunlay boshqa qatorda
      # ko'rinadi. Oraliq o'zgaruvchi buni o'qib bo'ladigan qiladi.
      if [ "$d" -ge 3600 ]; then
        hh=$((d / 3600))
        mm=$(( (d % 3600) / 60 ))
        age="${hh}s ${mm}d"
      elif [ "$d" -ge 60 ]; then
        age="$((d / 60))d"
      else
        age="${d}s"
      fi
    fi
  fi

  # Qotgan run: tugamagan va kutilgan vaqtdan ancha oshgan.
  if [ -n "$d" ] && [ "$wstatus" != "completed" ] && [ "$d" -ge "$STUCK_SECONDS" ]; then
    stuck=$((stuck + 1))
  fi

  label="$wstatus"
  colour=''
  if [ "$wstatus" = "completed" ]; then
    completed=$((completed + 1))
    label="$wconcl"
    case "$wconcl" in
      success) colour="$G" ;;
      startup_failure) colour="$R"; startup_fail=$((startup_fail + 1)) ;;
      *) colour="$Y" ;;
    esac
  elif [ "$wstatus" = "queued" ] || [ "$wstatus" = "in_progress" ]; then
    queued=$((queued + 1))
    colour="$Y"
  fi

  printf '%-14s %-11s %s%-18s%s %-8s %s\n' \
    "${wname:0:14}" "$wstatus" "$colour" "${wconcl:-—}" "$N" "${wsha:-—}" "$age"
done <<< "$runs_raw"

# ── 3. Hukm ─────────────────────────────────────────────────────────────
printf '\n'
problems=0

if [ "$online" -eq 0 ]; then
  printf "%s✗ Ishlaydigan runner YO'Q (%s ta ro'yxatda, 0 tasi online).%s\n" "$R" "$total" "$N"
  printf '  Bu holda pushdan keyingi HAR run navbatda qoladi va hech qachon\n'
  printf "  boshlamaydi — CI darvozasi JONSIZ. Tuzatish: runner'ni ishga tushirish.\n"
  problems=1
fi

if [ "$startup_fail" -gt 0 ]; then
  printf '%s✗ %s ta run `startup_failure` — workflow fayli yoki ruxsati xato.%s\n' \
    "$R" "$startup_fail" "$N"
  printf '  Bu runner holatidan MUSTAQIL: run umuman boshlanmaydi (0 job).\n'
  printf "  Eng ko'p uchraydigan sabab — chaqiriladigan workflow (%s) o'zida\n" 'uses: ./.github/workflows/…'
  printf "  so'ragan ruxsatni caller BERMAYAPTI. Ruxsat faqat KAMAYTIRILADI.\n"
  problems=1
fi

# Qotib qolgan run — runner TIRIK bo`lganda ham uchraydi, ya'ni yuqoridagi
# ikki sababdan MUSTAQIL. Bugun (2026-09-16) aynan shu bo`ldi: runner
# `online, busy=False`, run esa 22 daqiqa `queued`/`in progress`.
if [ "$stuck" -gt 0 ]; then
  printf '%s✗ %s ta run %s daqiqadan ortiq davom etmoqda (tugamagan).%s\n' \
    "$R" "$stuck" "$((STUCK_SECONDS / 60))" "$N"
  printf '  Runner tirik bo`lsa ham bu QOTISH bo`lishi mumkin: GitHub job`ni\n'
  printf '  boshlangan deb hisoblaydi, uni bajaradigan `Runner.Worker` esa yo`q.\n'
  printf '  Tekshirish:  docker exec rankwant-ci-runner ps -eo pid,etimes,args\n'
  printf '  Yechim:      gh run cancel <id> && sleep 20 && gh run rerun <id>\n'
  problems=1
fi

if [ "$problems" -eq 0 ] && [ "$online" -gt 0 ] && [ "$queued" -gt 0 ] && [ "$completed" -eq 0 ]; then
  printf "%s… Runner tirik, %s ta run navbatda — natija hali yo'q.%s\n" "$Y" "$queued" "$N"
fi

if [ "$problems" -eq 0 ]; then
  printf "%s✓ Runner tirik, run'lar haqiqiy natija beryapti.%s\n" "$G" "$N"
  exit 0
fi

exit 1
