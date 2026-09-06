from __future__ import annotations

from django.utils import timezone

from core.models import User
from hackathons.models import Hackathon, HackathonSubmission


class HackathonError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def submit(user: User, hackathon: Hackathon, **fields: object) -> HackathonSubmission:
    """Muddatgacha qayta topshirish mumkin — oxirgisi hisobga olinadi."""
    if not hackathon.accepts_submissions:
        raise HackathonError("closed", "Topshirish muddati ochiq emas")
    entry, _ = HackathonSubmission.objects.update_or_create(
        hackathon=hackathon, user=user, defaults=fields
    )
    return entry


def score(judge: User, entry: HackathonSubmission, value: int, feedback: str = "") -> None:
    if not judge.is_staff:
        raise HackathonError("forbidden", "Faqat hakam baholaydi")
    if not 0 <= value <= 100:
        raise HackathonError("range", "Ball 0–100 oralig'ida")
    entry.score = value
    entry.feedback = feedback
    entry.scored_by = judge
    entry.scored_at = timezone.now()
    entry.save(update_fields=["score", "feedback", "scored_by", "scored_at"])

    from notifications.models import Notification
    from notifications.services import notify

    notify(
        entry.user,
        Notification.Kind.SYSTEM,
        f"Hakaton bahosi: {value}/100",
        body=feedback[:200],
        ref_type="hackathon",
        ref_id=entry.hackathon.slug,
    )
