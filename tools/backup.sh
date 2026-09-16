#!/usr/bin/env bash
# RankWant preview zaxirasi — 10-operations § Backup.
#
# Postgres dump + MinIO nusxasi, `RANKWANT_BACKUP_KEEP` kun saqlanadi
# (standart 30; oylik Windows vazifasi 95 beradi). Preview bitta
# mashinada ishlaydi, ya'ni `rankwant_pgdata` va `rankwant_miniodata`
# volume'lari yo'qolsa 2000+ masalali import qaytadan qilinishi kerak
# bo'lardi (KEP API tezlik cheklovi bilan bir necha soat).
#
# Bitta nusxa ikkala tizim uchun: Linux'da ham, Windows'da (Git Bash)
# ham SHU skript ishlaydi. PowerShell'dagi ikkinchi nusxa ataylab
# yozilmagan — ikki nusxa jimgina ajralib ketadi (`runner-keepalive.ps1`
# va `runner_keepalive.ps1` bilan bir marta shunday bo'lgan).
#
# Jadval — 30 kunda bir marta, faqat lokal (2026-09-17 qarori).
# Linux, cron (har oyning 1-kuni 04:00 da) — yo'l repo qayerda bo'lsa o'sha:
#   0 4 1 * * RANKWANT_BACKUP_KEEP=95 "$HOME"/rankwant/tools/backup.sh >> "$HOME"/backups/rankwant/backup.log 2>&1
#
# Windows: `RankWant Monthly Backup` rejalashtirilgan vazifasi (to'liq
# ro'yxatga olish buyrug'i 10-operations § Backup da). Yalang'och `bash`
# ISHLATILMAYDI — u WSL relay'iga tushadi va skript umuman ishga
# tushmaydi; Git Bash'ning to'liq yo'li beriladi.
#
# Offsite nusxa (Cloudflare R2, `backups/` prefiksi) — STANDART O'CHIQ.
# Saidakbar aka qarori (2026-09-17): zaxira faqat lokal; yoqish faqat uning
# aniq tasdig'i bilan (CLAUDE.md § Saidakbar aka qarorlari).
#   tools/backup.sh              # faqat lokal (standart)
#   tools/backup.sh --offsite    # R2 majburiy — kalitlar bo'lmasa yiqiladi
#   tools/backup.sh --no-offsite # faqat lokal (aniq)
#
# Tiklash sinovi — HAR yurishda AVTOMATIK o'tkaziladi (hujjat talabi:
# usiz backup «yo'q» deb hisoblanadi). Alohida chaqirish ham mumkin:
#   tools/backup.sh --restore-test
# O'chirish: RANKWANT_BACKUP_RESTORE_TEST=off
#
# Bitta arxiv butunligini docker'siz tekshirish (salbiy test shuni
# ishlatadi):
#   tools/backup.sh --verify-dump <fayl.sql.gz>
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="${RANKWANT_BACKUP_DIR:-$HOME/backups/rankwant}"
keep_days="${RANKWANT_BACKUP_KEEP:-30}"
stamp="$(date +%Y%m%d-%H%M%S)"

# ⚠️ Yo'l konvertatsiyasi (o'lchandi 2026-09-16).
#
# Git Bash'ning har xil nashri `/c/Users/...` ni turlicha o'giradi:
#   · `C:\Program Files\Git\bin\bash.exe`  → to'g'ri
#   · PortableGit (agent shell)            → `C:\c\Users\...` — disk harfi
#                                            IKKI marta
# Ikkinchisida `docker compose --env-file` faylni topolmaydi va skript
# jim yiqiladi, ortda 0 baytli `*.sql.gz.part` qoladi. `MSYS_NO_PATHCONV=1`
# yordam bermadi (sinab ko'rilgan).
#
# `cygpath -w` har ikkala holatda ham to'g'ri Windows yo'lini beradi.
# Linux/CI da `cygpath` yo'q — u holda yo'l o'zgarishsiz qoladi.
winpath() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi
}
# ⚠️ `-p rankwant` SHART. `docker-compose.yml` da `name:` yo'q, ya'ni
# loyiha nomi KATALOGDAN olinadi. Boshqa klondan yoki git worktree'dan
# chaqirilsa nom `agent-…` bo'lib qoladi va skript jonli stack'ni emas,
# bo'sh loyihani ko'radi (o'lchandi 2026-09-15: worktree'da nom
# `agent-a51a101abc58a171f`). `tools/handoff.ps1` nomni aynan shu sababdan
# qotirib qo'ygan.
compose=(docker compose -p rankwant --env-file "$(winpath "$root/.env.public")"
         -f "$(winpath "$root/docker-compose.yml")"
         -f "$(winpath "$root/docker-compose.public.yml")")

# ── Dump butunligi ───────────────────────────────────────────────────
# Kunlik yurish ham, salbiy test ham SHU funksiyadan o'tadi: test
# tekshiruvning nusxasini emas, o'zini sinaydi.
#
# Ikki xil nosozlik ikki xil qadamda tutiladi:
#   `gzip -t` — arxiv kesilgan yoki buzilgan;
#   trailer   — gzip butun, lekin dump o'rtada tugagan (pg_dump o'ldi,
#               disk to'ldi). Ikkinchisi xavfliroq: arxiv «sog'lom»
#               ko'rinadi va faqat tiklash kunida bilinadi.
verify_dump() {
  local f="${1:-}"
  if [ -z "$f" ] || [ ! -f "$f" ]; then
    echo "XATO: fayl yo'q — ${f:-<berilmadi>}" >&2
    return 1
  fi
  if ! gzip -t "$f" 2>/dev/null; then
    echo "XATO: arxiv buzilgan (gzip -t) — $f" >&2
    return 1
  fi
  if ! zcat "$f" | tail -c 4096 | grep -q "PostgreSQL database dump complete"; then
    echo "XATO: dump chala — yakuniy qator yo'q: $f" >&2
    return 1
  fi
  echo "dump butun: $f"
}

# Bu rejim docker'ga ham, `$dest` katalogiga ham tegmaydi — shuning uchun
# `mkdir` dan OLDIN turadi va CI da ham ishlaydi.


# ── Offsite (Cloudflare R2) ──────────────────────────────────────────
#
# Nega: zaxira o'sha C: diskda yotadi. Disk o'lsa (yoki o'g'irlansa,
# yong'in bo'lsa) zaxira ham u bilan ketadi. 2026-09-17 da o'lchandi:
# offsite nusxa YO'Q edi va bu eng katta DR teshigi edi.
#
# Naqsh `tools/handoff.sh` dan OLINGAN, qaytadan yozilmagan: rclone
# KONTEYNERDA ishlaydi, ya'ni host'ga hech narsa o'rnatilmaydi, kalitlar
# esa buyruq qatoriga chiqmaydi - faqat muhit orqali beriladi.
#
# Rejim (`RANKWANT_BACKUP_OFFSITE` yoki argument):
#   off  (standart, --no-offsite) - umuman tegmaydi
#   on   (--offsite)              - kalitlar bo'lmasa YIQILADI
#   auto                          - kalitlar bo'lsa yuklaydi, bo'lmasa ogohlantiradi
# The default is `off` because the owner chose local-only backups. With `auto`,
# the keys in `.env.handoff` made every run upload unencrypted dumps (user PII)
# to R2 — which happened on 2026-09-17 before this default was restored.
# tools/check_decisions.py fails CI if it changes.
offsite="${RANKWANT_BACKUP_OFFSITE:-off}"
r2_keep_days="${RANKWANT_BACKUP_R2_KEEP:-180}"

r2_load() {
  [ -f "$root/.env.handoff" ] || return 1
  set -a
  # shellcheck disable=SC1091
  . "$root/.env.handoff"
  set +a
  [ -n "${R2_ACCOUNT_ID:-}" ] && [ -n "${R2_ACCESS_KEY_ID:-}" ] &&
    [ -n "${R2_SECRET_ACCESS_KEY:-}" ] && [ -n "${R2_BUCKET:-}" ]
}

r2_export() {
  export RCLONE_CONFIG_R2_TYPE=s3
  export RCLONE_CONFIG_R2_PROVIDER=Cloudflare
  export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
  export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
  export RCLONE_CONFIG_R2_ENDPOINT="https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com"
  export RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
}

# Mount uchun `cygpath -m` (C:/Users/...), `-w` EMAS: teskari chiziqlar
# `-v` argumentida ajratgich bilan chalkashadi.
r2_mount() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -m "$dest"; else printf '%s' "$dest"; fi
}

rc() {
  MSYS_NO_PATHCONV=1 docker run --rm -i --user "$(id -u):$(id -g)" \
    -v "$(r2_mount):/backups" \
    -e RCLONE_CONFIG_R2_TYPE -e RCLONE_CONFIG_R2_PROVIDER \
    -e RCLONE_CONFIG_R2_ACCESS_KEY_ID -e RCLONE_CONFIG_R2_SECRET_ACCESS_KEY \
    -e RCLONE_CONFIG_R2_ENDPOINT -e RCLONE_CONFIG_R2_NO_CHECK_BUCKET \
    rclone/rclone:1.75 -q "$@"
}

# Yuklaydi va HAJMNI solishtiradi. «rclone exit 0 berdi» yetarli emas:
# yarim yuklangan obyekt ham 0 qaytaradi.
r2_upload() {
  local target name local_bytes remote_bytes
  target="r2:$R2_BUCKET/backups"
  for f in "$sql" "$objects"; do
    name="$(basename "$f")"
    if ! rc copyto "/backups/$name" "$target/$name"; then
      echo "  R2 XATO: yuklanmadi - $name" >&2
      return 1
    fi
    local_bytes="$(wc -c <"$f" | tr -d ' ')"
    remote_bytes="$(rc lsl "$target/$name" | awk '{print $1}' | tr -d ' ')"
    if [ "$local_bytes" != "$remote_bytes" ]; then
      echo "  R2 XATO: hajm mos emas - $name lokal=$local_bytes masofada=$remote_bytes" >&2
      return 1
    fi
    echo "  R2 ok: $name ($local_bytes bayt)"
  done
  # Eskilarini tozalash. Faqat `backups/` prediksi ichida ishlaydi, ya'ni
  # handoff obyektlariga tegmaydi.
  rc delete "$target" --min-age "${r2_keep_days}d" || true
  return 0
}

offsite_run() {
  if [ "$offsite" = "off" ]; then
    echo "  R2: o'tkazib yuborildi (--no-offsite)"
    offsite_status=skip
    return 0
  fi
  if ! r2_load; then
    if [ "$offsite" = "on" ]; then
      echo "XATO: --offsite so'raldi, lekin R2 kalitlari yo'q (.env.handoff)" >&2
      offsite_status=fail
      return 1
    fi
    echo "  R2 OGOHLANTIRISH: kalitlar yo'q (.env.handoff) - offsite nusxa YO'Q"
    offsite_status=YOQ
    return 0
  fi
  r2_export
  echo "  R2 -> $R2_BUCKET/backups"
  if r2_upload; then
    offsite_status=ok
    return 0
  fi
  offsite_status=fail
  return 1
}

# Offsite rejimi argumentdan ham olinadi (blok yuqorida `auto` qo'yadi).
for arg in "$@"; do
  case "$arg" in
    --offsite) offsite=on ;;
    --no-offsite) offsite=off ;;
  esac
done

if [ "${1:-}" = "--verify-dump" ]; then
  if verify_dump "${2:-}"; then exit 0; fi
  exit 1
fi

mkdir -p "$dest"
umask 077

# ── Tiklash sinovi ───────────────────────────────────────────────────
# Hujjat: «Tiklash sinovi o'tkazilmasa, backup YO'Q deb hisoblanadi».
# Eng so'nggi dump ALOHIDA `restore_test` bazasiga tiklanadi, jadvallar
# bo'sh emasligi va havolalar butunligi tekshiriladi, keyin o'sha baza
# tashlanadi.
#
# ⚠️ Jonli `rankwant` bazasiga TEGILMAYDI: quyidagi har bir `psql`
# chaqiruvi `-d postgres` (faqat `restore_test` ni yaratish/tashlash
# uchun) yoki `-d restore_test` ga boradi, va `DROP DATABASE` hech qachon
# `rankwant` ni nomlamaydi. Dumpning o'z `--clean` qatorlari ham
# `restore_test` ichida bajariladi.
# ── Tiklash sinovi ───────────────────────────────────────────────────
# Hujjat: «Tiklash sinovi o'tkazilmasa, backup YO'Q deb hisoblanadi».
# Eng so'nggi dump ALOHIDA `restore_test` bazasiga tiklanadi, jadvallar
# bo'sh emasligi va havolalar butunligi tekshiriladi, keyin o'sha baza
# tashlanadi.
#
# ⚠️ Jonli `rankwant` bazasiga TEGILMAYDI: har bir `psql` chaqiruvi
# `-d postgres` (faqat `restore_test` ni yaratish/tashlash uchun) yoki
# `-d restore_test` ga boradi, va `DROP DATABASE` hech qachon `rankwant`
# ni nomlamaydi. Dumpning o'z `--clean` qatorlari ham `restore_test`
# ichida bajariladi.

restore_test() {
  local latest="${1:-}"
  latest="$(ls -t "$dest"/pg-*.sql.gz 2>/dev/null | head -1)"
  [ -n "$latest" ] || { echo "zaxira topilmadi: $dest" >&2; return 1; }
  echo "tiklanmoqda: $latest"

  # Tekshiruv jonli baza bilan SOLISHTIRMAYDI. Ilgari shunday edi va u
  # muntazam yolg'on yiqilardi: zaxira vaqt kesimi, jonli baza esa
  # o'shandan beri o'zgargan bo'ladi — o'lchandi, 128 ta sinov hisobi
  # o'chirilgandan keyin sinov «qator sonlari mos emas» dedi, holbuki
  # tiklash mukammal ishlagan edi. Muntazam yolg'on ogohlantirish esa
  # eng yomoni: odam uni e'tiborsiz qoldirishni o'rganadi.
  #
  # Haqiqiy savol boshqa: «shu zaxiradan tiklana olamanmi?» Uning javobi
  # dumpning to'liq va yaxlit ekanligida.
  tables="problems_problem core_user judging_attempt qvant_qvanttransaction problems_testcase"

  "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q \
    -c "DROP DATABASE IF EXISTS restore_test;" -c "CREATE DATABASE restore_test;"
  # `ON_ERROR_STOP=1` — asosiy nosozlik turini shu ushlaydi: kesilgan yoki
  # buzilgan dump o'rtasida to'xtaydi.
  if ! zcat "$latest" | "${compose[@]}" exec -T postgres psql -U rankwant -d restore_test -q \
      -v ON_ERROR_STOP=1 >/dev/null; then
    "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q -c "DROP DATABASE restore_test;"
    echo "XATO: dump tiklanmadi — zaxira yaroqsiz" >&2
    return 1
  fi

  fail=0
  for t in $tables; do
    n="$("${compose[@]}" exec -T postgres psql -U rankwant -d restore_test -t -A \
         -c "SELECT count(*) FROM $t;" 2>/dev/null | tr -d '\r')"
    if [ -z "$n" ]; then
      echo "  ✗ $t — jadval yo'q"; fail=1
    elif [ "$n" -eq 0 ]; then
      echo "  ✗ $t — bo'sh"; fail=1
    else
      echo "  ✓ $t: $n qator"
    fi
  done

  # Yaxlitlik: tiklangan nusxada osilib qolgan havola bo'lmasligi kerak.
  # Bu ustunlarni tanlab tashlagan yoki yarim ko'chirilgan dumpni ushlaydi.
  yetim="$("${compose[@]}" exec -T postgres psql -U rankwant -d restore_test -t -A -c "
    SELECT (SELECT count(*) FROM judging_attempt a
              LEFT JOIN core_user u ON u.id = a.user_id WHERE u.id IS NULL)
         + (SELECT count(*) FROM judging_attempt a
              LEFT JOIN problems_problem p ON p.id = a.problem_id WHERE p.id IS NULL);" 2>/dev/null | tr -d '\r')"
  if [ "${yetim:-1}" -eq 0 ]; then
    echo "  ✓ havolalar butun (yetim urinish yo'q)"
  else
    echo "  ✗ $yetim ta yetim urinish — dump yarim"; fail=1
  fi

  "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q -c "DROP DATABASE restore_test;"
  [ "$fail" -eq 0 ] || { echo "tiklash sinovi YIQILDI" >&2; return 1; }
  echo "tiklash sinovi o'tdi: $latest"
  return 0
}

# CLI: eng so'nggi dumpni sinaydi va shu bilan tugaydi.
if [ "${1:-}" = "--restore-test" ]; then
  newest="$(ls -t "$dest"/pg-*.sql.gz 2>/dev/null | head -1)"
  [ -n "$newest" ] || { echo "zaxira topilmadi: $dest" >&2; exit 1; }
  restore_test "$newest" || exit 1
  exit 0
fi

# ── Postgres ─────────────────────────────────────────────────────────
sql="$dest/pg-$stamp.sql.gz"
"${compose[@]}" exec -T postgres pg_dump -U rankwant --clean --if-exists rankwant \
  | gzip -9 > "$sql.part"
mv "$sql.part" "$sql"

# Dump o'qilishini TEKSHIRAMIZ: hujjat aytadi — tiklash sinovisiz backup
# yo'q deb hisoblanadi. To'liq tiklash kunlik ish uchun qimmat, lekin
# arxiv butunligini va oxirigacha yozilganini har safar tekshirish mumkin.
verify_dump "$sql"

# ── MinIO (masala testlari va ko'chirilgan media) ────────────────────
#
# ⚠️ Git Bash (MSYS) KONTEYNER ichidagi yo'llarni ham Windows yo'liga
# aylantiradi: `-C /data` → `C:/Program Files/Git/data`, tar esa
# «can't change directory» deb yiqiladi (o'lchandi 2026-09-15).
# Shuning uchun docker chaqiruvida konversiya o'chiriladi.
#
# ⚠️ Host katalogi endi MOUNT QILINMAYDI — arxiv stdout orqali oqadi.
# Sababi ham o'lchandi: `MSYS_NO_PATHCONV=1` bilan `-v "$dest:/out"`
# aylantirilmay o'tadi va Docker Desktop uni Linux VM ICHIDAGI yo'l deb
# ochadi. Buyruq `exit 0` beradi, host katalogi esa BO'SH qoladi —
# ya'ni «muvaffaqiyatli» deb yozilgan, ichida ma'lumoti yo'q zaxira.
# Mount bo'lmasa aylantiriladigan host yo'li ham yo'q.
#
# Linux'da `MSYS_NO_PATHCONV` shunchaki ishlatilmaydigan o'zgaruvchi —
# bitta nusxa ikkala tizimda ham bir xil ishlaydi.
objects="$dest/minio-$stamp.tar.gz"
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
  docker run --rm -v rankwant_miniodata:/data:ro alpine \
  tar czf - -C /data . > "$objects.part"
mv "$objects.part" "$objects"
tar tzf "$objects" >/dev/null

# ── Offsite nusxa (R2) ───────────────────────────────────────────────
# Lokal dump allaqachon yaroqli; offsite yiqilsa bu HISOBGA OLINADI va
# skript nolga teng bo'lmagan kod bilan tugaydi. Jimgina o'tib ketgan
# offsite — eng yomon holat: zaxira bor deb o'ylaysiz, u yo'q.
offsite_status=ok
offsite_run || true

# ── Tiklash sinovi (HAR yurishda) ────────────────────────────────────
# Doktrina sinovni choraklik MAJBURIY qiladi, lekin u qo'lda edi va
# 2026-09-17 gacha bir marta ham o'tkazilmagan. Sinov 9 soniya oladi
# (o'lchandi), ya'ni har yurishda o'tkazish arzon: zaxira YARATILGAN
# paytda tiklanishingiz tasdiqlanadi, «bir kun sinab ko'ramiz» emas.
#
# ⚠️ Sinov YIQILSA skript ham yiqiladi: tiklanmaydigan zaxira — zaxira
# emas. Bu ataylab, chunki jimgina o'tkazib yuborilgan tekshiruv eng
# yomon holat: qog'ozda bor, amalda yo'q.
if [ "${RANKWANT_BACKUP_RESTORE_TEST:-auto}" = "off" ]; then
  restore_status=skip
elif restore_test "$sql"; then
  restore_status=ok
else
  restore_status=YIQILDI
fi

# ── Eskilarini tozalash ──────────────────────────────────────────────
# ⚠️ Tozalash JIMGINA ishlamay qolmasligi kerak, shuning uchun o'chirilgan
# fayllar sanaladi va hisobotga chiqadi. `find` — GNU findutils; Git Bash
# ham shuni beradi (o'lchandi: 4.10.0, `/usr/bin/find`). Windows'ning
# `System32\find.exe` PATH'da keyinroq turadi va `-mtime` ni bilmaydi —
# u tanlansa raqam 0 bo'lib qoladi va buni hisobotdan ko'rish mumkin.
before="$(find "$dest" -name 'pg-*.sql.gz' -o -name 'minio-*.tar.gz' | wc -l)"
find "$dest" -name 'pg-*.sql.gz' -mtime "+$keep_days" -delete
find "$dest" -name 'minio-*.tar.gz' -mtime "+$keep_days" -delete
# ⚠️ Yiqilgan yurish `.part` bo'lagini qoldiradi, saqlash qoidasi esa uni
# KO'RMAYDI: u `pg-*.sql.gz` naqshiga tushmaydi. Ya'ni har yiqilgan yurish
# ~17 MB ni abadiy band qilardi va C: yagona disk bo'lgani uchun bu
# to'planib qolardi. Bir kundan eski bo'laklar tozalanadi; joriy
# yurishnikiga tegmaydi.
find "$dest" -name '*.gz.part' -mtime +1 -delete
after="$(find "$dest" -name 'pg-*.sql.gz' -o -name 'minio-*.tar.gz' | wc -l)"

# ⚠️ C: — yagona qattiq disk, undagi bo'sh joy esa tez o'zgaradi
# (2026-09-15 da bir necha soat ichida 5.8 GB dan 31.5 GB gacha). Shuning
# uchun skript bo'sh joyga emas, o'z NARXiga qaraydi: katalogning JAMI
# hajmi har yurishda yoziladi — oylik jadvalda ~3 ta nusxa ~75 MB turadi
# (kunlik jadvalda ~700 MB edi) va bu raqam jimgina o'sib ketmasligi kerak.
printf '%s  pg=%s  minio=%s  jami=%s  fayl=%s (-%s)  r2=%s  restore=%s\n' "$stamp" \
  "$(du -h "$sql" | cut -f1)" "$(du -h "$objects" | cut -f1)" \
  "$(du -sh "$dest" | cut -f1)" "$after" "$((before - after))" \
  "$offsite_status" "$restore_status"

# ⚠️ `skip` va `YOQ` — xato EMAS (lokal dump yaroqli), lekin ular ham
# «ok» bo'lib ko'rinmasligi kerak: aks holda log yashil o'qiladi-yu,
# offsite nusxa yo'q bo'ladi.
if [ "$offsite_status" = "fail" ] || [ "$restore_status" = "YIQILDI" ]; then
  echo "ZAXIRA ISHONCHSIZ: offsite=$offsite_status restore=$restore_status" >&2
  exit 1
fi
