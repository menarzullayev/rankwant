"""20 verdict kodi — 08-technical-spec 🔒."""

from __future__ import annotations

from django.db import models


class Verdict(models.TextChoices):
    PENDING = "PENDING", "Navbatda"
    RUNNING = "RUNNING", "Tekshirilmoqda"
    AC = "AC", "Accepted"
    WA = "WA", "Wrong Answer"
    TLE = "TLE", "Time Limit Exceeded"
    MLE = "MLE", "Memory Limit Exceeded"
    OLE = "OLE", "Output Limit Exceeded"
    RE = "RE", "Runtime Error"
    CE = "CE", "Compilation Error"
    PE = "PE", "Presentation Error"
    PARTIAL = "PARTIAL", "Qisman ball"
    IE = "IE", "Internal Error"
    SKIPPED = "SKIPPED", "O'tkazib yuborildi"
    COMPILE_TIMEOUT = "COMPILE_TIMEOUT", "Kompilyatsiya cho'zildi"
    IDLENESS = "IDLENESS", "Idleness Limit Exceeded"
    SECURITY_VIOLATION = "SECURITY_VIOLATION", "Xavfsizlik qoidasi buzildi"
    CHECKER_ERROR = "CHECKER_ERROR", "Checker xatosi"
    TESTING_ABORTED = "TESTING_ABORTED", "Tekshiruv bekor qilindi"
    RATE_LIMITED = "RATE_LIMITED", "Submit limiti"
    DENIAL_OF_JUDGEMENT = "DENIAL_OF_JUDGEMENT", "Infra nosozligi"


TERMINAL = frozenset(v for v in Verdict.values if v not in {Verdict.PENDING, Verdict.RUNNING})

#: Bu verdict SECURITY alert chiqaradi — 10-operations § monitoring.
ALERTING = frozenset({Verdict.SECURITY_VIOLATION})
