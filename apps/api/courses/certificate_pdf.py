"""Course certificate PDF — the contest certificate's look (ADR-0019).

The fonts live with the contest renderer; their folder is found through the
app registry, not an import, so `courses` does not load contest models.
"""

from __future__ import annotations

import logging
from pathlib import Path

import segno
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from fpdf import FPDF

from core.alphabet import for_user
from courses.models import CourseCertificate

logging.getLogger("fontTools").setLevel(logging.WARNING)
INK = (29, 41, 57)
MUTED = (91, 99, 118)
ACCENT = (68, 112, 230)
CJK_FROM = 0x2E80
QR_MM = 34.0


def _fonts() -> Path:
    return Path(apps.get_app_config("contests").path) / "fonts"


def verify_url(cert: CourseCertificate) -> str:
    return f"{settings.SITE_URL}/certificates/{cert.pk}"


def render(cert: CourseCertificate) -> bytes:
    fonts = _fonts()
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_title(f"RankWant — {cert.course_title}")
    pdf.set_author("RankWant")
    pdf.add_font("DejaVu", "", str(fonts / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(fonts / "DejaVuSans-Bold.ttf"))
    if any(ord(ch) >= CJK_FROM for ch in cert.name + cert.course_title):
        pdf.add_font("Fallback", "", str(fonts / "DroidSansFallbackFull.ttf"))
        pdf.set_fallback_fonts(["Fallback"], exact_match=False)
    pdf.add_page()
    width, height = pdf.w, pdf.h

    pdf.set_draw_color(*ACCENT)
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

    # Uzbek words in the owner's alphabet (ADR-0059); the name as typed.
    def uz(text: str) -> str:
        return for_user(text, cert.user)

    line(uz("KURS TUGATILDI  ·  COURSE COMPLETED"), 70, 15, "B", ACCENT)

    size = 30.0
    pdf.set_font("DejaVu", "B", size)
    while size > 14 and pdf.get_string_width(cert.name) > width - 70:
        size -= 2
        pdf.set_font("DejaVu", "B", size)
    line(cert.name, 88, size, "B", INK)

    title = for_user(cert.course_title, cert.user, cert.course.base_locale)
    line(f"«{title}» {uz('kursi')}", 108, 15, "", INK)
    if cert.final_score is not None:
        line(f"{uz('Yakuniy test')} / Final quiz: {cert.final_score}%", 118, 12, "", MUTED)

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
        f"ID: {cert.pk}\n{uz('Tekshirish')} / Verify: {verify_url(cert)}\n"
        f"{uz('Berilgan')} / Issued: {issued:%d.%m.%Y}",
        align="L",
    )
    return bytes(pdf.output())
