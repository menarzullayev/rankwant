"""Reference problems — one real problem for each way of grading.

`special`, `interactive` and `scorer` existed in the model and in the judge
and had never graded a single submission: of 2 096 problems on the site,
2 096 used the standard checker (measured 2026-10-07). A path nobody has
walked is a path that breaks at the first contest that needs it, so each
one gets a small, deterministic problem that is installed, published and
submitted to like any other.

They are also the regression suite: `SUBMISSIONS` lists, for each problem,
sources and the verdict and score each must receive. The end-to-end check
(`tools/e2e_evaluation_paths.py`) and the API tests read the same table.

Everything a problem needs is here — statement, tests, the checker or the
interactor, the reference solution — so `install()` is reproducible on an
empty database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: The language the checkers, the interactor and the sample solutions use.
PYTHON = "py313"

# ── special: any two positive integers with the given sum ────────────────────

PAIR_CHECKER = '''"""Checker: two positive integers whose sum is the number in the input.

Called as `checker <input> <output> <answer>`; exit 0 accepts. The jury's
answer is not read: any valid pair is right, which is the point of a
special checker.
"""
import sys

n = int(open(sys.argv[1]).read().split()[0])
tokens = open(sys.argv[2]).read().split()
if len(tokens) != 2:
    sys.exit(1)
try:
    a, b = int(tokens[0]), int(tokens[1])
except ValueError:
    sys.exit(1)
sys.exit(0 if a >= 1 and b >= 1 and a + b == n else 1)
'''

PAIR_REFERENCE = "n = int(input())\nprint(1, n - 1)\n"
#: A different valid answer from the jury's, printed one number per line.
PAIR_OTHER_VALID = "n = int(input())\nprint(n - 1)\nprint(1)\n"
#: Right for an even sum only.
PAIR_WRONG = "n = int(input())\nprint(n // 2, n // 2)\n"

# ── interactive: find the number in at most ten questions ────────────────────

GUESS_LIMIT = 1000
GUESS_QUERIES = 10

GUESS_INTERACTOR = f'''"""Interactor: a number in 1..{GUESS_LIMIT}, {GUESS_QUERIES} questions.

    solver      ? x          a question
    interactor  < | > | =    the number is smaller / larger / equal
    solver      ! x          the answer; the interactor exits 0 if right

The number is not fixed in advance. Every reply keeps the larger half of
what is still possible, so the answer is forced only when one candidate
is left — a solution cannot pass by printing a constant, and binary search
needs every one of its questions. Exit 0 accepts; anything else rejects.
"""
import sys

lo, hi = 1, {GUESS_LIMIT}
asked = 0
for raw in sys.stdin:
    parts = raw.split()
    if not parts:
        continue
    if len(parts) != 2 or parts[0] not in ("?", "!"):
        sys.exit(1)  # not the protocol
    try:
        x = int(parts[1])
    except ValueError:
        sys.exit(1)
    if parts[0] == "!":
        # Right only when nothing else is still possible.
        sys.exit(0 if lo == hi == x else 1)
    asked += 1
    if asked > {GUESS_QUERIES}:
        sys.exit(1)  # too many questions
    if x < lo:
        reply = ">"
    elif x > hi:
        reply = "<"
    elif lo == hi:
        reply = "="
    elif x - lo >= hi - x:
        reply, hi = "<", x - 1
    else:
        reply, lo = ">", x + 1
    print(reply, flush=True)
sys.exit(1)  # the solver stopped without answering
'''

GUESS_REFERENCE = f"""import sys

lo, hi = 1, {GUESS_LIMIT}
while lo < hi:
    mid = (lo + hi + 1) // 2
    print("?", mid, flush=True)
    reply = sys.stdin.readline().strip()
    if reply == "=":
        lo = hi = mid
    elif reply == "<":
        hi = mid - 1
    else:
        lo = mid
print("!", lo, flush=True)
"""
#: Answers without asking: the interactor still has a thousand candidates.
GUESS_BLIND = 'print("! 500", flush=True)\n'
#: Asks one by one and runs out of questions.
GUESS_TOO_MANY = f"""import sys

for x in range(1, {GUESS_LIMIT} + 1):
    print("?", x, flush=True)
    if sys.stdin.readline().strip() == "=":
        print("!", x, flush=True)
        break
"""
#: Does not read the replies and keeps asking long after it was rejected:
#: about 240 KB of questions, more than a pipe holds.
GUESS_FLOOD = f"""for x in range(30000):
    print("?", x % {GUESS_LIMIT} + 1, flush=True)
print("! 1", flush=True)
"""
#: Never flushes: the question stays in its own buffer, both sides wait.
GUESS_NO_FLUSH = 'import sys\n\nsys.stdout.write("? 500\\n")\nsys.stdin.readline()\n'

# ── scorer: pay the amount with as few coins as possible ─────────────────────

COIN_SCORER = '''"""Scorer: pay the amount with coins 1, 5, 10, 25 — fewer coins, more points.

Called as `checker <input> <output> <answer>`; the LAST line printed is the
score, 0 to 100. The jury's answer holds the smallest possible count. An
answer that does not pay the amount exactly scores 0.
"""
import sys

amount = int(open(sys.argv[1]).read().split()[0])
best = int(open(sys.argv[3]).read().split()[0])
try:
    tokens = [int(token) for token in open(sys.argv[2]).read().split()]
except ValueError:
    tokens = []
count = tokens[0] if tokens else 0
coins = tokens[1:]
valid = (
    count >= 1
    and count == len(coins)
    and all(coin in (1, 5, 10, 25) for coin in coins)
    and sum(coins) == amount
)
print(100 * best // count if valid else 0)
'''

_COIN_PAY = """s = int(input())
coins = []
for coin in ({order}):
    while s >= coin:
        coins.append(coin)
        s -= coin
print(len(coins))
print(*coins)
"""
COIN_REFERENCE = _COIN_PAY.format(order="25, 10, 5, 1")
#: Valid, never optimal above 24: it does not know the 25 coin.
COIN_NO_QUARTERS = _COIN_PAY.format(order="10, 5, 1")
#: Valid and the worst there is: ones only.
COIN_ONES = _COIN_PAY.format(order="1,")
#: Not a payment at all.
COIN_INVALID = "print(1)\nprint(25)\n"


def _coins(amount: int) -> str:
    """The jury's answer: the fewest coins, largest first."""
    out: list[int] = []
    for coin in (25, 10, 5, 1):
        while amount >= coin:
            out.append(coin)
            amount -= coin
    return f"{len(out)}\n{' '.join(map(str, out))}\n"


@dataclass(frozen=True)
class Case:
    """One submission and what the judge must return for it."""

    name: str
    source: str
    verdict: str
    score: int


@dataclass(frozen=True)
class Reference:
    slug: str
    title: str
    checker_type: str
    difficulty: int
    statement: str
    input_format: str
    output_format: str
    note: str
    #: `(input, expected, group)`; the first `samples` are shown on the page.
    tests: tuple[tuple[str, str, str], ...]
    samples: int
    reference: str
    checker: str = ""
    interactor: str = ""
    cases: tuple[Case, ...] = field(default_factory=tuple)


PAIR = Reference(
    slug="ref-juftlik-yigindi",
    title="Yig'indisi N bo'lgan juftlik",
    checker_type="special",
    difficulty=800,
    statement=(
        "Butun son $N$ berilgan. Yig'indisi $N$ ga teng bo'lgan ikkita **musbat** butun "
        "sonni toping.\n\nBunday juftliklar bir nechta bo'lishi mumkin — istalgan bittasini "
        "chiqaring. Javobni maxsus tekshiruvchi dastur (checker) tekshiradi, shuning uchun u "
        "namunadagi javob bilan bir xil bo'lishi shart emas."
    ),
    input_format="Yagona qatorda butun son $N$ ($2 \\le N \\le 10^9$).",
    output_format=(
        "Ikkita musbat butun son $a$ va $b$ ($a + b = N$) — probel yoki yangi qator bilan "
        "ajratilgan."
    ),
    note=(
        "Namunada `5 5` ko'rsatilgan, lekin `1 9`, `3 7` va boshqa har qanday to'g'ri juftlik "
        "ham qabul qilinadi."
    ),
    tests=(
        ("10\n", "5 5\n", "sample"),
        ("2\n", "1 1\n", "boundary"),
        ("7\n", "3 4\n", "special"),
        ("999999999\n", "499999999 500000000\n", "random"),
        ("1000000000\n", "500000000 500000000\n", "maximum"),
    ),
    samples=1,
    reference=PAIR_REFERENCE,
    checker=PAIR_CHECKER,
    cases=(
        Case("reference", PAIR_REFERENCE, "AC", 100),
        Case("another valid answer, one number per line", PAIR_OTHER_VALID, "AC", 100),
        Case("wrong for an odd sum", PAIR_WRONG, "WA", 0),
    ),
)

GUESS = Reference(
    slug="ref-sonni-top",
    title="Sonni toping (interaktiv)",
    checker_type="interactive",
    difficulty=1000,
    statement=(
        f"Bu **interaktiv** masala: dasturingiz tekshiruvchi dastur bilan suhbatlashadi.\n\n"
        f"Tekshiruvchi $1$ dan ${GUESS_LIMIT}$ gacha bo'lgan butun sonni o'ylagan. Uni ko'pi bilan "
        f"**{GUESS_QUERIES} ta** savol bilan toping.\n\n"
        "Savol berish uchun `? x` qatorini chiqaring. Javob bitta belgi bo'ladi:\n\n"
        "- `<` — o'ylangan son $x$ dan kichik;\n"
        "- `>` — o'ylangan son $x$ dan katta;\n"
        "- `=` — o'ylangan son $x$ ga teng.\n\n"
        "Javobni topgach `! x` qatorini chiqaring va dasturni tugating.\n\n"
        "**Har bir qatordan keyin chiqishni tozalang (flush)** — aks holda savolingiz "
        "tekshiruvchiga yetib bormaydi va ikkala dastur bir-birini kutib qoladi."
    ),
    input_format=(
        "Boshida hech narsa berilmaydi. Har savoldan keyin bitta qatorda `<`, `>` yoki `=` keladi."
    ),
    output_format="Savollar `? x` ko'rinishida, yakuniy javob `! x` ko'rinishida ($1 \\le x \\le "
    + str(GUESS_LIMIT)
    + "$).",
    note=(
        "Tekshiruvchi sonni oldindan tanlamaydi: u har doim hali mumkin bo'lgan sonlarning "
        "kattaroq qismini qoldiradi. Shuning uchun taxmin bilan topib bo'lmaydi.\n\n"
        "Flush: C++ da `cout << endl` yoki `cout.flush()`, Python'da `print(..., flush=True)`, "
        "Java'da `System.out.flush()`.\n\nNamuna testi shartli: bu masalada kiritma fayli yo'q, "
        "namunadagi son — faqat oraliqning yuqori chegarasi."
    ),
    tests=(
        (f"{GUESS_LIMIT}\n", "interaktiv\n", "sample"),
        ("1\n", "interaktiv\n", "boundary"),
        (f"{GUESS_LIMIT}\n", "interaktiv\n", "maximum"),
    ),
    samples=1,
    reference=GUESS_REFERENCE,
    interactor=GUESS_INTERACTOR,
    cases=(
        Case("reference: binary search", GUESS_REFERENCE, "AC", 100),
        Case("answers without asking", GUESS_BLIND, "WA", 0),
        Case("more than ten questions", GUESS_TOO_MANY, "WA", 0),
        Case("keeps asking after it was rejected", GUESS_FLOOD, "WA", 0),
        Case("never flushes", GUESS_NO_FLUSH, "IDLENESS", 0),
    ),
)

_COIN_AMOUNTS = (
    (30, "sample"),
    (1, "boundary"),
    (41, "special"),
    (99, "random"),
    (10000, "maximum"),
)

COINS = Reference(
    slug="ref-kam-tanga",
    title="Eng kam tanga",
    checker_type="scorer",
    difficulty=1000,
    statement=(
        "$S$ so'mni $1$, $5$, $10$ va $25$ so'mlik tangalar bilan to'lang. Har bir tangadan "
        "istalgancha bor.\n\nBu **baholanadigan** masala: har qanday to'g'ri to'lov qabul "
        "qilinadi, lekin tangalar qancha kam bo'lsa, ball shuncha yuqori. Har test uchun ball "
        "$\\lfloor 100 \\cdot K_{min} / K \\rfloor$, bu yerda $K$ — siz ishlatgan tangalar soni, "
        "$K_{min}$ — eng kam mumkin bo'lgan son. Yakuniy ball — testlar bo'yicha o'rtacha.\n\n"
        "Yig'indisi $S$ ga teng bo'lmagan yoki boshqa tanga ishlatilgan javob $0$ ball oladi."
    ),
    input_format="Yagona qatorda butun son $S$ ($1 \\le S \\le 10^4$).",
    output_format=(
        "Birinchi qatorda tangalar soni $K$. Ikkinchi qatorda $K$ ta son — tangalar qiymatlari."
    ),
    note=(
        "To'liq ball (100) olingandagina masala yechilgan hisoblanadi; undan past ball — «qisman»."
    ),
    tests=tuple((f"{amount}\n", _coins(amount), group) for amount, group in _COIN_AMOUNTS),
    samples=1,
    reference=COIN_REFERENCE,
    checker=COIN_SCORER,
    cases=(
        Case("reference: largest coin first", COIN_REFERENCE, "AC", 100),
        # 30→3 coins (66), 1→1 (100), 41→5 (80), 99→14 (64), 10000→1000 (40): mean 70.
        Case("valid, without the 25 coin", COIN_NO_QUARTERS, "PARTIAL", 70),
        # 30→30 (6), 1→1 (100), 41→41 (9), 99→99 (9), 10000→10000 (4): mean 25.
        Case("valid, ones only", COIN_ONES, "PARTIAL", 25),
        Case("does not pay the amount", COIN_INVALID, "WA", 0),
    ),
)

REFERENCES: tuple[Reference, ...] = (PAIR, GUESS, COINS)


def install(*, publish: bool = True) -> list[Any]:
    """Create or refresh the reference problems. Idempotent.

    A problem is written as a draft first and made public by a second
    `save()`: the public number is assigned there, and the staff rules for
    going public (tests, a hidden test) hold for these problems as for any.
    """
    from core.cache import cache_delete
    from problems import storage
    from problems.evaluation import evaluation_error
    from problems.languages import LANGUAGES, row_values
    from problems.models import Language, Problem, ReferenceSolution, TestCase

    spec = next(item for item in LANGUAGES if item["code"] == PYTHON)
    python, _ = Language.objects.update_or_create(code=PYTHON, defaults=row_values(spec))
    storage.ensure_bucket()

    installed = []
    for ref in REFERENCES:
        problem, _ = Problem.objects.update_or_create(
            slug=ref.slug,
            defaults={
                "title": ref.title,
                "statement": ref.statement,
                "input_format": ref.input_format,
                "output_format": ref.output_format,
                "note": ref.note,
                "difficulty": ref.difficulty,
                "time_limit_ms": 1000,
                "memory_limit_kb": 262144,
                "io_mode": Problem.IoMode.STDIO,
                "checker_type": ref.checker_type,
                "checker_source": ref.checker,
                "checker_language": python if ref.checker else None,
                "interactor_source": ref.interactor,
                "interactor_language": python if ref.interactor else None,
                "partial_scoring": ref.checker_type == Problem.Checker.SCORER,
                "source": "RankWant reference",
            },
        )
        for order, (test_in, test_out, group) in enumerate(ref.tests, start=1):
            TestCase.objects.update_or_create(
                problem=problem,
                order=order,
                defaults={
                    "input_ref": storage.put_test_data(f"tests/{ref.slug}/{order}.in", test_in),
                    "output_ref": storage.put_test_data(f"tests/{ref.slug}/{order}.out", test_out),
                    "is_sample": order <= ref.samples,
                    "group": group,
                },
            )
        problem.tests.filter(order__gt=len(ref.tests)).delete()
        ReferenceSolution.objects.update_or_create(
            problem=problem, defaults={"language": python, "source": ref.reference}
        )
        cache_delete(storage.samples_cache_key(ref.slug))

        error = evaluation_error(problem)
        if error:
            raise RuntimeError(f"{ref.slug}: {error}")
        if publish and not problem.is_public:
            problem.is_public = True
            problem.save()
        installed.append(problem)
    return installed
