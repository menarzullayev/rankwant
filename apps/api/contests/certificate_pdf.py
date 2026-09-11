"""Sertifikat PDF — fpdf2 va segno (ADR-0019).

Shrift repoda (DejaVu Sans, `fonts/LICENSE`): production image'da tizim
shriftlari yo'q, ism esa lotin yoki kirill yozuvida bo'lishi mumkin. QR
rasm sifatida emas, modul-modul chiziladi — rasm kutubxonasiga ehtiyoj yo'q.
"""

from __future__ import annotations

import logging
from pathlib import Path

import segno
from django.conf import settings
from django.utils import timezone
from fpdf import FPDF

from contests.models import Certificate

FONTS = Path(__file__).resolve().parent / "fonts"
# fpdf2 shriftni fontTools bilan qisqartiradi, u esa har glif ro'yxatini INFO
# darajasida yozadi — har PDF api logiga yuzlab qator tushardi (o'lchandi).
logging.getLogger("fontTools").setLevel(logging.WARNING)
INK = (29, 41, 57)
MUTED = (91, 99, 118)
ACCENT = {
    Certificate.Tier.GOLD: (184, 134, 11),
    Certificate.Tier.SILVER: (112, 122, 138),
    Certificate.Tier.BRONZE: (160, 98, 42),
    Certificate.Tier.TOP10: (68, 112, 230),
    Certificate.Tier.PARTICIPANT: (91, 99, 118),
}
RIBBON = {
    Certificate.Tier.GOLD: "1-O'RIN  ·  FIRST PLACE",
    Certificate.Tier.SILVER: "2-O'RIN  ·  SECOND PLACE",
    Certificate.Tier.BRONZE: "3-O'RIN  ·  THIRD PLACE",
    Certificate.Tier.TOP10: "ENG YAXSHI 10%  ·  TOP 10%",
    Certificate.Tier.PARTICIPANT: "ISHTIROKCHI  ·  PARTICIPANT",
}
QR_MM = 34.0


def verify_url(cert: Certificate) -> str:
    return f"{settings.SITE_URL}/sertifikat/{cert.pk}"


def render(cert: Certificate) -> bytes:
    contest = cert.contest
    accent = ACCENT[Certificate.Tier(cert.tier)]
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_title(f"RankWant — {contest.title}")
    pdf.set_author("RankWant")
    pdf.add_font("DejaVu", "", str(FONTS / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONTS / "DejaVuSans-Bold.ttf"))
    pdf.add_page()
    width, height = pdf.w, pdf.h

    # Ramka: tashqi qalin chiziq daraja rangida, ichki ingichka.
    pdf.set_draw_color(*accent)
    pdf.set_line_width(2.2)
    pdf.rect(10, 10, width - 20, height - 20)
    pdf.set_line_width(0.4)
    pdf.rect(14, 14, width - 28, height - 28)

    def line(text: str, y: float, size: float, style: str, color: tuple[int, int, int]) -> None:
        pdf.set_font("DejaVu", style, size)
        pdf.set_text_color(*color)
        pdf.set_xy(20, y)
        pdf.cell(width - 40, size * 0.5, text, align="C")

    line("RANKWANT", 26, 11, "B", MUTED)
    line("SERTIFIKAT", 38, 34, "B", INK)
    line("CERTIFICATE", 56, 12, "", MUTED)
    line(RIBBON[Certificate.Tier(cert.tier)], 70, 15, "B", accent)

    # Uzun ism kichraytiriladi — varaqdan chiqmasin.
    size = 30.0
    pdf.set_font("DejaVu", "B", size)
    while size > 14 and pdf.get_string_width(cert.name) > width - 70:
        size -= 2
        pdf.set_font("DejaVu", "B", size)
    line(cert.name, 88, size, "B", INK)

    ended = timezone.localtime(contest.end_at)
    line(f"«{contest.title}» musobaqasi", 108, 15, "", INK)
    line(
        f"{cert.place}-o'rin  ·  {cert.participants} ishtirokchi  ·  {ended:%d.%m.%Y}",
        118,
        12,
        "",
        MUTED,
    )
    line(f"Place {cert.place} of {cert.participants}", 126, 10, "", MUTED)

    qr = segno.make(verify_url(cert), error="m")
    rows = [list(row) for row in qr.matrix_iter(border=0)]
    module = QR_MM / len(rows)
    x0, y0 = width - 26 - QR_MM, height - 26 - QR_MM
    pdf.set_fill_color(*INK)
    for y, row in enumerate(rows):
        for x, dark in enumerate(row):
            if dark:
                pdf.rect(x0 + x * module, y0 + y * module, module, module, style="F")

    issued = timezone.localtime(cert.issued_at)
    pdf.set_font("DejaVu", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(26, height - 44)
    pdf.multi_cell(
        160,
        5,
        f"ID: {cert.pk}\nTekshirish / Verify: {verify_url(cert)}\n"
        f"Berilgan / Issued: {issued:%d.%m.%Y}",
        align="L",
    )
    return bytes(pdf.output())
