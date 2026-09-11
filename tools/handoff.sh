#!/usr/bin/env bash
# Ikki tizimli preview — Linux tomoni (Linux va Windows bitta mashinada, dual-boot).
#
# Har tizimda preview'ning o'z bazasi va MinIO'si bor. Ma'lumot tizimdan
# tizimga Cloudflare R2 dagi eksport orqali ko'chadi, R2 dagi `state.json`
# esa qaysi tizim hozir live ekanini saqlaydi. To'liq protokol:
# docs/10-operations/README.md § «Ikki tizimli preview».
#
#   tools/handoff.sh status
#   tools/handoff.sh init            # bir marta, hozir live bo'lgan tizimda
#   tools/handoff.sh out             # boshqa tizimga o'tishdan OLDIN
#   tools/handoff.sh in [--force]    # tizim yuklangandan keyin
#
# Asosiy qoida: toza topshirilmagan tizim live bo'lmaydi. Aks holda ikkala
# tomonda ham yangi hisob va urinishlar paydo bo'ladi va ularni keyin
# birlashtirib bo'lmaydi.
set -euo pipefail

me=linux
other=windows
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$root/.handoff"
local_id_file="$work/local-export-id"
mkdir -p "$work"

if [ ! -f "$root/.env.handoff" ]; then
  echo ".env.handoff yo'q — .env.handoff.example dan nusxa olib to'ldiring" >&2
  exit 1
fi
set -a
# shellcheck disable=SC1091
. "$root/.env.handoff"
set +a
: "${R2_ACCOUNT_ID:?}" "${R2_ACCESS_KEY_ID:?}" "${R2_SECRET_ACCESS_KEY:?}" "${R2_BUCKET:?}"

# R2 bilan rclone gaplashadi: minio/mc image'i Docker Hub'dan olib tashlangan.
# Sozlama muhit orqali — kalit buyruq qatoriga chiqmaydi, `docker run -e NOM`
# qiymatni shu muhitdan oladi.
export RCLONE_CONFIG_R2_TYPE=s3
export RCLONE_CONFIG_R2_PROVIDER=Cloudflare
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"
export RCLONE_CONFIG_R2_ENDPOINT="https://$R2_ACCOUNT_ID.r2.cloudflarestorage.com"
# Token faqat obyektlarga ruxsat beradi: bucket'ni tekshirish yoki yaratishga urinmasin.
export RCLONE_CONFIG_R2_NO_CHECK_BUCKET=true
r2="r2:$R2_BUCKET"

# Loyiha nomi qat'iy: katalogdan olinsa, worktree yoki boshqa klon boshqa
# volume'larga tushardi.
project=rankwant
compose=(docker compose -p "$project" --env-file "$root/.env.public"
         -f "$root/docker-compose.yml" -f "$root/docker-compose.public.yml")
# Postgres va MinIO'dan boshqa hammasi bazaga yozadi yoki navbatdan oladi.
writers=(web api worker beat judge)

# Yuklab olingan fayllar root'niki emas, joriy foydalanuvchiniki bo'lsin.
rc() {
  docker run --rm -i --user "$(id -u):$(id -g)" -v "$work:/work" \
    -e RCLONE_CONFIG_R2_TYPE -e RCLONE_CONFIG_R2_PROVIDER \
    -e RCLONE_CONFIG_R2_ACCESS_KEY_ID -e RCLONE_CONFIG_R2_SECRET_ACCESS_KEY \
    -e RCLONE_CONFIG_R2_ENDPOINT -e RCLONE_CONFIG_R2_NO_CHECK_BUCKET \
    rclone/rclone:1.75 -q "$@"
}
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
local_export() { cat "$local_id_file" 2>/dev/null || true; }

state=""
# R2 ga ulanib bo'lmasa to'xtaydi: «state.json yo'q» deb qabul qilinsa,
# `init` mavjud holat ustiga yozib yuborardi.
load_state() {
  local found
  if ! found="$(rc lsf --files-only --max-depth 1 --include state.json "$r2")"; then
    echo "R2 ga ulanib bo'lmadi — holat o'qilmadi, hech narsa o'zgartirilmadi" >&2
    exit 1
  fi
  state=""
  if [ -n "$found" ]; then state="$(rc cat "$r2/state.json")"; fi
}

# `get owner` — state.json maydoni, yo'q bo'lsa bo'sh satr.
get() {
  python3 - "$1" "$state" <<'PY'
import json, sys
key, raw = sys.argv[1], sys.argv[2]
value = (json.loads(raw) if raw.strip() else {}).get(key)
print("" if value is None else value)
PY
}

# save_state OWNER SINCE EXPORT_ID EXPORT_AT — bo'sh qiymat null bo'ladi.
save_state() {
  python3 - "$@" <<'PY' | rc rcat "$r2/state.json"
import json, sys
keys = ("owner", "since", "export_id", "export_at")
print(json.dumps({k: (v or None) for k, v in zip(keys, sys.argv[1:5])}))
PY
}

remote_size() {
  rc size --json "$r2/$1" | python3 -c 'import json, sys; print(json.load(sys.stdin)["bytes"])'
}

# Dump oxirigacha yozilganini va arxiv o'qilishini tekshiradi.
check_archives() {
  docker run --rm -v "$1:/in:ro" alpine sh -ec 'gzip -t /in/pg.sql.gz; tar tzf /in/minio.tar.gz >/dev/null'
}

tunnel_stop()  { sudo systemctl stop cloudflared; }
tunnel_start() { sudo systemctl start cloudflared; }
tunnel_state() { systemctl is-active cloudflared 2>/dev/null || true; }

wait_healthy() {
  for _ in $(seq 1 60); do
    curl -fsS -o /dev/null -H 'Host: rankwant.uz' http://127.0.0.1:8301/api/v1/health/ && return 0
    sleep 2
  done
  echo "API sog'lom emas: http://127.0.0.1:8301/api/v1/health/" >&2
  return 1
}

# R2 da oxirgi ikkita eksport qoladi (bepul 10 GB), lokal nusxadan faqat joriysi.
# `purge` bucket versiyasini o'qiy olmay 403 haqida yozadi — token bucket
# sozlamalariga kirmaydi, bu kutilgan va o'chirishga ta'sir qilmaydi.
prune() {
  local keep="$1" old
  old="$(rc lsf --dirs-only --max-depth 1 "$r2/exports" | tr -d '/' | sort | head -n -2)"
  for name in $old; do rc purge "$r2/exports/$name" 2>/dev/null; done
  find "$work/out" "$work/in" -mindepth 1 -maxdepth 1 ! -name "$keep" -exec rm -rf {} + 2>/dev/null || true
}

import_export() {
  local id="$1" dir="$work/in/$1"
  mkdir -p "$dir"
  echo "Eksport yuklab olinmoqda: $id"
  for f in pg.sql.gz minio.tar.gz; do
    rc copyto "$r2/exports/$id/$f" "/work/in/$id/$f"
  done
  check_archives "$dir"

  echo "Baza tiklanmoqda"
  "${compose[@]}" stop "${writers[@]}" 2>/dev/null || true
  "${compose[@]}" up -d --wait postgres minio
  # Bo'sh bazaga tiklanadi: `--clean` faqat dumpdagi obyektlarni tashlaydi,
  # bu tomonda qo'shimcha migratsiya bo'lsa undan qolgan jadvallar turib qolardi.
  "${compose[@]}" exec -T postgres psql -U rankwant -d postgres -q -v ON_ERROR_STOP=1 \
    -c 'DROP DATABASE IF EXISTS rankwant WITH (FORCE);' -c 'CREATE DATABASE rankwant OWNER rankwant;'
  "${compose[@]}" cp "$dir/pg.sql.gz" postgres:/tmp/handoff-pg.sql.gz
  "${compose[@]}" exec -T postgres sh -ec \
    'gunzip -c /tmp/handoff-pg.sql.gz | psql -U rankwant -d rankwant -q -v ON_ERROR_STOP=1 >/dev/null'

  echo "MinIO tiklanmoqda"
  "${compose[@]}" stop minio
  docker run --rm -v "${project}_miniodata:/data" -v "$dir:/in:ro" alpine \
    sh -ec 'find /data -mindepth 1 -delete; tar xzf /in/minio.tar.gz -C /data'
  echo "$id" > "$local_id_file"
}

cmd_status() {
  load_state
  if [ -z "$state" ]; then
    echo "R2 da state.json yo'q — birinchi marta: tools/handoff.sh init"
    return
  fi
  echo "R2 holati:      owner=$(get owner) since=$(get since)"
  echo "Oxirgi eksport: $(get export_id) ($(get export_at))"
  echo "Bu tizim ($me): lokal eksport=$(local_export) tunnel=$(tunnel_state)"
}

cmd_init() {
  load_state
  if [ -n "$state" ]; then
    echo "state.json allaqachon bor — init kerak emas" >&2
    cmd_status
    exit 1
  fi
  save_state "$me" "$(now)" "" ""
  echo "Boshlandi: $me live."
}

cmd_out() {
  load_state
  local owner id dir
  owner="$(get owner)"
  if [ "$owner" != "$me" ]; then
    echo "Live tizim: '${owner:-hech kim}'. 'out' faqat live tizimda ishlaydi." >&2
    exit 1
  fi
  id="$(date -u +%Y%m%d-%H%M%S)-$me"
  dir="$work/out/$id"
  mkdir -p "$dir"

  echo "1/6 Tunnel to'xtatilmoqda — sayt texnik ishlar sahifasiga o'tadi"
  tunnel_stop
  echo "2/6 Yozuvchi servislar to'xtatilmoqda"
  "${compose[@]}" stop "${writers[@]}"
  echo "3/6 Postgres dump"
  "${compose[@]}" exec -T postgres sh -ec "pg_dump -U rankwant --clean --if-exists rankwant | gzip -9 > /tmp/handoff-pg.sql.gz && gunzip -c /tmp/handoff-pg.sql.gz | tail -c 4096 | grep -q 'PostgreSQL database dump complete'"
  "${compose[@]}" cp postgres:/tmp/handoff-pg.sql.gz "$dir/pg.sql.gz"
  echo "4/6 MinIO arxivi"
  docker run --rm -v "${project}_miniodata:/data:ro" -v "$dir:/out" alpine tar czf /out/minio.tar.gz -C /data .
  check_archives "$dir"
  echo "5/6 R2 ga yuklanmoqda"
  for f in pg.sql.gz minio.tar.gz; do
    rc copyto "/work/out/$id/$f" "$r2/exports/$id/$f"
    if [ "$(remote_size "exports/$id/$f")" != "$(stat -c %s "$dir/$f")" ]; then
      echo "R2 dagi $f hajmi mos emas — holat o'zgartirilmadi" >&2
      exit 1
    fi
  done
  echo "6/6 Holat yozilmoqda"
  save_state "" "" "$id" "$(now)"
  echo "$id" > "$local_id_file"
  prune "$id"
  "${compose[@]}" stop
  echo "Topshirildi: $id. Endi Windows'ga o'tib 'tools\\handoff.ps1 in' qiling."
}

cmd_in() {
  load_state
  local owner export_id
  owner="$(get owner)"
  export_id="$(get export_id)"
  if [ "$owner" = "$other" ] && [ "${1:-}" != "--force" ]; then
    echo "Windows hali live ($(get since) dan beri) va topshirmagan." >&2
    echo "Windows'ga kirib 'tools\\handoff.ps1 out' qiling, keyin qaytib keling." >&2
    echo "Windows'ga kira olmasangiz: tools/handoff.sh in --force" >&2
    echo "  (Windows'da oxirgi eksportdan keyin yozilgan ma'lumot yo'qoladi)." >&2
    exit 1
  fi
  if [ "$owner" != "$me" ] && [ -n "$export_id" ] && [ "$export_id" != "$(local_export)" ]; then
    import_export "$export_id"
    prune "$export_id"
  fi
  echo "Stek ko'tarilmoqda"
  "${compose[@]}" up -d --build --wait
  wait_healthy
  tunnel_start
  save_state "$me" "$(now)" "$export_id" "$(get export_at)"
  echo "Live: $me. Sayt tunnel orqali ochiladi."
}

case "${1:-}" in
  status) cmd_status ;;
  init) cmd_init ;;
  out) cmd_out ;;
  in) shift; cmd_in "$@" ;;
  *) echo "foydalanish: $0 status | init | out | in [--force]" >&2; exit 2 ;;
esac
