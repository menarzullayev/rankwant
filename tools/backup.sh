#!/usr/bin/env bash
# RankWant preview zaxirasi — 10-operations § Backup.
#
# Postgres dump + MinIO nusxasi, 30 kun saqlanadi. Preview bitta
# mashinada ishlaydi, ya'ni `rankwant_pgdata` va `rankwant_miniodata`
# volume'lari yo'qolsa 2000+ masalali import qaytadan qilinishi kerak
# bo'lardi (KEP API tezlik cheklovi bilan bir necha soat).
#
# Cron uchun (har kuni 04:00 da):
#   0 4 * * * /home/nsn/Workspace/Web_Projects/rankwant/tools/backup.sh >> ~/backups/rankwant/backup.log 2>&1
#
# Choraklik tiklash sinovi (hujjat talabi):
#   tools/backup.sh --restore-test
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="${RANKWANT_BACKUP_DIR:-$HOME/backups/rankwant}"
keep_days="${RANKWANT_BACKUP_KEEP:-30}"
stamp="$(date +%Y%m%d-%H%M%S)"
compose=(docker compose --env-file "$root/.env.public"
         -f "$root/docker-compose.yml" -f "$root/docker-compose.public.yml")

mkdir -p "$dest"
umask 077

# ── Tiklash sinovi ───────────────────────────────────────────────────
# Hujjat: «Tiklash sinovi o'tkazilmasa, backup YO'Q deb hisoblanadi».
# Eng so'nggi dump alohida bazaga tiklanadi va qator sonlari asl baza
# bilan solishtiriladi.
if [ "${1:-}" = "--restore-test" ]; then
  latest="$(ls -t "$dest"/pg-*.sql.gz 2>/dev/null | head -1)"
  [ -n "$latest" ] || { echo "zaxira topilmadi: $dest" >&2; exit 1; }
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
    exit 1
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
  [ "$fail" -eq 0 ] || { echo "tiklash sinovi YIQILDI" >&2; exit 1; }
  echo "tiklash sinovi o'tdi: $latest"
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
gzip -t "$sql"
if ! zcat "$sql" | tail -c 4096 | grep -q "PostgreSQL database dump complete"; then
  echo "XATO: dump chala — $sql" >&2
  exit 1
fi

# ── MinIO (masala testlari va ko'chirilgan media) ────────────────────
objects="$dest/minio-$stamp.tar.gz"
docker run --rm -v rankwant_miniodata:/data:ro -v "$dest:/out" alpine \
  tar czf "/out/$(basename "$objects").part" -C /data . 
mv "$objects.part" "$objects"
tar tzf "$objects" >/dev/null

# ── Eskilarini tozalash ──────────────────────────────────────────────
find "$dest" -name 'pg-*.sql.gz' -mtime "+$keep_days" -delete
find "$dest" -name 'minio-*.tar.gz' -mtime "+$keep_days" -delete

printf '%s  pg=%s  minio=%s\n' "$stamp" \
  "$(du -h "$sql" | cut -f1)" "$(du -h "$objects" | cut -f1)"
