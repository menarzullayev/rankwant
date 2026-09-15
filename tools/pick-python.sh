#!/usr/bin/env bash
# ISHLAYDIGAN Python interpretatorining yo'lini chiqaradi.
#
# Nega `command -v python3` YETARLI EMAS: Windows'da Git Bash `python3` ni
# %LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe ga hal qiladi — bu
# Microsoft Store'ning "App Execution Alias" stub'i. U PATH'da turadi va
# bajariladigan fayl, ya'ni `command -v python3` MUVAFFAQIYAT qaytaradi.
# Lekin ishga tushirilganda faqat shuni yozadi:
#
#   Python was not found; run without arguments to install from the
#   Microsoft Store...
#
# va nolga teng bo'lmagan kod bilan chiqadi.
#
# ⚠️ 2026-09-15 da o'lchandi: `.githooks/pre-push` aynan shu stub'ni
# tanladi va `check_i18n`, `check_negative`, `check_contrast`,
# `check_docs` ni «yiqildi» deb ko'rsatdi — holbuki kod soz edi va
# `C:\Python314\python.exe` o'sha mashinada ishlab turardi. Ya'ni darvoza
# haqiqiy nuqsonni emas, o'z muhitini xato o'qidi.
#
# Shuning uchun savol «nom PATH'dami?» EMAS, «ishga tushadimi?».
#
# Ishlatish:
#   PY="$(bash tools/pick-python.sh)" || exit 1
#
# Chiqish kodi:
#   0 — ishlaydigan interpretator stdout'ga yozildi
#   1 — hech biri ishga tushmadi. Chaqiruvchi TO'XTASHI kerak; bu holatni
#       «o'tkazib yuborish» jim, jonsiz darvoza yasaydi.
set -u

# `PYTHON` birinchi: CI yoki konteyner interpretatorni qotirib qo'ya oladi.
for candidate in "${PYTHON:-}" python3 python py; do
  [ -n "$candidate" ] || continue
  command -v "$candidate" >/dev/null 2>&1 || continue

  # Sinov interpretatorni HAQIQATAN ishga tushiradi. Faqat PATH'ga
  # qaraydigan har qanday tekshiruv Store stub'ini yana qabul qilardi.
  # Versiya sharti ham shu yerda: kod `list[str]` va `X | None`
  # sintaksisini ishlatadi.
  "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' \
    >/dev/null 2>&1 || continue

  # ⚠️ `command -v` Git Bash'da MSYS yo'lini beradi (`/c/Python314/python`).
  # Uni bash ishga tushira oladi, lekin WINDOWS dasturi topa olmaydi —
  # `subprocess.run(["/c/Python314/python", …])` `FileNotFoundError` beradi
  # (2026-09-15 da o'lchandi). Shuning uchun yo'lni interpretatorning
  # O'ZIDAN so'raymiz va teskari chiziqlarni to'g'rilaymiz: `C:/…/python.exe`
  # ko'rinishini bash ham, Windows ham tushunadi.
  resolved="$("$candidate" -c 'import sys; print(sys.executable)' 2>/dev/null)"
  [ -n "$resolved" ] || resolved="$(command -v "$candidate")"
  printf '%s\n' "$resolved" | tr '\\' '/'
  exit 0
done

exit 1
