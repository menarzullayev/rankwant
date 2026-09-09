"""Test baholash va Qvant mukofoti."""

from __future__ import annotations

from typing import TypedDict

from django.db import transaction

from core.models import User
from quizzes.models import Quiz, QuizAttempt
from qvant import ledger
from qvant.models import QvantTransaction


class ReviewItem(TypedDict):
    question_id: int
    chosen: int | None
    correct: int | None
    is_correct: bool
    explanation: str


def grade(quiz: Quiz, answers: dict[int, int]) -> tuple[int, int, list[ReviewItem]]:
    """Tanlangan javoblarni to'g'ri variant bilan solishtiradi.

    Test SERVERDA baholanadi: to'g'ri javob mijozga hech qachon yuborilmaydi
    (serializer `is_correct` ni bermaydi), aks holda test ma'nosiz.
    """
    review: list[ReviewItem] = []
    score = 0
    items = quiz.items.select_related("question").prefetch_related("question__choices")
    for item in items:
        question = item.question
        correct = question.correct_choice_id
        chosen = answers.get(question.pk)
        ok = chosen is not None and chosen == correct
        if ok:
            score += 1
        review.append(
            {
                "question_id": question.pk,
                "chosen": chosen,
                "correct": correct,
                "is_correct": ok,
                "explanation": question.explanation,
            }
        )
    return score, len(review), review


@transaction.atomic
def submit(user: User, quiz: Quiz, answers: dict[int, int]) -> tuple[QuizAttempt, list[ReviewItem]]:
    score, total, review = grade(quiz, answers)

    # Qvant faqat BIRINCHI yakunlashda — qayta topshirib fermerlik
    # qilib bo'lmaydi (ADR-0002 anti-farm).
    #
    # `QuizAttempt` da uniq cheklov yo'q (qayta topshirish ruxsat etilgan),
    # shuning uchun tekshiruvni hamyon qulfi ushlab turadi. O'lchandi:
    # qulfsiz 6 ta parallel topshirish 25 o'rniga 100 Qvant bergan —
    # va faqat kunlik shift to'xtatgani uchun 150 emas.
    ledger.lock_wallet(user)
    first_time = not QuizAttempt.objects.filter(user=user, quiz=quiz).exists()
    awarded = 0
    if first_time and quiz.reward_qvant and total:
        tx = ledger.credit(
            user,
            quiz.reward_qvant,
            QvantTransaction.Reason.QUIZ,
            ref_type="quiz",
            ref_id=quiz.slug,
        )
        awarded = tx.amount if tx else 0

    attempt = QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        answers={str(k): v for k, v in answers.items()},
        score=score,
        total=total,
        qvant_awarded=awarded,
    )
    return attempt, review
