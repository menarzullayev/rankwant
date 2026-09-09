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

  counts="SELECT (SELECT count(*) FROM problems_problem), (SELECT count(*) FROM core_user),
                 (SELECT count(*) FROM judging_attempt), (SELECT count(*) FROM qvant_qvanttransaction),
                 (SELECT count(*) FROM problems_testcase);"
  "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q \
    -c "DROP DATABASE IF EXISTS restore_test;" -c "CREATE DATABASE restore_test;"
  zcat "$latest" | "${compose[@]}" exec -T postgres psql -U rankwant -d restore_test -q \
    -v ON_ERROR_STOP=1 >/dev/null
  tiklangan="$("${compose[@]}" exec -T postgres psql -U rankwant -d restore_test -t -A -F, -c "$counts")"
  asl="$("${compose[@]}" exec -T postgres psql -U rankwant -d rankwant -t -A -F, -c "$counts")"
  "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q -c "DROP DATABASE restore_test;"

  echo "  asl:       $asl"
  echo "  tiklangan: $tiklangan"
  [ "$asl" = "$tiklangan" ] || { echo "XATO: qator sonlari mos emas" >&2; exit 1; }
  echo "tiklash sinovi o'tdi"
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
