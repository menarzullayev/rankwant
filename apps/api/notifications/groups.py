"""Notification groups — what a person switches on and off (decision 2026-11-16).

A stored row still carries the coarse `Notification.Kind` (eight values, used by
the feed filter chips). The SETTINGS are finer: every `code` belongs to one of
fourteen groups, and a person chooses site / Telegram / email per group.

Two lookups, in this order, so nothing already saved is lost:

1. `notify_prefs[group]` — what the settings page writes now;
2. `notify_prefs[kind]` — what it wrote before groups existed (and what an
   old unsubscribe link names).

Rules kept here, in one place:

* a code that is not listed falls back to the group of its kind
  (`KIND_GROUP`), so a new call site cannot silently lose its settings;
* `MANDATORY` channels cannot be switched off — account security is the only
  group with one (site; email and Telegram stay the person's choice);
* `DORMANT` codes exist in the catalogue (a code can never be removed:
  `tools/check_notification_codes.py`) but nothing sends them yet — the
  feature behind them is not built. A group whose codes are all dormant is
  hidden from the settings page, so the page never promises what does not exist.
"""

from __future__ import annotations

GROUPS: tuple[str, ...] = (
    "security",
    "contest",
    "new_contests",
    "hosting",
    "moderation",
    "class",
    "my_class",
    "tests",
    "streak",
    "my_content",
    "competition",
    "community",
    "plan_limits",
    "team_prizes",
)

#: Channels a group never lets a person switch off.
MANDATORY: dict[str, frozenset[str]] = {"security": frozenset({"site"})}

#: The group of the pre-group kinds — the fallback for an unlisted code.
KIND_GROUP: dict[str, str] = {
    "rating_changed": "contest",
    "problem_rerated": "tests",
    "contest_result": "contest",
    "quest_awarded": "streak",
    "streak_milestone": "streak",
    "duel": "competition",
    "hack": "competition",
    "system": "community",
}

CODE_GROUP: dict[str, str] = {
    # account security
    "security_new_device": "security",
    "security_password_changed": "security",
    "security_password_reset": "security",
    "security_email_changed": "security",
    "security_telegram_linked": "security",
    "security_deletion_scheduled": "security",
    "security_deletion_cancelled": "security",
    # contests, as a participant
    "contest_announcement": "contest",
    "contest_answer": "contest",
    "contest_result": "contest",
    "contest_disqualified": "contest",
    "contest_starts_in_day": "contest",
    "contest_starts_in_hour": "contest",
    "contest_standing_changed": "contest",
    "contest_rating_reverted": "contest",
    "contest_invited": "contest",
    "contest_new": "new_contests",
    # contests, as the host
    "contest_question": "hosting",
    "host_contest_starts_in_hour": "hosting",
    "host_contest_ended": "hosting",
    "host_moderator_answered": "hosting",
    "host_plagiarism_found": "hosting",
    # moderation
    "contest_tester": "moderation",
    "contest_moderator_invited": "moderation",
    "contest_moderator_removed": "moderation",
    # classes
    "classroom_join_approved": "class",
    "classroom_join_rejected": "class",
    "class_invited": "class",
    "class_invite_cancelled": "class",
    "classroom_join_requested": "my_class",
    "my_class_invite_accepted": "my_class",
    "my_class_invite_declined": "my_class",
    "my_class_student_left": "my_class",
    # tests and attempts
    "problem_rerated": "tests",
    "quiz_invited": "tests",
    "attempt_verdict_changed": "tests",
    # streak
    "streak": "streak",
    "streak_at_risk": "streak",
    "streak_broken": "streak",
    # my content and reports
    "report_on_my_content": "my_content",
    "report_reviewed": "my_content",
    "report_resolved": "my_content",
    "problem_archived": "my_content",
    "quiz_published": "my_content",
    "problem_review_requested": "my_content",
    # competition
    "duel_accepted": "competition",
    "duel_cancelled": "competition",
    "duel_draw": "competition",
    "duel_lost": "competition",
    "duel_won": "competition",
    "hack_crashed": "competition",
    "hack_failed": "competition",
    "hack_ignored": "competition",
    "hack_invalid": "competition",
    "hack_received": "competition",
    "hack_succeeded": "competition",
    "hackathon_scored": "competition",
    # community, coaching, courses
    "blog_entry": "community",
    "comment_mention": "community",
    "comment_reply": "community",
    "coach_accepted": "community",
    "coach_declined": "community",
    "coach_recommended": "community",
    "coach_requested": "community",
    "course_published": "community",
    "course_returned": "community",
    "course_review_requested": "community",
    # plan and limits
    "tutor_budget": "plan_limits",
    "plan_ending": "plan_limits",
    "plan_ended": "plan_limits",
    "plan_activated": "plan_limits",
    "judge_access_ending": "plan_limits",
    "judge_access_ended": "plan_limits",
    "judge_limit_reached": "plan_limits",
    # teams and prizes
    "contest_prize": "team_prizes",
    "team_invited": "team_prizes",
    "team_invite_answered": "team_prizes",
    "team_captain": "team_prizes",
    "team_invite_cancelled": "team_prizes",
}

#: In the catalogue, sent by nothing yet — the feature does not exist.
DORMANT: frozenset[str] = frozenset(
    {
        "contest_prize",
        "plan_ending",
        "plan_ended",
        "plan_activated",
        "judge_access_ending",
        "judge_access_ended",
        "judge_limit_reached",
        "team_invited",
        "team_invite_answered",
        "team_captain",
        "team_invite_cancelled",
    }
)


def group_of(code: str, kind: str) -> str:
    """The settings group of a notification: by its code, else by its kind."""
    return CODE_GROUP.get(code) or KIND_GROUP.get(kind, "community")


def visible_groups() -> tuple[str, ...]:
    """Groups with at least one code something sends — the settings page lists these."""
    live = {group for code, group in CODE_GROUP.items() if code not in DORMANT}
    return tuple(g for g in GROUPS if g in live)


def preference_keys() -> frozenset[str]:
    """Every key `notify_prefs` may hold: a group, or a pre-group kind."""
    return frozenset(GROUPS) | frozenset(KIND_GROUP)
