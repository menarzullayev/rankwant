"""Reyting formulalari — 04-prd 🔒 dagi qiymatlarga qarshi.

DoD: bu sohada qamrov MAJBURIY.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from ratings import formulas

DIFFICULTIES = st.integers(min_value=800, max_value=3500).map(lambda x: x // 100 * 100)


class TestSkills:
    def test_hujjatdagi_qiymatlar(self) -> None:
        """04-prd da e'lon qilingan raqamlar."""
        assert formulas.skills_rating([800] * 500) == 16000
        assert formulas.skills_rating([2500] * 20) == 32076

    def test_chuqurlik_grinddan_ustun(self) -> None:
        grind = formulas.skills_rating([800] * 500)
        depth = formulas.skills_rating([2500] * 20)
        assert depth > grind

    def test_bo_sh(self) -> None:
        assert formulas.skills_rating([]) == 0

    @given(st.lists(DIFFICULTIES, max_size=60), DIFFICULTIES)
    @settings(max_examples=400, deadline=None)
    def test_monoton(self, solved: list[int], extra: int) -> None:
        """Yangi masala yechish reytingni HECH QACHON kamaytirmaydi.

        Bu 04-prd da e'lon qilingan kafolat (ADR-0007 bilan aniqlashtirilgan:
        kafolat foydalanuvchi HARAKATI uchun).
        """
        before = formulas.skills_rating(solved)
        after = formulas.skills_rating([*solved, extra])
        assert after >= before

    @given(st.lists(DIFFICULTIES, min_size=1, max_size=80))
    @settings(max_examples=200, deadline=None)
    def test_yigirma_barobar_chegara(self, solved: list[int]) -> None:
        """Natija eng katta masaladan 20 baravardan oshmaydi."""
        assert formulas.skills_rating(solved) <= max(solved) * 20 + 1

    @given(st.lists(DIFFICULTIES, max_size=40))
    @settings(max_examples=100, deadline=None)
    def test_tartibga_bogliq_emas(self, solved: list[int]) -> None:
        assert formulas.skills_rating(solved) == formulas.skills_rating(list(reversed(solved)))


class TestContestElo:
    def test_seed_yigindisi(self) -> None:
        """Barcha seed'lar yig'indisi ishtirokchilar sonining yarmi + n/2."""
        ratings = [1400, 1500, 1600, 1300]
        seeds = [formulas.seed(r, ratings[:i] + ratings[i + 1 :]) for i, r in enumerate(ratings)]
        # har juftlik uchun P(a>b)+P(b>a)=1 → Σseed = n + n(n-1)/2
        n = len(ratings)
        assert abs(sum(seeds) - (n + n * (n - 1) / 2)) < 1e-6

    def test_inflyatsiya_nolga_teng(self) -> None:
        """Musobaqa umumiy reytingni shishirmaydi."""
        deltas = formulas.contest_deltas([1400, 1500, 1600, 1200], [1, 2, 3, 4])
        assert abs(sum(deltas)) <= 2  # yaxlitlash xatosi

    def test_gholib_yutadi(self) -> None:
        deltas = formulas.contest_deltas([1500, 1500, 1500], [1, 2, 3])
        assert deltas[0] > 0
        assert deltas[-1] < 0

    def test_kutilgan_natija_kam_ozgartiradi(self) -> None:
        """Kuchli ishtirokchi birinchi bo'lsa — o'zgarish kichik."""
        strong = formulas.contest_deltas([2000, 1400, 1300], [1, 2, 3])[0]
        surprise = formulas.contest_deltas([1200, 1400, 1300], [1, 2, 3])[0]
        assert surprise > strong

    def test_yangi_foydalanuvchi_volatilligi(self) -> None:
        few = formulas.contest_deltas([1500, 1500, 1500], [1, 2, 3], [0, 6, 6])
        many = formulas.contest_deltas([1500, 1500, 1500], [1, 2, 3], [6, 6, 6])
        assert abs(few[0]) > abs(many[0])

    def test_quyi_chegara(self) -> None:
        assert formulas.apply_floor(-50) == 0
        assert formulas.apply_floor(120) == 120


class TestActivity:
    def test_maksimal(self) -> None:
        assert formulas.activity_rating(30, 30, 30) == formulas.ACTIVITY_MAX

    def test_streak_chegaralangan(self) -> None:
        assert formulas.activity_rating(0, 0, 100) == 60

    def test_nol(self) -> None:
        assert formulas.activity_rating(0, 0, 0) == 0


class TestDuel:
    def test_teng_raqib(self) -> None:
        assert formulas.duel_delta(1400, 1400, 1.0, 0) == 16  # K=32, E=0.5
        assert formulas.duel_delta(1400, 1400, 0.0, 0) == -16

    def test_k_kamayadi(self) -> None:
        new = abs(formulas.duel_delta(1400, 1400, 1.0, 0))
        old = abs(formulas.duel_delta(1400, 1400, 1.0, 50))
        assert new > old
