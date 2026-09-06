"""Hakaton — loyiha topshirish va hakam bahosi."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from hackathons.models import Hackathon, HackathonSubmission
from hackathons.services import HackathonError, score, submit
from notifications.models import Notification

ENTRY = {"title": "Bot", "description": "Telegram bot", "repo_url": "https://github.com/x/y"}


def _hackathon(deadline_offset_h: int) -> Hackathon:
    now = timezone.now()
    return Hackathon.objects.create(
        slug=f"h{deadline_offset_h}",
        title="Hakaton",
        start_at=now - timedelta(days=1),
        submission_deadline=now + timedelta(hours=deadline_offset_h),
        end_at=now + timedelta(days=3),
    )


@pytest.mark.django_db
class TestHackathon:
    def test_topshirish_va_qayta_topshirish(self, user) -> None:
        h = _hackathon(24)
        submit(user, h, **ENTRY)
        submit(user, h, **{**ENTRY, "title": "Bot v2"})
        assert HackathonSubmission.objects.filter(hackathon=h).count() == 1
        assert HackathonSubmission.objects.get(hackathon=h).title == "Bot v2"

    def test_muddat_otgach_yopiq(self, user) -> None:
        with pytest.raises(HackathonError) as exc:
            submit(user, _hackathon(-1), **ENTRY)
        assert exc.value.code == "closed"

    def test_baholash_faqat_hakam(self, user, other_user) -> None:
        h = _hackathon(24)
        entry = submit(user, h, **ENTRY)
        with pytest.raises(HackathonError):
            score(other_user, entry, 90)
        judge = User.objects.create_user("hakam", password="x", is_staff=True)
        score(judge, entry, 90, "zo'r")
        entry.refresh_from_db()
        assert entry.score == 90 and entry.scored_by == judge
        assert Notification.objects.filter(user=user, ref_type="hackathon").exists()

    def test_muddatgacha_faqat_oziniki_korinadi(self, user, other_user) -> None:
        h = _hackathon(24)
        submit(user, h, **ENTRY)
        submit(other_user, h, **{**ENTRY, "title": "Boshqa"})
        c = APIClient()
        c.force_authenticate(user=user)
        mine = c.get(reverse("hackathon-submissions", args=[h.slug])).json()["results"]
        assert [e["title"] for e in mine] == ["Bot"]
        assert (
            APIClient().get(reverse("hackathon-submissions", args=[h.slug])).json()["results"] == []
        )

        Hackathon.objects.filter(pk=h.pk).update(
            submission_deadline=timezone.now() - timedelta(minutes=1)
        )
        everyone = APIClient().get(reverse("hackathon-submissions", args=[h.slug])).json()
        assert len(everyone["results"]) == 2

    def test_api_score_admin_only(self, user) -> None:
        h = _hackathon(24)
        entry = submit(user, h, **ENTRY)
        c = APIClient()
        c.force_authenticate(user=user)
        url = reverse("hackathon-score-entry", args=[h.slug, entry.pk])
        assert c.post(url, {"score": 50}, format="json").status_code == 403
        judge = User.objects.create_user("hakam2", password="x", is_staff=True)
        c.force_authenticate(user=judge)
        assert c.post(url, {"score": 77}, format="json").json()["score"] == 77
