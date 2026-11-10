"""What the server writes to a person follows their alphabet (ADR-0059).

Mail, Telegram and certificates are made without a browser, so the
choice lives on the account (`User.alphabet`); the switcher keeps it in
step with the device cookie.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from core import emails
from core.models import User
from notifications import messages
from notifications.services import compose

pytestmark = pytest.mark.django_db


def _user(name: str, alphabet: str = "new", locale: str = "uz") -> User:
    return User.objects.create_user(name, password="x", locale=locale, alphabet=alphabet)


def test_the_account_keeps_the_choice() -> None:
    user = _user("alifbo-hisob")
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.get("/api/v1/me/").json()["alphabet"] == "new"
    assert client.patch("/api/v1/me/", {"alphabet": "old"}, format="json").status_code == 200
    user.refresh_from_db()
    assert user.alphabet == "old"
    assert client.patch("/api/v1/me/", {"alphabet": "latin"}, format="json").status_code == 400


def test_catalogue_text_follows_the_alphabet_but_names_do_not() -> None:
    params = {"contest": "Chess Shootout", "reason": "x"}
    new_title, _ = messages.render("contest_disqualified", params, "uz", "new")
    old_title, _ = messages.render("contest_disqualified", params, "uz", "old")
    # The template is converted, the contest's name is shown as typed.
    assert "chetlatildingiz" in old_title and "çetlatildingiz" in new_title
    assert "Chess Shootout" in new_title and "Chess Shootout" in old_title


def test_other_languages_are_left_alone() -> None:
    title, _ = messages.render("contest_disqualified", {"contest": "A", "reason": "b"}, "ru", "new")
    assert "ç" not in title and "ş" not in title


def test_a_notification_is_composed_in_the_users_alphabet() -> None:
    old = _user("alifbo-old", "old")
    new = _user("alifbo-new")
    params = {"contest": "Bahor", "reason": "x"}
    assert (
        "chetlatildingiz"
        in compose(old, "contest", code="contest_disqualified", params=params).title
    )
    assert (
        "çetlatildingiz"
        in compose(new, "contest", code="contest_disqualified", params=params).title
    )


def test_mail_strings_follow_the_alphabet(monkeypatch) -> None:
    sent: list[dict] = []
    monkeypatch.setattr(emails, "_send", lambda context, purpose, to: sent.append(context))
    emails.send_email_verify(_user("pochta-old", "old"), token="t", code="123456", to="a@b.uz")
    emails.send_email_verify(_user("pochta-new"), token="t", code="123456", to="a@b.uz")
    old_text = " ".join(sent[0]["t"].values())
    new_text = " ".join(sent[1]["t"].values())
    assert any(ch in new_text for ch in "şçöğ")
    assert not any(ch in old_text for ch in "şçöğ")


def _certificate_text(cert, render) -> str:  # type: ignore[no-untyped-def]
    """Everything the certificate writes, read off the PDF calls."""
    import fpdf

    seen: list[str] = []
    patch = pytest.MonkeyPatch()
    cell, multi = fpdf.FPDF.cell, fpdf.FPDF.multi_cell

    def spy_cell(self, w=None, h=None, text="", *args, **kwargs):  # type: ignore[no-untyped-def]
        seen.append(text)
        return cell(self, w, h, text, *args, **kwargs)

    def spy_multi(self, w, h=None, text="", *args, **kwargs):  # type: ignore[no-untyped-def]
        seen.append(text)
        return multi(self, w, h, text, *args, **kwargs)

    patch.setattr(fpdf.FPDF, "cell", spy_cell)
    patch.setattr(fpdf.FPDF, "multi_cell", spy_multi)
    try:
        assert render(cert).startswith(b"%PDF")
    finally:
        patch.undo()
    return "\n".join(seen)


def test_course_certificate_follows_the_owners_alphabet() -> None:
    from courses import certificate_pdf
    from courses.models import Course, CourseCertificate

    owner = _user("sertifikat-kurs", "old")
    course = Course.objects.create(slug="alifbo-kurs", base_locale="uz")
    cert = CourseCertificate.objects.create(
        user=owner, course=course, name="Shahzod Cho'liyev", course_title="Saralash usullari"
    )
    old = _certificate_text(cert, certificate_pdf.render)
    assert "Tekshirish / Verify" in old and "Tekşiriş" not in old
    owner.alphabet = "new"
    owner.save(update_fields=["alphabet"])
    new = _certificate_text(cert, certificate_pdf.render)
    assert "Tekşiriş / Verify" in new
    # The person's name is never converted.
    assert "Shahzod Cho'liyev" in new and "Shahzod Cho'liyev" in old


def test_contest_certificate_follows_the_owners_alphabet() -> None:
    from django.utils import timezone

    from contests import certificate_pdf
    from contests.models import Certificate, Contest

    owner = _user("sertifikat-musobaqa")
    now = timezone.now()
    contest = Contest.objects.create(
        slug="alifbo-raund", title="Chess Round", start_at=now, end_at=now
    )
    cert = Certificate.objects.create(
        user=owner,
        contest=contest,
        name="Shahzod",
        place=1,
        participants=10,
        tier=Certificate.Tier.PARTICIPANT,
    )
    text = _certificate_text(cert, certificate_pdf.render)
    assert "IŞTIROKÇI  ·  PARTICIPANT" in text
    assert "«Chess Round»" in text  # the contest's own title, as typed
