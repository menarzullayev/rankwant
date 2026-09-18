#!/usr/bin/env python3
"""Owner decisions must stay true in the code, not only in CLAUDE.md.

Every rule mirrors a row of CLAUDE.md § "Saidakbar aka qarorlari". On
2026-09-17 the owner chose local-only backups, and within hours another agent
that had not seen the decision merged unencrypted offsite uploads (#31); dumps
with user data left the machine. A table nobody checks does not stop that.
This script runs on every PR, so reverting a decision needs a deliberate edit
of both the code and the table.

Exit codes: 0 every decision holds, 1 a decision is violated, 2 a file could
not be read (never treated as "fine").
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SELF_HOSTED = "[self-hosted, rankwant]"
# A runner under trial gets its own label, and only its self-test may target it.
# On 2026-09-17 a trial runner registered with the production label took real CI
# jobs and failed them, because this rule left the self-test no other label.
TRIAL_RUNNER = {"runner-selftest.yml": "[self-hosted, rankwant-container]"}
# Where the container runner, the production CI runner since 2026-09-17, gets its
# labels whenever the container is recreated and registers again.
RUNNER_DEFAULTS = ("tools/runner/docker-compose.runner.yml", "tools/runner/entrypoint.sh")
# Everything tools/deploy.sh must rebuild: services built from this repo's sources.
DEPLOYED_SERVICES = {"api", "worker", "beat", "judge", "web"}
# Layout chrome drawn on every page: sidebar, top bar, header and footer. Its
# links prefetch on intent only (owner decision 2026-09-18).
NAV_CHROME = (
    "apps/web/src/layout/AppSidebar.tsx",
    "apps/web/src/layout/AppTopNav.tsx",
    "apps/web/src/layout/AppFooter.tsx",
    "apps/web/src/layout/HeaderStatus.tsx",
    "apps/web/src/layout/UserMenu.tsx",
)
INTENT_LINK = "apps/web/src/components/ui/IntentLink.tsx"
# Homepage <main> content links: same intent rule, this page only (2026-09-18).
HOME_MAIN = "apps/web/src/app/page.tsx"
# The dictionary travels as a cached file, not inside the page (2026-09-18).
DICTIONARY_ROUTE = "apps/web/src/app/i18n/[file]/route.ts"


class Unreadable(Exception):
    pass


def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise Unreadable(f"{rel}: {exc}") from exc


def backup_local_only() -> str | None:
    match = re.search(
        r'^offsite="\$\{RANKWANT_BACKUP_OFFSITE:-([a-z]*)\}"', read("tools/backup.sh"), re.M
    )
    if match is None:
        return "tools/backup.sh: offsite standart qiymati topilmadi"
    if match.group(1) != "off":
        return f"tools/backup.sh: offsite standarti `{match.group(1)}` — qaror: faqat lokal (`off`)"
    return None


def main_only_via_pr() -> str | None:
    # The hook also mentions the guard in a comment, so only a non-comment line
    # counts as a call — otherwise removing the call would still pass.
    calls = [
        line
        for line in read(".githooks/pre-push").splitlines()
        if "tools/push_guard.py" in line and not line.lstrip().startswith("#")
    ]
    if not calls:
        return ".githooks/pre-push push_guard'ni chaqirmaydi — `main` ga to'g'ridan push ochiq"
    if not re.search(
        r'^PROTECTED_REFS\s*=\s*\(.*"refs/heads/main"', read("tools/push_guard.py"), re.M
    ):
        return "tools/push_guard.py `refs/heads/main` ni himoya qilmaydi"
    return None


def ci_self_hosted_only() -> str | None:
    workflows = sorted((ROOT / ".github/workflows").glob("*.yml"))
    if not workflows:
        raise Unreadable(".github/workflows: workflow topilmadi")
    bad: list[str] = []
    for path in workflows:
        text = read(path.relative_to(ROOT).as_posix())
        allowed = {SELF_HOSTED, TRIAL_RUNNER.get(path.name, SELF_HOSTED)}
        for lineno, line in enumerate(text.splitlines(), 1):
            match = re.match(r"\s*runs-on:\s*(.*?)\s*$", line)
            if match and match.group(1) not in allowed:
                bad.append(f"{path.name}:{lineno} `{match.group(1) or '(blok)'}`")
    if bad:
        return "faqat self-hosted runner (bepul daqiqalar tugagan): " + ", ".join(bad)
    return None


def container_runner_takes_ci() -> str | None:
    # A recreated container registers with these defaults. Without `rankwant`
    # it comes back unable to take a single CI job, and nothing fails loudly:
    # the runs just sit in `queued`.
    bad: list[str] = []
    for rel in RUNNER_DEFAULTS:
        match = re.search(r"\$\{RUNNER_LABELS:[-=]([^}]*)\}", read(rel))
        if match is None:
            return f"{rel}: RUNNER_LABELS standart qiymati topilmadi"
        if "rankwant" not in [label.strip() for label in match.group(1).split(",")]:
            bad.append(f"{rel} `{match.group(1)}`")
    if bad:
        return "konteyner runner qayta ro'yxatdan o'tsa production label'siz qoladi: " + ", ".join(bad)
    return None


def deploy_builds_every_service() -> str | None:
    # A service missing from this list keeps running old code after a deploy
    # that reports success for the rest. `web` was left out until 2026-09-17,
    # when the owner decided one deploy updates everything.
    match = re.search(r"^SERVICES=\(([^)]*)\)", read("tools/deploy.sh"), re.M)
    if match is None:
        return "tools/deploy.sh: SERVICES ro'yxati topilmadi"
    missing = sorted(DEPLOYED_SERVICES - set(match.group(1).split()))
    if missing:
        return "tools/deploy.sh deploy'da qurmaydi: " + ", ".join(missing)
    return None


def deploy_manual_only() -> str | None:
    lines = read(".github/workflows/deploy.yml").splitlines()
    try:
        start = lines.index("on:")
    except ValueError:
        return "deploy.yml: `on:` bo'limi topilmadi"
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        block.append(line)
    triggers = {m.group(1) for line in block if (m := re.match(r"^  ([a-z_]+):", line))}
    if triggers != {"workflow_dispatch"}:
        return (
            f"deploy.yml trigger'lari {sorted(triggers)} — "
            "qaror: deploy faqat qo'lda (`workflow_dispatch`)"
        )
    return None


def deploy_gated_on_green_main() -> str | None:
    # Agents may deploy without asking only because deploy.sh refuses a commit
    # whose main CI is not green and runs one deploy at a time. Comment lines
    # mention both, so only code lines count.
    code = [
        line for line in read("tools/deploy.sh").splitlines() if not line.lstrip().startswith("#")
    ]
    if not any("tools/check_deploy_gate.py" in line for line in code):
        return (
            "tools/deploy.sh main CI darvozasini chaqirmaydi — "
            "agent qizil main'ni deploy qilishi mumkin"
        )
    if not any(re.search(r'\bmkdir "\$LOCK"', line) for line in code):
        return (
            "tools/deploy.sh deploy qulfini olmaydi — ikki agent bir vaqtda deploy qilishi mumkin"
        )
    return None


AI_CRAWLERS_REQUIRED = (
    "GPTBot",
    "ClaudeBot",
    "CCBot",
    "Google-Extended",
    "PerplexityBot",
    "Bytespider",
)


def search_open_ai_crawlers_blocked() -> str | None:
    """Search engines may crawl, AI crawlers may not (ADR-0023)."""
    if not re.search(r"^export const SITE_INDEXABLE = true;", read("apps/web/src/lib/site.ts"), re.M):
        return "apps/web/src/lib/site.ts: `SITE_INDEXABLE` `true` emas — sayt qidiruvga yopiq"
    robots = read("apps/web/src/app/robots.ts")
    listed = re.search(r"const AI_CRAWLERS = \[(.*?)\];", robots, re.S)
    if listed is None:
        return "apps/web/src/app/robots.ts: `AI_CRAWLERS` ro'yxati topilmadi"
    names = set(re.findall(r'"([^"]+)"', listed.group(1)))
    missing = [name for name in AI_CRAWLERS_REQUIRED if name not in names]
    if missing:
        return "apps/web/src/app/robots.ts: AI kraulerlar ro'yxatida yo'q — " + ", ".join(missing)
    if not re.search(r'userAgent: AI_CRAWLERS,\s*disallow: "/"', robots):
        return 'apps/web/src/app/robots.ts: AI kraulerlarga `disallow: "/"` qoidasi yo\'q'
    return None


def nav_prefetch_on_intent() -> str | None:
    """Links in the layout chrome prefetch on hover, focus or touch only.

    Prefetched on sight, the ~23 chrome links cost the server ~130-150 ms of
    CPU per visit, nine times the page render (profiled 2026-09-18). A plain
    `next/link` import in one of these files would quietly bring that back.
    """
    for rel in NAV_CHROME:
        if re.search(r'from\s+"next/link"', read(rel)):
            return f"{rel}: `next/link` to'g'ridan-to'g'ri ishlatilgan — navigatsiya linklari `IntentLink` orqali bo'lsin"
    if "prefetch={intent ? null : false}" not in read(INTENT_LINK):
        return f"{INTENT_LINK}: prefetch endi niyatga (hover/fokus) bog'liq emas"
    return None


def home_main_prefetch_on_intent() -> str | None:
    """Homepage <main> links prefetch on hover, focus or touch only.

    At 1000 visits/s, on-sight prefetch of the in-view content links (7 RSC)
    closed connections (EOF). Chrome is already on intent; this page's
    `<main>` was not. A plain `next/link` import would bring the storm back.
    """
    src = read(HOME_MAIN)
    if re.search(r'from\s+"next/link"', src):
        return (
            f"{HOME_MAIN}: `next/link` to'g'ridan-to'g'ri — "
            "bosh sahifa `<main>` `IntentLink` orqali bo'lsin"
        )
    if "IntentLink" not in src:
        return f"{HOME_MAIN}: `IntentLink` import yo'q"
    for block in re.finditer(r"<ButtonLink\b([^>]*)>", src):
        if not re.search(r"\bintent\b", block.group(1)):
            return f"{HOME_MAIN}: `ButtonLink` `intent` siz — hero ham niyatda prefetch qilsin"
    return None


def dictionary_as_cached_file() -> str | None:
    """The browser gets the dictionary as a separate cached file.

    As a prop of `LocaleProvider` it was serialized into every page: 72 kB of
    a 142 kB homepage and a third of the render CPU (profiled 2026-09-18).
    """
    layout = read("apps/web/src/app/layout.tsx")
    if re.search(r"<LocaleProvider[^>]*\bdict=", layout):
        return "apps/web/src/app/layout.tsx: lug'at yana `LocaleProvider` ga prop bo'lib uzatilmoqda"
    if "dictionaryUrl=" not in layout:
        return "apps/web/src/app/layout.tsx: `LocaleProvider` lug'at fayli manzilini olmayapti"
    route = read(DICTIONARY_ROUTE)
    if 'dynamic = "force-static"' not in route or "immutable" not in route:
        return f"{DICTIONARY_ROUTE}: lug'at fayli statik va `immutable` keshlanadigan emas"
    if not re.search(r"matcher:.*\|i18n/", read("apps/web/src/proxy.ts")):
        return "apps/web/src/proxy.ts: `/i18n/` middleware'dan chiqarilmagan — `Vary` keshni bo'ladi"
    return None


USER_MODEL = "apps/api/core/models.py"
#: ADR-0024: the 21 columns added for parity with Codeforces, Robocontest and KEP.
#: Thirteen of them stay unused until their features exist, on the owner's choice.
PARITY_USER_FIELDS = (
    "last_seen_at",
    "max_rating_skills",
    "max_rating_contest",
    "max_rating_activity",
    "max_rating_challenges",
    "streak_max",
    "solved_count",
    "shirt_size",
    "plan",
    "plan_expires_at",
    "postal_recipient",
    "postal_country",
    "postal_region",
    "postal_city",
    "postal_address",
    "postal_code",
    "coach_can_view_attempts",
    "message_min_rating",
    "contribution",
    "device_fingerprint",
    "duel_ready_until",
)


def user_parity_fields_kept() -> str | None:
    """The `User` columns added for competitor parity stay (ADR-0024).

    The owner chose to add the dormant columns before the features that use
    them. They look like dead fields, and an agent tidying them would undo
    that choice without asking.
    """
    src = read(USER_MODEL)
    missing = [
        name for name in PARITY_USER_FIELDS if not re.search(rf"^    {name} = models\.", src, re.M)
    ]
    if missing:
        return f"{USER_MODEL}: ADR-0024 ustunlari yo'q — {', '.join(missing)}"
    return None


def _workflow_triggers(rel: str) -> set[str]:
    lines = read(rel).splitlines()
    try:
        start = lines.index("on:")
    except ValueError:
        raise Unreadable(f"{rel}: `on:` bo'limi topilmadi")
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        block.append(line)
    return {m.group(1) for line in block if (m := re.match(r"^  ([a-z_]+):", line))}


def pr_skips_heavy_ci() -> str | None:
    # 2026-09-18: CI+Security on every PR doubled the single-runner queue.
    # Smoke on a PR held the runner for a full compose build.
    triggers = _workflow_triggers(".github/workflows/security.yml")
    if "pull_request" in triggers:
        return "security.yml PR'da ham yuguradi — qaror: Security faqat main + cron"
    if "github.event_name != 'pull_request'" not in read(".github/workflows/ci.yml"):
        return "ci.yml smoke PR'da ham yuguradi"
    compose = read("tools/runner/docker-compose.runner.yml")
    if "rankwant-ci-runner-2" not in compose or "rankwant-ci-work-2" not in compose:
        return "ikkinchi runner alohida volume'siz — /work ni bo'lishish checkout'ni buzadi"
    if 'profiles: ["second"]' not in compose:
        return "runner-2 profile'siz — oddiy `up -d` uni token'siz ko'taradi"
    recreate = read("tools/runner/recreate.sh")
    recreate_code = "\n".join(
        line for line in recreate.splitlines() if not line.lstrip().startswith("#")
    )
    if re.search(r"\bdown\b", recreate_code):
        return "recreate.sh `down` qiladi — ikkala runner birga o'ladi"
    if "--second" not in recreate:
        return "recreate.sh `--second` ni qabul qilmaydi"
    if "nsn-pc-rankwant-container-2" not in read("tools/runner_watchdog.py"):
        return "watchdog ikkinchi runner uchun restart buyrug'isiz"
    return None


def language_rule_written() -> str | None:
    if not re.search(r"^## Til\s*$", read("CONTRIBUTING.md"), re.M):
        return "CONTRIBUTING.md: `## Til` qoidasi yo'q"
    return None


def decisions_table_present() -> str | None:
    if "## Saidakbar aka qarorlari" not in read("CLAUDE.md"):
        return "CLAUDE.md: `## Saidakbar aka qarorlari` jadvali yo'q"
    return None


RULES: list[tuple[str, Callable[[], str | None]]] = [
    ("zaxira faqat lokal", backup_local_only),
    ("main faqat PR orqali", main_only_via_pr),
    ("CI faqat self-hosted", ci_self_hosted_only),
    ("CI runner konteynerda", container_runner_takes_ci),
    ("deploy faqat qo'lda", deploy_manual_only),
    ("deploy hamma servisni quradi", deploy_builds_every_service),
    ("deploy faqat yashil main'dan", deploy_gated_on_green_main),
    ("qidiruv ochiq, AI kraulerlar yopiq", search_open_ai_crawlers_blocked),
    ("navigatsiya prefetch'i niyatda", nav_prefetch_on_intent),
    ("bosh sahifa <main> prefetch'i niyatda", home_main_prefetch_on_intent),
    ("lug'at alohida faylda", dictionary_as_cached_file),
    ("User modeli tenglik maydonlari", user_parity_fields_kept),
    ("til qoidasi", language_rule_written),
    ("qarorlar jadvali", decisions_table_present),
    ("PR'da og'ir CI yo'q", pr_skips_heavy_ci),
]


def main() -> int:
    problems: list[str] = []
    try:
        for label, rule in RULES:
            problem = rule()
            if problem:
                problems.append(f"{label}: {problem}")
    except Unreadable as exc:
        print(f"✗ Qarorlarni o'qib bo'lmadi — {exc}")
        return 2
    if problems:
        print(f"✗ {len(problems)} ta qaror buzilgan (CLAUDE.md § Saidakbar aka qarorlari):")
        for problem in problems:
            print(f"  - {problem}")
        print("  Qarorni o'zgartirish faqat Saidakbar akaning aniq tasdig'i bilan.")
        return 1
    print(f"✓ {len(RULES)} ta qaror kodda amalda")
    return 0


if __name__ == "__main__":
    sys.exit(main())
