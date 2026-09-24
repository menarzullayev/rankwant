#!/usr/bin/env bash
# ADR-0028 (judge konteyner izolyatsiyasi) — MinIO identitet init'i.
#
# Maqsad: judge navbatdagi ishlarning test ma'lumotini FAQAT o'qiy oladi.
# Root kredensiali (`S3_SECRET: devdevdev`) judge env'idan chiqariladi va
# uning o'rniga `judge-ro` useri beriladi — bucket'ga read-only policy bilan.
# Bu A-2 ning judge tomonidagi yarmini yopadi: sandbox'dan qochish bo'lsa ham
# yashirin testlarni YOZISH mumkin bo'lmaydi (threat model §11).
#
# Ishlash tartibi (idempotent — har `up` da qayta yuradi):
#   1. serverga ulanadi (healthcheck'dan keyin ham tayyorlikni kutadi);
#   2. bucket mavjudligini kafolatlaydi (`mb --ignore-existing`);
#   3. eski `judge-ro` useri/policy'sini o'chiradi (kalit rotatsiyasi);
#   4. read-only policy + user yaratadi — kalit `JUDGE_S3_SECRET` muhitidan
#      keladi, compose uni judge'ga HAM, shu skriptga HAM bir xil beradi
#      (statik kalit — `env_file` yondashuvi ishlamaydi: compose uni parse
#      vaqtida o'qiydi, init esa keyin yuradi; lokal qiymat oshkor — repo'dagi
#      boshqa dev kredensiallar kabi, prod `.env.public` bilan beriladi);
#   5. self-test: root yozgan probe'ni judge-ro O'QIYDI, YOZA OLMA YDI —
#      yozsa skript YIQILADI (judge `completed_successfully` kutadi).
set -uo pipefail

BUCKET="${S3_BUCKET:-rankwant}"
ALIAS="local"
SECRET="${JUDGE_S3_SECRET:-}"
FLAG="/done/flag"

log() { printf '[minio-init] %s\n' "$*"; }
die() { log "XATO: $*"; exit 1; }

[ -n "$SECRET" ] || die "JUDGE_S3_SECRET bo'sh — compose berishi kerak"

# ── 1. Server tayyorligi ─────────────────────────────────────────────
# MinIO healthcheck o'tgach ham bir necha ms kerak bo'lishi mumkin —
# alias'ni 30 marta, 1 s oralig'i bilan urinamiz (umumiy 30 s chegara).
ready=""
for _ in $(seq 1 30); do
  if mc alias set "$ALIAS" http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; then
    ready=1
    break
  fi
  log "serverni kutish..."
  sleep 1
done
[ -n "$ready" ] || die "MinIO 30 s ichida tayyor bo'lmadi"
log "serverga ulandi ($ALIAS)"

# ── 2. Bucket (idempotent) ───────────────────────────────────────────
# Bugunga qadar bucket qo'lda yaratilgan edi — stack endi o'zi kafolatlaydi.
mc mb --ignore-existing "$ALIAS/$BUCKET" >/dev/null || die "bucket yaratilmadi ($BUCKET)"

# ── 3. Eski identitetni tozalash (idempotentlik + kalit rotatsiyasi) ──
mc admin user remove "$ALIAS" judge-ro >/dev/null 2>&1 || true
mc admin policy remove "$ALIAS" judge-ro-policy >/dev/null 2>&1 || true

# ── 4. Policy: bucket ichida faqat o'qish ────────────────────────────
# `s3:GetObject` — test fayllarini o'qish; `s3:ListBucket` — minio-go
# ba'zi yo'llarda obyektni o'qishdan oldin bucket'ni sanaydi. YOZISH
# huquqi ATAYLAB yo'q (PutObject/DeleteObject taqiqlangan).
POLICY_FILE="/tmp/judge-ro-policy.json"
cat > "$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::$BUCKET/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::$BUCKET"]
    }
  ]
}
EOF
mc admin policy create "$ALIAS" judge-ro-policy "$POLICY_FILE" >/dev/null \
  || die "policy yaratilmadi"
mc admin user add "$ALIAS" judge-ro "$SECRET" >/dev/null || die "user yaratilmadi"
mc admin policy attach "$ALIAS" judge-ro-policy --user judge-ro >/dev/null \
  || die "policy bog'lanmadi"

# ── 5. Self-test: o'qish OK, yozish XATO ─────────────────────────────
PROBE=".minio-init-probe.txt"
echo probe > "/tmp/$PROBE"
mc cp "/tmp/$PROBE" "$ALIAS/$BUCKET/$PROBE" >/dev/null || die "root probe yozilmadi"
mc alias set judgero http://minio:9000 judge-ro "$SECRET" >/dev/null \
  || die "judge-ro alias"
mc cat "judgero/$BUCKET/$PROBE" >/dev/null || die "judge-ro o'qiy olmadi (policy xato)"
if mc cp "/tmp/$PROBE" "judgero/$BUCKET/$PROBE" >/dev/null 2>&1; then
  die "judge-ro YOZA oladi — policy read-only emas!"
fi
mc rm "$ALIAS/$BUCKET/$PROBE" >/dev/null 2>&1 || true
log "self-test OK: judge-ro o'qiydi, yoza olmaydi"

# ── 6. Tayyor flagi (healthcheck shu faylni kutadi; konteyner ichida) ─
mkdir -p /done
touch "$FLAG"
log "tugadi — judge-ro tayyor"
