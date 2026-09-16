"""Hack oqimining uchdan-uchiga sinovi — HAQIQIY judge bilan.

Ishga tushirish va nima tekshirilishi: `tests/hack/README.md`.

    docker compose -p rwhack exec -T api python manage.py shell < tests/hack/flow.py

Skript `manage.py shell` ichida bajariladi, ya'ni ORM to'g'ridan-to'g'ri
ishlatiladi. Natijalarni WORKER yozadi (`judging.drain_results` beat orqali
har 2 soniyada), shuning uchun har qadam bazani pollab kutadi.
"""

import os
import sys
import time

from django.db.models import F
from django.utils import timezone

from core.models import User
from hacks.models import Hack
from hacks.services import submit
from judging.models import Attempt
from judging.services import enqueue
from judging.verdicts import Verdict
from problems import storage
from problems.models import (
    Language,
    Problem,
    ReferenceSolution,
    TestCase,
    Validator,
)
from qvant.models import QvantTransaction
from ratings.models import UserSolvedProblem

SLUG = "e2e-hack"
CPP = ["g++", "-std=c++23", "-O2", "-o", "{bin}", "{src}"]

#: To'g'ri yechim — javob 64 bitda hisoblanadi.
REFERENCE = """#include <cstdio>
int main(){long long a,b;scanf("%lld %lld",&a,&b);printf("%lld\\n",a+b);return 0;}
"""

#: Himoyachining yechimi: o'qishi to'g'ri, YIG'INDISI 32 bitda. Muallif
#: testida (2+3) to'g'ri javob beradi, katta sonlarda esa to'lib ketadi —
#: hack aynan shu chekka holatni topishi kerak.
DEFENDER = """#include <cstdio>
int main(){long long a,b;scanf("%lld %lld",&a,&b);int s=a+b;printf("%d\\n",s);return 0;}
"""

#: Kirish validatori: ikkita son va chegara. Nolga teng bo'lmagan chiqish
#: kodi — kiritma yaroqsiz, sababi stderr'da (protocol.md § «Kirish
#: validatori»).
VALIDATOR = """#include <cstdio>
int main(){
  long long a,b;
  if(scanf("%lld %lld",&a,&b)!=2){fprintf(stderr,"ikkita butun son kerak\\n");return 1;}
  if(a<1||a>1000000000000LL||b<1||b>1000000000000LL){
    fprintf(stderr,"son 1..10^12 oraligida bolishi kerak\\n");return 1;}
  return 0;
}
"""


def step(text: str) -> None:
    print(f"\n=== {text}", flush=True)


def fail(text: str) -> None:
    print(f"\nE2E YIQILDI: {text}", flush=True)
    sys.exit(1)


def wait_for(check, what: str, timeout: int = 240):
    """Fon ishini kutadi — natijani worker `drain_results` orqali yozadi."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = check()
        if value is not None:
            return value
        time.sleep(2)
    fail(f"kutish tugadi — {what}")


def hack_status(pk: int):
    """Hack yakunlangan bo'lsa holatini, aks holda `None` qaytaradi."""
    status = Hack.objects.values_list("status", flat=True).get(pk=pk)
    return None if status == Hack.Status.TESTING else status


# Skript ommaviy masala yaratadi, ya'ni uni to'la bazada ishlatish arxivga
# begona yozuv qo'shadi. `tests/chaos` dagi bilan bir xil himoya.
if (
    Problem.objects.exclude(slug=SLUG).count() > 50
    and os.environ.get("RANKWANT_E2E_FORCE") != "yes"
):
    fail(
        "baza to'la ko'rinadi — bu skript izolyatsiyalangan stack uchun. "
        "Baribir ishlatmoqchi bo'lsangiz: RANKWANT_E2E_FORCE=yes"
    )

step("tozalash")
Problem.objects.filter(slug=SLUG).delete()
User.objects.filter(username__startswith="e2e_").delete()

step("til, masala, testlar")
language, _ = Language.objects.get_or_create(
    code="cpp23",
    defaults={
        "name": "C++",
        "version": "23",
        "compile_cmd": CPP,
        "run_cmd": ["{bin}"],
    },
)
problem = Problem.objects.create(
    slug=SLUG,
    title="E2E: ikki sonning yigindisi",
    statement="a va b ni qo'shing (1 <= a, b <= 10^12)",
    difficulty=800,
    is_public=True,
    time_limit_ms=2000,
    memory_limit_kb=262144,
)
storage.ensure_bucket()
TestCase.objects.create(
    problem=problem,
    order=1,
    input_ref=storage.put_test_data(f"tests/{SLUG}/1.in", "2 3\n"),
    output_ref=storage.put_test_data(f"tests/{SLUG}/1.out", "5\n"),
)
Validator.objects.create(problem=problem, language=language, source=VALIDATOR)
ReferenceSolution.objects.create(problem=problem, language=language, source=REFERENCE)
print(f"masala #{problem.pk}, testlar: {problem.tests.count()}")

step("himoyachining yechimi — haqiqiy judge")
defender = User.objects.create_user(username="e2e_defender", password="Parol!12345")
hacker = User.objects.create_user(username="e2e_hacker", password="Parol!12345")
attempt = Attempt.objects.create(
    user=defender,
    problem=problem,
    language=language,
    source_code=DEFENDER,
    verdict=Verdict.PENDING,
)
enqueue(attempt)
verdict = wait_for(
    lambda: (
        None
        if Attempt.objects.values_list("verdict", flat=True).get(pk=attempt.pk)
        in (Verdict.PENDING, Verdict.RUNNING)
        else Attempt.objects.values_list("verdict", flat=True).get(pk=attempt.pk)
    ),
    "himoyachining verdikti",
)
print(f"verdikt: {verdict}")
if verdict != Verdict.AC:
    fail(f"himoyachi AC olishi kerak edi, oldi: {verdict}")
# Verdiktni WORKER yozdi, bu yerdagi obyekt esa hali `PENDING` — usiz
# `submit` «faqat qabul qilingan yechim hack qilinadi» deb rad etadi.
attempt.refresh_from_db()

step("hacker ham masalani yechgan deb belgilanadi")
UserSolvedProblem.objects.get_or_create(
    user=hacker, problem=problem, defaults={"difficulty_at_solve": problem.difficulty}
)
# Hisoblagich qatorlar bilan mos turishi SHART: hack `AC` ni bekor
# qilganda uni kamaytiradi.
Problem.objects.filter(pk=problem.pk).update(solved_count=F("solved_count") + 1)

step("1-hack: YAROQSIZ kiritma — validator rad etishi kerak")
bad = submit(hacker, attempt, raw_input="-5 3\n")
status = wait_for(lambda: hack_status(bad.pk), "yaroqsiz kiritma natijasi")
bad.refresh_from_db()
print(f"holat: {status} · sabab: {bad.detail.strip()[:120]}")
if status != Hack.Status.INVALID_INPUT:
    fail(f"INVALID_INPUT kutilgan edi, keldi: {status}")
if bad.points != 0:
    fail("yaroqsiz kiritma JAZOLANMASLIGI kerak (ADR-0020, 3-qaror)")
# Sabab validatorning O'ZINIKI bo'lishi kerak: sandbox jurnali bu yerga
# tushsa, foydalanuvchi nsjail ichki xabarini o'qirdi.
if "oraligida" not in bad.detail:
    fail(f"validator xabari yetib kelmadi: {bad.detail[:200]}")

step("2-hack: to'g'ri kiritma, 32 bitni to'ldiradi")
good = submit(hacker, attempt, raw_input="3000000000 3000000000\n")
status = wait_for(lambda: hack_status(good.pk), "hack natijasi")
good.refresh_from_db()
attempt.refresh_from_db()
print(f"holat: {status} · himoyachi verdikti: {good.defender_verdict}")

if status != Hack.Status.SUCCESSFUL:
    fail(f"SUCCESSFUL kutilgan edi, keldi: {status} ({good.detail[:200]})")
if attempt.verdict != Verdict.HACKED:
    fail(f"urinish HACKED bo'lishi kerak edi: {attempt.verdict}")
if not TestCase.objects.filter(problem=problem, origin=TestCase.Origin.HACK).exists():
    fail("hack testi masalaga qo'shilmadi")
if UserSolvedProblem.objects.filter(user=defender, problem=problem).exists():
    fail("himoyachining yechgan masalasi bekor qilinmadi")
if not QvantTransaction.objects.filter(
    user=hacker, reason=QvantTransaction.Reason.HACK
).exists():
    fail("amaliyot mukofoti ledgerga yozilmadi (ADR-0002)")

step("natija")
print(f"  hack #{good.pk}: {good.status}, ball {good.points}")
print(f"  urinish #{attempt.pk}: {attempt.verdict}")
print(f"  masaladagi testlar: {problem.tests.count()} (hack testi bilan)")
print(f"  yakunlandi: {timezone.now():%H:%M:%S}")
print("\nE2E: OK", flush=True)
