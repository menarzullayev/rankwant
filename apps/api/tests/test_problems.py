"""Masala arxivi va masala sahifasi.

Qamrov: namuna testlar (S3 dan o'qish, keshlash, S3 yiqilgandagi
xatti-harakat), sevimlilar, jamoa bahosi, ommaviy raqam va ro'yxatning
so'rov soni — qator ortganda u o'zgarmasligi kerak.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from problems import storage
from problems.models import TestCase as ProblemTestCase


@pytest.fixture
def staff_client(db) -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff-samples", is_staff=True))
    return client


@pytest.fixture
def samples(problem, monkeypatch) -> None:
    contents = {
        "s3://rankwant/tests/a-plus-b/1.in": "2 3\n",
        "s3://rankwant/tests/a-plus-b/1.out": "5\n",
        "s3://rankwant/tests/a-plus-b/2.in": "10 20\n",
        "s3://rankwant/tests/a-plus-b/2.out": "30\n",
    }
    for order in (1, 2):
        ProblemTestCase.objects.create(
            problem=problem,
            order=order,
            input_ref=f"s3://rankwant/tests/a-plus-b/{order}.in",
            output_ref=f"s3://rankwant/tests/a-plus-b/{order}.out",
            is_sample=order == 1,
        )
    monkeypatch.setattr(storage, "get_test_data", lambda ref: contents[ref])
    cache.delete(storage.samples_cache_key(problem.slug))


def test_faqat_namuna_testlar_qaytadi(samples, problem) -> None:
    response = APIClient().get(reverse("problem-detail", args=[problem.slug]))

    assert response.status_code == 200
    # 2-test namuna emas — javob ochiq sahifada ko'rinmasligi kerak.
    assert response.data["samples"] == [{"order": 1, "input": "2 3\n", "expected": "5\n"}]


def test_s3_yiqilsa_sahifa_baribir_ochiladi(samples, problem, monkeypatch) -> None:
    def boom(ref: str) -> str:
        raise OSError("S3 javob bermadi")

    monkeypatch.setattr(storage, "get_test_data", boom)

    response = APIClient().get(reverse("problem-detail", args=[problem.slug]))

    assert response.status_code == 200
    assert response.data["samples"] == []
    assert response.data["statement"]


def test_kesh_takroriy_s3_o_qishini_yo_qotadi(samples, problem) -> None:
    calls: list[str] = []
    original = storage.get_test_data

    def counted(ref: str) -> str:
        calls.append(ref)
        return original(ref)

    storage.get_test_data = counted  # type: ignore[assignment]
    try:
        url = reverse("problem-detail", args=[problem.slug])
        APIClient().get(url)
        first = len(calls)
        APIClient().get(url)
        assert len(calls) == first, "ikkinchi so'rov keshdan olinishi kerak"
    finally:
        storage.get_test_data = original  # type: ignore[assignment]


def test_test_yuklanganda_kesh_tozalanadi(samples, problem, staff_client, monkeypatch) -> None:
    url = reverse("problem-detail", args=[problem.slug])
    APIClient().get(url)  # keshni to'ldiradi

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "put_test_data", lambda key, content: f"s3://rankwant/{key}")
    monkeypatch.setattr(
        storage, "get_test_data", lambda ref: "7 8\n" if ref.endswith(".in") else "15\n"
    )

    staff_client.post(
        reverse("staff-problem-tests", args=[problem.slug]),
        {"order": 1, "input": "7 8\n", "expected": "15\n", "is_sample": True, "points": 0},
        format="json",
    )

    assert APIClient().get(url).data["samples"] == [
        {"order": 1, "input": "7 8\n", "expected": "15\n"}
    ]


def test_yechilgan_masala_royxatda_belgilanadi(problem, user) -> None:
    from ratings.models import UserSolvedProblem

    url = reverse("problem-list")
    client = APIClient()

    assert client.get(url).data["results"][0]["is_solved"] is False, "mehmonga false"

    client.force_authenticate(user)
    assert client.get(url).data["results"][0]["is_solved"] is False

    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    assert client.get(url).data["results"][0]["is_solved"] is True


def test_sevimlilar_qo_shiladi_va_olib_tashlanadi(problem, user) -> None:
    client = APIClient()
    url = reverse("problem-favourite", args=[problem.slug])
    detail = reverse("problem-detail", args=[problem.slug])

    assert client.post(url).status_code in (401, 403), "mehmon belgilay olmaydi"

    client.force_authenticate(user)
    assert client.post(url).data["is_favourite"] is True
    assert client.get(detail).data["is_favourite"] is True
    # Takroriy POST xato bermaydi — tugma ikki marta bosilishi mumkin.
    assert client.post(url).data["is_favourite"] is True

    assert client.delete(url).data["is_favourite"] is False
    assert client.get(detail).data["is_favourite"] is False


def test_baho_ozgartiriladi_va_ortacha_hisoblanadi(problem, user, other_user) -> None:
    url = reverse("problem-rate", args=[problem.slug])
    client = APIClient()

    client.force_authenticate(user)
    assert client.post(url, {"score": 5}, format="json").data["average"] == 5.0
    # Qayta baholash yangi yozuv emas, o'zgartirish.
    body = client.post(url, {"score": 3}, format="json").data
    assert (body["average"], body["count"]) == (3.0, 1)
    assert client.post(url, {"score": 9}, format="json").status_code == 400

    client.force_authenticate(other_user)
    assert client.post(url, {"score": 5}, format="json").data == {
        "average": 4.0,
        "count": 2,
        "my_rating": 5,
    }

    detail = APIClient().get(reverse("problem-detail", args=[problem.slug]))
    assert detail.data["rating"] == {"average": 4.0, "count": 2}
    assert detail.data["my_rating"] is None, "mehmonda o'z bahosi yo'q"


class TestProblemCode:
    """Ommaviy raqam — `#0431`. Berilgach o'zgarmaydi va qayta ishlatilmaydi."""

    def test_qoralamaga_raqam_berilmaydi(self, db) -> None:
        from problems.models import Problem

        draft = Problem.objects.create(
            slug="qoralama", title="Qoralama", statement="…", difficulty=800, is_public=False
        )
        assert draft.code is None

    def test_elon_qilinganda_raqam_beriladi(self, db, problem) -> None:
        from problems.models import Problem

        assert problem.code is not None

        draft = Problem.objects.create(
            slug="ikkinchi", title="Ikkinchi", statement="…", difficulty=900, is_public=False
        )
        draft.is_public = True
        draft.save()
        draft.refresh_from_db()

        assert draft.code == problem.code + 1

    def test_raqam_ochirilgandan_keyin_qayta_ishlatilmaydi(self, db, problem) -> None:
        from problems.models import Problem

        first = problem.code
        second = Problem.objects.create(
            slug="uchinchi", title="Uchinchi", statement="…", difficulty=900, is_public=True
        )
        assert second.code == first + 1

        second.delete()
        third = Problem.objects.create(
            slug="tortinchi", title="To'rtinchi", statement="…", difficulty=900, is_public=True
        )
        # Teshik qoladi — bu ataylab: tarqalgan raqam boshqa masalaga o'tmasin.
        assert third.code == first + 2

    def test_qayta_saqlash_raqamni_ozgartirmaydi(self, db, problem) -> None:
        original = problem.code
        problem.title = "Boshqa nom"
        problem.save()
        problem.refresh_from_db()
        assert problem.code == original


def test_royxat_qator_soniga_qarab_sorov_kopaytirmaydi(
    db, user, problem, hard_problem, django_assert_num_queries
) -> None:
    """Sevimli, baho va oxirgi urinish — guruh so'rovlar bilan.

    Qator ortganda so'rov soni o'zgarmasligi kerak; aks holda 100 masalali
    sahifa 300 ta so'rov qilardi.
    """
    from problems.models import Favourite

    client = APIClient()
    client.force_authenticate(user)
    Favourite.objects.create(user=user, problem=problem)

    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    url = reverse("problem-list")
    with CaptureQueriesContext(connection) as ctx:
        client.get(url)
    baseline = len(ctx.captured_queries)

    from problems.models import Problem

    for i in range(8):
        Problem.objects.create(
            slug=f"yuk-{i}", title=f"Yuk {i}", statement="…", difficulty=1000, is_public=True
        )

    with django_assert_num_queries(baseline):
        client.get(url)


class TestProgress:
    """Yon paneldagi progress bloki — 04-prd shkalasi bo'yicha."""

    def test_mehmonga_arxiv_hajmi_korinadi(self, problem, hard_problem) -> None:
        data = APIClient().get(reverse("problem-progress")).data

        assert data["total"] == 2
        assert data["solved"] == 0
        # Barcha darajalar qaytadi, bo'shlari ham — chiziqlar joyida tursin.
        assert [level["code"] for level in data["levels"]] == [
            "beginner",
            "basic",
            "intermediate",
            "upper",
            "hard",
            "expert",
            "master",
        ]

    def test_yechilganlar_darajasi_boyicha_sanaladi(self, user, problem, hard_problem) -> None:
        from ratings.models import UserSolvedProblem

        UserSolvedProblem.objects.create(
            user=user, problem=problem, difficulty_at_solve=problem.difficulty
        )
        client = APIClient()
        client.force_authenticate(user)

        data = client.get(reverse("problem-progress")).data
        levels = {level["code"]: level for level in data["levels"]}

        assert data["solved"] == 1
        # 800 → beginner (<1000), 2500 → expert (<2700)
        assert levels["beginner"] == {
            "code": "beginner",
            "label": "Boshlang'ich",
            "total": 1,
            "solved": 1,
        }
        assert levels["expert"]["total"] == 1
        assert levels["expert"]["solved"] == 0


def test_korish_soni_sahifa_ochilganda_ortadi(problem) -> None:
    """«Ko'p ko'rilgan» ro'yxatining manbai."""
    url = reverse("problem-detail", args=[problem.slug])
    client = APIClient()

    client.get(url)
    client.get(url)
    problem.refresh_from_db()

    assert problem.view_count == 2


class TestProblemStats:
    """Statistika sahifasi — verdikt/til taqsimoti va yechganlar."""

    @pytest.fixture
    def attempts(self, db, user, other_user, problem, language):
        from judging.models import Attempt

        made = []
        for owner, verdict in [
            (user, "WA"),
            (user, "AC"),
            (user, "AC"),  # ikkinchi AC — ro'yxatda takrorlanmasligi kerak
            (other_user, "TLE"),
        ]:
            made.append(
                Attempt.objects.create(
                    user=owner,
                    problem=problem,
                    language=language,
                    source_code="x",
                    verdict=verdict,
                )
            )
        return made

    def test_verdikt_va_til_taqsimoti(self, attempts, problem) -> None:
        data = APIClient().get(reverse("problem-stats", args=[problem.slug])).data

        assert data["total"] == 4
        assert {v["verdict"]: v["count"] for v in data["verdicts"]} == {
            "AC": 2,
            "WA": 1,
            "TLE": 1,
        }
        assert data["languages"][0]["count"] == 4
        assert data["languages"][0]["solved"] == 2

    def test_eng_tez_yechim_tilma_til(self, problem, user, other_user, language, db) -> None:
        from judging.models import Attempt
        from problems.models import Language

        python = Language.objects.create(
            code="py313", name="Python", version="3.13", run_cmd=["python3", "{src}"]
        )
        for owner, lang, ms in [
            (user, language, 120),
            (other_user, language, 45),
            (user, python, 900),
        ]:
            Attempt.objects.create(
                user=owner,
                problem=problem,
                language=lang,
                source_code="x",
                verdict="AC",
                time_ms=ms,
            )

        data = APIClient().get(reverse("problem-stats", args=[problem.slug])).data

        # Python C++ bilan bitta jadvalda taqqoslanmaydi — har til alohida.
        assert [(row["language"], row["username"], row["time_ms"]) for row in data["fastest"]] == [
            ("cpp23", other_user.username, 45),
            ("py313", user.username, 900),
        ]

    def test_statistikada_yechganlar_royxati_yoq(self, attempts, problem) -> None:
        """Yechganlar alohida bo'limda — bu yerda faqat taqsimot."""
        data = APIClient().get(reverse("problem-stats", args=[problem.slug])).data

        assert set(data) == {"total", "verdicts", "languages", "fastest"}

    def test_yopiq_masala_korinmaydi(self, db, problem) -> None:
        problem.is_public = False
        problem.save()

        assert APIClient().get(reverse("problem-stats", args=[problem.slug])).status_code == 404


# ── Yechim tahlili — ADR-0013 spoyler darvozasi ──────────────────────
@pytest.fixture
def with_editorial(problem) -> None:
    problem.editorial = "Ochko'zlik: eng qisqasidan boshlab tartiblang."
    problem.editorial_price = 30
    problem.save()


def test_yechmagan_odam_tahlil_matnini_umuman_olmaydi(with_editorial, problem, user) -> None:
    client = APIClient()
    client.force_authenticate(user)

    data = client.get(reverse("problem-detail", args=[problem.slug])).data

    # Frontendda yashirish yetarli emas — matn javobda BO'LMASLIGI kerak.
    assert data["editorial"] == ""
    assert data["editorial_state"] == {"available": True, "access": "locked", "price": 30}


def test_yechgan_odamga_tahlil_bepul(with_editorial, problem, user) -> None:
    from ratings.models import UserSolvedProblem

    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    client = APIClient()
    client.force_authenticate(user)

    data = client.get(reverse("problem-detail", args=[problem.slug])).data

    assert data["editorial"].startswith("Ochko'zlik")
    assert data["editorial_state"]["access"] == "solved"


def test_qvant_sarflab_ochiladi_va_bir_marta_yechiladi(with_editorial, problem, user) -> None:
    from qvant import ledger
    from qvant.models import QvantTransaction

    ledger.credit(user, 100, QvantTransaction.Reason.ADMIN)
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("problem-editorial", args=[problem.slug])

    assert client.post(url).data["editorial"].startswith("Ochko'zlik")
    assert ledger.get_wallet(user).balance == 70

    # Takroriy ochish PUL OLMAYDI — huquq abadiy.
    assert client.post(url).status_code == 200
    assert ledger.get_wallet(user).balance == 70
    assert (
        client.get(reverse("problem-detail", args=[problem.slug])).data["editorial_state"]["access"]
        == "purchased"
    )


def test_balans_yetmasa_tahlil_ochilmaydi(with_editorial, problem, user) -> None:
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(reverse("problem-editorial", args=[problem.slug]))

    assert response.status_code == 402
    assert problem.unlocks.count() == 0


def test_mehmon_tahlilni_kormaydi(with_editorial, problem) -> None:
    data = APIClient().get(reverse("problem-detail", args=[problem.slug])).data

    assert data["editorial"] == ""
    assert data["editorial_state"]["access"] == "anonymous"


# ── Yoqdi / yoqmadi ──────────────────────────────────────────────────
def test_ovoz_import_sanogiga_qoshiladi(problem, user, other_user) -> None:
    problem.likes_count = 141  # KEP dan kelgan tarix
    problem.save()
    url = reverse("problem-vote", args=[problem.slug])
    client = APIClient()
    client.force_authenticate(user)

    assert client.post(url, {"value": 1}).data == {"up": 142, "down": 0, "mine": 1}

    # Fikr o'zgardi — yangi qator emas, o'shaning o'zi yangilanadi.
    assert client.post(url, {"value": -1}).data == {"up": 141, "down": 1, "mine": -1}

    client.force_authenticate(other_user)
    assert client.post(url, {"value": 1}).data["up"] == 142

    client.force_authenticate(user)
    assert client.post(url, {"value": 0}).data == {"up": 142, "down": 0, "mine": 0}


def test_ovoz_detalda_korinadi(problem, user) -> None:
    client = APIClient()
    client.force_authenticate(user)
    client.post(reverse("problem-vote", args=[problem.slug]), {"value": 1})

    assert client.get(reverse("problem-detail", args=[problem.slug])).data["votes"] == {
        "up": 1,
        "down": 0,
        "mine": 1,
    }


# ── Masalaga xos tillar va o'xshash masalalar ────────────────────────
def test_til_royxati_bosh_bolsa_hamma_faol_til_ochiq(problem, language) -> None:
    data = APIClient().get(reverse("problem-detail", args=[problem.slug])).data

    assert [row["code"] for row in data["languages"]] == ["cpp23"]
    assert data["languages"][0]["time_limit_ms"] == problem.time_limit_ms


def test_til_royxati_bolsa_faqat_osha_tillar_va_ustma_ust_limit(problem, language) -> None:
    from problems.models import ProblemLanguage

    ProblemLanguage.objects.create(
        problem=problem, language=language, time_limit_ms=3000, code_template="int main(){}"
    )
    data = APIClient().get(reverse("problem-detail", args=[problem.slug])).data

    assert [row["code"] for row in data["languages"]] == ["cpp23"]
    assert data["languages"][0]["time_limit_ms"] == 3000
    # Masalada berilmagan xotira limiti masalanikidan olinadi.
    assert data["languages"][0]["memory_limit_kb"] == problem.memory_limit_kb
    assert data["languages"][0]["code_template"] == "int main(){}"


def test_oxshash_masalalar_faqat_ommaviysi(problem, hard_problem, db) -> None:
    from problems.models import Problem, SimilarProblem

    draft = Problem.objects.create(
        slug="qoralama", title="Qoralama", statement="x", difficulty=900, is_public=False
    )
    SimilarProblem.objects.create(problem=problem, similar=hard_problem, score=0.9)
    SimilarProblem.objects.create(problem=problem, similar=draft, score=0.95)

    data = APIClient().get(reverse("problem-detail", args=[problem.slug])).data

    assert [row["slug"] for row in data["similar"]] == [hard_problem.slug]
    assert data["similar"][0]["score"] == 0.9


def test_mavzular_royxatida_faqat_ommaviy_masalasi_bori(problem, db) -> None:
    from problems.models import Problem, Topic

    ishlatilgan = Topic.objects.create(slug="dp", name_uz="Dinamik dasturlash")
    problem.topics.add(ishlatilgan)
    # Import qilingan teg — hali faqat qoralamada.
    qoralama = Problem.objects.create(
        slug="import", title="Import", statement="x", difficulty=900, is_public=False
    )
    qoralama.topics.add(Topic.objects.create(slug="aiohttp", name_uz="aiohttp"))

    data = APIClient().get(reverse("topic-list")).data

    assert [t["slug"] for t in data["results"]] == ["dp"]


def test_import_muallifiga_havola_qoyilmaydi(problem, db) -> None:
    """Soya hisob nofaol — profil sahifasi yo'q, havola 404 ga olib borardi."""
    from core.models import User

    author = User.objects.create(
        username="kep-admin", display_name="Nazarbek Baltabaev", is_active=False
    )
    problem.author = author
    problem.save()

    data = APIClient().get(reverse("problem-detail", args=[problem.slug])).data

    assert data["author"] == {
        "username": "kep-admin",
        "display_name": "Nazarbek Baltabaev",
        "has_profile": False,
    }


# ── Mavzu kesimidagi kuch ────────────────────────────────────────────
@pytest.fixture
def topic_history(problem, hard_problem, user, language, db) -> None:
    from judging.models import Attempt
    from problems.models import Topic
    from ratings.models import UserSolvedProblem

    dp = Topic.objects.create(slug="dp", name_uz="Dinamik dasturlash")
    graphs = Topic.objects.create(slug="graphs", name_uz="Graflar")
    problem.topics.add(dp)
    hard_problem.topics.add(graphs)

    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    # Graflarda urindi, lekin yechmadi — «taqalib qolgan» signali.
    Attempt.objects.create(
        user=user, problem=hard_problem, language=language, source_code="x", verdict="WA"
    )


def test_mavzu_kuchi_global_skills_formulasi_bilan(topic_history, problem, user) -> None:
    from ratings.formulas import skills_rating

    client = APIClient()
    client.force_authenticate(user)

    rows = {t["slug"]: t for t in client.get(reverse("problem-skills")).data["topics"]}

    assert rows["dp"]["solved"] == 1
    assert rows["dp"]["rating"] == skills_rating([problem.difficulty])
    assert rows["graphs"]["solved"] == 0
    assert rows["graphs"]["stuck"] == 1, "urinilgan, lekin yechilmagan"


def test_mehmonga_arxiv_hajmi_korinadi(topic_history) -> None:
    rows = APIClient().get(reverse("problem-skills")).data["topics"]

    assert {t["slug"] for t in rows} == {"dp", "graphs"}
    assert all(t["solved"] == 0 and t["rating"] == 0 for t in rows)
    assert all(t["total"] == 1 for t in rows)


def test_mavzu_filtri_hammasini_talab_qiladi(problem, hard_problem, db) -> None:
    """`?topics=dp,trees` — ikkalasi ham bor masalalar (Codeforces kabi)."""
    from problems.models import Topic

    dp = Topic.objects.create(slug="dp", name_uz="Dinamik dasturlash")
    trees = Topic.objects.create(slug="trees", name_uz="Daraxtlar")
    problem.topics.add(dp)
    hard_problem.topics.add(dp, trees)

    url = reverse("problem-list")
    client = APIClient()

    only_dp = client.get(url, {"topics": "dp"}).data["results"]
    assert {row["slug"] for row in only_dp} == {problem.slug, hard_problem.slug}

    both = client.get(url, {"topics": "dp,trees"}).data["results"]
    # YOKI bo'lganda bu yerda ikkalasi qaytardi va filtr ma'nosini yo'qotardi.
    assert [row["slug"] for row in both] == [hard_problem.slug]


def test_taqalib_qolganlar_filtri(problem, hard_problem, user, language, db) -> None:
    """`attempted=true&solved=false` — urinib, yecha olmaganlar."""
    from judging.models import Attempt
    from ratings.models import UserSolvedProblem

    for target, verdict in [(problem, "AC"), (hard_problem, "WA")]:
        Attempt.objects.create(
            user=user, problem=target, language=language, source_code="x", verdict=verdict
        )
    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )

    client = APIClient()
    client.force_authenticate(user)
    rows = client.get(reverse("problem-list"), {"attempted": "true", "solved": "false"}).data[
        "results"
    ]

    assert [row["slug"] for row in rows] == [hard_problem.slug]


def test_testsiz_masala_belgilanadi(problem, samples, hard_problem) -> None:
    """41 % arxivda test yo'q — foydalanuvchi buni oldindan bilishi kerak."""
    client = APIClient()

    rows = {row["slug"]: row for row in client.get(reverse("problem-list")).data["results"]}
    assert rows[problem.slug]["has_tests"] is True
    assert rows[hard_problem.slug]["has_tests"] is False

    detail = client.get(reverse("problem-detail", args=[hard_problem.slug])).data
    assert detail["has_tests"] is False


# ── Nuqson haqida xabar ──────────────────────────────────────────────
def test_xabar_yuboriladi_va_takrorlanmaydi(problem, user) -> None:
    from problems.models import ProblemReport

    url = reverse("problem-report", args=[problem.slug])
    client = APIClient()

    assert client.post(url, {"reason": "tests"}).status_code in (401, 403)

    client.force_authenticate(user)
    assert client.post(url, {"reason": "tests", "comment": "3-test noto'g'ri"}).status_code == 201

    # Tugmani ikki marta bosish navbatni to'ldirmaydi — o'sha yozuv
    # yangilanadi.
    assert client.post(url, {"reason": "statement"}).status_code == 201
    report = ProblemReport.objects.get()
    assert (report.reason, report.status) == ("statement", "open")


def test_notogri_sabab_rad_etiladi(problem, user) -> None:
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(reverse("problem-report", args=[problem.slug]), {"reason": "yoq"})

    assert response.status_code == 400


def test_xabarlar_faqat_xodimga_korinadi(problem, user, staff_client) -> None:
    from problems.models import ProblemReport

    ProblemReport.objects.create(user=user, problem=problem, reason="tests")

    guest = APIClient()
    assert guest.get(reverse("staff-problem-report-list")).status_code in (401, 403)

    rows = staff_client.get(reverse("staff-problem-report-list")).data["results"]
    assert [(r["problem"], r["username"], r["status"]) for r in rows] == [
        (problem.slug, user.username, "open")
    ]


# ── Qidiruv ──────────────────────────────────────────────────────────
@pytest.fixture
def searchable(db) -> None:
    from problems.models import Problem, Topic

    dp = Topic.objects.create(slug="dinamik-dasturlash", name_uz="Dinamik dasturlash")
    # Import qilingan sarlavhalarda apostrof besh xil belgi bilan keladi.
    for slug, title in [
        ("ikki-sonni-yigindisi", "Ikki sonni yig'indisi"),
        ("uchta-sonni-yigindisi", "Uchta sonni yig`indisi"),
        ("ryukzak", "Ryukzak masalasi"),
    ]:
        problem = Problem.objects.create(
            slug=slug, title=title, statement="x", difficulty=800, is_public=True
        )
        if slug == "ryukzak":
            problem.topics.add(dp)


def test_qidiruv_apostrofdan_qatiy_nazar_bir_xil(searchable) -> None:
    url = reverse("problem-list")
    client = APIClient()

    def found(term: str) -> set[str]:
        rows = client.get(url, {"search": term}).data["results"]
        return {row["slug"] for row in rows}

    kutilgan = {"ikki-sonni-yigindisi", "uchta-sonni-yigindisi"}
    # Uchala yozuv ham bir xil natija berishi kerak.
    assert found("yig'indi") == kutilgan
    assert found("yig`indi") == kutilgan
    assert found("yigindi") == kutilgan
    assert found("YIG'INDI") == kutilgan


def test_qidiruv_mavzuni_ham_qamraydi(searchable) -> None:
    rows = APIClient().get(reverse("problem-list"), {"search": "dinamik"}).data["results"]

    # Sarlavhada «dinamik» yo'q — mavzu orqali topiladi.
    assert [row["slug"] for row in rows] == ["ryukzak"]


def test_mavzu_slugi_inglizcha_bolsa_ham_topiladi(searchable, db) -> None:
    """Birlashtirilgan mavzuda slug inglizcha qoladi (`dp`), nomi esa
    o'zbekcha — qidiruv NOM bo'yicha ham ishlashi kerak."""
    from problems.models import Problem, Topic

    topic = Topic.objects.get(slug="dinamik-dasturlash")
    topic.slug = "dp"
    topic.save()

    rows = APIClient().get(reverse("problem-list"), {"search": "dinamik"}).data["results"]

    assert [row["slug"] for row in rows] == ["ryukzak"]
    assert Problem.objects.get(slug="ryukzak").topics.get().slug == "dp"


def test_qidiruv_takror_qator_bermaydi(searchable, db) -> None:
    from problems.models import Problem, Topic

    problem = Problem.objects.get(slug="ryukzak")
    problem.topics.add(Topic.objects.create(slug="dinamik-2", name_uz="Dinamik #2"))

    rows = APIClient().get(reverse("problem-list"), {"search": "dinamik"}).data["results"]

    # Ikki mavzu mos keladi — masala BIR MARTA chiqishi kerak.
    assert [row["slug"] for row in rows] == ["ryukzak"]


# ── Yechganlar bo'limi ───────────────────────────────────────────────
@pytest.fixture
def solvers_history(problem, user, other_user, language) -> None:
    from judging.models import Attempt

    # `user` ikkinchi urinishda yechdi, `other_user` birinchisida.
    for owner, verdict, source, ms in [
        (user, "WA", "int main(){}", 0),
        (user, "AC", "int main(){return 0;}", 120),
        (user, "AC", "x", 10),  # AC dan keyingi urinish sanalmaydi
        (other_user, "AC", "main(){}", 45),
    ]:
        Attempt.objects.create(
            user=owner,
            problem=problem,
            language=language,
            source_code=source,
            verdict=verdict,
            time_ms=ms,
        )


def test_yechganlar_urinish_soni_va_kod_uzunligi(solvers_history, problem, user) -> None:
    data = APIClient().get(reverse("problem-solvers", args=[problem.slug])).data

    assert data["count"] == 2
    mine = next(row for row in data["results"] if row["username"] == user.username)
    # AC gacha ikki urinish; AC dan keyingisi sanalmaydi.
    assert mine["attempts"] == 2
    assert mine["code_length"] == len("int main(){return 0;}")


def test_yechganlarni_saralash(solvers_history, problem, user, other_user) -> None:
    client = APIClient()
    url = reverse("problem-solvers", args=[problem.slug])

    def order(term: str) -> list[str]:
        return [row["username"] for row in client.get(url, {"ordering": term}).data["results"]]

    assert order("first") == [user.username, other_user.username], "birinchi yechgan"
    assert order("fast") == [other_user.username, user.username], "eng tez"
    assert order("short") == [other_user.username, user.username], "eng qisqa kod"


def test_yopiq_masalada_yechganlar_korinmaydi(solvers_history, problem) -> None:
    problem.is_public = False
    problem.save()

    assert APIClient().get(reverse("problem-solvers", args=[problem.slug])).status_code == 404


def test_tahlil_takroriy_ochilganda_pul_bir_marta_yechiladi(with_editorial, problem, user) -> None:
    """Tugmani ikki marta bosish 30 emas, 60 Qvant yechardi.

    Ilgari tartib teskari edi: `exists()` → pul → yozuv. Bir vaqtda
    kelgan olti so'rov 180 Qvant yechib, beshtasi 500 qaytargan edi.
    """
    from qvant import ledger
    from qvant.models import QvantTransaction

    ledger.credit(user, 100, QvantTransaction.Reason.ADMIN)
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("problem-editorial", args=[problem.slug])

    for _ in range(4):
        assert client.post(url).status_code == 200

    assert ledger.get_wallet(user).balance == 70
    assert problem.unlocks.count() == 1


def test_balans_yetmasa_yozuv_qolmaydi(with_editorial, problem, user) -> None:
    """Yozuv AVVAL yaratiladi — pul yechilmasa u ham qaytarib olinishi shart."""
    client = APIClient()
    client.force_authenticate(user)

    assert client.post(reverse("problem-editorial", args=[problem.slug])).status_code == 402

    # Aks holda foydalanuvchi to'lamasdan tahlilga ega bo'lardi.
    assert problem.unlocks.count() == 0


def test_s3_yiqilganda_nosozlik_qisqa_keshlanadi(samples, problem, monkeypatch) -> None:
    """Bir soatlik kesh MinIO qaytgach ham sahifani namunasiz qoldirardi."""
    from problems import storage

    cache.delete(storage.samples_cache_key(problem.slug))
    ttls: list[int] = []
    original = cache.set

    def spy(key, value, timeout=None, **kw):
        ttls.append(timeout)
        return original(key, value, timeout, **kw)

    monkeypatch.setattr(cache, "set", spy)
    monkeypatch.setattr(storage, "get_test_data", _raise_s3)

    assert storage.sample_tests(problem) == []
    assert ttls == [storage.FAILURE_TTL], "nosozlik uzoq keshlanmaydi"


def test_s3_yiqilganda_qolgan_testlar_urinilmaydi(samples, problem, monkeypatch) -> None:
    """Har biriga alohida timeout sahifani 15 soniyaga cho'zgan edi."""
    from problems import storage

    cache.delete(storage.samples_cache_key(problem.slug))
    calls: list[str] = []

    def counting(ref: str) -> str:
        calls.append(ref)
        raise OSError("saqlash yiqildi")

    monkeypatch.setattr(storage, "get_test_data", counting)
    storage.sample_tests(problem)

    assert len(calls) == 1, "birinchi xatodan keyin to'xtaydi"


def _raise_s3(ref: str) -> str:
    raise OSError("saqlash yiqildi")


@pytest.mark.django_db
def test_recount_problems_ochirilgan_foydalanuvchidan_keyin_tuzatadi(
    problem, user, other_user, language
) -> None:
    """Foydalanuvchi o'chirilsa `UserSolvedProblem` kaskad bilan ketadi,
    `solved_count` esa qolaveradi — o'lchandi: arxiv «N kishi yechgan» ni
    doimiy ravishda oshirib ko'rsatardi."""
    from io import StringIO

    from django.core.management import call_command

    from judging.models import Attempt
    from judging.services import apply_result

    for u in (user, other_user):
        attempt = Attempt.objects.create(
            user=u, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
    problem.refresh_from_db()
    assert problem.solved_count == 2

    other_user.delete()
    problem.refresh_from_db()
    assert problem.solved_count == 2  # drift: qator ketdi, sanoq qoldi

    call_command("recount_problems", stdout=StringIO())

    problem.refresh_from_db()
    assert problem.solved_count == 1
    assert problem.attempt_count == 1


@pytest.mark.django_db
class TestMediaEndpointi:
    """Ko'chirilgan rasm va fayllar shu yerdan beriladi (ADR-0005).

    Saqlash tashqariga ochilmagan, tunnel esa `/api/*` ni API ga
    yo'naltiradi — shuning uchun yo'l API ostida.
    """

    def _url(self, path: str) -> str:
        return reverse("media", args=[path])

    def test_fayl_beriladi_va_abadiy_keshlanadi(self, monkeypatch) -> None:
        from problems import media_views

        monkeypatch.setattr(media_views, "get_media", lambda key: (b"\x89PNG data", "image/png"))

        r = APIClient().get(self._url("abc123.png"))

        assert r.status_code == 200
        assert r["Content-Type"] == "image/png"
        assert r["X-Content-Type-Options"] == "nosniff"
        assert "immutable" in r["Cache-Control"]
        assert "max-age=31536000" in r["Cache-Control"]

    def test_yoq_fayl_404(self, monkeypatch) -> None:
        from problems import media_views

        def yiqil(key: str) -> tuple[bytes, str]:
            raise OSError("yo'q")

        monkeypatch.setattr(media_views, "get_media", yiqil)

        assert APIClient().get(self._url("yoq.png")).status_code == 404

    def test_yol_boylab_chiqib_bolmaydi(self, monkeypatch) -> None:
        from problems import media_views

        chaqirildi: list[str] = []

        def kuzat(key: str) -> tuple[bytes, str]:
            chaqirildi.append(key)
            return b"", "text/plain"

        monkeypatch.setattr(media_views, "get_media", kuzat)

        assert APIClient().get(self._url("../../etc/passwd")).status_code == 404
        assert chaqirildi == []

    def test_yozish_metodlari_rad_etiladi(self, monkeypatch) -> None:
        from problems import media_views

        monkeypatch.setattr(media_views, "get_media", lambda key: (b"x", "image/png"))

        assert APIClient().post(self._url("abc.png")).status_code == 405
