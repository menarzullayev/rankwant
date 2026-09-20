"""Contest-scale seed data — 30K participants, 122K attempts.

Usage:
    python manage.py seed_contest_scale --contest <slug> --dry-run
    python manage.py seed_contest_scale --contest <slug>
    python manage.py seed_contest_scale --contest <slug> --rebuild-standings
    python manage.py seed_contest_scale --contest <slug> --purge

Why: `Standing` is materialised precisely because live computation breaks
under contest load, and the standings path has never been exercised at
contest scale (measured 2026-09-20: 0 registrations, 0 standings in the
live DB). Invented numbers would be worthless here — the *load shape* is
what the test measures — so every distribution below is taken from a real
Codeforces contest, Div. 3 #1996 (Codeforces Round 962), measured
2026-09-20 through the public API:

    in-window submissions   122,242      (2.5 h, 150 minutes)
    distinct participants    27,685
    peak                       4,568/min  = 76.1/s  (minute 2)
    mean per participant         4.42     (median 4, p95 9, max 36)
    verdicts                 OK 59.8% / TLE 15.5% / WA 13.5% / CE 3.5%
    languages                C++ 84.6% / Java 5.1% / PyPy 4.1% / Py 3.9%

Caveat on the source: `contest.status` returns practice and virtual
submissions too (294,656 rows for that contest), so the profile is filtered
to `startTimeSeconds <= t <= startTimeSeconds + durationSeconds`. The
per-minute histogram has a 60-minute artefact (minutes 10, 70, 130 dip to
roughly half of their neighbours) — it is reproduced as measured rather
than smoothed, because smoothing it would hide a property of the source.

The participant pool defaults to the imported Codeforces rows (`email=""`),
which is what makes the seeded contest look like the real one: real handles,
real ratings (participants average 1,332 vs 1,015 for the whole rated
population, both measured).

`Attempt.created_at` is `auto_now_add`, and `bulk_create` still calls
`pre_save()`, so the field overwrites any value we pass. The contest window
is the whole point of this seed, so the flag is temporarily cleared around
the insert — see `_explicit_timestamps`.
"""

from __future__ import annotations

import random
from argparse import ArgumentParser
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Min
from django.utils import timezone

from contests.models import Contest, ContestProblem, ContestRegistration, Standing
from core.models import User
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Language, Problem

#: Per-minute submission counts, Codeforces Div. 3 #1996 (150 minutes).
#: Index 0 is the first minute. Peak is index 2 (4,568/min = 76.1/s).
PROFILE_MINUTES: tuple[int, ...] = (
    83,
    3578,
    4568,
    3434,
    2918,
    2466,
    2157,
    2012,
    1826,
    1364,
    636,
    1190,
    2204,
    1887,
    1529,
    1447,
    1247,
    1296,
    1321,
    1226,
    1195,
    1068,
    1104,
    1059,
    1084,
    1063,
    1033,
    1061,
    1030,
    1038,
    964,
    986,
    958,
    1021,
    953,
    914,
    966,
    889,
    895,
    894,
    859,
    868,
    839,
    801,
    844,
    805,
    859,
    774,
    815,
    820,
    802,
    738,
    729,
    712,
    743,
    747,
    739,
    747,
    692,
    647,
    685,
    642,
    651,
    695,
    700,
    637,
    648,
    656,
    665,
    451,
    329,
    766,
    748,
    655,
    590,
    641,
    634,
    579,
    595,
    623,
    576,
    548,
    596,
    564,
    529,
    485,
    565,
    521,
    484,
    553,
    566,
    515,
    494,
    526,
    525,
    522,
    540,
    505,
    481,
    514,
    500,
    463,
    474,
    477,
    527,
    511,
    496,
    507,
    500,
    512,
    495,
    501,
    463,
    495,
    452,
    442,
    479,
    460,
    476,
    508,
    458,
    467,
    481,
    429,
    479,
    474,
    460,
    461,
    485,
    386,
    313,
    584,
    526,
    548,
    522,
    534,
    410,
    564,
    512,
    520,
    499,
    473,
    534,
    517,
    520,
    545,
    496,
    559,
    566,
    839,
)

#: Attempts per participant (measured), and how many participants had each.
#: Only the 1..12 buckets are modelled; the ~251 longer tails carry well
#: under 1% of the attempts.
PROFILE_USER_COUNTS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
PROFILE_USER_WEIGHTS: tuple[int, ...] = (
    2504,
    3432,
    5067,
    5138,
    3978,
    2979,
    1821,
    1101,
    649,
    401,
    232,
    132,
)

#: Verdict mix (measured). SKIPPED and CHALLENGED are Codeforces-only
#: states with no RankWant equivalent, so their share is dropped and the
#: rest is normalised by `random.choices`.
PROFILE_VERDICTS: tuple[str, ...] = (
    Verdict.AC,
    Verdict.TLE,
    Verdict.WA,
    Verdict.CE,
    Verdict.RE,
    Verdict.MLE,
)
PROFILE_VERDICT_WEIGHTS: tuple[float, ...] = (59.8, 15.5, 13.5, 3.5, 3.0, 2.7)

#: RankWant language code → measured Codeforces share. CF's four C++ rows
#: collapse into `cpp23` and its two Java rows into `java21`, because
#: RankWant ships one image per family; the *share* is what the load test
#: cares about, not which compiler version produced it.
PROFILE_LANGUAGES: tuple[tuple[str, float], ...] = (
    ("cpp23", 84.6),
    ("java21", 5.1),
    ("pypy73", 4.1),
    ("py313", 3.9),
    ("c17", 1.6),
    ("rust185", 0.7),
)

#: Problem index → share of attempts (measured). A is attempted most
#: often and G barely at all; a flat split would put 14x too much load on
#: the hardest problem's test data.
PROFILE_PROBLEM_WEIGHTS: tuple[float, ...] = (26.5, 25.7, 27.3, 8.7, 6.4, 4.6, 0.7)

#: Realistic sources. Size matters here: `source_code` is the largest
#: column on `Attempt`, so 122K attempts of ~1 KB is ~115 MB of payload
#: where 200-byte stubs would be 24 MB — a 5x difference in the one column
#: that dominates insert volume and the submission-detail response.
#: These produce 781-1,091 bytes, measured after seeding.
SOURCE_TEMPLATES: tuple[str, ...] = (
    "\n".join(
        [
            "// Problem: sum of an array, fast I/O, 1-indexed prefix sums.",
            "#include <bits/stdc++.h>",
            "using namespace std;",
            "using ll = long long;",
            "",
            "static inline ll readInt() {",
            "    ll x = 0; int sign = 1; char c = getchar();",
            "    while (c < '0' || c > '9') { if (c == '-') sign = -1; c = getchar(); }",
            "    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }",
            "    return x * sign;",
            "}",
            "",
            "static inline void writeInt(ll x) {",
            "    if (x < 0) { putchar('-'); x = -x; }",
            "    if (x > 9) writeInt(x / 10);",
            "    putchar(char('0' + x % 10));",
            "}",
            "",
            "int main() {",
            "    ios::sync_with_stdio(false);",
            "    cin.tie(nullptr);",
            "    int n = int(readInt());",
            "    vector<ll> pref(n + 1, 0);",
            "    for (int i = 1; i <= n; ++i) pref[i] = pref[i - 1] + readInt();",
            "    writeInt(pref[n]);",
            "    putchar('\\n');",
            "    return 0;",
            "}",
        ]
    ),
    "\n".join(
        [
            "// Problem: count pairs with a given sum, two pointers over sorted input.",
            "#include <bits/stdc++.h>",
            "using namespace std;",
            "using ll = long long;",
            "",
            "template <typename T>",
            "vector<T> readVec(int n) {",
            "    vector<T> v(n);",
            "    for (auto& x : v) cin >> x;",
            "    return v;",
            "}",
            "",
            "ll countPairs(vector<ll>& a, ll target) {",
            "    sort(a.begin(), a.end());",
            "    ll total = 0;",
            "    size_t lo = 0, hi = a.size();",
            "    while (lo < hi) {",
            "        if (a[lo] + a[hi - 1] == target) {",
            "            ll left = 1, right = 1;",
            "            ll value = a[lo];",
            "            while (lo + 1 < hi && a[lo + 1] == value) { ++lo; ++left; }",
            "            value = a[hi - 1];",
            "            while (hi - 2 > lo && a[hi - 2] == value) { --hi; ++right; }",
            "            total += left * right;",
            "            ++lo; --hi;",
            "        } else if (a[lo] + a[hi - 1] < target) {",
            "            ++lo;",
            "        } else {",
            "            --hi;",
            "        }",
            "    }",
            "    return total;",
            "}",
            "",
            "int main() {",
            "    ios::sync_with_stdio(false);",
            "    cin.tie(nullptr);",
            "    int n; ll target;",
            "    cin >> n >> target;",
            "    auto a = readVec<ll>(n);",
            "    cout << countPairs(a, target) << '\\n';",
            "    return 0;",
            "}",
        ]
    ),
    "\n".join(
        [
            "# Problem: shortest path on an unweighted grid (BFS).",
            "import sys",
            "from collections import deque",
            "",
            "input = sys.stdin.readline",
            "DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))",
            "",
            "",
            "def bfs(grid, start, goal):",
            "    rows, cols = len(grid), len(grid[0])",
            "    dist = [[-1] * cols for _ in range(rows)]",
            "    queue = deque([start])",
            "    dist[start[0]][start[1]] = 0",
            "    while queue:",
            "        r, c = queue.popleft()",
            "        if (r, c) == goal:",
            "            return dist[r][c]",
            "        for dr, dc in DIRS:",
            "            nr, nc = r + dr, c + dc",
            "            if not (0 <= nr < rows and 0 <= nc < cols):",
            "                continue",
            "            if grid[nr][nc] == '#' or dist[nr][nc] != -1:",
            "                continue",
            "            dist[nr][nc] = dist[r][c] + 1",
            "            queue.append((nr, nc))",
            "    return -1",
            "",
            "",
            "def main():",
            "    rows, cols = map(int, input().split())",
            "    grid = [input().strip() for _ in range(rows)]",
            "    print(bfs(grid, (0, 0), (rows - 1, cols - 1)))",
            "",
            "",
            "main()",
        ]
    ),
    "\n".join(
        [
            "// Problem: range sum queries over a static array (sparse table).",
            "import java.io.*;",
            "import java.util.*;",
            "",
            "public class Main {",
            "    static int[] readInts(BufferedReader in) throws IOException {",
            "        StringTokenizer st = new StringTokenizer(in.readLine());",
            "        int[] out = new int[st.countTokens()];",
            "        for (int i = 0; i < out.length; i++)",
            "            out[i] = Integer.parseInt(st.nextToken());",
            "        return out;",
            "    }",
            "",
            "    public static void main(String[] args) throws IOException {",
            "        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));",
            "        StringBuilder sb = new StringBuilder();",
            "        int[] head = readInts(in);",
            "        int n = head[0], q = head[1];",
            "        int[] a = readInts(in);",
            "        long[] prefix = new long[n + 1];",
            "        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];",
            "        for (int i = 0; i < q; i++) {",
            "            int[] range = readInts(in);",
            "            sb.append(prefix[range[1]] - prefix[range[0] - 1]).append('\\n');",
            "        }",
            "        System.out.print(sb);",
            "    }",
            "}",
        ]
    ),
)

BATCH = 2000


@contextmanager
def _explicit_timestamps(*field_names: str) -> Iterator[None]:
    """Let `bulk_create` keep the timestamps we pass.

    `bulk_create` skips `save()` but not `pre_save()`, and `auto_now_add`
    lives in `pre_save()` — it would stamp `now()` over every row. The
    contest window is the entire point of this seed, so the flag is cleared
    for the duration of the insert and restored afterwards.

    Takes `"Model.field"` strings so the caller reads as prose.
    """
    patched: list[Any] = []
    for name in field_names:
        field = _field_for(name)
        if field.auto_now_add:
            field.auto_now_add = False
            patched.append(field)
    try:
        yield
    finally:
        for field in patched:
            field.auto_now_add = True


def _field_for(name: str) -> Any:
    """Resolve `"Attempt.created_at"` → the field instance."""
    model_name, _, field_name = name.partition(".")
    model = {"Attempt": Attempt, "ContestRegistration": ContestRegistration}[model_name]
    return model._meta.get_field(field_name)


class Command(BaseCommand):
    help = "Contest-scale seed data: N registrations and M attempts, shaped like a real contest."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--contest", required=True, help="Contest slug to seed")
        parser.add_argument(
            "--participants", type=int, default=30_000, help="Registrations to create"
        )
        parser.add_argument("--submissions", type=int, default=122_000, help="Attempts to create")
        parser.add_argument("--problems", type=int, default=7, help="Contest problems to attach")
        parser.add_argument(
            "--source",
            choices=("cf", "stress"),
            default="cf",
            help="Participant pool: `cf` = imported Codeforces rows, `stress` = neytron_ users",
        )
        parser.add_argument("--seed", type=int, default=42, help="Reproducible randomness")
        parser.add_argument(
            "--window-hours",
            type=float,
            default=0.0,
            help=(
                "If set, rewrite the contest window to this length, ending one hour ago. "
                "0 keeps the contest's existing window."
            ),
        )
        parser.add_argument(
            "--rebuild-standings",
            action="store_true",
            help="Run rebuild_standings() after seeding and report how long it took",
        )
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Delete this contest's registrations, attempts and standings, then exit",
        )
        parser.add_argument(
            "--append",
            action="store_true",
            help=(
                "Add to whatever this contest already has. Without it, a contest that "
                "already holds attempts is refused rather than silently doubled."
            ),
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Report what would be created, write nothing"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            contest = Contest.objects.get(slug=options["contest"])
        except Contest.DoesNotExist as exc:
            raise CommandError(f"Contest topilmadi: {options['contest']}") from exc

        if options["purge"]:
            self._purge(contest)
            return

        existing = Attempt.objects.filter(contest=contest).count()
        if existing and not options["append"]:
            raise CommandError(
                f"`{contest.slug}` da allaqachon {existing} urinish bor. "
                "Ustiga qo'shish uchun `--append`, tozalab qaytadan yozish uchun "
                "avval `--purge` ishlating."
            )

        if options["window_hours"]:
            self._set_window(contest, options["window_hours"])

        rng = random.Random(options["seed"])
        participants: int = options["participants"]
        submissions: int = options["submissions"]

        problems, planned = self._contest_problems(contest, options["problems"], options["dry_run"])
        users = self._pick_users(rng, options["source"], participants)
        if len(users) < participants:
            self.stdout.write(
                self.style.WARNING(
                    f"Faqat {len(users)} foydalanuvchi topildi (so'ralgan {participants}). "
                    "`seed_stress` bilan ko'proq yarating."
                )
            )
        languages = self._languages()
        problems_meta = self._problem_points(problems)

        self.stdout.write(
            f"contest={contest.slug}  oyna={contest.start_at:%Y-%m-%d %H:%M} → "
            f"{contest.end_at:%Y-%m-%d %H:%M}  masala={planned}  "
            f"foydalanuvchi={len(users)}  til={len(languages)}"
        )

        if options["dry_run"]:
            per_user = self._attempts_per_user(rng, len(users), submissions)
            self.stdout.write(
                self.style.WARNING(
                    f"[dry-run] {len(users)} ro'yxatdan o'tish va {sum(per_user)} urinish "
                    "yaratilardi — hech narsa yozilmadi"
                )
            )
            return

        registrations = self._seed_registrations(contest, users, rng)
        created = self._seed_attempts(contest, users, problems_meta, languages, rng, submissions)
        self.stdout.write(
            self.style.SUCCESS(f"{registrations} ro'yxatdan o'tish va {created} urinish yozildi")
        )

        if options["rebuild_standings"]:
            self._rebuild(contest)

    # -- setup helpers ----------------------------------------------------

    def _set_window(self, contest: Contest, hours: float) -> None:
        """Put the contest in the past so standings can be computed."""
        end = timezone.now() - timedelta(hours=1)
        contest.start_at = end - timedelta(hours=hours)
        contest.end_at = end
        contest.save(update_fields=["start_at", "end_at"])
        self.stdout.write(f"Oyna qayta yozildi: {hours} soat, 1 soat oldin tugagan")

    def _contest_problems(
        self, contest: Contest, count: int, dry_run: bool
    ) -> tuple[list[ContestProblem], int]:
        """Attach problems, reusing whatever is already on the contest.

        Returns the rows and the number the contest would end up with, so
        `--dry-run` reports the real figure instead of what already exists.
        """
        existing = list(contest.problems.order_by("index_letter"))
        if len(existing) >= count:
            return existing[:count], count

        need = count - len(existing)
        used = {cp.problem_id for cp in existing}
        candidates = list(
            Problem.objects.filter(is_public=True, tests__isnull=False)
            .exclude(pk__in=used)
            .distinct()
            .order_by("difficulty", "pk")[:need]
        )
        if len(candidates) < need:
            raise CommandError(
                f"{need} ta testli ommaviy masala kerak, {len(candidates)} ta topildi"
            )
        if dry_run:
            return existing, len(existing) + len(candidates)

        letters = "ABCDEFGHIJ"
        start = len(existing)
        rows = [
            ContestProblem(
                contest=contest,
                problem=problem,
                index_letter=letters[start + i],
                points=100 + (start + i) * 250,
            )
            for i, problem in enumerate(candidates)
        ]
        ContestProblem.objects.bulk_create(rows)
        created = list(contest.problems.order_by("index_letter"))
        return created, len(created)

    def _problem_points(self, contest_problems: list[ContestProblem]) -> list[tuple[int, int]]:
        return [(cp.problem_id, cp.points) for cp in contest_problems]

    def _languages(self) -> list[tuple[int, float]]:
        """RankWant language ids paired with their measured CF share."""
        codes = {code: weight for code, weight in PROFILE_LANGUAGES}
        rows = Language.objects.filter(is_active=True, code__in=codes).values_list("pk", "code")
        found = [(pk, codes[code]) for pk, code in rows]
        if not found:
            raise CommandError("Faol til topilmadi — `seed_demo` ishga tushiring")
        return found

    def _pick_users(self, rng: random.Random, source: str, count: int) -> list[int]:
        """Random participants, drawn from the requested pool.

        `order_by("?")` would be both slow on ~1M rows and unreproducible
        (no seed). Sampling ids out of the primary-key range instead is
        seeded, fast, and dense enough that almost every draw hits a row.
        """
        if source == "cf":
            pool = User.objects.filter(email="", is_active=True)
        else:
            pool = User.objects.filter(username__startswith="neytron_")

        bounds = pool.aggregate(low=Min("pk"), high=Max("pk"))
        if bounds["low"] is None:
            raise CommandError(
                "Foydalanuvchi hovuzi bo'sh — `sync_codeforces` yoki `seed_stress` ishga tushiring"
            )
        low, high = bounds["low"], bounds["high"]

        picked: set[int] = set()
        while len(picked) < count:
            need = count - len(picked)
            draw = {rng.randint(low, high) for _ in range(need * 2)}
            found = set(pool.filter(pk__in=draw - picked).values_list("pk", flat=True))
            if not found:
                break
            picked |= found
        return sorted(picked)[:count]

    def _attempts_per_user(
        self, rng: random.Random, participants: int, submissions: int
    ) -> list[int]:
        """Split `submissions` across `participants` along the measured curve.

        Sampling the measured buckets and then scaling keeps the *shape*
        (most people submit 3-5 times, a few submit 20+) while still
        hitting the requested total exactly.
        """
        if participants < 1:
            return []
        sampled = rng.choices(PROFILE_USER_COUNTS, weights=PROFILE_USER_WEIGHTS, k=participants)
        total = sum(sampled)
        if total == 0:
            return [0] * participants

        scaled = [max(0, round(value * submissions / total)) for value in sampled]
        drift = submissions - sum(scaled)
        # Push the rounding drift onto the busiest participants, where one
        # extra attempt is invisible, instead of spreading it evenly.
        order = sorted(range(participants), key=lambda i: -scaled[i])
        step = 1 if drift > 0 else -1
        for i in range(abs(drift)):
            idx = order[i % participants]
            if step < 0 and scaled[idx] == 0:
                continue
            scaled[idx] += step
        return scaled

    # -- writers ----------------------------------------------------------

    def _seed_registrations(self, contest: Contest, users: list[int], rng: random.Random) -> int:
        """Register everyone before the contest starts, as real users do."""
        already = set(
            ContestRegistration.objects.filter(contest=contest).values_list("user_id", flat=True)
        )
        window = max((contest.start_at - timezone.now()).total_seconds(), 0.0)
        base = contest.start_at - timedelta(seconds=max(window, 3600))

        rows = [
            ContestRegistration(
                contest=contest,
                user_id=user_id,
                registered_at=base + timedelta(seconds=rng.uniform(0, 3600)),
            )
            for user_id in users
            if user_id not in already
        ]
        with _explicit_timestamps("ContestRegistration.registered_at"):
            ContestRegistration.objects.bulk_create(rows, batch_size=BATCH)
        return len(rows)

    def _seed_attempts(
        self,
        contest: Contest,
        users: list[int],
        problems: list[tuple[int, int]],
        languages: list[tuple[int, float]],
        rng: random.Random,
        submissions: int,
    ) -> int:
        if not problems:
            raise CommandError("Contestda masala yo'q — `--problems` bilan qo'shing")

        per_user = self._attempts_per_user(rng, len(users), submissions)
        duration = (contest.end_at - contest.start_at).total_seconds()
        profile_len = len(PROFILE_MINUTES)

        problem_ids = [pk for pk, _ in problems]
        problem_weights = PROFILE_PROBLEM_WEIGHTS[: len(problem_ids)]
        points = {pk: pts for pk, pts in problems}
        language_ids = [pk for pk, _ in languages]
        language_weights = [weight for _, weight in languages]

        rows: list[Attempt] = []
        for user_id, n in zip(users, per_user, strict=True):
            if n <= 0:
                continue
            # Draw the whole batch of minutes at once: one `choices` call per
            # user instead of one per attempt keeps 122K draws cheap.
            minutes = rng.choices(range(profile_len), weights=PROFILE_MINUTES, k=n)
            for minute in minutes:
                verdict = rng.choices(PROFILE_VERDICTS, weights=PROFILE_VERDICT_WEIGHTS, k=1)[0]
                problem_id = rng.choices(problem_ids, weights=problem_weights, k=1)[0]
                language_id = rng.choices(language_ids, weights=language_weights, k=1)[0]
                # Fractional minute + sub-minute jitter, so the peak lands at
                # the same relative position regardless of contest length.
                offset = (minute + rng.random()) / profile_len * duration
                created = contest.start_at + timedelta(seconds=offset)
                source = rng.choice(SOURCE_TEMPLATES)
                rows.append(
                    Attempt(
                        user_id=user_id,
                        problem_id=problem_id,
                        contest=contest,
                        language_id=language_id,
                        source_code=source,
                        # `bulk_create` skips `save()`, which is where
                        # `source_size` is normally set.
                        source_size=len(source.encode()),
                        verdict=verdict,
                        score=points[problem_id] if verdict == Verdict.AC else 0,
                        time_ms=rng.randint(15, 3000),
                        memory_kb=rng.randint(1024, 262144),
                        failed_test_index=(
                            rng.randint(1, 40)
                            if verdict in (Verdict.WA, Verdict.TLE, Verdict.RE, Verdict.MLE)
                            else None
                        ),
                        created_at=created,
                        judged_at=created + timedelta(milliseconds=rng.randint(400, 9000)),
                    )
                )

        with _explicit_timestamps("Attempt.created_at"):
            with transaction.atomic():
                Attempt.objects.bulk_create(rows, batch_size=BATCH)
        return len(rows)

    def _rebuild(self, contest: Contest) -> None:
        from contests.services import rebuild_standings

        started = timezone.now()
        count = rebuild_standings(contest)
        elapsed = (timezone.now() - started).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(f"Standings qayta qurildi: {count} qator, {elapsed:.2f} s")
        )

    def _purge(self, contest: Contest) -> None:
        """Remove everything this command writes, keeping the contest itself."""
        with transaction.atomic():
            attempts = Attempt.objects.filter(contest=contest).delete()[0]
            standings = Standing.objects.filter(contest=contest).delete()[0]
            registrations = ContestRegistration.objects.filter(contest=contest).delete()[0]
        self.stdout.write(
            self.style.WARNING(
                f"Tozalandi: {attempts} urinish, {standings} standing, "
                f"{registrations} ro'yxatdan o'tish"
            )
        )
