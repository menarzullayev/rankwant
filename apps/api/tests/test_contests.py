"""Contest, ACM standings va Contests reytingi."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestProblem, ContestRegistration, Standing
from contests.services import WRONG_ATTEMPT_PENALTY_MIN, finalize_contest, rebuild_standings
from contests.views import STANDINGS_TOP
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Problem
from ratings.models import RatingHistory

# ADR-0027: a fresh account starts at `droplet` (1200), not 1400 — the model
# default was lowered there. Read it from the model instead of writing the
# number again: the assertions below kept saying 1400 long after the change
# landed, and PR CI does not run pytest (`pr_skips_heavy_ci`), so only Nightly
# saw them fail.
CONTEST_BASE = User._meta.get_field("rating_contest").default


def submit(user, contest, problem, language, verdict, minutes_in):
    a = Attempt.objects.create(
        user=user,
        problem=problem,
        contest=contest,
        language=language,
        source_code="x",
        verdict=verdict,
    )
    Attempt.objects.filter(pk=a.pk).update(
        created_at=contest.start_at + timedelta(minutes=minutes_in)
    )
    a.refresh_from_db()
    return a


@pytest.mark.django_db
class TestStandings:
    def test_yechganlar_soni_ustun(self, contest, problem, language, user, other_user) -> None:
        third = User.objects.create_user(username="dilnoza", password="Parol!12345")
        p2 = type(problem).objects.create(
            slug="b", title="B", statement="…", difficulty=1200, is_public=True
        )
        ContestProblem.objects.create(contest=contest, problem=p2, index_letter="B")

        submit(user, contest, problem, language, Verdict.AC, 10)
        submit(user, contest, p2, language, Verdict.AC, 20)
        submit(other_user, contest, problem, language, Verdict.AC, 5)
        submit(third, contest, problem, language, Verdict.WA, 5)

        assert rebuild_standings(contest) == 3
        rows = list(Standing.objects.filter(contest=contest).order_by("rank"))
        assert rows[0].user_id == user.pk and rows[0].solved_count == 2
        assert rows[1].user_id == other_user.pk and rows[1].solved_count == 1
        assert rows[2].solved_count == 0

    def test_penalty_hisobi(self, contest, problem, language, user) -> None:
        """Penalty = AC vaqti + 20 × noto'g'ri urinishlar."""
        submit(user, contest, problem, language, Verdict.WA, 5)
        submit(user, contest, problem, language, Verdict.TLE, 8)
        submit(user, contest, problem, language, Verdict.AC, 30)
        rebuild_standings(contest)
        standing = Standing.objects.get(contest=contest, user=user)
        assert standing.penalty == 30 + 2 * WRONG_ATTEMPT_PENALTY_MIN

    def test_ce_penalty_bermaydi(self, contest, problem, language, user) -> None:
        submit(user, contest, problem, language, Verdict.CE, 3)
        submit(user, contest, problem, language, Verdict.AC, 10)
        rebuild_standings(contest)
        assert Standing.objects.get(contest=contest, user=user).penalty == 10

    def test_ac_dan_keyingi_urinish_penalty_bermaydi(
        self, contest, problem, language, user
    ) -> None:
        submit(user, contest, problem, language, Verdict.AC, 10)
        submit(user, contest, problem, language, Verdict.WA, 20)
        rebuild_standings(contest)
        assert Standing.objects.get(contest=contest, user=user).penalty == 10


@pytest.mark.django_db
class TestContestRating:
    def _ten_participants(self, contest, problem, language):
        users = []
        for i in range(10):
            u = User.objects.create_user(username=f"u{i}", password="Parol!12345")
            submit(u, contest, problem, language, Verdict.AC, 5 + i)
            users.append(u)
        return users

    def test_kam_ishtirokchi_reyting_bermaydi(self, contest, problem, language, user) -> None:
        """ADR-0006: >= 10 ishtirokchi sharti."""
        submit(user, contest, problem, language, Verdict.AC, 10)
        assert finalize_contest(contest) == 0
        user.refresh_from_db()
        assert user.rating_contest == CONTEST_BASE

    def test_reyting_hisoblanadi(self, contest, problem, language) -> None:
        users = self._ten_participants(contest, problem, language)
        assert finalize_contest(contest) == 10

        for u in users:
            u.refresh_from_db()
        # Birinchi o'rin yutadi, oxirgisi yo'qotadi — bazaga nisbatan
        assert users[0].rating_contest > CONTEST_BASE
        assert users[-1].rating_contest < CONTEST_BASE
        # The batch write keeps the stored maximum too (ADR-0024).
        assert users[0].max_rating_contest == users[0].rating_contest
        assert users[-1].max_rating_contest == users[-1].rating_contest
        # Har birida audit yozuvi
        assert RatingHistory.objects.filter(rating_type="contest").count() == 10
        entry = RatingHistory.objects.filter(user=users[0], rating_type="contest").first()
        assert entry is not None and entry.rank == 1 and entry.seed is not None

    def test_ikki_marta_hisoblanmaydi(self, contest, problem, language) -> None:
        self._ten_participants(contest, problem, language)
        finalize_contest(contest)
        contest.refresh_from_db()
        assert finalize_contest(contest) == 0

    def test_eskirgan_obyekt_qoriqchini_chetlab_otmaydi(self, contest, problem, language) -> None:
        """Ikkinchi chaqiruv o'z obyektini ALLAQACHON o'qib olgan bo'lishi mumkin.

        Beat `finalize_due` ni har 60 soniyada yuboradi, worker esa ikkita
        jarayonda ishlaydi — uzoq yakunlanish ustma-ust tushadi. O'lchandi
        (preview, 12 ishtirokchi): qulfsiz holatda reyting to'g'ri qoldi,
        lekin `RatingHistory` 24 qator va bildirishnoma ham 24 ta bo'ldi.
        """
        self._ten_participants(contest, problem, language)
        eskirgan = Contest.objects.get(pk=contest.pk)  # ratings_applied_at hali None

        assert finalize_contest(contest) == 10
        assert finalize_contest(eskirgan) == 0
        assert RatingHistory.objects.filter(rating_type="contest").count() == 10

    def test_unrated_contest(self, contest, problem, language) -> None:
        contest.is_rated = False
        contest.save()
        self._ten_participants(contest, problem, language)
        assert finalize_contest(contest) == 0

    def test_tugamagan_contest_yakunlanmaydi(self, problem, language) -> None:
        now = timezone.now()
        running = Contest.objects.create(
            slug="live",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
            is_rated=True,
        )
        assert finalize_contest(running) == 0


@pytest.mark.django_db
class TestContestApi:
    def test_royxat_va_standings(self, contest, problem, language, user) -> None:
        submit(user, contest, problem, language, Verdict.AC, 10)
        rebuild_standings(contest)
        c = APIClient()
        assert c.get(reverse("contest-list")).status_code == 200
        body = c.get(reverse("contest-standings", args=[contest.slug])).json()
        assert body["results"][0]["username"] == user.username
        assert body["frozen"] is False

    def test_royxatdan_otish(self, problem, user) -> None:
        now = timezone.now()
        upcoming = Contest.objects.create(
            slug="kelasi",
            title="Kelasi",
            start_at=now + timedelta(hours=1),
            end_at=now + timedelta(hours=3),
        )
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.post(reverse("contest-register", args=[upcoming.slug])).status_code == 201
        assert c.post(reverse("contest-register", args=[upcoming.slug])).status_code == 200

    def test_tugagan_contestga_royxatdan_otib_bolmaydi(self, contest, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-register", args=[contest.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "contest_finished"

    def test_freeze_bayrogi(self, problem, language) -> None:
        now = timezone.now()
        frozen = Contest.objects.create(
            slug="muzlagan",
            title="Muzlagan",
            start_at=now - timedelta(hours=2),
            end_at=now + timedelta(minutes=10),
            freeze_minutes=30,
        )
        assert frozen.is_frozen is True


@pytest.mark.django_db
class TestVirtualContest:
    """PRD P1-1 — virtual ishtirok."""

    def test_tugagan_contestda_boshlash(self, contest, user) -> None:
        from contests.services import start_virtual, virtual_deadline

        reg = start_virtual(contest, user)
        assert reg.virtual_start_at is not None
        expected = contest.end_at - contest.start_at
        assert virtual_deadline(reg) - reg.virtual_start_at == expected

    def test_ketayotgan_contestda_boshlab_bolmaydi(self, problem, user) -> None:
        from contests.services import start_virtual

        now = timezone.now()
        running = Contest.objects.create(
            slug="live2",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
        )
        with pytest.raises(ValueError):
            start_virtual(running, user)

    def test_ikki_marta_boshlanmaydi(self, contest, user) -> None:
        from contests.services import start_virtual

        first = start_virtual(contest, user).virtual_start_at
        assert start_virtual(contest, user).virtual_start_at == first

    def test_virtual_rasmiy_jadvalga_kirmaydi(
        self, contest, problem, language, user, other_user
    ) -> None:
        """Virtual ishtirokchi javoblarni bilib turib yechadi — uning
        natijasi rasmiy jadvalga va reytingga TUSHMASLIGI kerak.

        Virtual yechim musobaqa TUGAGANIDAN keyin yuboriladi (boshqacha
        bo'lishi mumkin emas: `start_virtual` tugamagan musobaqani rad
        etadi) — fixture ham shuni aks ettiradi.
        """
        from contests.services import rebuild_standings, start_virtual

        submit(other_user, contest, problem, language, Verdict.AC, 10)
        start_virtual(contest, user)
        after_end = int((contest.end_at - contest.start_at).total_seconds() // 60) + 5
        submit(user, contest, problem, language, Verdict.AC, after_end)

        rebuild_standings(contest)
        usernames = set(
            Standing.objects.filter(contest=contest).values_list("user__username", flat=True)
        )
        assert other_user.username in usernames
        assert user.username not in usernames

    def test_api_endpointi(self, contest, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-virtual", args=[contest.slug]))
        assert r.status_code == 201
        assert r.json()["virtual_start_at"] is not None

    def test_ketayotgan_contestda_api_400(self, problem, user) -> None:
        now = timezone.now()
        running = Contest.objects.create(
            slug="live3",
            title="Live",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(hours=1),
        )
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("contest-virtual", args=[running.slug]))
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "not_finished"


@pytest.mark.django_db
class TestContestSubmission:
    """Musobaqaga submit — urinish contestga bog'lanishi kerak.

    Avval `contest` maydoni serializerda bor edi, lekin view uni
    ishlatmasdi: har urinish `contest=None` bo'lib yozilar, standings
    esa hech qachon to'lmasdi. Unit testlar buni ko'rmagan, chunki ular
    `rebuild_standings` ni contestga bog'langan urinishlar bilan
    to'g'ridan-to'g'ri chaqirardi.
    """

    @pytest.fixture
    def running(self, db, problem) -> Contest:
        """Umumiy `contest` fixture'i TUGAGAN musobaqa — submit uchun faol kerak."""
        now = timezone.now()
        c = Contest.objects.create(
            slug="faol-round",
            title="Faol Round",
            start_at=now - timedelta(hours=1),
            end_at=now + timedelta(hours=1),
            is_rated=True,
        )
        ContestProblem.objects.create(contest=c, problem=problem, index_letter="A")
        return c

    def _submit(self, client, slug="a-plus-b", contest="demo"):
        payload = {"problem": slug, "language": "cpp23", "source_code": "int main(){}"}
        if contest:
            payload["contest"] = contest
        return client.post(reverse("attempt-list"), payload)

    def test_urinish_contestga_boglanadi(self, user, running, language) -> None:
        ContestRegistration.objects.create(contest=running, user=user)
        c = APIClient()
        c.force_authenticate(user=user)

        r = self._submit(c, contest=running.slug)
        assert r.status_code == 201
        assert Attempt.objects.get(pk=r.json()["id"]).contest_id == running.pk

    def test_royxatdan_otmagan_submit_qila_olmaydi(self, user, running, language) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = self._submit(c, contest=running.slug)
        assert r.status_code == 400
        # The API answers in English (`tools/check_api_english.py`); the source
        # of this string is `judging/serializers.py`.
        assert "register for the contest" in str(r.json()).lower()

    def test_contestda_yoq_masala_rad_etiladi(self, user, running, language) -> None:
        ContestRegistration.objects.create(contest=running, user=user)
        other = Problem.objects.create(
            slug="boshqa", title="Boshqa", difficulty=800, is_public=True
        )
        c = APIClient()
        c.force_authenticate(user=user)
        r = self._submit(c, slug=other.slug, contest=running.slug)
        assert r.status_code == 400

    def test_contestsiz_submit_hamon_ishlaydi(self, user, problem, language) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = self._submit(c, contest=None)
        assert r.status_code == 201
        assert Attempt.objects.get(pk=r.json()["id"]).contest_id is None


def test_start_dan_oldingi_urinish_jadvalni_buzmaydi(db, contest, problem, user, language) -> None:
    """Manfiy jarima butun standings qurilishini to'xtatardi.

    Urinish musobaqa boshlanishidan oldin turishi mumkin: rejudge yoki
    `start_at` keyin o'zgartirilgan bo'lsa. Bitta qator emas, HAMMASI
    yiqilardi — `penalty` `PositiveIntegerField`.
    """
    from datetime import timedelta

    from contests.models import ContestProblem, ContestRegistration, Standing
    from contests.services import rebuild_standings
    from judging.models import Attempt

    ContestProblem.objects.update_or_create(
        contest=contest, index_letter="A", defaults={"problem": problem}
    )
    ContestRegistration.objects.get_or_create(contest=contest, user=user)
    attempt = Attempt.objects.create(
        user=user,
        problem=problem,
        contest=contest,
        language=language,
        source_code="x",
        verdict="AC",
    )
    Attempt.objects.filter(pk=attempt.pk).update(created_at=contest.start_at - timedelta(hours=2))

    assert rebuild_standings(contest) == 1
    assert Standing.objects.get(contest=contest, user=user).penalty == 0


@pytest.mark.django_db
def test_muzlatilgan_oynadagi_ac_jadvalga_tushmaydi(contest, problem, language, user) -> None:
    """Freeze faqat bayroq edi — `rebuild_standings` uni umuman ko'rmasdi.

    O'lchandi: `is_frozen=True` bo'lgan oynada kelgan AC jadvalga darhol
    tushib, oxirgi daqiqalardagi kurashni oshkor qilardi.
    """
    ContestProblem.objects.update_or_create(
        contest=contest, index_letter="A", defaults={"problem": problem}
    )
    now = timezone.now()
    Contest.objects.filter(pk=contest.pk).update(
        start_at=now - timedelta(hours=2), end_at=now + timedelta(minutes=10), freeze_minutes=30
    )
    contest.refresh_from_db()
    assert contest.is_frozen

    late = Attempt.objects.create(
        user=user,
        problem=problem,
        contest=contest,
        language=language,
        source_code="x",
        verdict=Verdict.AC,
    )
    # Muzlatish oynasi ichida, lekin tugashdan oldin — haqiqiy holat.
    Attempt.objects.filter(pk=late.pk).update(created_at=now - timedelta(minutes=5))
    assert rebuild_standings(contest) == 0

    # Tugagach muzlatish tarqaydi va haqiqiy jadval quriladi.
    Contest.objects.filter(pk=contest.pk).update(end_at=now - timedelta(seconds=1))
    contest.refresh_from_db()
    assert rebuild_standings(contest) == 1
    assert Standing.objects.get(contest=contest, user=user).solved_count == 1
    assert late.verdict == Verdict.AC


@pytest.mark.django_db
def test_virtual_boshlash_rasmiy_natijani_ochirmaydi(
    contest, problem, language, user, other_user
) -> None:
    """Ilgari jadval foydalanuvchi bo'yicha filtrlanardi — o'lchandi:
    musobaqada haqiqatan qatnashgan odam keyin uni virtual takrorlasa,
    rasmiy qatori jadvaldan butunlay yo'qolardi."""
    from contests.services import rebuild_standings, start_virtual

    submit(user, contest, problem, language, Verdict.AC, 20)
    submit(other_user, contest, problem, language, Verdict.AC, 30)
    rebuild_standings(contest)
    assert Standing.objects.filter(contest=contest).count() == 2

    start_virtual(contest, user)
    rebuild_standings(contest)

    row = Standing.objects.get(contest=contest, user=user)
    assert row.rank == 1 and row.solved_count == 1


@pytest.mark.django_db
def test_jadval_chekkada_keshlanadi(contest, problem, language, user) -> None:
    """Jadval hamma uchun bir xil — CDN uni keshlashi SHART.

    Ilgari bu yerda SSE oqimi turardi va o'lchandi: to'rtta tomoshabin
    gunicorn ning to'rtta sinxron ishchisini band qilib, butun API ni
    javobsiz qoldirardi. `Vary: Cookie` bo'lsa kesh ishlamaydi — har
    sessiyaning o'z cookie'si bor.
    """
    submit(user, contest, problem, language, Verdict.AC, 10)
    rebuild_standings(contest)

    r = APIClient().get(reverse("contest-standings", args=[contest.slug]))

    assert r.status_code == 200
    assert "s-maxage=10" in r["Cache-Control"]
    assert "public" in r["Cache-Control"]
    assert "Cookie" not in r.get("Vary", "")


@pytest.mark.django_db
class TestVirtualYuborish:
    """PRD P1-1 — virtual ishtirok BOSHDAN OXIRIGACHA ishlashi kerak.

    O'lchandi: «boshlash» tugmasi muddat ko'rsatardi, keyin har yuborish
    400 qaytarardi — `is_running` tugagan musobaqada hech qachon rost
    emas, virtual esa faqat tugaganida mumkin.
    """

    def _submit(self, client, problem, language, slug):
        return client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "print(1)",
                "contest": slug,
            },
            format="json",
        )

    def test_virtual_oyna_ichida_yuborish_otadi(self, contest, problem, language, user) -> None:
        from contests.services import start_virtual

        ContestProblem.objects.update_or_create(
            contest=contest, index_letter="A", defaults={"problem": problem}
        )
        start_virtual(contest, user)

        client = APIClient()
        client.force_authenticate(user=user)
        r = self._submit(client, problem, language, contest.slug)

        assert r.status_code == 201
        assert Attempt.objects.filter(user=user, contest=contest).count() == 1

    def test_muddat_otgach_yuborish_rad_etiladi(self, contest, problem, language, user) -> None:
        from contests.services import start_virtual

        ContestProblem.objects.update_or_create(
            contest=contest, index_letter="A", defaults={"problem": problem}
        )
        reg = start_virtual(contest, user)
        duration = contest.end_at - contest.start_at
        ContestRegistration.objects.filter(pk=reg.pk).update(
            virtual_start_at=timezone.now() - duration - timedelta(minutes=1)
        )

        client = APIClient()
        client.force_authenticate(user=user)
        r = self._submit(client, problem, language, contest.slug)

        assert r.status_code == 400
        assert not Attempt.objects.filter(user=user, contest=contest).exists()

    def test_virtualsiz_tugagan_musobaqaga_yuborib_bolmaydi(
        self, contest, problem, language, user
    ) -> None:
        ContestProblem.objects.update_or_create(
            contest=contest, index_letter="A", defaults={"problem": problem}
        )
        ContestRegistration.objects.get_or_create(contest=contest, user=user)

        client = APIClient()
        client.force_authenticate(user=user)

        assert self._submit(client, problem, language, contest.slug).status_code == 400

    def test_virtual_urinish_rasmiy_jadvalga_kirmaydi(
        self, contest, problem, language, user, other_user
    ) -> None:
        from contests.services import rebuild_standings, start_virtual

        ContestProblem.objects.update_or_create(
            contest=contest, index_letter="A", defaults={"problem": problem}
        )
        submit(other_user, contest, problem, language, Verdict.AC, 10)
        start_virtual(contest, user)
        client = APIClient()
        client.force_authenticate(user=user)
        self._submit(client, problem, language, contest.slug)
        Attempt.objects.filter(user=user, contest=contest).update(verdict=Verdict.AC)

        rebuild_standings(contest)

        assert list(
            Standing.objects.filter(contest=contest).values_list("user__username", flat=True)
        ) == [other_user.username]


@pytest.mark.django_db
class TestIoiJadvali:
    """IOI musobaqasi BALL bo'yicha saralanishi kerak.

    O'lchandi: `scoring_type` tanlanardi va judge qisman ballarni to'g'ri
    hisoblardi, jadval esa uni umuman o'qimasdi — 270 ballik ishtirokchi
    200 ballikdan pastda turardi.
    """

    def _setup(self, contest, problem, language):
        Contest.objects.filter(pk=contest.pk).update(scoring_type=Contest.Scoring.IOI)
        contest.refresh_from_db()
        extra = [
            type(problem).objects.create(
                slug=f"ioi-{i}", title=f"IOI {i}", statement="…", difficulty=1000, is_public=True
            )
            for i in range(2)
        ]
        problems = [problem, *extra]
        for i, p in enumerate(problems):
            ContestProblem.objects.update_or_create(
                contest=contest, index_letter="ABC"[i], defaults={"problem": p}
            )
        return problems

    def _submit(self, user, contest, problem, language, score, verdict, minutes):
        attempt = Attempt.objects.create(
            user=user,
            problem=problem,
            contest=contest,
            language=language,
            source_code="x",
            verdict=verdict,
            score=score,
        )
        Attempt.objects.filter(pk=attempt.pk).update(
            created_at=contest.start_at + timedelta(minutes=minutes)
        )

    def test_qisman_ball_yigindisi_tartibni_belgilaydi(
        self, contest, problem, language, user, other_user
    ) -> None:
        problems = self._setup(contest, problem, language)
        # 3 × 90 = 270, hech biri to'liq emas
        for i, p in enumerate(problems):
            self._submit(user, contest, p, language, 90, "PARTIAL", 10 + i)
        # 2 × 100 = 200, ikkitasi to'liq
        for i, p in enumerate(problems[:2]):
            self._submit(other_user, contest, p, language, 100, Verdict.AC, 10 + i)

        rebuild_standings(contest)

        rows = list(
            Standing.objects.filter(contest=contest)
            .order_by("rank")
            .values_list("user__username", "total_score", "penalty")
        )
        assert rows == [(user.username, 270, 0), (other_user.username, 200, 0)]

    def test_har_masaladan_eng_yaxshisi_olinadi(self, contest, problem, language, user) -> None:
        problems = self._setup(contest, problem, language)
        self._submit(user, contest, problems[0], language, 40, "PARTIAL", 10)
        self._submit(user, contest, problems[0], language, 95, "PARTIAL", 20)
        self._submit(user, contest, problems[0], language, 60, "PARTIAL", 30)

        rebuild_standings(contest)

        assert Standing.objects.get(contest=contest, user=user).total_score == 95

    def test_acm_ozgarmadi(self, contest, problem, language, user, other_user) -> None:
        ContestProblem.objects.update_or_create(
            contest=contest, index_letter="A", defaults={"problem": problem}
        )
        submit(user, contest, problem, language, Verdict.AC, 10)
        submit(other_user, contest, problem, language, Verdict.AC, 30)

        rebuild_standings(contest)

        rows = list(
            Standing.objects.filter(contest=contest)
            .order_by("rank")
            .values_list("user__username", "solved_count", "penalty")
        )
        assert rows == [(user.username, 1, 10), (other_user.username, 1, 30)]


@pytest.mark.django_db
class TestOzQatori:
    """Ommaviy jadval `STANDINGS_TOP` bilan cheklangan — o'z qatori alohida."""

    def _kop_qatnashchi(self, contest: Contest, n: int) -> User:
        users = [User(username=f"q{i}") for i in range(n)]
        User.objects.bulk_create(users)
        rows = User.objects.filter(username__startswith="q").order_by("pk")
        Standing.objects.bulk_create(
            [
                Standing(contest=contest, user=u, rank=i + 1, solved_count=1, penalty=i)
                for i, u in enumerate(rows)
            ]
        )
        return rows[n - 1]

    def test_ommaviy_jadval_cheklangan(self, contest) -> None:
        self._kop_qatnashchi(contest, STANDINGS_TOP + 20)

        body = APIClient().get(reverse("contest-standings", args=[contest.slug])).json()

        assert len(body["results"]) == STANDINGS_TOP

    def test_chegaradan_tashqaridagi_ozini_koradi(self, contest) -> None:
        oxirgi = self._kop_qatnashchi(contest, STANDINGS_TOP + 20)
        c = APIClient()
        c.force_authenticate(user=oxirgi)

        r = c.get(reverse("contest-my-standing", args=[contest.slug]))

        assert r.status_code == 200
        assert r.data["rank"] == STANDINGS_TOP + 20
        assert r.data["username"] == oxirgi.username

    def test_ommaviy_javob_keshlanadigan_qoladi(self, contest) -> None:
        """O'z qatorini umumiy javobga qo'shish CDN keshini yo'q qilardi."""
        self._kop_qatnashchi(contest, 3)

        r = APIClient().get(reverse("contest-standings", args=[contest.slug]))

        assert "public" in r["Cache-Control"]
        assert "Cookie" not in r.get("Vary", "")

    def test_anonim_ololmaydi(self, contest) -> None:
        assert APIClient().get(reverse("contest-my-standing", args=[contest.slug])).status_code in (
            401,
            403,
        )

    def test_qatnashmaganga_404(self, contest, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)

        assert c.get(reverse("contest-my-standing", args=[contest.slug])).status_code == 404
