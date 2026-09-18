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
HOSTED = "ubuntu-latest"
# CI/Security/Nightly run on GitHub-hosted VMs (public repo, $0 minutes).
# Deploy stays on this machine: it touches the live Docker stack.
# The trial self-test is the only workflow allowed on the container label.
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
# The header must fit the narrowest supported screen — 320 px, the width the
# auth tabs were measured against. Owner decision 2026-09-18.
LOCALE_SWITCH = "apps/web/src/layout/LocaleSwitch.tsx"
SIGN_IN_LINK = "apps/web/src/layout/UserMenu.tsx"
# Mobile navigation drawer: the trigger announces its state, the panel is a
# named dialog while it is open, focus moves in and comes back, Esc closes it
# and the page behind it does not scroll. Owner decision 2026-09-18.
MOBILE_DRAWER_ID = "rw-sidenav-drawer"
APP_HEADER = "apps/web/src/layout/AppHeader.tsx"
APP_SIDEBAR = "apps/web/src/layout/AppSidebar.tsx"
APP_SHELL = "apps/web/src/layout/AppShell.tsx"
SIDEBAR_CONTEXT = "apps/web/src/context/SidebarContext.tsx"
# KPI grid: 4-up from `lg`, and the value steps down while the cards are
# narrow. Owner decision 2026-09-18.
STAT_CARD = "apps/web/src/components/ui/Card.tsx"


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


def ci_test_on_hosted() -> str | None:
    """CI must not run on the laptop once the repo is public.

    A public `pull_request` on `[self-hosted, rankwant]` would execute
    fork code on the live machine. Deploy is the exception: it has no
    `pull_request` trigger and needs the Desktop engine.
    """
    workflows = sorted((ROOT / ".github/workflows").glob("*.yml"))
    if not workflows:
        raise Unreadable(".github/workflows: workflow topilmadi")
    bad: list[str] = []
    for path in workflows:
        text = read(path.relative_to(ROOT).as_posix())
        if path.name == "deploy.yml":
            allowed = {SELF_HOSTED}
        elif path.name == "runner-selftest.yml":
            allowed = {TRIAL_RUNNER[path.name]}
        else:
            allowed = {HOSTED}
        for lineno, line in enumerate(text.splitlines(), 1):
            match = re.match(r"\s*runs-on:\s*(.*?)\s*$", line)
            if match and match.group(1) not in allowed:
                bad.append(f"{path.name}:{lineno} `{match.group(1) or '(blok)'}`")
    if bad:
        return "CI/nightly/security hosted, deploy self-hosted (jonli stack): " + ", ".join(
            bad
        )
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


def mobile_header_fits_narrow_screen() -> str | None:
    """The header fits 320 px — the narrowest screen the project supports.

    Measured in a live browser 2026-09-18: with the full language name in the
    control the header overflowed 15 px logged out and 59 px logged in at
    320 px, and 10 px at 375 px logged in. Showing the language CODE below
    `sm` and forbidding the sign-in label to wrap brought every one of those
    cases to 0 px. Restoring the full name at narrow widths, or dropping
    `whitespace-nowrap`, silently brings the horizontal scroll back.
    """
    switch = read(LOCALE_SWITCH)
    classes = re.findall(r'className="([^"]*)"', switch)

    def has_class(*tokens: str) -> bool:
        return any(all(token in value for token in tokens) for value in classes)

    if not has_class("hidden", "sm:block"):
        return (
            f"{LOCALE_SWITCH}: to'liq til nomi `sm` dan pastda yashirilmagan — "
            "320 px da header toshadi"
        )
    if not has_class("sm:hidden"):
        return f"{LOCALE_SWITCH}: tor ekranda til kodi ko'rinmaydi (`sm:hidden` span yo'q)"
    if "currentCode" not in switch:
        return f"{LOCALE_SWITCH}: til kodi (`currentCode`) hisoblanmayapti"

    # WCAG 2.5.3 «Label in Name»: the visible text differs per width, so the
    # accessible name has to carry BOTH forms — the full name and the code.
    label = re.search(r"aria-label=\{`([^`]*)`\}", switch)
    if label is None:
        return f"{LOCALE_SWITCH}: `aria-label` topilmadi"
    if "currentLabel" not in label.group(1) or "currentCode" not in label.group(1):
        return (
            f"{LOCALE_SWITCH}: `aria-label` ikkala ko'rinadigan matnni olmagan "
            "(WCAG 2.5.3, `label-content-name-mismatch`)"
        )

    # The check is scoped to the sign-in link's OWN class attribute, not to the
    # file. Measured while writing this rule: a file-wide substring test passed
    # even with the class removed, because the explanatory comment above the
    # link also contains the words `whitespace-nowrap` — the guard was reading
    # its own documentation. Anchor on the href instead.
    link = re.search(
        r'href=\{?"/login\?tab=login"[^>]*?className="([^"]*)"', read(SIGN_IN_LINK), re.S
    )
    if link is None:
        return f"{SIGN_IN_LINK}: kirish havolasi (`/login?tab=login`) topilmadi"
    if "whitespace-nowrap" not in link.group(1):
        return (
            f"{SIGN_IN_LINK}: kirish yorlig'ida `whitespace-nowrap` yo'q — "
            "tor ekranda ikki qatorga bo'linadi"
        )
    return None


def mobile_drawer_is_accessible() -> str | None:
    """The mobile navigation drawer is announced, focusable and escapable.

    Measured in a live browser 2026-09-18 (390x844x2, production build): the
    trigger never announced its state (`aria-expanded` stayed `null` even
    while the panel was open), the panel had no role, name or `aria-modal`,
    focus stayed on `body`, the page scrolled behind the panel, and a real
    Escape key press left it open (`asideLeft: 0`, `stillOpen: true`).

    Each clause below guards one of those measurements. The two attribute
    checks are scoped to their own element — a file-wide substring test would
    also match the explanatory comments next to them, which is how an earlier
    guard of this kind passed while the class was gone.
    """
    trigger = re.search(
        r'<button\s+type="button"\s+onClick=\{toggleMobileSidebar\}([^>]*)>',
        read(APP_HEADER),
        re.S,
    )
    if trigger is None:
        return f"{APP_HEADER}: mobil menyu tugmasi (`toggleMobileSidebar`) topilmadi"
    if "aria-expanded={isMobileOpen}" not in trigger.group(1):
        return (
            f"{APP_HEADER}: menyu tugmasi holatni e'lon qilmaydi "
            "(`aria-expanded` yo'q) — ekran o'quvchi panel ochilganini bilmaydi"
        )
    if f'aria-controls="{MOBILE_DRAWER_ID}"' not in trigger.group(1):
        return f'{APP_HEADER}: menyu tugmasida `aria-controls="{MOBILE_DRAWER_ID}"` yo\'q'

    sidebar = read(APP_SIDEBAR)
    aside = re.search(r"<aside\b(.*?)>", sidebar, re.S)
    if aside is None:
        return f"{APP_SIDEBAR}: `<aside>` topilmadi"
    opening = aside.group(1)
    if f'id="{MOBILE_DRAWER_ID}"' not in opening:
        return (
            f"{APP_SIDEBAR}: panelda `id=\"{MOBILE_DRAWER_ID}\"` yo'q — "
            "`aria-controls` nishonsiz qoladi"
        )
    if 'role={isMobileOpen ? "dialog" : undefined}' not in opening:
        return f"{APP_SIDEBAR}: panel ochiq holatda dialog rolini olmaydi"
    if "aria-modal={isMobileOpen || undefined}" not in opening:
        return f"{APP_SIDEBAR}: panelda `aria-modal` shartli emas"
    if 'aria-label={t(locale, "nav.main")}' not in opening:
        return f"{APP_SIDEBAR}: panel nomlanmagan (`aria-label` yo'q)"
    if "closeButtonRef.current?.focus()" not in sidebar:
        return f"{APP_SIDEBAR}: panel ochilganda fokus ichkariga kirmaydi"
    if "opener?.isConnected" not in sidebar:
        return f"{APP_SIDEBAR}: panel yopilganda fokus ochgan tugmaga qaytmaydi"

    if 'event.key === "Escape"' not in read(SIDEBAR_CONTEXT):
        return f"{SIDEBAR_CONTEXT}: `Esc` ochiq mobil panelni yopmaydi"

    if 'document.body.style.overflow = "hidden"' not in read(APP_SHELL):
        return f"{APP_SHELL}: panel ochiq ekan orqa fon scroll'i qulflanmagan"
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


def kpi_grid_steps_at_lg() -> str | None:
    """The home KPI grid goes 4-up at `lg`, and its numbers shrink to match.

    Measured in a live browser 2026-09-18 (1024x768, live origin): with
    `sm:grid-cols-2 xl:grid-cols-4` the four cards stayed 2-up across
    1024-1279 px, so the next section showed only 38 px above the fold. At
    4-up it shows 216 px and the page is 178 px shorter.

    A 3-up step was rejected BY MEASUREMENT, not by taste: four cards still
    occupy two rows at 3 columns, so it buys exactly 0 px of vertical space
    and leaves the fourth card alone on row two. Hence the explicit check that
    no `lg:grid-cols-3` creeps back in as an "improvement".

    The narrower card has a price. The value is `text-title-sm` (30 px bold,
    ~17.2 px per digit) and a 4-up card is 121 px wide inside at 1024 px, so a
    7-digit counter sits exactly on the edge (121/121) and 8 digits overflow.
    The value therefore steps down to 24 px until `xl`. The last clause checks
    that the component actually APPLIES the prop — a prop that is passed but
    never rendered looks green while doing nothing.
    """
    grid = re.search(r'<section className="([^"]*sm:grid-cols-2[^"]*)"', read(HOME_MAIN))
    if grid is None:
        return f"{HOME_MAIN}: bosh sahifa KPI to'ri (`sm:grid-cols-2`) topilmadi"
    classes = grid.group(1)

    if "lg:grid-cols-4" not in classes:
        return (
            f"{HOME_MAIN}: KPI to'rida `lg:grid-cols-4` yo'q — 1024-1279 px da "
            "kartalar 2 ustunda qolib, keyingi bo'limni pastga suradi"
        )
    if "lg:grid-cols-3" in classes:
        return (
            f"{HOME_MAIN}: KPI to'rida `lg:grid-cols-3` bor — 4 karta baribir 2 "
            "qatorni egallaydi (vertikal yutuq 0) va 4-karta yolg'iz qoladi"
        )

    # Every card in this section must opt in, otherwise the grid got denser
    # while one number stayed 30 px and can now overflow.
    section = read(HOME_MAIN).split('<section className="' + classes + '"', 1)[1]
    section = section.split("</section>", 1)[0]
    cards = section.count("<StatCard")
    opted_in = section.count('valueClassName="lg:text-2xl xl:text-title-sm"')
    if cards == 0:
        return f"{HOME_MAIN}: KPI to'rida `StatCard` topilmadi"
    if opted_in != cards:
        return (
            f"{HOME_MAIN}: KPI to'rining {cards} kartasidan {opted_in} tasida "
            "`valueClassName` raqam pog'onasi bor — tor ustunda sanoq toshadi"
        )

    rendered = re.search(
        r"<p className=\{`([^`]*)`\}>\{value\}</p>", read(STAT_CARD)
    )
    if rendered is None:
        return f"{STAT_CARD}: `StatCard` raqami topilmadi"
    if "valueClassName" not in rendered.group(1):
        return (
            f"{STAT_CARD}: `StatCard` `valueClassName` ni qo'llamaydi — prop "
            "uzatiladi, lekin hech narsa qilmaydi"
        )
    return None


RULES: list[tuple[str, Callable[[], str | None]]] = [
    ("zaxira faqat lokal", backup_local_only),
    ("main faqat PR orqali", main_only_via_pr),
    ("CI testlari hosted", ci_test_on_hosted),
    ("CI runner konteynerda", container_runner_takes_ci),
    ("deploy faqat qo'lda", deploy_manual_only),
    ("deploy hamma servisni quradi", deploy_builds_every_service),
    ("deploy faqat yashil main'dan", deploy_gated_on_green_main),
    ("qidiruv ochiq, AI kraulerlar yopiq", search_open_ai_crawlers_blocked),
    ("navigatsiya prefetch'i niyatda", nav_prefetch_on_intent),
    ("bosh sahifa <main> prefetch'i niyatda", home_main_prefetch_on_intent),
    ("lug'at alohida faylda", dictionary_as_cached_file),
    ("User modeli tenglik maydonlari", user_parity_fields_kept),
    ("header 320 px ga sig'adi", mobile_header_fits_narrow_screen),
    ("mobil panel foydalanishga yaroqli", mobile_drawer_is_accessible),
    ("KPI to'ri lg da 4 ustun", kpi_grid_steps_at_lg),
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
