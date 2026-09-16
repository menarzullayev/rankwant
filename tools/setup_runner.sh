#!/usr/bin/env bash
# GitHub Actions self-hosted runner'ni WSL2 Ubuntu ichida o'rnatadi.
#
# Nega skript: runner Linux talab qiladi (`runs-on: [self-hosted, Linux,
# X64, rankwant]`), CI esa Docker, Postgres va `python3` ni ishlatadi —
# Windows'ning o'zida bularning hech biri yo'q (batafsil:
# `docs/research/2026-09-13-rankwant-review/CI-WINDOWS-ANALYSIS.md`).
#
# ISHLATISH (Ubuntu-24.04 distro ichida, root yoki sudo bilan):
#
#   bash tools/setup_runner.sh <REGISTRATION_TOKEN> [RUNNER_NAME] [RUNNER_VERSION]
#
# Registration token bir martalik va ~1 soat yashaydi. Uni shunday olamiz:
#
#   gh api -X POST repos/menarzullayev/rankwant/actions/runners/registration-token \
#     --jq .token
#
# Skript IDEMPOTENT: qayta ishga tushirilsa mavjud runner'ni qayta
# ro'yxatdan o'tkazmaydi (`config.sh` faqat `.runner` fayli yo'q bo'lsa
# chaqiriladi), faqat xizmatni tiklaydi.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/menarzullayev/rankwant}"
TOKEN="${1:-}"
NAME="${2:-$(hostname)-wsl}"
VERSION="${3:-2.329.0}"

RUNNER_HOME="${RUNNER_HOME:-/opt/actions-runner}"
RUNNER_USER="${RUNNER_USER:-runner}"

if [ -z "$TOKEN" ]; then
  printf '\033[31m✗ Registration token berilmadi.\033[0m\n' >&2
  printf '  gh api -X POST repos/menarzullayev/rankwant/actions/runners/registration-token --jq .token\n' >&2
  printf '  keyin: bash tools/setup_runner.sh <token>\n' >&2
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  printf '\033[31m✗ root kerak (yoki sudo).\033[0m\n' >&2
  exit 1
fi

step() {
  printf '\n\033[1m→ %s\033[0m\n' "$1"
}

# ── 1. Paketlar ─────────────────────────────────────────────────────────
# Runner `./config.sh` uchun: curl, tar. CI ishi uchun: docker.io,
# python3, jq (workflow'lar `jq` bilan JSON o'qiydi).
step "Paketlar o'rnatilmoqda"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  curl ca-certificates tar jq git \
  docker.io docker-compose-v2 \
  python3 python3-venv python3-pip

# ── 2. Xizmat foydalanuvchisi ───────────────────────────────────────────
# Runner root sifatida ISHLAMASLIGI kerak: `docker` guruhi allaqachon
# root ekvivalenti, ya'ni CI job root huquqini ochiq olardi.
step "Xizmat foydalanuvchisi: $RUNNER_USER"
if ! id "$RUNNER_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$RUNNER_USER"
  printf '  yaratildi: %s\n' "$RUNNER_USER"
else
  printf '  allaqachon bor: %s\n' "$RUNNER_USER"
fi
# `docker` guruhi paketdan keyin paydo bo'ladi — a'zolikni shundan keyin
# yozamiz, aks holda `groupadd` xato berardi.
usermod -aG docker "$RUNNER_USER"

# Sudo'siz docker uchun guruh a'zoligi YANGI sessiyada kuchga kiradi.
# Runner xizmati yangi sessiya ochadi, ya'ni bu yetarli.

# ── 3. Runner arxivi ────────────────────────────────────────────────────
step "Runner $VERSION yuklab olinmoqda"
mkdir -p "$RUNNER_HOME"
cd "$RUNNER_HOME"
if [ ! -f ./config.sh ]; then
  tarball="actions-runner-linux-x64-${VERSION}.tar.gz"
  curl -fsSL -o "$tarball" \
    "https://github.com/actions/runner/releases/download/v${VERSION}/${tarball}"
  tar xzf "$tarball"
  rm -f "$tarball"
  printf '  ochildi: %s\n' "$RUNNER_HOME"
else
  printf '  allaqachon bor, yuklab olinmadi\n'
fi

# ── 4. Ro'yxatdan o'tkazish ─────────────────────────────────────────────
# `.runner` fayli — "ro'yxatdan o'tgan" belgisi. U bor bo'lsa `config.sh`
# yana chaqirilsa GitHub'da IKINCHI runner paydo bo'ladi va eskisi
# "offline" bo'lib qoladi. Shu sababli tekshiriladi.
step "Ro'yxatdan o'tkazish"
chown -R "$RUNNER_USER":"$RUNNER_USER" "$RUNNER_HOME"
if [ -f "$RUNNER_HOME/.runner" ]; then
  printf '  allaqachon ro'\''yxatdan o'\''tgan — config.sh chaqirilmadi\n'
else
  # `--unattended` — interaktiv savol yo'q.
  #
  # ⚠️ `--replace` ATAYLAB YO'Q. U bo'lsa GitHub'da bir xil nomli ESKI
  # runner o'chib ketardi. O'lchandi: ro'yxatda `nsn-pc-rankwant` va
  # `nsn-pc-rankwant-2` qoldiq sifatida turgan edi va `--replace` bilan
  # ikkalasi ham jimgina yo'qolar, tarixi ham ketardi. Buning o'rniga
  # nom bo'sh bo'lishi TALAB qilinadi — qoldiqni odam ongli o'chiradi.
  out="$(sudo -u "$RUNNER_USER" ./config.sh \
    --url "$REPO_URL" \
    --token "$TOKEN" \
    --name "$NAME" \
    --labels "rankwant" \
    --work "_work" \
    --unattended 2>&1)" || {
      printf '%s\n' "$out"
      case "$out" in
        *"runner exists with the same name"*)
          printf '\n\033[31m✗ "%s" nomli runner GitHub'"'"'da allaqachon bor.\033[0m\n' "$NAME" >&2
          printf '  Qoldiqni o'"'"'chiring yoki boshqa nom bering:\n' >&2
          printf '    gh api -X DELETE repos/menarzullayev/rankwant/actions/runners/<ID>\n' >&2
          printf '    yoki: bash tools/setup_runner.sh <token> boshqa-nom\n\n' >&2
          ;;
      esac
      exit 1
    }
  printf '%s\n' "$out" | tail -3
fi

# ── 5. Xizmat ───────────────────────────────────────────────────────────
# `svc.sh install` runner'ni systemd xizmati qiladi — WSL qayta
# ishga tushganda o'zi ko'tariladi. Usiz runner faqat qo'lda
# (`./run.sh`) ishlaydi va `wsl --shutdown` dan keyin o'ladi.
step "Xizmat o'rnatilmoqda"
./svc.sh install "$RUNNER_USER" >/dev/null 2>&1 || true
./svc.sh start || true

# ── 6. Tekshiruv ────────────────────────────────────────────────────────
step "Holat"
printf '  runner nomi : %s\n' "$NAME"
printf '  labels      : self-hosted, Linux, X64, rankwant\n'
printf '  katalog     : %s\n' "$RUNNER_HOME"
./svc.sh status 2>&1 | head -5 || true

printf '\n\033[32m✓ Tayyor.\033[0m GitHub tomonda tekshirish:\n'
printf '  gh api repos/menarzullayev/rankwant/actions/runners \\\n'
printf '    --jq '"'"'.runners[] | "\\(.name) \\(.status)"'"'"'\n\n'
