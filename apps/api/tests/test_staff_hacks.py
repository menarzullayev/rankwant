"""Validator va etalon yechim uchun staff yuzasi — ADR-0020, ADR-0021.

Bu endpointlarsiz hacking hech bir masalada yoqilmaydi: dvigatel
ikkalasini ham majburiy darvoza deb biladi va ularni yuklashning boshqa
yo'li yo'q.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from hacks.models import Hack
from hacks.services import HackError, submit
from problems.models import ReferenceSolution, Validator

SOURCE = 'int main(){int n;scanf("%d",&n);return 0;}\n'


@pytest.fixture(autouse=True)
def fake_storage(fake_hack_storage: dict[str, str]) -> dict[str, str]:
    return fake_hack_storage


@pytest.fixture
def staff_client(db) -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff1", password="x", is_staff=True))
    return client


def _url(problem_slug: str, what: str) -> str:
    return reverse(f"staff-problem-{what}", args=[problem_slug])


@pytest.mark.django_db
class TestValidatorEndpoint:
    def test_yuklanadi(self, staff_client, problem, language) -> None:
        r = staff_client.put(
            _url(problem.slug, "validator"),
            {"language": language.code, "source": SOURCE},
            format="json",
        )

        assert r.status_code == 201, r.content
        assert Validator.objects.get(problem=problem).source == SOURCE

    def test_ikkinchi_yuklash_almashtiradi(self, staff_client, problem, language) -> None:
        """Bitta-bitta bog'lanish: ikkinchi validator EMAS, yangilanish."""
        url = _url(problem.slug, "validator")
        staff_client.put(url, {"language": language.code, "source": SOURCE}, format="json")
        r = staff_client.put(url, {"language": language.code, "source": "yangi\n"}, format="json")

        assert r.status_code == 200
        assert Validator.objects.filter(problem=problem).count() == 1
        assert Validator.objects.get(problem=problem).source == "yangi\n"

    def test_bosh_manba_rad_etiladi(self, staff_client, problem, language) -> None:
        r = staff_client.put(
            _url(problem.slug, "validator"),
            {"language": language.code, "source": "   \n"},
            format="json",
        )

        assert r.status_code == 400
        assert not Validator.objects.exists()

    def test_yoq_bolsa_404(self, staff_client, problem) -> None:
        assert staff_client.get(_url(problem.slug, "validator")).status_code == 404

    def test_ochiriladi(self, staff_client, problem, language) -> None:
        Validator.objects.create(problem=problem, language=language, source=SOURCE)

        assert staff_client.delete(_url(problem.slug, "validator")).status_code == 204
        assert not Validator.objects.exists()

    def test_oddiy_foydalanuvchi_kira_olmaydi(self, problem, user, language) -> None:
        """Etalon yechim — masalaning TO'G'RI javobi.

        Sizib chiqsa, uni ko'chirgan har kim `AC` olardi.
        """
        client = APIClient()
        client.force_authenticate(user)

        assert client.get(_url(problem.slug, "validator")).status_code == 403
        assert client.get(_url(problem.slug, "reference-solution")).status_code == 403


@pytest.mark.django_db
class TestReferenceSolutionEndpoint:
    def test_yuklanadi(self, staff_client, problem, language) -> None:
        r = staff_client.put(
            _url(problem.slug, "reference-solution"),
            {"language": language.code, "source": SOURCE},
            format="json",
        )

        assert r.status_code == 201, r.content
        assert ReferenceSolution.objects.get(problem=problem).language_id == language.pk

    def test_notanish_til_rad_etiladi(self, staff_client, problem) -> None:
        r = staff_client.put(
            _url(problem.slug, "reference-solution"),
            {"language": "brainfuck", "source": SOURCE},
            format="json",
        )

        assert r.status_code == 400
        assert not ReferenceSolution.objects.exists()


@pytest.mark.django_db
class TestGatesOpenHacking:
    def test_ikkalasi_yuklangach_hack_ochiladi(
        self, staff_client, defender_attempt, problem, language, user
    ) -> None:
        """Yuzaning butun ma'nosi shu: hackni ochadigan yagona yo'l."""
        Validator.objects.all().delete()
        ReferenceSolution.objects.all().delete()
        with pytest.raises(HackError, match="validator"):
            submit(user, defender_attempt, raw_input="1 2\n")

        for what in ("validator", "reference-solution"):
            r = staff_client.put(
                _url(problem.slug, what),
                {"language": language.code, "source": SOURCE},
                format="json",
            )
            assert r.status_code == 201, r.content

        hack = submit(user, defender_attempt, raw_input="1 2\n")
        assert hack.status == Hack.Status.TESTING

    def test_darvoza_olib_tashlansa_hack_yopiladi(
        self, defender_attempt, problem, user, memory_judge
    ) -> None:
        """Bosqichlar orasida o'chirilsa hack `TESTING` da qolib ketmasin.

        Generator bosqichidan keyin etalon yechim izlanadi; o'sha
        oraliqda xodim uni olib tashlashi mumkin.
        """
        from hacks.services import _enqueue_reference

        hack = submit(user, defender_attempt, raw_input="1 2\n")
        ReferenceSolution.objects.all().delete()

        _enqueue_reference(hack, "1 2\n")

        hack.refresh_from_db()
        assert hack.status == Hack.Status.IGNORED
        assert "olib tashlandi" in hack.detail
