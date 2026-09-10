"""Testlar (P2-6) — baholash serverda, Qvant faqat birinchi marta."""

from __future__ import annotations

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from quizzes.models import Choice, Question, Quiz, QuizQuestion
from quizzes.services import grade
from qvant import ledger


@pytest.fixture
def quiz(db) -> Quiz:
    q = Quiz.objects.create(slug="asoslar", title="Asoslar", is_published=True, reward_qvant=10)
    for i in range(2):
        question = Question.objects.create(text=f"Savol {i}")
        Choice.objects.create(question=question, order=1, text="to'g'ri", is_correct=True)
        Choice.objects.create(question=question, order=2, text="noto'g'ri")
        QuizQuestion.objects.create(quiz=q, question=question, order=i + 1)
    return q


def _correct_answers(quiz: Quiz) -> dict[str, int]:
    return {
        str(item.question_id): item.question.choices.get(is_correct=True).pk
        for item in quiz.items.select_related("question")
    }


@pytest.mark.django_db
class TestQuiz:
    def test_togri_javob_mijozga_berilmaydi(self, quiz) -> None:
        body = APIClient().get(reverse("quiz-detail", args=[quiz.slug])).json()
        assert body["question_count"] == 2
        for question in body["questions"]:
            for choice in question["choices"]:
                assert "is_correct" not in choice

    def test_baholash_va_qvant(self, user, quiz) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(
            reverse("quiz-submit", args=[quiz.slug]),
            {"answers": _correct_answers(quiz)},
            format="json",
        )
        assert r.status_code == 201
        assert (r.json()["score"], r.json()["total"]) == (2, 2)
        assert r.json()["qvant_awarded"] == 10
        assert ledger.get_wallet(user).balance == 10
        assert all(item["is_correct"] for item in r.json()["review"])

    def test_qayta_topshirish_qvant_bermaydi(self, user, quiz) -> None:
        """ADR-0002 anti-farm: ikkinchi marta 0 Qvant."""
        c = APIClient()
        c.force_authenticate(user=user)
        url = reverse("quiz-submit", args=[quiz.slug])
        c.post(url, {"answers": _correct_answers(quiz)}, format="json")
        r = c.post(url, {"answers": _correct_answers(quiz)}, format="json")
        assert r.json()["qvant_awarded"] == 0
        assert ledger.get_wallet(user).balance == 10

    def test_notogri_javob_tushuntirish_bilan(self, user, quiz) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.post(reverse("quiz-submit", args=[quiz.slug]), {"answers": {}}, format="json")
        assert r.json()["score"] == 0
        assert r.json()["review"][0]["correct"] is not None

    def test_eng_yaxshi_natija_royxatda(self, user, quiz) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        c.post(reverse("quiz-submit", args=[quiz.slug]), {"answers": {}}, format="json")
        c.post(
            reverse("quiz-submit", args=[quiz.slug]),
            {"answers": _correct_answers(quiz)},
            format="json",
        )
        body = c.get(reverse("quiz-list")).json()
        assert body["results"][0]["best_score"] == 2

    def test_chop_etilmagan_korinmaydi(self, quiz) -> None:
        quiz.is_published = False
        quiz.save()
        assert APIClient().get(reverse("quiz-list")).json()["count"] == 0


@pytest.mark.django_db(transaction=True)
def test_parallel_topshirishda_mukofot_bir_marta(user, quiz) -> None:
    """`exists()` bilan `credit()` orasidagi oyna — o'lchandi.

    Olti parallel topshirish 25 lik mukofotni to'rt marta bergan (100
    Qvant), va faqat kunlik shift uchinchi-to'rtinchisidan keyin
    to'xtatgani uchun undan ham ko'p emas.
    """
    import threading

    from django.db import connection, connections

    from quizzes.services import submit

    if connection.vendor != "postgresql":
        pytest.skip("qulf semantikasi faqat Postgres'da tekshiriladi")

    answers = {int(k): v for k, v in _correct_answers(quiz).items()}
    barrier = threading.Barrier(6)

    def send():
        try:
            barrier.wait()
            submit(user, quiz, answers)
        finally:
            connections.close_all()

    threads = [threading.Thread(target=send) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert ledger.get_wallet(user).balance == quiz.reward_qvant


@pytest.mark.django_db
class TestBaholashSorovSoni:
    def test_savol_soni_bilan_osmaydi(self) -> None:
        """`correct_choice_id` dagi `filter()` prefetch keshini chetlab
        o'tib, har savol uchun alohida so'rov berardi."""

        def yasa(slug: str, savollar: int) -> Quiz:
            q = Quiz.objects.create(slug=slug, title=slug, is_published=True)
            for i in range(savollar):
                savol = Question.objects.create(text=f"s{i}", explanation="")
                for j in range(4):
                    Choice.objects.create(
                        question=savol, order=j, text=f"v{j}", is_correct=(j == 0)
                    )
                QuizQuestion.objects.create(quiz=q, question=savol, order=i)
            return q

        kichik, katta = yasa("kichik", 2), yasa("katta", 20)
        grade(kichik, {})

        with CaptureQueriesContext(connection) as a:
            grade(kichik, {})
        with CaptureQueriesContext(connection) as b:
            grade(katta, {})

        assert len(b) == len(a), (
            f"2 savolda {len(a)}, 20 savolda {len(b)} so'rov — "
            "to'g'ri variant har savol uchun alohida olinyapti"
        )

    def test_togri_variant_hali_ham_topiladi(self) -> None:
        savol = Question.objects.create(text="s", explanation="")
        Choice.objects.create(question=savol, order=0, text="a", is_correct=False)
        togri = Choice.objects.create(question=savol, order=1, text="b", is_correct=True)

        assert savol.correct_choice_id == togri.pk
