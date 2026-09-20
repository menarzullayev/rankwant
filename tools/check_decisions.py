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

import importlib.util
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
    "apps/web/src/layout/BrandMark.tsx",
)
INTENT_LINK = "apps/web/src/components/ui/IntentLink.tsx"
# Homepage <main> content links: same intent rule, this page only (2026-09-18).
HOME_MAIN = "apps/web/src/app/page.tsx"
# The dictionary travels as a cached file, not inside the page (2026-09-18).
DICTIONARY_ROUTE = "apps/web/src/app/i18n/[file]/route.ts"
# The header must fit the narrowest supported screen — 320 px, the width the
# auth tabs were measured against. Owner decision 2026-09-18.
LOCALE_SWITCH = "apps/web/src/layout/LocaleSwitch.tsx"
# The visible endonym lives on the header ComboboxInput, not a dummy span
# in LocaleSwitch (that span used to satisfy this check while the trigger
# could grow unbounded).
DROPDOWN = "apps/web/src/components/ui/Dropdown.tsx"
# The dictionary registry and the load-promise cache are two caches over one
# thing; they must be dropped together. Owner decision 2026-09-19.
LOCALE_PROVIDER = "apps/web/src/i18n/LocaleProvider.tsx"
# The locale travels in the URL as well (`?lang=<code>`), so a shared link
# carries its own language. Owner decisions S5 + S5b, 2026-09-19. The three
# names live in ONE module because the edge proxy cannot import `next/headers`
# and would otherwise have to duplicate the list.
LOCALE_PARAMS = "apps/web/src/i18n/locale-params.ts"
LOCALE_RESOLVE = "apps/web/src/i18n/resolve.ts"
LOCALE_SERVER = "apps/web/src/i18n/server.ts"
PROXY = "apps/web/src/proxy.ts"
# Guest GET `/` CDN cache (2026-09-19): origin headers + Worker skip.
HOME_CACHE = "apps/web/src/lib/home-cache.ts"
WORKER_TOML = "services/maintenance-worker/wrangler.toml"
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
# Profile KPI grid: its content column is far narrower than the home page's
# (the 300 px sidebar eats the width), so it steps at `xl`, not `lg`. Owner
# decision 2026-09-18.
PROFILE_LAYOUT = "apps/web/src/app/users/[username]/layout.tsx"
# Filter badge: the difficulty range is one filter even though it rides in two
# params, so the badge counts it once. Owner decision 2026-09-18.
FILTERS = "apps/web/src/components/ProblemFilters.tsx"
# Brand and footer: the brand lives in the header via a single `BrandMark`
# (it used to be duplicated in the sidebar/topnav and missing from the header
# entirely — on phones the brand was only visible inside the drawer), and the
# footer is a 3-column grid with a legal row. Owner decision 2026-09-19.
BRAND_MARK = "apps/web/src/layout/BrandMark.tsx"
APP_HEADER = "apps/web/src/layout/AppHeader.tsx"
APP_SIDEBAR = "apps/web/src/layout/AppSidebar.tsx"
APP_TOPNAV = "apps/web/src/layout/AppTopNav.tsx"
APP_FOOTER = "apps/web/src/layout/AppFooter.tsx"
# Content-name coverage is visible (2026-09-19). Topic/skill/quest names exist
# only in the uz/ru/en columns, so every other language shows Uzbek text and
# the UI has to say so (owner decision 10). Measured before the fix: the
# fallback worked in 8 places but the marker appeared in 2, and the `uz`
# dictionary itself was marked as a fallback on its own pages.
MESSAGES = "apps/web/src/i18n/messages.ts"
CONTENT_BADGE = "apps/web/src/components/ui/UzFallbackBadge.tsx"
ARCHIVE_SIDEBAR = "apps/web/src/components/ArchiveSidebar.tsx"
ABOUT_TAB = "apps/web/src/components/profile/AboutTab.tsx"
TOPIC_STRENGTH = "apps/web/src/components/profile/TopicStrength.tsx"
ACTIVITY_TABS = "apps/web/src/components/profile/ActivityTabs.tsx"
SKILLS_SECTION = "apps/web/src/components/settings/SkillsSection.tsx"
PROBLEMS_PAGE = "apps/web/src/app/problems/page.tsx"

#: Every place a content name can fall back: the file, the marker it must
#: carry, and how many times it must appear.
#:
#: The needle is the RENDER SITE, not the bare symbol — the negative tests
#: mutate the first occurrence only (`Mutation` uses `replace(..., 1)`), so a
#: needle that also matches the import line would survive the mutation and the
#: test would report a live guard as dead. Counting also catches a file with
#: two call sites losing one of them.
CONTENT_MARKER_SITES: tuple[tuple[str, str, int], ...] = (
    (ARCHIVE_SIDEBAR, "<ContentName", 1),
    (ABOUT_TAB, "<ContentName", 1),
    (TOPIC_STRENGTH, "<ContentName", 1),
    (ACTIVITY_TABS, "<ContentName", 2),
    (SKILLS_SECTION, "<ContentName", 1),
    # Native `<option>` cannot hold JSX, so the same marker travels as text.
    (SKILLS_SECTION, "contentNameText(s, locale)", 1),
    (FILTERS, "UzFallbackBadge", 2),
    (FILTERS, "fallback={root.fallback}", 1),
    (FILTERS, "fallback={child.fallback}", 1),
    (PROBLEMS_PAGE, "fallback: info.locale === null", 1),
    # The language list says which languages lack content names, so the
    # choice is informed BEFORE it is made.
    (LOCALE_SWITCH, "hasContentNames(code)", 1),
)


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


def users_profiles_stay_noindex() -> str | None:
    """2026-09-20 HITL keep-users-closed: `/users/` stays out of the crawl.

    974k profiles (Codeforces import + test handles). Wiping users is
    forbidden, so “open after cleanup” is not a plan. Allowlist is a later
    HITL. The `*` rule must keep `/users/` in `disallow`.
    """
    robots = read("apps/web/src/app/robots.ts")
    if not re.search(
        r'disallow: \["/admin", "/notifications", "/users/"\]',
        robots,
    ):
        return (
            "apps/web/src/app/robots.ts: `*` qoidasida `/users/` yo'q — "
            "2026-09-20 HITL keep-users-closed"
        )
    return None


def rank_colour_groups_not_sixteen_tokens() -> str | None:
    """2026-09-20 HITL encode-167: 7 colour groups, not 16 `--rw-rank-N`.

    Live #167 collapsed tokens to grey/green/cyan/blue/violet/orange/red.
    Numbered tokens coming back would duplicate CSS and drift from
    `title.colour_group`.
    """
    titles = read("apps/api/profiles/titles.py")
    if '"colour_group": COLOUR_GROUPS[tier_index]' not in titles:
        return "apps/api/profiles/titles.py: `colour_group` COLOUR_GROUPS dan emas"
    for name in ("grey", "green", "cyan", "blue", "violet", "orange", "red"):
        if f'"{name}"' not in titles:
            return f"apps/api/profiles/titles.py: guruh `{name}` yo'q"
    css = read("apps/web/src/app/globals.css")
    if re.search(r"--rw-rank-\d", css):
        return "apps/web/src/app/globals.css: raqamli `--rw-rank-N` qaytdi (#167)"
    for name in ("grey", "green", "cyan", "blue", "violet", "orange", "red"):
        if f"--rw-rank-{name}" not in css:
            return f"apps/web/src/app/globals.css: `--rw-rank-{name}` yo'q"
    if "rw-rank-${title.colour_group}" not in read("apps/web/src/components/UserName.tsx"):
        return "apps/web/src/components/UserName.tsx: class `colour_group` emas"
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
    if not re.search(r"matcher:.*\|i18n/", read(PROXY)):
        return "apps/web/src/proxy.ts: `/i18n/` middleware'dan chiqarilmagan — `Vary` keshni bo'ladi"
    return None


def dictionary_survives_return() -> str | None:
    """Returning to a language must re-inject its dictionary.

    The registry and the load-promise cache are two caches over one thing.
    Keyed by URL and never cleared, the promise cache outlived the eviction, so
    a second visit to a language injected no `<script>` and the page rendered
    raw keys — measured 2026-09-19 on the live stack with a real mouse and
    keyboard: `ru` -> `zh` -> `es` -> back to `zh` left 38 raw keys on screen
    (`nav.problems`, `locale.switchLabel`, ...) until a full reload. They have
    to be dropped together, which is what `keepOnly` exists for.
    """
    provider = read(LOCALE_PROVIDER)
    if "useEffect(() => keepOnly(locale), [locale])" not in provider:
        return (
            f"{LOCALE_PROVIDER}: til almashinuvi `keepOnly` ni chaqirmaydi — "
            "registr va yuklash va'dasi keshining tozalanishi ajralib qolgan, "
            "ya'ni qaytib o'sha tilga o'tilganda sahifa xom kalit ko'rsatadi"
        )
    keep = re.search(r"function keepOnly\(keep: Locale\): void \{(.*?)\n\}", provider, re.S)
    if keep is None:
        return f"{LOCALE_PROVIDER}: `keepOnly` topilmadi"
    body = keep.group(1)
    if "loading.delete(" not in body:
        return (
            f"{LOCALE_PROVIDER}: `keepOnly` yuklash va'dasi keshini tozalamaydi — "
            "evict qilingan tilning va'dasi qolib ketadi va lug'at qayta kiritilmaydi"
        )
    if "evictOtherLocales(keep)" not in body:
        return f"{LOCALE_PROVIDER}: `keepOnly` registrni tozalamaydi"
    if not re.search(r"new Map<Locale, \{ url: string; promise: Promise<void> \}>", provider):
        return (
            f"{LOCALE_PROVIDER}: yuklash keshining kaliti til emas — URL bo'yicha "
            "kalitlangan kesh eviction bilan mos kelmaydi"
        )
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
    # ADR-0026: rating tier and social fields, written by `sync_codeforces`.
    # They look dead today because nothing else writes them.
    "rank_title",
    "max_rank_title",
    "friend_count",
    "title_photo_url",
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
    """The header AND the language panel fit 320 px — the narrowest screen.

    Measured in a live browser 2026-09-18: with the full language name in the
    control the header overflowed 15 px logged out and 59 px logged in at
    320 px, and 10 px at 375 px logged in. Showing the language CODE below
    `sm` and forbidding the sign-in label to wrap brought every one of those
    cases to 0 px.

    Re-measured 2026-09-19 (`main` = 6486cd6) before the owner's decision
    (S4), because "the code was chosen" is not the same as "the endonym does
    not fit": an UNBOUNDED endonym overflows again — `Qaraqalpaqsha` makes
    the control 149 px (+29 px), `O'zbekcha` 124 px (+7), `Кыргызча`
    123 px (+6), and the header has no slack left (the right-hand group is
    already shrunk by `min-w-0`). Bounding the label at 48 px
    (`max-w-[3rem]`) keeps all ten endonyms at ≤ 117 px with 0 px overflow,
    while 7 of 10 still render in full. So the code is no longer needed.

    The same measurement found the dropdown overflowing 44 px to the LEFT at
    320 px — `w-64` (256 px) hanging from a trigger whose right edge is only
    212 px — which pushed ALL 11 flags to `left = -32…-11`, i.e. off-screen.
    At 360 px it is `left = -4` with the flag visible, so the boundary is
    ~352 px. The panel is therefore anchored to the VIEWPORT whenever the
    trigger sits closer than `PANEL_W + PANEL_GAP` to the right edge.
    """
    switch = read(LOCALE_SWITCH)
    dropdown = read(DROPDOWN)

    if "sm:hidden" in switch:
        return (
            f"{LOCALE_SWITCH}: tor ekranda til KODI qaytgan — endonim o'rniga "
            "kod ko'rsatiladi (qaror: endonim har kenglikda ko'rinadi)"
        )
    # The bound must be on the visible header input. A hidden span in
    # LocaleSwitch used to pass this check while the Combobox showed the
    # full endonym and overflowed 320 px.
    if "max-w-[3rem]" not in dropdown or "truncate" not in dropdown:
        return (
            f"{DROPDOWN}: header triggerda `max-w-[3rem] truncate` yo'q — "
            "320 px da header toshadi (`Qaraqalpaqsha` +29 px, o'lchandi)"
        )
    if "sm:max-w-[7.5rem]" not in dropdown:
        return f"{DROPDOWN}: keng ekran chegarasi (`sm:max-w-[7.5rem]`) yo'q"

    # Panel: tor ekranda viewport'ga bog'lanmasa bayroqlar ekrandan chiqadi.
    for needle in (
        "const PANEL_W = 256;",
        "const PANEL_GAP = 8;",
        "rect.right < PANEL_W + PANEL_GAP",
        '"fixed mt-1"',
        "left: PANEL_GAP, right: PANEL_GAP",
    ):
        if needle not in switch:
            return (
                f"{LOCALE_SWITCH}: `{needle}` yo'q — panel tor ekranda "
                "viewport'ga bog'lanmagan, bayroqlar ko'rinmaydi"
            )

    # WCAG 2.5.3 «Label in Name»: the visible text is the endonym — visually
    # truncated below `sm`, but the DOM text stays whole — so the accessible
    # name has to carry it. The code rides along for voice control.
    label = re.search(r"aria-label=\{`([^`]*)`\}", switch)
    if label is None:
        return f"{LOCALE_SWITCH}: `aria-label` topilmadi"
    if "currentLabel" not in label.group(1):
        return (
            f"{LOCALE_SWITCH}: `aria-label` ko'rinadigan endonimni olmagan "
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
    if "if (!isMobileOpen) return;" not in read(APP_SHELL):
        return (
            f"{APP_SHELL}: scroll qulfi `isMobileOpen` ga bog'lanmagan — "
            "topnav drawer ochiqda orqa fon siljiydi"
        )

    topnav = read(APP_TOPNAV)
    if "aria-expanded={isMobileOpen}" not in topnav:
        return f"{APP_TOPNAV}: burger holatni e'lon qilmaydi (`aria-expanded` yo'q)"
    if 'aria-controls="rw-topnav-drawer"' not in topnav:
        return f'{APP_TOPNAV}: burgerda `aria-controls="rw-topnav-drawer"` yo\'q'
    if 'id="rw-topnav-drawer"' not in topnav:
        return f"{APP_TOPNAV}: `rw-topnav-drawer` yo'q"
    if "hidden={!isMobileOpen}" not in topnav:
        return (
            f"{APP_TOPNAV}: drawer yopiqda DOM'dan chiqadi — `aria-controls` "
            "nishonsiz qoladi"
        )
    if 'role={isMobileOpen ? "dialog" : undefined}' not in topnav:
        return f"{APP_TOPNAV}: ochiq drawer dialog rolini olmaydi"
    if "drawerRef.current?.querySelector<HTMLElement>(\"a\")?.focus()" not in topnav:
        return f"{APP_TOPNAV}: ochilganda fokus ichkariga kirmaydi"
    if "menuButtonRef.current?.isConnected" not in topnav:
        return f"{APP_TOPNAV}: yopilganda fokus burgerga qaytmaydi"
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


def _workflow_job(src: str, job: str) -> str:
    lines = src.splitlines()
    out: list[str] = []
    in_job = False
    for ln in lines:
        if re.match(r"^  \w[\w-]*:\s*$", ln):
            if in_job:
                break
            in_job = ln.strip().rstrip(":") == job
            continue
        if in_job:
            out.append(ln)
    return "\n".join(out)


def pr_skips_heavy_ci() -> str | None:
    # 2026-09-18: CI+Security on every PR doubled the single-runner queue.
    # 2026-09-20: smoke / bake-off / language matrix / API pytest left main
    # CI entirely (Nightly only). Putting any of those jobs back on ci.yml
    # restores the 17 min wall measured on 35f1e93.
    triggers = _workflow_triggers(".github/workflows/security.yml")
    if "pull_request" in triggers:
        return "security.yml PR'da ham yuguradi — qaror: Security faqat main + cron"
    ci = read(".github/workflows/ci.yml")
    for job in ("smoke", "language_matrix", "bakeoff"):
        if re.search(rf"^  {job}:\s*$", ci, re.M):
            return f"ci.yml da {job} job bor — og'ir stack faqat Nightly"
    if re.search(r"(?m)^\s+- name: pytest\b", _workflow_job(ci, "api")) or re.search(
        r"(?m)^\s+pytest\b", _workflow_job(ci, "api")
    ):
        return "ci.yml api pytest yugurtiradi — pytest faqat Nightly coverage"
    nightly = read(".github/workflows/nightly.yml")
    e2e = _workflow_job(nightly, "e2e")
    if "run --rm smoke" not in e2e:
        return "nightly.yml e2e smoke yugurtirmaydi"
    if "--profile bakeoff" not in e2e:
        return "nightly.yml e2e bake-off yugurtirmaydi"
    if "check_languages.py" not in _workflow_job(nightly, "compatibility"):
        return "nightly.yml compatibility language matrix emas"
    if "pytest" not in _workflow_job(nightly, "coverage"):
        return "nightly.yml coverage pytest yugurtirmaydi"
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
    # Token bo'yicha tekshiriladi (sabab: `profil_kpi_grid_steps_at_xl` ga qarang).
    tokens = classes.split()

    if "lg:grid-cols-4" not in tokens:
        return (
            f"{HOME_MAIN}: KPI to'rida `lg:grid-cols-4` yo'q — 1024-1279 px da "
            "kartalar 2 ustunda qolib, keyingi bo'limni pastga suradi"
        )
    if "lg:grid-cols-3" in tokens:
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


def profile_sidebar_stacks_below_xl() -> str | None:
    """The profile stacks below `xl`; the 300 px sidebar returns at 1280.

    Owner decision (HITL, 2026-09-19): the profile card sits ABOVE the content
    in 1024–1279 px, so the content column gets the home page's measured
    geometry (#96) — 701 px at 1024, cards ~163 px with ~121 px inside, where
    an 8-digit counter fits at the 24 px value step. The two-column
    `300px_minmax(0,1fr)` grid and the sticky sidebar return at `xl`.

    Why the sidebar decision had to come first (measured 2026-09-18): with the
    300 px sidebar at `lg` the content column is only 377 px; forcing 4-up
    there gave 82 px cards with 40 px inside and clipped the values by 27 px.
    At 1280 two columns return (content 633 px, 104 px inside a card) — a
    6-digit counter measures exactly 104 px, so the value stays at 24 px
    until `2xl` restores 30 px.
    """
    layout = read(PROFILE_LAYOUT)
    outer = re.search(r'<div className="(grid gap-6[^"]*)"', layout)
    if outer is None:
        return f"{PROFILE_LAYOUT}: profil tashqi to'ri (`grid gap-6`) topilmadi"
    # ⚠️ Token bo'yicha tekshiriladi (sabab: `kpi_grid_steps_at_lg` ga qarang —
    # substring tekshiruvi `2xl` ichidagi `xl` ni «bor» deb olib yuboradi).
    outer_tokens = outer.group(1).split()
    if "lg:grid-cols-[300px_minmax(0,1fr)]" in outer_tokens:
        return (
            f"{PROFILE_LAYOUT}: yon panel `lg` da qaytgan — 1024 px da kontent "
            "ustuni 377 px qoladi va KPI to'ri 2 ustunda qolib ketadi (qaror 21)"
        )
    if "xl:grid-cols-[300px_minmax(0,1fr)]" not in outer_tokens:
        return (
            f"{PROFILE_LAYOUT}: yon panel `xl` dan qaytmaydi — ikki ustunli "
            "profil 1280 dan boshlanishi kerak (qaror 21)"
        )

    grid = re.search(r'<section className="([^"]*sm:grid-cols-2[^"]*)"', layout)
    if grid is None:
        return f"{PROFILE_LAYOUT}: profil KPI to'ri (`sm:grid-cols-2`) topilmadi"
    tokens = grid.group(1).split()
    if "xl:grid-cols-4" in tokens:
        return (
            f"{PROFILE_LAYOUT}: KPI to'rida ortiqcha `xl:grid-cols-4` bor — "
            "4 ustun endi `lg` dan, qo'shimcha pog'ona eskirgan holat (qaror 21)"
        )
    if "lg:grid-cols-4" not in tokens:
        return (
            f"{PROFILE_LAYOUT}: KPI to'rida `lg:grid-cols-4` yo'q — panel `xl` "
            "gacha stekda, 1024 px da kontent 701 px va 4 ustun sig'adi (qaror 21)"
        )

    section = layout.split('<section className="' + grid.group(1) + '"', 1)[1]
    section = section.split("</section>", 1)[0]
    cards = section.count("<StatCard")
    opted_in = section.count('valueClassName="lg:text-2xl 2xl:text-title-sm"')
    if cards == 0:
        return f"{PROFILE_LAYOUT}: profil KPI to'rida `StatCard` topilmadi"
    if opted_in != cards:
        return (
            f"{PROFILE_LAYOUT}: profil to'rining {cards} kartasidan {opted_in} tasida "
            "`valueClassName` raqam pog'onasi bor — 1280 px da ichki 104 px va "
            "6 xonali sanoq chegarada qoladi"
        )
    return None


def brand_in_header_and_footer_columns() -> str | None:
    """The brand lives in the header, the footer is a 3-column grid.

    Owner decision (HITL, 2026-09-19): the sidenav stays the default nav
    (topnav remains an optional mode), the mobile drawer stays, and the
    brand moves into the header — it used to be duplicated in the
    sidebar/topnav and missing from the header entirely, so on phones the
    brand was only visible inside the drawer. The footer becomes three
    columns (brand + tagline, platform links, contacts) over a legal row.

    The legal row is not decoration: Terms and Privacy must be on EVERY
    page because Google OAuth verification expects the privacy policy
    reachable from there (ADR-0016), and the footer links are crawled
    since the site became indexable (ADR-0023).
    """
    header = read(APP_HEADER)
    if "<BrandMark" not in header:
        return (
            f"{APP_HEADER}: header'da `<BrandMark` yo'q — brend telefonda "
            "faqat drawer ichida ko'rinardi (qaror 22)"
        )
    sidebar = read(APP_SIDEBAR)
    if "Rank<span" in sidebar:
        return (
            f"{APP_SIDEBAR}: yon panel brendni qayta chizyapti — brend bitta "
            "manbadan (`BrandMark`, header) beriladi (qaror 22)"
        )
    topnav = read(APP_TOPNAV)
    if "<BrandMark" not in topnav:
        return (
            f"{APP_TOPNAV}: topnav `BrandMark` dan foydalanmaydi — wordmark "
            "nusxasi qaytgan bo'ladi (qaror 22)"
        )
    brand = read(BRAND_MARK)
    if 'href="/"' not in brand or "rw-accent-ink" not in brand:
        return (
            f"{BRAND_MARK}: brend havolasi yoki urg'u rangi yo'qolgan "
            "(qaror 22)"
        )
    footer = read(APP_FOOTER)
    if "lg:grid-cols-[1fr_auto_auto]" not in footer:
        return (
            f"{APP_FOOTER}: footer uch ustunga bo'linmagan — brend, "
            "platforma havolalari va aloqa alohida ustunlarda (qaror 22)"
        )
    for key in ("footer.copyright", "footer.terms", "footer.privacy"):
        if key not in footer:
            return (
                f"{APP_FOOTER}: huquqiy qator to'liq emas (`{key}` yo'q) — "
                "Terms/Privacy HAR sahifada turishi shart (ADR-0016)"
            )
    if 'TELEGRAM_URL = "https://t.me/rankwant"' not in footer:
        return f"{APP_FOOTER}: rasmiy Telegram `t.me/rankwant` emas (2026-09-20 HITL)"
    if 'CONTACT_EMAIL = "support@rankwant.uz"' not in footer:
        return f"{APP_FOOTER}: rasmiy email `support@rankwant.uz` emas (2026-09-20 HITL)"
    return None


def difficulty_range_counts_as_one_filter() -> str | None:
    """The filter badge counts the difficulty range as ONE filter.

    Measured 2026-09-18 in the CI smoke run: a single "Qiyin" chip writes
    `difficulty__gte=1800` AND `difficulty__lte=2199` (#90 moved the chips to
    the Codeforces-style range), while `activeCount` counted `PANEL_KEYS`
    entries — so the badge read "Filtrlar2" for one choice. The E2E spec pinned
    "1" and had been red on `main` since #90, which in turn kept the deploy
    gate shut, so #93/#96/#98 never reached the live site.

    `level` is the pre-#90 spelling and is still honoured on read, so all three
    keys must collapse into the same single filter.
    """
    source = read(FILTERS)
    declared = re.search(r"const DIFFICULTY_KEYS[^=]*=\s*\[([^\]]*)\]", source)
    if declared is None:
        return (
            f"{FILTERS}: `DIFFICULTY_KEYS` topilmadi — diapazon yana kalit bo'yicha "
            "sanaladi va bitta chip «2 filtr» bo'lib ko'rinadi"
        )
    keys = re.findall(r'"([^"]+)"', declared.group(1))
    missing = [k for k in ("level", "difficulty__gte", "difficulty__lte") if k not in keys]
    if missing:
        return (
            f"{FILTERS}: `DIFFICULTY_KEYS` da {', '.join(missing)} yo'q — "
            "diapazonning uchala shakli bitta filtr bo'lishi kerak"
        )

    counted = re.search(r"const activeCount =([^;]*);", source, re.S)
    if counted is None:
        return f"{FILTERS}: `activeCount` topilmadi"
    body = counted.group(1)
    if "DIFFICULTY_KEYS" not in body:
        return (
            f"{FILTERS}: `activeCount` `DIFFICULTY_KEYS` ni ishlatmaydi — "
            "bitta chip yana «2 filtr» bo'lib ko'rinadi"
        )
    if re.search(
        r"PANEL_KEYS\.filter\(\s*\(key\) => params\.get\(key\),?\s*\)\.length", body
    ):
        return (
            f"{FILTERS}: `activeCount` yana xom kalitlarni sanaydi — diapazonning "
            "ikki yarmi ikkita filtr bo'lib chiqadi"
        )
    return None


def content_coverage_visible() -> str | None:
    """Missing content names show the English property, never another locale.

    Three checks: coverage source is one list (`CONTENT_NAME_LOCALES`), a
    missing translation does not copy `name_uz`, and every render site
    still marks the identifier so a `zh` reader does not take a slug for
    a Chinese name.
    """
    messages = read(MESSAGES)
    if 'export const CONTENT_NAME_LOCALES = ["uz", "ru", "en"] as const;' not in messages:
        return f"{MESSAGES}: CONTENT_NAME_LOCALES yo'q — qamrov manbai yo'qolgan"
    if "export function hasContentNames(" not in messages:
        return f"{MESSAGES}: hasContentNames() yo'q — tanlash ro'yxati qamrovni bilmaydi"
    if "function nameProperty(" not in messages:
        return f"{MESSAGES}: nameProperty() yo'q — yetishmagan tarjima property ko'rsatilmaydi"
    if "source: DEFAULT_LOCALE" in messages:
        return (
            f"{MESSAGES}: yetishmagan tarjima `DEFAULT_LOCALE` ga tushadi — "
            "zaxira til taqiqlangan"
        )
    badge = read(CONTENT_BADGE)
    for symbol in ("export function ContentName(", "export function contentNameText("):
        if symbol not in badge:
            return f"{CONTENT_BADGE}: `{symbol}` yo'q"
    if "info.locale === null" not in badge:
        return f"{CONTENT_BADGE}: ContentName qaytishni tekshirmaydi"
    for rel, needle, want in CONTENT_MARKER_SITES:
        got = read(rel).count(needle)
        if got < want:
            return (
                f"{rel}: `{needle}` {got} marta, {want} kerak — "
                "qaytish belgisiz qolgan"
            )
    return None


def locale_travels_in_the_url() -> str | None:
    """Til havolada ham keladi — `?lang=<kod>` (S5), va qurilma eslab qoladi
    (S5b). Saidakbar aka qarori, 2026-09-19.

    Tuzatishdan oldin o'lchandi: `/about?lang=ru` o'zbekcha berilardi —
    query satri sahifaga yetib borardi, lekin uni hech kim o'qimasdi, ya'ni
    yagona manba cookie edi. Havolani olgan odamda esa u yo'q.

    Uch joyi JIM buzilishi mumkin, shuning uchun uchtasi ham tekshiriladi:

    1. USTUNLIK — havola cookie'dan kuchli. `resolveLocale()` sof funksiya,
       ya'ni tartib manba satridan o'qiladi: `param` shoxobchasi OLDIN
       turishi shart. Aks holda ulashilgan havola o'z tilini olib kelmaydi.
    2. PROXY ICHIDAGI TARTIB — sarlavha `NextResponse.next()` dan OLDIN
       yozilishi shart. `next()` `request.headers` ni CHAQIRUV paytida
       `x-middleware-request-*` qatorlariga ko'chiradi (o'lchandi:
       `next@16.3.4`, `dist/server/web/spec-extension/response.js:128`),
       ya'ni keyin yozilgan qiymat joriy render'ga yetib bormaydi. Oqibati
       ayyor: sahifa cookie tilida chiziladi va xususiyat «bir so'rov
       kechikib ishlaydi» — yashil ko'rinadi, aslida buzuq.
    3. COOKIE — usiz havola faqat BIRINCHI sahifani tuzatadi, har bir
       ichki bosish qurilma tiliga qaytadi. U bilan hech bir ichki havolani
       o'zgartirish shart emas.
    """
    params = read(LOCALE_PARAMS)
    for needle in (
        'export const LOCALE_COOKIE = "rw_locale";',
        'export const LOCALE_PARAM = "lang";',
        'export const LOCALE_HEADER = "x-rw-locale";',
    ):
        if needle not in params:
            return f"{LOCALE_PARAMS}: `{needle}` yo'q — nomlar yagona manbada bo'lishi shart"
    if "export const LOCALE_COOKIE" in read(LOCALE_SERVER):
        return f"{LOCALE_SERVER}: `LOCALE_COOKIE` ikkinchi marta e'lon qilingan — drift manbai"

    resolve = read(LOCALE_RESOLVE)
    param_branch = resolve.find("if (param !== null && isLocale(param))")
    cookie_branch = resolve.find("if (cookie !== null && isLocale(cookie))")
    if param_branch < 0 or cookie_branch < 0:
        return f"{LOCALE_RESOLVE}: `?lang=` yoki cookie shoxobchasi topilmadi"
    if param_branch > cookie_branch:
        return (
            f"{LOCALE_RESOLVE}: cookie havoladan USTUN — ulashilgan havola "
            "o'z tilini olib kelmaydi (qaror S5)"
        )

    proxy = read(PROXY)
    if "request.nextUrl.searchParams.get(LOCALE_PARAM)" not in proxy:
        return f"{PROXY}: `?lang=` o'qilmaydi — havoladagi til e'tiborsiz qoladi"
    header_set = proxy.find("requestHeaders.set(LOCALE_HEADER, fromParam)")
    next_call = proxy.find("NextResponse.next({ request: { headers: requestHeaders } })")
    if header_set < 0 or next_call < 0:
        return f"{PROXY}: til sarlavhasi yoki `next()` chaqiruvi topilmadi"
    if header_set > next_call:
        return (
            f"{PROXY}: sarlavha `next()` dan KEYIN yozilgan — `next()` "
            "`request.headers` ni chaqiruv paytida ko'chiradi "
            "(`response.js:128`), ya'ni joriy javob eski tilda chiziladi"
        )
    if "response.cookies.set(LOCALE_COOKIE, locale" not in proxy:
        return f"{PROXY}: cookie yozilmaydi — qurilma tilni eslab qolmaydi"
    if "rememberLocale(response, fromParam)" not in proxy:
        return (
            f"{PROXY}: havoladagi til cookie'ga yozilmaydi — birinchi "
            "sahifadan keyin til qaytib ketadi (qaror S5b)"
        )

    switch = read(LOCALE_SWITCH)
    if "url.searchParams.delete(LOCALE_PARAM)" not in switch:
        return (
            f"{LOCALE_SWITCH}: qo'lda tanlov `?lang=` ni tozalamaydi — "
            "havola parametri yangi tanlovni bosib ketadi"
        )
    return None


def homepage_guest_cdn_cache() -> str | None:
    """100k ochilishda bosh sahifa qotmasin (2026-09-19).

    Mehmon GET `/`: `public, s-maxage=30, stale-while-revalidate`.
    Kirgan: `private, no-store`. Cloudflare `/` ni Worker'siz, origin
    header bo'yicha keshlaydi. Catch-all `rankwant.uz/*` qaytsa GET `/`
    yana har so'rovda Worker kvotasini yeydi.
    """
    src = read(HOME_CACHE)
    if "public, s-maxage=30, stale-while-revalidate=86400" not in src:
        return (
            f"{HOME_CACHE}: mehmon Cache-Control `public, s-maxage=30, "
            "stale-while-revalidate` emas"
        )
    if 'HOME_CACHE_PRIVATE = "private, no-store"' not in src:
        return f"{HOME_CACHE}: kirgan Cache-Control `private, no-store` emas"
    if 'SESSION_COOKIE = "sessionid"' not in src:
        return f"{HOME_CACHE}: sessiya cookie `sessionid` emas"
    if "export function homeCacheDecision" not in src:
        return f"{HOME_CACHE}: `homeCacheDecision` yo'q"

    proxy = read(PROXY)
    if "homeCacheDecision" not in proxy:
        return f"{PROXY}: bosh sahifa kesh qarori qo'llanmaydi"
    if "homeCache.assignExperiments" not in proxy:
        return (
            f"{PROXY}: keshlangan GET `/` ga eksperiment cookie yozilishi "
            "mumkin — Cloudflare Set-Cookie'li javobni saqlamaydi"
        )

    toml = read(WORKER_TOML)
    if '{ pattern = "rankwant.uz/*"' in toml:
        return (
            f"{WORKER_TOML}: catch-all `rankwant.uz/*` GET `/` ni Worker'ga "
            "qaytaradi (kvota)"
        )
    if '{ pattern = "www.rankwant.uz/*"' in toml:
        return (
            f"{WORKER_TOML}: catch-all `www.rankwant.uz/*` GET `/` ni "
            "Worker'ga qaytaradi"
        )
    if "rankwant.uz/a*" not in toml:
        return f"{WORKER_TOML}: `/` dan boshqa yo'llar Worker'siz qolmasin"
    return None


CF_GUEST_CACHE_RULE = "tools/cf-guest-cache-rule.json"
CF_GUEST_CACHE_APPLY = "tools/cf_guest_cache_apply.py"


def problems_list_guest_cdn() -> str | None:
    """2026-09-20 HITL problems-al: `/problems` mehmon CDN, til majburiy emas.

    Query'siz; `uz` force yo'q (`Vary: Accept-Language`). Worker `problems*`
    kvotani yeydi — faqat `problems/*` (slug). CF Cache Rule `Eligible`.
    """
    src = read(HOME_CACHE)
    if 'PROBLEMS_CACHE_PATH = "/problems"' not in src:
        return f"{HOME_CACHE}: `/problems` kesh yo'li yo'q"
    if "isLocaleAwareGuestCachePath" not in src:
        return f"{HOME_CACHE}: tilga bog'liq kesh yo'li yo'q"
    if "forceDefaultLocale: uzForced" not in src:
        return f"{HOME_CACHE}: `/problems` ham `uz` majburiy — Vary foydasiz"
    if 'HOME_CACHE_MARK_GUEST_LOCALE = "guest-al"' not in src:
        return f"{HOME_CACHE}: tilga bog'liq kesh belgisi yo'q"
    inst = read("apps/web/src/instrumentation.ts")
    if "HOME_CACHE_MARK_GUEST_LOCALE" not in inst:
        return "apps/web/src/instrumentation.ts: guest-al Vary yozilmaydi"
    if "Accept-Language" not in inst:
        return "apps/web/src/instrumentation.ts: origin Vary da Accept-Language yo'q"
    toml = read(WORKER_TOML)
    if '{ pattern = "rankwant.uz/problems*"' in toml:
        return f"{WORKER_TOML}: `problems*` ro'yxatni Worker kvotasiga qaytaradi"
    if '{ pattern = "www.rankwant.uz/problems*"' in toml:
        return f"{WORKER_TOML}: www `problems*` ro'yxatni Worker kvotasiga qaytaradi"
    if '{ pattern = "rankwant.uz/problems/*"' not in toml:
        return f"{WORKER_TOML}: slug sahifalari `problems/*` siz 503 yo'q"
    spec = read(CF_GUEST_CACHE_RULE)
    if 'path eq \\"/problems\\"' not in spec:
        return f"{CF_GUEST_CACHE_RULE}: `/problems` Eligible emas — CF DYNAMIC"
    if '"cache": true' not in spec:
        return f"{CF_GUEST_CACHE_RULE}: cache true emas"
    if '"accept-language"' not in spec:
        return f"{CF_GUEST_CACHE_RULE}: Cache Rule Vary Accept-Language yo'q"
    if '"normalize"' not in spec:
        return f"{CF_GUEST_CACHE_RULE}: Accept-Language normalize emas — Free Vary kalitlamaydi"
    if '"passthrough"' not in spec:
        return (
            f"{CF_GUEST_CACHE_RULE}: Vary default `bypass` Next RSC tokenlarida "
            "CDN ni o'chiradi — `passthrough` kerak"
        )
    apply = read(CF_GUEST_CACHE_APPLY)
    if "rankwant_guest_html_cache" not in apply:
        return f"{CF_GUEST_CACHE_APPLY}: qoida ref i yo'q"
    if "boshqa cache qoidalari saqlanadi" not in apply:
        return f"{CF_GUEST_CACHE_APPLY}: butun ruleset o'chirilishi mumkin"
    return None


def guest_auth_cdn_cache() -> str | None:
    """50k: login/register/terms/privacy mehmon HTML + Worker tashqarida.

    `rw_exp` keshlangan yo'lda yozilmasin (`assignExperiments: false`).
    `l*` `/login` ni Worker'ga qaytarardi (~200 ms, 100k/kun).
    """
    src = read(HOME_CACHE)
    if "export function isGuestCachePath" not in src:
        return f"{HOME_CACHE}: `isGuestCachePath` yo'q"
    if '"/login"' not in src or '"/terms"' not in src or '"/privacy"' not in src:
        return f"{HOME_CACHE}: mehmon yo'llari `/login` `/terms` `/privacy` emas"
    if "assignExperiments: false" not in src:
        return f"{HOME_CACHE}: keshlangan mehmonga eksperiment cookie yoziladi"

    toml = read(WORKER_TOML)
    if '{ pattern = "rankwant.uz/l*"' in toml:
        return f"{WORKER_TOML}: `l*` `/login` ni Worker'ga qaytaradi (kvota)"
    if '{ pattern = "www.rankwant.uz/l*"' in toml:
        return f"{WORKER_TOML}: www `l*` `/login` ni Worker'ga qaytaradi"
    if "rankwant.uz/leaderboard*" not in toml:
        return f"{WORKER_TOML}: `/leaderboard` Worker'siz qolmasin"
    return None


def scale_50k_locked() -> str | None:
    """2026-09-19: 7 ta 50k qaror kodda qolsin (Sentry/Kafka/K8s yo'q)."""
    views = read("apps/api/core/views.py")
    if "class SloView" not in views:
        return "apps/api/core/views.py: SloView yo'q (SLO, Sentry emas)"
    if "sentry_sdk" in views or "import sentry" in views:
        return "apps/api/core/views.py: Sentry qo'shilgan"
    cache_src = read("apps/api/core/cache.py")
    if "def cache_delete" not in cache_src:
        return "apps/api/core/cache.py: cache_delete yo'q"
    compose = read("docker-compose.yml")
    if "shared_preload_libraries=pg_stat_statements" not in compose:
        return "docker-compose.yml: pg_stat_statements preload yo'q"
    if "GUNICORN_WORKERS" not in compose:
        return "docker-compose.yml: GUNICORN_WORKERS yo'q"
    replicas = read("docker-compose.replicas.yml")
    if "origin-lb" not in replicas or "--scale web=2" not in replicas:
        return "docker-compose.replicas.yml: web×2/api×2 overlay emas"
    four = read("compose/four-host/README.md")
    if "K8s yo" not in four and "K8s yo‘q" not in four:
        return "compose/four-host/README.md: to'rt-host qaror yo'q"
    req = read("apps/api/requirements.lock")
    if "sentry-sdk" in req:
        return "apps/api/requirements.lock: sentry-sdk (Sentry kerakmas)"
    if "confluent-kafka" in req or "kafka-python" in req:
        return "apps/api/requirements.lock: Kafka qo'shilgan"
    return None


def roles_groups_and_object_authors() -> str | None:
    """ADR-0025: staff Groups + obyekt M2M, User.role CharField yo'q."""
    groups = read("apps/api/core/groups.py")
    if 'GROUPS: tuple[str, ...] = ("staff-support", "staff-content", "staff-ops")' not in groups:
        return "apps/api/core/groups.py: GROUPS staff-support/content/ops emas"
    if "def sync_staff_groups" not in groups:
        return "apps/api/core/groups.py: sync_staff_groups yo'q"

    contests = read("apps/api/contests/models.py")
    if "organizers" not in contests or 'related_name="organized_contests"' not in contests:
        return "apps/api/contests/models.py: organizers M2M yo'q"

    problems = read("apps/api/problems/models.py")
    if "authors" not in problems or 'related_name="authored_problems"' not in problems:
        return "apps/api/problems/models.py: authors M2M yo'q"

    if 'router.register("contests/mine"' not in read("apps/api/contests/urls.py"):
        return "apps/api/contests/urls.py: contests/mine yo'q"
    if 'router.register("problems/mine"' not in read("apps/api/problems/urls.py"):
        return "apps/api/problems/urls.py: problems/mine yo'q"

    seed = read("apps/api/core/migrations/0021_seed_staff_groups.py")
    if "staff-support" not in seed or "is_staff=True" not in seed:
        return "0021_seed_staff_groups: mavjud staff guruhlarga qo'shilmaydi"

    if "role = models.CharField" in read("apps/api/core/models.py"):
        return "apps/api/core/models.py: User.role CharField qaytdi (ADR-0025 Groups)"
    return None


AUTO_DEPLOY = "tools/auto_deploy.sh"
ROLLBACK = "tools/rollback.sh"
CHECK_DEPLOY = "tools/check_deploy.sh"
DEPLOY_SCOPE = "tools/deploy_scope.py"
KICK_AUTO_DEPLOY = "tools/kick_auto_deploy.sh"


def deploy_automation_is_safe() -> str | None:
    """Avtomatik deploy zanjiri — tartib buzilsa JIM buziladigan yetti joy.

    Saidakbar aka qarori (2026-09-19): deploy to'liq avtomatik bo'ladi —
    host watcher orqali (`tools/auto_deploy.sh` + `RankWant Auto Deploy`
    vazifasi). ⚠️ GitHub Actions'dagi `deploy` job ATAYLAB qo'lda qoladi
    (`deploy_manual_only`): o'lchandi — runner konteyneri jonli
    `.env.public` ni ko'rmaydi (u `/work` volume'ida) va unda `gh` yo'q,
    ya'ni u `check_deploy_gate.py` ni yurgiza olmaydi. Shuning uchun
    avtomatlashtirish Actions'ni yoqish bilan emas, watcher bilan qurildi.

    Beshta shart tartibga bog'liq: buzilganda kod ISHLAYDI, natija esa
    noto'g'ri bo'ladi — ya'ni xato faqat hodisa paytida bilinadi.
    Qolgan ikkitasi (6, 7) 2026-09-19 da birinchi haqiqiy yurishda
    o'lchandi va BIR XIL sababga ega: ular faqat zanjir BUTUN yurganda
    ko'rinadi, ya'ni unit darajasidagi tekshiruvlar ularni o'tkazib
    yuboradi.

    1. ZAXIRA MIGRATSIYADAN OLDIN. `backup.sh --dump-only` `run --rm
       migrate` dan keyin tursa sxema zaxirasiz o'zgaradi va qaytish yo'li
       qolmaydi — Django'da «orqaga» migratsiya yo'q, oylik to'liq zaxira
       esa 30 kungacha orqada bo'lishi mumkin.
    2. MUZLATISH QULFDAN OLDIN. Aks holda muzlatilgan tizim qulfni band
       qiladi va boshqa agentning deploy'i «band» deb xato o'qiladi.
    3. SHA TEG SAQLANMAYDI. `rankwant/<svc>:<sha>` har deploy'da
       qolsa VHDX o'saveradi (40→132 GB, 2026-09-15..20). Tasdiq'dan
       keyin `prune_docker_disk.sh` chaqiriladi.
    4. WATCHER'DA TIRIKLIK TEKSHIRUVI. `check_deploy.sh` konteyner YO'Q
       bo'lganda ham 0 qaytaradi (o'lchandi 2026-09-19: `missing` faqat
       xabar uchun, `exit 1` esa faqat `stale`/`envbad` da), ya'ni stack
       yiqilgan bo'lsa «joriy kodda» deb YOLG'ON YASHIL beradi. `all_up`
       shu teshikni yopadi.
    5. ENV-FAYL IKKALA JOYDA BIR XIL. Deploy worktree'da `.env.public`
       YO'Q (`.gitignore`: `.env.*`), ya'ni watcher uni
       `RANKWANT_AUTO_DEPLOY_ENV` bilan ko'rsatadi. Tekshiruv ham,
       `deploy.sh` ga uzatish ham `$ENV_FILE` dan o'qilmasa, watcher bir
       faylni tekshirib boshqasini uzatadi: deploy bo'sh env bilan ketadi,
       API har so'rovga 400 qaytaradi — xato faqat jonli saytda bilinadi.
    6. QULF QAYTA OLINMAYDI. Watcher qulfni o'zi oladi, `deploy.sh` esa
       AYNAN o'sha qulfni so'rab `mkdir` da yiqiladi — watcher o'zini
       bloklaydi va avtomatik deploy hech qachon ishlamaydi. Chaqiruvchi
       `RANKWANT_LOCK_HELD=1` bilan qulfni topshiradi.
    7. STDIN YOPIQ EMAS. Vazifa (`conhost --headless`) stdin bermaydi;
       MSYS `sha256sum` yopiq fd bilan yiqiladi, xato `2>/dev/null` ortida
       qoladi va `check_deploy.sh` YOLG'ON «ESKIRGAN» deydi. Watcher
       `exec 0</dev/null` bilan ochadi, `check_deploy.sh` esa o'zi ham
       `sha256sum` ga `< /dev/null` beradi.
    """
    deploy = read("tools/deploy.sh")
    auto = read(AUTO_DEPLOY)
    try:
        read(ROLLBACK)
    except Unreadable:
        return f"{ROLLBACK} yo'q — avtomatik deploy yiqilganda qaytish yo'li yo'q"

    def position(text: str, needle: str) -> int:
        return text.find(needle)

    backup_at = position(deploy, "bash tools/backup.sh --dump-only")
    migrate_at = position(deploy, "run --rm migrate")
    if backup_at < 0:
        return "tools/deploy.sh migratsiyadan oldin zaxira olmaydi (`backup.sh --dump-only` yo'q)"
    if migrate_at < 0:
        return "tools/deploy.sh da `run --rm migrate` topilmadi"
    if backup_at > migrate_at:
        return "tools/deploy.sh: zaxira migratsiyadan KEYIN — sxema zaxirasiz o'zgaradi"

    freeze_at = position(deploy, '[ -n "${DEPLOY_FREEZE:-}" ]')
    lock_at = position(deploy, 'mkdir "$LOCK"')
    if freeze_at < 0:
        return "tools/deploy.sh da muzlatish kaliti (`DEPLOY_FREEZE`) yo'q"
    if lock_at < 0:
        return "tools/deploy.sh deploy qulfini olmaydi"
    if freeze_at > lock_at:
        return "tools/deploy.sh: muzlatish qulfdan KEYIN — qulf behuda band bo'ladi"

    if "rankwant/${svc}:${SHA_TAG}" in deploy:
        return "tools/deploy.sh SHA tegini saqlaydi — VHDX o'saveradi (2026-09-20: hammasi tozalanadi)"
    up_at = position(deploy, 'up -d --no-deps "${BUILD_SERVICES[@]}"')
    if up_at < 0:
        up_at = position(deploy, 'up -d --no-deps "${SERVICES[@]}"')
    if up_at < 0:
        return "tools/deploy.sh da `up -d --no-deps` topilmadi"
    check_at = position(deploy, "bash tools/check_deploy.sh")
    prune_at = position(deploy, "bash tools/prune_docker_disk.sh")
    if prune_at < 0:
        return "tools/deploy.sh disk tozalamaydi (`prune_docker_disk.sh` yo'q)"
    if check_at < 0:
        return "tools/deploy.sh da `check_deploy.sh` topilmadi"
    if prune_at < check_at:
        return "tools/deploy.sh: disk tozalash tasdiqdan OLDIN — yiqilgan deploy ham cache ni o'chiradi"

    if "if all_up; then" not in auto:
        return (
            f"{AUTO_DEPLOY}: konteynerlar tirikligi tekshirilmaydi — "
            "`check_deploy.sh` stack yiqilganda ham 0 qaytaradi"
        )
    if 'mkdir "$LOCK"' not in auto:
        return f"{AUTO_DEPLOY}: qulfni olmaydi — qo'lda deploy bilan to'qnashadi"
    attempt_at = position(auto, 'record_attempt "$TARGET"')
    deploy_at = position(auto, "bash tools/deploy.sh --yes")
    if attempt_at < 0:
        return f"{AUTO_DEPLOY}: urinish yozilmaydi — yiqilgan deploy har 5 daqiqada takrorlanadi"
    if deploy_at < 0:
        return f"{AUTO_DEPLOY}: `deploy.sh --yes` chaqirilmaydi"
    if attempt_at > deploy_at:
        return f"{AUTO_DEPLOY}: urinish deploy'dan KEYIN yoziladi — yiqilgan yurish takrorlanadi"

    # Env-fayl worktree'dan TASHQARIDA: `.env.public` `.gitignore` da
    # (`.env.*`), ya'ni yangi worktree'da u yo'q. Ikkala joy BIR XIL
    # o'zgaruvchidan o'qilishi shart — tekshiruv ham, `deploy.sh` ga
    # uzatish ham `$ENV_FILE` dan. Ajralib ketsa watcher bir faylni
    # tekshirib, boshqasini uzatardi: deploy bo'sh env bilan ketadi va API
    # har so'rovga 400 qaytaradi — jimgina, faqat jonli saytda bilinadi.
    if "RANKWANT_AUTO_DEPLOY_ENV:-$LIVE_DIR/.env.public" not in auto:
        return (
            f"{AUTO_DEPLOY}: env-fayl worktree'dan tashqarida "
            "ko'rsatilmaydi (`RANKWANT_AUTO_DEPLOY_ENV`)"
        )
    if '[ -f "$ENV_FILE" ] || die' not in auto:
        return f"{AUTO_DEPLOY}: env-fayl mavjudligi tekshirilmaydi"
    if 'RANKWANT_ENV_FILE="$ENV_FILE"' not in auto:
        return f"{AUTO_DEPLOY}: `deploy.sh` ga boshqa env-fayl uzatiladi"

    # ⚠️ Ikki nosozlik 2026-09-19 da BIRINCHI HAQIQIY yurishda o'lchandi —
    # ikkalasi ham «yashil» unit tekshiruvlardan o'tib ketgan edi, chunki
    # faqat zanjir BUTUN yurganda ko'rinadi. Ikkalasi ham jim: biri deploy
    # qilishni butunlay to'xtatadi, ikkinchisi esa uni behuda qo'zg'atadi.
    #
    # 6. QULF QAYTA OLINMAYDI. Watcher qulfni o'zi oladi (qo'lda deploy
    #    bilan to'qnashmasin), keyin `deploy.sh` AYNAN o'sha qulfni
    #    so'raydi va `mkdir` da yiqiladi — ya'ni watcher O'ZINI bloklaydi
    #    va avtomatik deploy HECH QACHON ishlamaydi. O'lchandi: log'da
    #    «✗ boshqa deploy ishlayapti (auto-deploy pid 1303)».
    # 7. STDIN YOPIQ BO'LMASIN. Task Scheduler → `conhost --headless`
    #    farzandga stdin bermaydi; MSYS `sha256sum` yopiq fd bilan
    #    yiqiladi («failed to set file descriptor text/binary mode»),
    #    xato `2>/dev/null` ortida qoladi va `check_deploy.sh` YOLG'ON
    #    «ESKIRGAN» deydi. O'lchandi: qo'lda «joriy», vazifada «3
    #    konteyner eskirgan» — ya'ni watcher behuda deploy qo'zg'atadi.
    if "RANKWANT_LOCK_HELD=1 RANKWANT_ENV_FILE" not in auto:
        return (
            f"{AUTO_DEPLOY}: qulfni `deploy.sh` ga topshirmaydi — watcher "
            "o'zini bloklaydi, deploy hech qachon ishlamaydi"
        )
    if '${RANKWANT_LOCK_HELD:-0}' not in deploy:
        return (
            "tools/deploy.sh: `RANKWANT_LOCK_HELD` ni tan olmaydi — "
            "watcher'ning qulf topshirishi ishlamaydi"
        )
    if "exec 0</dev/null" not in auto:
        return (
            f"{AUTO_DEPLOY}: stdin'ni ochmaydi — vazifada `sha256sum` "
            "yiqilib yolg'on drift chiqaradi"
        )
    if 'sha256sum "$src" < /dev/null' not in read(CHECK_DEPLOY):
        return (
            f"{CHECK_DEPLOY}: `sha256sum` atrofdagi stdin'ga tayanadi — "
            "yopiq stdin'da yolg'on «ESKIRGAN»"
        )
    # 8. SORT LOCALE. Git Bash va Alpine `sort` har xil collate; `comm`
    #    tartiblanmagan input da yolg'on missing chiqaradi. O'lchandi
    #    2026-09-20: `./arena/migrations/__init__.py` konteynerda BOR,
    #    yorliq HEAD, 3 Python servis «ESKIRGAN», auto-deploy 1800s to'siq.
    check = read(CHECK_DEPLOY)
    if "| LC_ALL=C sort )" not in check or '| LC_ALL=C sort"' not in check:
        return (
            f"{CHECK_DEPLOY}: inventory locale'siz sort — comm yolg'on «ESKIRGAN»"
        )
    return None


def deploy_skips_non_image_bake() -> str | None:
    """2026-09-20: docs/tools bake yo'q; judge faqat manba; health; kick.

    O'lchangan: obrazga tushmaydigan PR dan keyin 2.6 min (judge miss
    16 min); watcher 5 min teshik; tools-only npm ci 14–20 s; verify
    sleep 10.
    """
    scope = read(DEPLOY_SCOPE)
    for needle in ("apps/api", "apps/web", "services/judge-go", "tools/deploy.sh"):
        if needle not in scope:
            return f"{DEPLOY_SCOPE}: {needle} yo'li yo'q"
    if "ALL_SERVICES" not in scope:
        return f"{DEPLOY_SCOPE}: servis ro'yxati yo'q"

    deploy = read("tools/deploy.sh")
    if "deploy_scope.py" not in deploy:
        return "tools/deploy.sh: deploy_scope.py chaqirilmaydi — docs/tools ham bake qiladi"
    if "wait_health" not in deploy or "api/v1/health" not in deploy:
        return "tools/deploy.sh: health kutish yo'q"
    verify = deploy.split("time_begin verify", 1)[-1].split("time_finish verify", 1)[0]
    if re.search(r"^sleep 10\b", verify, re.M):
        return "tools/deploy.sh verify: sleep 10 — health emas"

    auto = read(AUTO_DEPLOY)
    if "deploy_scope.py" not in auto:
        return f"{AUTO_DEPLOY}: obraz doirasi hisoblanmaydi"
    if 'log "obrazga tushmaydi — bake yo\'q' not in auto:
        return f"{AUTO_DEPLOY}: bo'sh doirada bake o'tkazilmaydi"

    kick = read(KICK_AUTO_DEPLOY)
    if 'schtasks /run /tn "RankWant Auto Deploy"' not in kick:
        return f"{KICK_AUTO_DEPLOY}: schtasks /run yo'q"
    if "MSYS_NO_PATHCONV=1" not in kick:
        return f"{KICK_AUTO_DEPLOY}: Git Bash /run ni yo'lga aylantiradi"

    hook = read(".githooks/pre-push")
    if "check_negative.py" not in hook or "decisions" not in hook:
        return "pre-push: deploy.sh o'zgarsa decisions ishlamaydi"

    ci = read(".github/workflows/ci.yml")
    if "tools_node" not in ci or "NEGATIVE_SKIP_NODE" not in ci:
        return "ci.yml: Python-only tools ham npm ci qiladi"
    return None


def docker_disk_stays_bounded() -> str | None:
    """2026-09-20: log 10m/3, builder GC 5GB, SHA teg yo'q, prune tasdiq'dan keyin.

    O'lchandi: docker_data.vhdx 5 kunda 40 GB → 132 GB. Ildiz — cheksiz
    json-file log, 20 GB builder cache, har deploy'dagi SHA teglar.
    """
    for rel, min_logging in (
        ("docker-compose.yml", 9),
        ("docker-compose.public.yml", 9),
        ("docker-compose.ci.yml", 2),
        ("docker-compose.replicas.yml", 1),
        ("tools/runner/docker-compose.runner.yml", 2),
    ):
        text = read(rel)
        if 'max-size: "10m"' not in text or 'max-file: "3"' not in text:
            return f"{rel}: json-file log cheklovi yo'q (max-size 10m / max-file 3)"
        n = text.count("logging:")
        if n < min_logging:
            return f"{rel}: logging {n} ta (kamida {min_logging} servis kerak)"

    daemon = read("tools/docker-daemon.json")
    if '"defaultKeepStorage": "5GB"' not in daemon:
        return "tools/docker-daemon.json: builder GC 5GB emas"
    if '"max-size": "10m"' not in daemon or '"max-file": "3"' not in daemon:
        return "tools/docker-daemon.json: json-file 10m/3 emas"

    prune = read("tools/prune_docker_disk.sh")
    if "docker image prune -f" not in prune:
        return "tools/prune_docker_disk.sh: `docker image prune -f` yo'q"
    if "docker builder prune -f" not in prune:
        return "tools/prune_docker_disk.sh: `docker builder prune -f` yo'q"
    if "docker volume prune" in prune:
        return "tools/prune_docker_disk.sh: volume prune — postgres/minio o'chadi"
    if "docker builder prune -af" in prune or "docker builder prune --all" in prune:
        return "tools/prune_docker_disk.sh: builder prune --all joriy cache ni ham o'chiradi"
    if not re.search(
        r"rankwant/\(api\|worker\|beat\|judge\|web\|migrate\):",
        prune,
    ):
        return "tools/prune_docker_disk.sh: SHA teg naqshi yo'q"
    if re.search(r"docker rmi\b.*ci-runner", prune):
        return "tools/prune_docker_disk.sh: ci-runner obrazi o'chiriladi"
    return None


def typescript_side_by_side() -> str | None:
    """2026-09-20: TS 7 native typecheck, TS 6 JS API `require("typescript")`.

    `typescript@7` Go rewrite — JS `transpileModule` yo'q. eslint-config-next
    peer <6.1; `i18n-runtime-hook.mjs` JS API ga tayanadi. Alias:
    `typescript` = @typescript/typescript6, `@typescript/native` = typescript@7.
    """
    pkg = read("apps/web/package.json")
    if '"typescript": "npm:@typescript/typescript6@' not in pkg:
        return "apps/web/package.json: `typescript` TS 6 JS API alias emas"
    if '"@typescript/native": "npm:typescript@7.' not in pkg:
        return "apps/web/package.json: `@typescript/native` TS 7 emas"
    if "tsc --noEmit" not in pkg:
        return "apps/web/package.json: typecheck native `tsc` ishlatmaydi"
    if "tsc6" in pkg:
        return "apps/web/package.json: typecheck `tsc6` (JS) — native `tsc` emas"
    if '"typescript": "npm:typescript@7' in pkg:
        return "apps/web/package.json: `typescript` o'zi 7 — JS API yo'qoladi"
    hook = read("tools/i18n-runtime-hook.mjs")
    if 'require("typescript")' not in hook:
        return "tools/i18n-runtime-hook.mjs: JS `typescript` API chaqirilmaydi"
    return None


def types_node_tracks_runtime() -> str | None:
    """2026-09-20: `@types/node` major = Node major (CI + image 22).

    Dependabot #143 `@types/node@26` ni Node 22 ustiga qo'ymoqchi edi.
    `skipLibCheck: true` shu yolg'on yashilni o'tkazib yuboradi.
    """
    pkg = read("apps/web/package.json")
    if '"@types/node": "22.' not in pkg:
        return "apps/web/package.json: `@types/node` Node 22 bilan mos emas"
    yml = read(".github/dependabot.yml")
    idx = yml.find('dependency-name: "@types/node"')
    if idx < 0:
        return ".github/dependabot.yml: `@types/node` ignore yo'q"
    if "version-update:semver-major" not in yml[idx : idx + 180]:
        return ".github/dependabot.yml: `@types/node` major ignore yo'q"
    if "node-version: '22'" not in read(".github/workflows/ci.yml"):
        return ".github/workflows/ci.yml: Node 22 emas"
    if read("apps/web/Dockerfile").count("FROM node:22-slim") < 3:
        return "apps/web/Dockerfile: image Node 22 emas (3 bosqich kerak)"
    return None


KIT_TS = "apps/web/src/lib/theme/kit.ts"
COPY_CONTROL = "apps/web/src/components/kit/CopyControl.tsx"
CMD_PALETTE = "apps/web/src/components/kit/CommandPalette.tsx"
SHARE_BUTTON = "apps/web/src/components/profile/ShareButton.tsx"


def selected_kit_frozen() -> str | None:
    """2026-09-20 HITL fail-toast-freeze: tanlangan kit + clipboard xato toast.

    Omitted variants (confirm v2/v3/v6/v7/v8, check v10 `big`, copy v9 `burn`)
    and MiniCal/Notificationsi/countdown polish stay out unless asked.
    """
    kit = read(KIT_TS)
    if '"burn"' in kit:
        return f"{KIT_TS}: copy v9 `burn` qaytdi — tanlangan kitda yo'q"
    if '"big"' in kit:
        return f"{KIT_TS}: check v10 `big` qaytdi — tanlangan kitda yo'q"
    copy = read(COPY_CONTROL)
    if copy.count("problem.copyFailed") < 2:
        return f"{COPY_CONTROL}: clipboard xatoda `problem.copyFailed` toast to'liq emas"
    cmdk = read(CMD_PALETTE)
    if "problem.copyFailed" not in cmdk:
        return f"{CMD_PALETTE}: clipboard xatoda `problem.copyFailed` toast yo'q"
    if ".catch(() => {})" in cmdk:
        return f"{CMD_PALETTE}: clipboard xatoni yutadi"
    share = read(SHARE_BUTTON)
    if "problem.copyFailed" not in share:
        return f"{SHARE_BUTTON}: clipboard xatoda `problem.copyFailed` toast yo'q"
    return None


def eslint_ten_uses_ts_parser() -> str | None:
    """2026-09-20: ESLint 10 + typescript-eslint parser (Next babel parser yo'q).

    eslint-config-next 16.3.5 compiled babel parser ESLint 10 ScopeManager
    (`addGlobals`) bermaydi — lint TypeError. `.mts` ham shu parserda.
    """
    pkg = read("apps/web/package.json")
    if '"eslint": "^10.' not in pkg and '"eslint": "10.' not in pkg:
        return "apps/web/package.json: ESLint 10 emas"
    cfg = read("apps/web/eslint.config.mjs")
    if "parser: tseslint.parser" not in cfg:
        return "apps/web/eslint.config.mjs: typescript-eslint parser yo'q (Next babel ESLint 10 da yiqiladi)"
    if "eslint-config-next/parser" in cfg:
        return "apps/web/eslint.config.mjs: Next babel parser qaytdi"
    return None


def pytest_nine_and_django_plugin() -> str | None:
    """2026-09-20 HITL: pytest ≥9.1.1 va pytest-django ≥4.14 birga.

    Lock allaqachon 9.1.1 / 4.14.0 edi; floor `>=8` / `>=4.9` qolsa
    `uv pip compile` pytest 8 ga qaytishi mumkin. pytest-django 4.14
    pytest 9 uchun; 4.9 yetarli emas.
    """
    floors = read("apps/api/requirements-dev.txt")
    if not re.search(r"(?m)^pytest>=9\.1\.1$", floors):
        return "apps/api/requirements-dev.txt: pytest floor 9.1.1 emas"
    if not re.search(r"(?m)^pytest-django>=4\.14\.0$", floors):
        return "apps/api/requirements-dev.txt: pytest-django floor 4.14.0 emas"
    lock = read("apps/api/requirements-dev.lock")
    if not re.search(r"(?m)^pytest==9\.", lock):
        return "apps/api/requirements-dev.lock: pytest 9.x emas"
    if not re.search(r"(?m)^pytest-django==4\.14\.", lock):
        return "apps/api/requirements-dev.lock: pytest-django 4.14 emas"
    return None


def react_and_dom_stay_paired() -> str | None:
    """2026-09-20 HITL: react va react-dom 19.3 juftligi, ajratilmaydi.

    ViewTransition/Fragment refs shu PR da ishlatilmaydi. Juftlik buzilsa
    (react 19.3 + react-dom 19.0) runtime noaniq.
    """
    pkg = read("apps/web/package.json")

    def pin(name: str) -> str | None:
        m = re.search(rf'"{re.escape(name)}": "([^"]+)"', pkg)
        return m.group(1) if m else None

    react = pin("react")
    dom = pin("react-dom")
    if react is None or dom is None:
        return "apps/web/package.json: react yoki react-dom yo'q"
    if react != dom:
        return f"apps/web/package.json: react {react} ≠ react-dom {dom}"
    if not react.startswith("19.3."):
        return f"apps/web/package.json: react/react-dom {react} (19.3.x kerak)"
    types_r = pin("@types/react")
    types_d = pin("@types/react-dom")
    if types_r is None or types_d is None:
        return "apps/web/package.json: @types/react juftligi yo'q"
    if not types_r.startswith("19.3.") or not types_d.startswith("19.3."):
        return "apps/web/package.json: @types/react juftligi 19.3.x emas"
    cfg = read("apps/web/eslint.config.mjs")
    if 'version: "19.3.0"' not in cfg:
        return 'apps/web/eslint.config.mjs: react version 19.3.0 emas'
    return None


APP_LAYOUT = "apps/web/src/app/layout.tsx"
LANG_ALTERNATES = "apps/web/src/i18n/locale-alternates.ts"
LANG_ALTERNATES_SERVER = "apps/web/src/i18n/locale-alternates.server.ts"
PROBLEM_SLUG_PAGE = "apps/web/src/app/problems/[slug]/page.tsx"
UPDATE_ID_PAGE = "apps/web/src/app/updates/[id]/page.tsx"
ROADMAP_ID_PAGE = "apps/web/src/app/platform-roadmap/[id]/page.tsx"


def lang_query_self_canonical() -> str | None:
    """2026-09-20 HITL hreflang-self: `?lang=` o'ziga canonical + hreflang.

    `canonical: "./"` 10 tilni bitta URL qilardi. Cookie tilini
    canonical'ga yozmaslik — crawler cookie'siz. `uz` toza yo'l.
    """
    params = read(LOCALE_PARAMS)
    if 'export const LANG_PARAM_HEADER = "x-rw-lang-param";' not in params:
        return f"{LOCALE_PARAMS}: `LANG_PARAM_HEADER` yo'q — layout `?lang=` ni ko'rmaydi"
    helper = read(LANG_ALTERNATES)
    if '"x-default"' not in helper:
        return f"{LANG_ALTERNATES}: `x-default` hreflang yo'q"
    if "hrefForLocale" not in helper or "localeAlternates" not in helper:
        return f"{LANG_ALTERNATES}: canonical/hreflang helper yo'q"
    if "DEFAULT_LOCALE" not in helper:
        return f"{LANG_ALTERNATES}: `uz` toza yo'l qoidasi yo'q"
    server = read(LANG_ALTERNATES_SERVER)
    if "localeAlternatesFor" not in server or "LANG_PARAM_HEADER" not in server:
        return f"{LANG_ALTERNATES_SERVER}: layout `?lang=` sarlavhasini o'qimaydi"
    layout = read(APP_LAYOUT)
    if 'alternates: { canonical: "./" }' in layout:
        return f"{APP_LAYOUT}: canonical `./` — `?lang=` o'ziga yig'ilmaydi"
    if "localeAlternatesFor" not in layout:
        return f"{APP_LAYOUT}: hreflang/canonical helper chaqirilmaydi"
    proxy = read(PROXY)
    param_hdr = proxy.find("requestHeaders.set(LANG_PARAM_HEADER, fromParam)")
    next_call = proxy.find("NextResponse.next({ request: { headers: requestHeaders } })")
    if param_hdr < 0:
        return f"{PROXY}: `LANG_PARAM_HEADER` yozilmaydi — canonical cookie tilini oladi"
    if next_call < 0 or param_hdr > next_call:
        return f"{PROXY}: `LANG_PARAM_HEADER` `next()` dan keyin — joriy render ko'rmaydi"
    for rel in (PROBLEM_SLUG_PAGE, UPDATE_ID_PAGE, ROADMAP_ID_PAGE):
        page = read(rel)
        if "localeAlternatesFor" not in page:
            return f"{rel}: sahifa canonical hreflang'ni yutadi"
        if "alternates: { canonical:" in page:
            return f"{rel}: til'siz canonical qaytdi"
    return None


SITEMAP = "apps/web/src/app/sitemap.ts"


def sitemap_locale_xhtml_alternates() -> str | None:
    """2026-09-20 HITL sitemap-hreflang: har yozuvda xhtml:link tillari.

    `url` toza uz yo'l; 10 til + x-default `alternates.languages` da.
    10× alohida `<url>` yo'q.
    """
    helper = read(LANG_ALTERNATES)
    if "sitemapLanguageAlternates" not in helper:
        return f"{LANG_ALTERNATES}: sitemap til helper yo'q"
    sitemap = read(SITEMAP)
    if "sitemapLanguageAlternates" not in sitemap:
        return f"{SITEMAP}: xhtml:link tillari chaqirilmaydi"
    if "alternates: { languages:" not in sitemap:
        return f"{SITEMAP}: alternates.languages yo'q"
    if sitemap.count("sitemapEntry(") < 3:
        return f"{SITEMAP}: statik/slug/id yozuvlari til'siz qolgan"
    if "url: absolute(`${prefix}" in sitemap:
        return f"{SITEMAP}: til'siz absolute() yozuvi qaytdi"
    return None


CF_VARY_JSON = "tools/cf-vary-accept-language.json"
CF_VARY_APPLY = "tools/cf_vary_apply.py"


def vary_accept_language_at_edge() -> str | None:
    """2026-09-20 HITL cf-transform: Vary Accept-Language chekkada `add`.

    Next.js 16 in-process `Vary` ni o'chiradi. `set` Next RSC tokenlarini
    yutadi. Mehmon kesh yo'llari chiqariladi — `uz` majburiy HTML 100k
    fragment bo'lmasin. Kesh doirasi kengaytirilmaydi.
    """
    spec = read(CF_VARY_JSON)
    if '"operation": "set"' in spec:
        return f"{CF_VARY_JSON}: `set` Next.js Vary tokenlarini o'chiradi — `add` kerak"
    if '"operation": "add"' not in spec:
        return f"{CF_VARY_JSON}: `add` yo'q"
    if '"value": "Accept-Language"' not in spec:
        return f"{CF_VARY_JSON}: `Accept-Language` yo'q"
    for path in ("/", "/login", "/register", "/terms", "/privacy"):
        needle = f'ne \\"{path}\\"'
        if needle not in spec:
            return (
                f"{CF_VARY_JSON}: mehmon kesh yo'li `{path}` chiqarilmagan — "
                "100k fragment"
            )
    if "text/html" not in spec:
        return f"{CF_VARY_JSON}: faqat HTML — static Vary fragment bo'lmasin"
    apply = read(CF_VARY_APPLY)
    if "rankwant_vary_accept_language" not in apply:
        return f"{CF_VARY_APPLY}: qoida ref i yo'q"
    if "boshqa transform qoidalari saqlanadi" not in apply:
        return f"{CF_VARY_APPLY}: butun ruleset o'chirilishi mumkin"
    return None


def aop_owned_paths_no_star_star() -> str | None:
    """2026-09-20 HITL no-star-star: owned_paths cannot lock the whole tree.

    Flexible slots mean any agent can take any task. A `**` or `apps/**`
    claim starves every other slot. Directory globs need ≥2 segments;
    several packages on one card stay legal. Predicate: tools/owned_paths.py.
    """
    src = ROOT / "tools" / "owned_paths.py"
    spec = importlib.util.spec_from_file_location("owned_paths", src)
    if spec is None or spec.loader is None:
        return "tools/owned_paths.py: yuklanmadi"
    owned_paths = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owned_paths)

    aop = read("docs/10-operations/parallel-agents.md")
    if "HITL 2026-09-20 `no-star-star`" not in aop:
        return "docs/10-operations/parallel-agents.md: no-star-star HITL yo'q"
    if "apps/**" not in aop:
        return "docs/10-operations/parallel-agents.md: `apps/**` taqiqi yo'q"
    if "legal_owned_path" not in aop:
        return "docs/10-operations/parallel-agents.md: `legal_owned_path` yo'q"
    if "no-star-star" not in read(".cursor/rules/parallel-agents.mdc"):
        return ".cursor/rules/parallel-agents.mdc: no-star-star yo'q"
    if "no-star-star" not in read("CONTRIBUTING.md"):
        return "CONTRIBUTING.md: no-star-star yo'q"
    for glob in owned_paths.ILLEGAL_OWNED_PATHS:
        if owned_paths.legal_owned_path(glob):
            return f"tools/owned_paths.py: `{glob}` no-star-star da qonuniy"
    for glob in owned_paths.LEGAL_OWNED_PATHS:
        if not owned_paths.legal_owned_path(glob):
            return f"tools/owned_paths.py: `{glob}` no-star-star da noqonuniy"
    return None


def aop_stale_worktree_reap() -> str | None:
    """2026-09-20 HITL stale-reap: leftover trees under your tool folder.

    Flexible slots have no janitor. `wt/deploy` and `cp/rankwant` stay.
    Another tool's folder is out of bounds.
    """
    aop = read("docs/10-operations/parallel-agents.md")
    if "HITL 2026-09-20 `stale-reap`" not in aop:
        return "docs/10-operations/parallel-agents.md: stale-reap HITL yo'q"
    if "wt/deploy" not in aop:
        return "docs/10-operations/parallel-agents.md: `wt/deploy` himoyasi yo'q"
    src = read("tools/reap_stale_worktrees.py")
    if "HITL 2026-09-20 `stale-reap`" not in src:
        return "tools/reap_stale_worktrees.py: stale-reap HITL yo'q"
    if 'NEVER_REAP = ("wt/deploy", "cp/rankwant")' not in src:
        return "tools/reap_stale_worktrees.py: NEVER_REAP `wt/deploy`/`cp/rankwant` emas"
    if "ALLOWED_TOOLS" not in src:
        return "tools/reap_stale_worktrees.py: ALLOWED_TOOLS yo'q"
    if "stale-reap" not in read(".cursor/rules/parallel-agents.mdc"):
        return ".cursor/rules/parallel-agents.mdc: stale-reap yo'q"
    if "stale-reap" not in read("CONTRIBUTING.md"):
        return "CONTRIBUTING.md: stale-reap yo'q"
    return None


def aop_restore_when_idle() -> str | None:
    """2026-09-20 HITL restore-when-idle: canonical tree back to origin/main.

    Dirty or claimed `cp/rankwant` is skipped. `git reset --hard` is forbidden.
    """
    aop = read("docs/10-operations/parallel-agents.md")
    if "HITL 2026-09-20 `restore-when-idle`" not in aop:
        return "docs/10-operations/parallel-agents.md: restore-when-idle HITL yo'q"
    src = read("tools/restore_canonical.py")
    if "HITL 2026-09-20 `restore-when-idle`" not in src:
        return "tools/restore_canonical.py: restore-when-idle HITL yo'q"
    if 'FORBIDDEN_GIT = ("reset", "clean")' not in src:
        return "tools/restore_canonical.py: FORBIDDEN_GIT reset/clean emas"
    if 'git(CANONICAL, "merge", "--ff-only", "origin/main")' not in src:
        return "tools/restore_canonical.py: ff-only yo'q"
    if "restore-when-idle" not in read(".cursor/rules/parallel-agents.mdc"):
        return ".cursor/rules/parallel-agents.mdc: restore-when-idle yo'q"
    if "restore-when-idle" not in read("CONTRIBUTING.md"):
        return "CONTRIBUTING.md: restore-when-idle yo'q"
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
    ("/users/ noindex", users_profiles_stay_noindex),
    ("rank colour_group 7 token", rank_colour_groups_not_sixteen_tokens),
    ("owned_paths no-star-star", aop_owned_paths_no_star_star),
    ("stale worktree reap", aop_stale_worktree_reap),
    ("canonical restore-when-idle", aop_restore_when_idle),
    ("navigatsiya prefetch'i niyatda", nav_prefetch_on_intent),
    ("bosh sahifa <main> prefetch'i niyatda", home_main_prefetch_on_intent),
    ("lug'at alohida faylda", dictionary_as_cached_file),
    ("lug'at qaytishda saqlanadi", dictionary_survives_return),
    ("User modeli tenglik maydonlari", user_parity_fields_kept),
    ("tor ekran 320 px ga sig'adi", mobile_header_fits_narrow_screen),
    ("mobil panel foydalanishga yaroqli", mobile_drawer_is_accessible),
    ("KPI to'ri lg da 4 ustun", kpi_grid_steps_at_lg),
    ("profil paneli xl gacha stekda", profile_sidebar_stacks_below_xl),
    ("diapazon bitta filtr", difficulty_range_counts_as_one_filter),
    ("brend headerda, footer uch ustun", brand_in_header_and_footer_columns),
    ("kontent qamrovi ko'rinadi", content_coverage_visible),
    ("til havolada ham keladi", locale_travels_in_the_url),
    ("bosh sahifa mehmon CDN keshi", homepage_guest_cdn_cache),
    ("login mehmon CDN keshi", guest_auth_cdn_cache),
    ("50k masshtab qarorlari", scale_50k_locked),
    ("staff guruhlari va obyekt mualliflari", roles_groups_and_object_authors),
    ("avtomatik deploy xavfsiz", deploy_automation_is_safe),
    ("docs/tools obraz qurilmasin", deploy_skips_non_image_bake),
    ("docker disk chegaralangan", docker_disk_stays_bounded),
    ("TypeScript 7 yonma-yon", typescript_side_by_side),
    ("@types/node runtime bilan", types_node_tracks_runtime),
    ("tanlangan kit muzlatilgan", selected_kit_frozen),
    ("ESLint 10 typescript parser", eslint_ten_uses_ts_parser),
    ("pytest 9 va pytest-django 4.14", pytest_nine_and_django_plugin),
    ("react va react-dom juft", react_and_dom_stay_paired),
    ("?lang= self-canonical hreflang", lang_query_self_canonical),
    ("sitemap xhtml:link tillari", sitemap_locale_xhtml_alternates),
    ("Vary Accept-Language chekkada", vary_accept_language_at_edge),
    ("arxiv ro'yxat mehmon CDN keshi", problems_list_guest_cdn),
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
