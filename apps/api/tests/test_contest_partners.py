"""Partner contests, official qualifiers and mirrors (ADR-0063)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, Organization
from core.models import User
from olympiads.models import Event, Season

pytestmark = pytest.mark.django_db


def _contest(slug: str, **fields: object) -> Contest:
    now = timezone.now()
    defaults: dict[str, object] = {
        "title": slug.title(),
        "start_at": now - timedelta(hours=2),
        "end_at": now - timedelta(hours=1),
    }
    defaults.update(fields)
    return Contest.objects.create(slug=slug, **defaults)


@pytest.fixture
def staff() -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff1", password="x", is_staff=True))
    return client


@pytest.fixture
def event() -> Event:
    season = Season.objects.create(slug="2026-27", title="2026–27")
    return Event.objects.create(
        season=season, slug="respublika-2027", title="Respublika olimpiadasi"
    )


def test_contest_page_shows_partner_prizes_and_official_status() -> None:
    partner = Organization.objects.create(
        slug="tatu",
        name="TATU",
        kind=Organization.Kind.UNIVERSITY,
        logo_url="/partners/tatu.png",
        website="https://tuit.uz",
    )
    _contest(
        "tatu-cup",
        partner=partner,
        prizes="1-o'rin: noutbuk",
        official_title="Respublika olimpiadasi, saralash bosqichi",
        official_url="https://example.uz/buyruq",
    )
    body = APIClient().get(reverse("contest-detail", args=["tatu-cup"])).json()
    assert body["partner"]["name"] == "TATU"
    assert body["partner"]["website"] == "https://tuit.uz"
    assert body["prizes"] == "1-o'rin: noutbuk"
    assert body["official_title"].startswith("Respublika")
    assert body["official_url"] == "https://example.uz/buyruq"
    listed = APIClient().get(reverse("contest-list")).json()["results"][0]
    assert listed["partner"] == {
        "slug": "tatu",
        "name": "TATU",
        "kind": "university",
        "logo_url": "/partners/tatu.png",
    }
    assert listed["is_mirror"] is False


def test_a_mirror_names_its_original_and_the_original_lists_it(event: Event) -> None:
    original = _contest("asl")
    _contest("kozgu", mirror_of=original)
    _contest("arxiv-kozgu", mirror_of_event=event)
    _contest("yashirin-kozgu", mirror_of=original, is_public=False)

    mirror = APIClient().get(reverse("contest-detail", args=["kozgu"])).json()
    assert mirror["is_mirror"] is True
    assert mirror["mirror_source"] == {"kind": "contest", "slug": "asl", "title": "Asl"}
    on_event = APIClient().get(reverse("contest-detail", args=["arxiv-kozgu"])).json()
    assert on_event["mirror_source"]["kind"] == "olympiad"
    assert on_event["mirror_source"]["slug"] == "respublika-2027"

    source = APIClient().get(reverse("contest-detail", args=["asl"])).json()
    assert [m["slug"] for m in source["mirrors"]] == ["kozgu"]
    olympiad = APIClient().get(reverse("olympiad-event", args=["respublika-2027"])).json()
    assert [m["slug"] for m in olympiad["mirror_contests"]] == ["arxiv-kozgu"]


def test_a_hidden_original_is_not_named() -> None:
    original = _contest("ichki", is_public=False)
    _contest("ochiq-kozgu", mirror_of=original)
    body = APIClient().get(reverse("contest-detail", args=["ochiq-kozgu"])).json()
    assert body["mirror_source"] is None


def test_the_database_refuses_a_rated_mirror(event: Event) -> None:
    original = _contest("manba")
    for fields in ({"mirror_of": original}, {"mirror_of_event": event}):
        with pytest.raises(IntegrityError), transaction.atomic():
            _contest(f"reytingli-{len(fields)}-{next(iter(fields))}", is_rated=True, **fields)


def test_staff_cannot_rate_a_mirror(staff: APIClient, event: Event) -> None:
    contest = _contest("staff-kozgu", is_rated=True)
    response = staff.patch(
        f"/api/v1/staff/contests/{contest.slug}/",
        {"mirror_of_event": event.slug},
        format="json",
    )
    assert response.status_code == 400
    assert "is_rated" in str(response.content)
    ok = staff.patch(
        f"/api/v1/staff/contests/{contest.slug}/",
        {"mirror_of_event": event.slug, "is_rated": False},
        format="json",
    )
    assert ok.status_code == 200, ok.content
    contest.refresh_from_db()
    assert contest.mirror_of_event_id == event.pk


def test_staff_manage_organizations_and_links_are_safe(staff: APIClient) -> None:
    url = "/api/v1/staff/organizations/"
    for bad in (
        "javascript:alert(1)",
        "http://x.uz/l.png",
        "//x.uz/l.png",
        "data:image/png;base64,AA",
    ):
        r = staff.post(url, {"slug": "bad", "name": "Bad", "logo_url": bad}, format="json")
        assert r.status_code == 400, bad
    r = staff.post(
        url, {"slug": "it-park", "name": "IT Park", "website": "http://itpark.uz"}, format="json"
    )
    assert r.status_code == 400
    r = staff.post(
        url,
        {"slug": "it-park", "name": "IT Park", "kind": "government", "logo_url": "/p/it.png"},
        format="json",
    )
    assert r.status_code == 201, r.content
    contest = _contest("park-cup")
    r = staff.patch(
        f"/api/v1/staff/contests/{contest.slug}/",
        {"partner": "it-park", "official_url": "http://example.uz"},
        format="json",
    )
    assert r.status_code == 400
    r = staff.patch(
        f"/api/v1/staff/contests/{contest.slug}/", {"partner": "it-park"}, format="json"
    )
    assert r.status_code == 200, r.content
    # Deleting a partner keeps its contests.
    assert staff.delete(f"{url}it-park/").status_code == 204
    contest.refresh_from_db()
    assert contest.partner_id is None


def test_an_organizer_writes_prizes_but_not_partner_or_official_status() -> None:
    organizer = User.objects.create_user("org1", password="x")
    partner = Organization.objects.create(slug="markaz", name="Markaz")
    now = timezone.now()
    contest = _contest(
        "org-draft", start_at=now + timedelta(days=1), end_at=now + timedelta(days=1, hours=2)
    )
    contest.organizers.add(organizer)
    client = APIClient()
    client.force_login(organizer)
    r = client.patch(
        f"/api/v1/contests/mine/{contest.slug}/",
        {
            "prizes": "Sovg'alar",
            "partner": partner.slug,
            "official_title": "Rasmiy",
            "mirror_of_event": "x",
        },
        format="json",
    )
    assert r.status_code == 200, r.content
    contest.refresh_from_db()
    assert contest.prizes == "Sovg'alar"
    assert contest.partner_id is None
    assert contest.official_title == ""
    assert contest.mirror_of_event_id is None
