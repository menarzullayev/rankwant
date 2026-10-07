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
DEPLOYED_SERVICES = {"api", "worker", "beat", "judge", "web", "realtime"}
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
HOME_MAIN = "apps/web/src/app/(site)/page.tsx"
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
# Render-blocking CSS off the homepage critical path (HITL 2026-09-20).
WEB_NEXT_CONFIG = "apps/web/next.config.ts"
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
PROFILE_LAYOUT = "apps/web/src/app/(site)/users/[username]/layout.tsx"
# Filter badge: the difficulty range is one filter even though it rides in two
# params, so the badge counts it once. Owner decision 2026-09-18.
FILTERS = "apps/web/src/features/problems/components/ProblemFilters.tsx"
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
# RW-ARCH-013 moved the i18n mechanism (and with it `CONTENT_NAME_LOCALES` /
# `hasContentNames`) into the shared package; `messages.ts` is now a thin
# re-export shim, so the coverage source has to be read from core.ts.
SHARED_I18N_CORE = "packages/shared/src/i18n/core.ts"
CONTENT_BADGE = "apps/web/src/components/ui/UzFallbackBadge.tsx"
ARCHIVE_SIDEBAR = "apps/web/src/components/layout/ArchiveSidebar.tsx"
ABOUT_TAB = "apps/web/src/features/profile/components/AboutTab.tsx"
TOPIC_STRENGTH = "apps/web/src/features/profile/components/TopicStrength.tsx"
ACTIVITY_TABS = "apps/web/src/features/profile/components/ActivityTabs.tsx"
SKILLS_SECTION = "apps/web/src/features/account/components/SkillsSection.tsx"
PROBLEMS_PAGE = "apps/web/src/app/(site)/problems/page.tsx"

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
    css = read("apps/web/src/app/theme.css")
    if re.search(r"--rw-rank-\d", css):
        return "apps/web/src/app/theme.css: raqamli `--rw-rank-N` qaytdi (#167)"
    for name in ("grey", "green", "cyan", "blue", "violet", "orange", "red"):
        if f"--rw-rank-{name}" not in css:
            return f"apps/web/src/app/theme.css: `--rw-rank-{name}` yo'q"
    if "rw-rank-${title.colour_group}" not in read("apps/web/src/components/ui/Identity/UserName.tsx"):
        return "apps/web/src/components/ui/Identity/UserName.tsx: class `colour_group` emas"
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


def locale_use_is_unconditional() -> str | None:
    """`use()` hook tartibi hidratsiyada o'zgarmasin (HITL 2026-09-20).

    `if (typeof window && !hasMessages) use(loadDictionary)` serverda va
    tez mijozda hookni o'tkazib yubordi; Slow 4G + inline CSS (~551 KiB
    HTML) da lug'at hidratsiyadan kechikib hook QO'SHILDI. React minified
    #467 (`Update hook called on initial render`) — Lighthouse Best
    practices 100 → 96, AFTER-08, 2026-09-20.
    """
    src = read(LOCALE_PROVIDER)
    if "use(dictionaryReady(locale, dictionaryUrl))" not in src:
        return (
            f"{LOCALE_PROVIDER}: `use(dictionaryReady)` yo'q — "
            "sekin tarmoqda xom kalit yoki shartli hook (React #467)"
        )
    if re.search(
        r"if\s*\(\s*typeof window !== \"undefined\" && !hasMessages\(locale\)\)\s*\{\s*use\(",
        src,
    ):
        return (
            f"{LOCALE_PROVIDER}: shartli `use()` qaytdi — hidratsiyada React #467"
        )
    if "function dictionaryReady(" not in src:
        return f"{LOCALE_PROVIDER}: `dictionaryReady` yo'q — `use()` ga barqaror thenable kerak"
    if "const READY:" not in src and "const READY =" not in src:
        return f"{LOCALE_PROVIDER}: `READY` thenable yo'q — har render yangi `Promise.resolve()`"
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


#: Vaqt tamg'alari endi `core/bases.py` dan olinadi (qaror 2026-09-20:
#: abstrakt bazalar kiritildi, sxema o'zgarmadi). Modelda to'g'ridan-to'g'ri
#: e'lon faqat INDEKSLI `created_at` uchun qoladi — indeksni birxillashtirish
#: DDL bo'lgani uchun alohida qaror (`apps/api/core/bases.py` docstringi).
#:
#: 9 — o'lchandi 2026-09-20: core.EmailDelivery, core.EmailVerifyToken,
#: core.PasswordResetToken, judging.Attempt, notifications.Notification,
#: problems.ProblemReport, profiles.Follow, qvant.QvantTransaction, hacks.Hack.
TIMESTAMP_BASES = "apps/api/core/bases.py"
TIMESTAMP_INDEX_EXCEPTIONS = 9


def timestamps_come_from_bases() -> str | None:
    """Timestamp fields are declared once, in `core/bases.py`.

    Before the change every model wrote `created_at`/`updated_at` by hand —
    54 declarations of two identical expressions across 21 apps, and the
    copies had already drifted apart. A shared abstract base makes that
    drift impossible: there is one place to change.

    Nine indexed `created_at` fields stay declared on purpose. Normalising
    them is DDL, which is a separate decision — see the `core/bases.py`
    docstring. `updated_at` has no such exception: it never carries an index.
    """
    try:
        bases = read(TIMESTAMP_BASES)
    except Unreadable as exc:
        return f"{TIMESTAMP_BASES}: {exc}"
    for name in ("CreatedModel", "TimeStampedModel", "UpdatedModel"):
        if f"class {name}(models.Model):" not in bases:
            return f"{TIMESTAMP_BASES}: `{name}` bazasi yo'q"
    if bases.count("abstract = True") != 3:
        return f"{TIMESTAMP_BASES}: uchta abstrakt baza emas"
    direct = 0
    for path in sorted((ROOT / "apps/api").glob("*/models.py")):
        rel = path.relative_to(ROOT).as_posix()
        for line in read(rel).split("\n"):
            if line.startswith("    created_at = models.DateTimeField("):
                direct += 1
                if "db_index=True" not in line:
                    return f"{rel}: `created_at` indekssiz e'lon qilingan — bazadan oling"
            elif line.startswith("    updated_at = models.DateTimeField("):
                return f"{rel}: `updated_at` to'g'ridan-to'g'ri e'lon qilingan — bazadan oling"
    # `>` emas `!=`: `check_negative.py`'s decisions sandbox copies only the
    # files in `_DECISIONS_SANDBOX_FILES`, so a sandbox scan legitimately sees
    # one `models.py` instead of 21 and an equality check would fail there for
    # a reason that has nothing to do with the rule. The alarm that matters is
    # growth: a new model must not slip in with a hand-declared index.
    # Normalising an exception away is an improvement — lower the constant.
    if direct > TIMESTAMP_INDEX_EXCEPTIONS:
        return (
            f"indeksli `created_at` {direct} ta, ko'pi {TIMESTAMP_INDEX_EXCEPTIONS} — "
            "yangi istisno qo'shildi, `core/bases.py` dan oling"
        )
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

    # The lock itself lives in `lib/scroll.ts` since 2026-10-06 (counted,
    # shared with the search palette and the notification panel).
    if "    return lockBodyScroll();\n" not in read(APP_SHELL) or (
        'document.body.style.overflow = "hidden"' not in read("apps/web/src/lib/scroll.ts")
    ):
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
    # 2026-10-06: the footer was redesigned on the owner's request — a band
    # of its own, the brand from `BrandMark`, and three labelled link groups
    # (product, resources, contact) instead of one list.
    if "lg:grid-cols-[minmax(0,1.6fr)_repeat(3,minmax(0,1fr))]" not in footer:
        return (
            f"{APP_FOOTER}: footer guruhlarga bo'linmagan — brend, platforma, "
            "resurslar va aloqa alohida ustunlarda (qaror 22, 2026-10-06)"
        )
    if "<BrandMark variant=\"full\"" not in footer:
        return f"{APP_FOOTER}: brend `BrandMark` dan emas — wordmark yana nusxalangan (qaror 22)"
    if footer.count("<nav aria-labelledby=") != 3:
        return f"{APP_FOOTER}: uchta nomlangan havola guruhi (`<nav aria-labelledby>`) yo'q"
    # Twice: the link row and the wordmark link.
    if footer.count("[@media(pointer:coarse)]:min-h-11") < 2:
        return f"{APP_FOOTER}: havolalar sensorli ekranda 44 px emas"
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


def homepage_skips_cf_email_decode() -> str | None:
    """CF email-decode High script bosh sahifada bo'lmasin (HITL 2026-09-20).

    AFTER-09: `/cdn-cgi/scripts/.../email-decode.min.js` High (1 KiB) +
    `/cdn-cgi/rum`. Sabab — footer `support@rankwant.uz`. Manzil allaqachon
    ochiq (HITL confirm-current). `<!--email_off-->` CF ni script kiritishdan
    to'xtatadi. Beacon (analytics) alohida.
    """
    footer = read(APP_FOOTER)
    if "<!--email_off-->" not in footer or "<!--email_on-->" not in footer:
        return (
            f"{APP_FOOTER}: CF `<!--email_off-->` yo'q — email-decode High "
            "script Lighthouse tarmog'iga qaytadi"
        )
    if "<!--email_off--><a href=" not in footer:
        return (
            f"{APP_FOOTER}: `email_off` faqat matnni o'raydi — CF `mailto` "
            "href ni `/cdn-cgi/l/email-protection` qiladi va script qoladi "
            "(o'lchandi 2026-09-20, #198)"
        )
    if "dangerouslySetInnerHTML" not in footer:
        return (
            f"{APP_FOOTER}: `email_off` React kommentariyasida — HTML ga "
            "chiqmaydi, CF baribir script kiritadi"
        )
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

    ⚠️ Qamrov qoidalari `packages/shared/src/i18n/core.ts` ga ko'chdi
    (RW-ARCH-013). Ilova endi ularni QAYTA EKSPORT qiladi — ya'ni
    chaqiruv joylari o'zgarmagan, lekin HAQIQIY ta'rif shared paketda.
    Tekshiruv ikkala faylni birga o'qiydi, chunki qoida ikkalasida ham
    bo'lishi shart: ta'rif shared'da, ilova ulanishi `messages.ts` da.
    """
    shared = read(SHARED_I18N_CORE)
    messages = read(MESSAGES)
    combined = shared + messages
    if 'export const CONTENT_NAME_LOCALES = ["uz", "ru", "en"] as const;' not in combined:
        return f"{SHARED_I18N_CORE}: CONTENT_NAME_LOCALES yo'q — qamrov manbai yo'qolgan"
    if "export function hasContentNames(" not in combined:
        return f"{SHARED_I18N_CORE}: hasContentNames() yo'q — tanlash ro'yxati qamrovni bilmaydi"
    if "function nameProperty(" not in combined:
        return f"{SHARED_I18N_CORE}: nameProperty() yo'q — yetishmagan tarjima property ko'rsatilmaydi"
    if "source: DEFAULT_LOCALE" in combined:
        return (
            f"{SHARED_I18N_CORE}: yetishmagan tarjima `DEFAULT_LOCALE` ga tushadi — "
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


def homepage_css_is_inlined() -> str | None:
    """Bosh sahifa CSS so'rovi FCP ni to'simasin (HITL 2026-09-20).

    App Router + streaming da Critters/`optimizeCss` ishlamaydi. Next 16
    `experimental.inlineCss` `<link rel="stylesheet">` o'rniga `<style>`
    qo'yadi — Slow 4G labda ikkita chunk (~150 ms) zanjiri yo'qoladi.
    """
    src = read(WEB_NEXT_CONFIG)
    if "inlineCss: true" not in src:
        return f"{WEB_NEXT_CONFIG}: `experimental.inlineCss: true` yo'q"
    if "experimental:" not in src:
        return f"{WEB_NEXT_CONFIG}: `experimental` bloki yo'q"
    return None


#: Customization contract invariantlari (2026-09-24). Manba — contract §7;
#: bu yerdagi nusxa ataylab qisqa, chunki vazifasi boshqa: contract ularni
#: E'LON qiladi, bu qoida esa ular `CLAUDE.md` da — ya'ni agentlar o'qiydigan
#: joyda — borligini tekshiradi. To'liq moslikni
#: `tools/check_customization_contract.py` qo'riqlaydi.
CUSTOMIZATION_INVARIANTS = (
    "MUST NOT introduce a new customization setting",
    "MUST NOT add a key to the client",
    "MUST NOT change the precedence of an existing setting",
    "MUST NOT introduce a second persistence mechanism",
    "MUST NOT bypass customization validation",
    "Unknown values MUST have an explicit fallback",
)


def customization_invariants_are_written() -> str | None:
    """Customization invariantlari `CLAUDE.md` da yozilganmi?

    ⚠️ Nega kerak — o'lchandi 2026-09-24. `themeToggle` klientda #244 dan
    beri bor edi, serverning `APPEARANCE_KEYS` ida yo'q edi ⇒ mavzu tugmasi
    uslubini tanlash BUTUN `appearance` yozuvini 400 ga uchratardi. Qoida
    kodda yozilgan bo'lsa ham, uni hech narsa majburlamasdi.

    Endi invariantlar `CLAUDE.md` da (agentlar o'sha yerdan o'qiydi) va
    `check_customization_contract.py` ularning contract bilan mosligini
    tekshiradi. Bu qoida — zanjirning `CLAUDE.md` halqasi.
    """
    text = read("CLAUDE.md")
    for invariant in CUSTOMIZATION_INVARIANTS:
        if invariant not in text:
            return f"CLAUDE.md: customization invarianti yo'q — {invariant!r}"
    return None


def login_uses_narrow_auth_css() -> str | None:
    """`/login` to'liq globals.css ni inline qilmasin (LH-LOGIN-CSS).

    Ildiz layout 534 KiB HTML berardi; desktop Slow 4G FCP 1.1–1.2 s
    (92–96). Auth guruh `auth.css` — tokenlar + tor Tailwind `@source`.
    """
    root = read("apps/web/src/app/layout.tsx")
    if 'import "./globals.css"' in root:
        return (
            "apps/web/src/app/layout.tsx: ildiz yana to'liq globals.css ni "
            "chizadi — /login 534 KiB HTML oladi"
        )
    auth = read("apps/web/src/app/(auth)/layout.tsx")
    if 'import "../auth.css"' not in auth:
        return "apps/web/src/app/(auth)/layout.tsx: auth.css ulanmagan"
    site = read("apps/web/src/app/(site)/layout.tsx")
    if 'import "../globals.css"' not in site:
        return "apps/web/src/app/(site)/layout.tsx: globals.css ulanmagan"
    sheet = read("apps/web/src/app/auth.css")
    # The narrowing is now carried by an explicit include list rather than by
    # `@source not`, so the invariant to guard changed with it. Matching the
    # old literal stayed green while 8 of 11 paths were dead (measured
    # 2026-09-24). The resolution half lives in `tools/check_css_sources.py`,
    # which runs on the real tree — this sandbox has no directory tree.
    #
    # ⚠️ The import directive is matched, not a bare `"source(none)" in sheet`:
    # the stylesheet's own comment mentions `source(none)`, so a substring test
    # would stay green after the import lost the argument (measured).
    entry = re.search(r'@import\s+"tailwindcss"\s*(?:source\(([^)]*)\))?\s*;', sheet)
    if entry is None or (entry.group(1) or "").strip() != "none":
        return (
            "apps/web/src/app/auth.css: import `source(none)` bilan emas — "
            "avtomatik skan ochiq qolsa ro'yxat bezak bo'ladi va sheet jimgina kengayadi"
        )
    return None


def security_run_is_disabled() -> str | None:
    """Security workflow job ishlamasin (owner 2026-09-21).

    `audit` `if: false`; avtomatik `push`/`schedule` yo'q. Deploy
    darvozasi faqat `CI` kutadi — Security run bo'lmasa ham ochiladi.
    """
    src = read(".github/workflows/security.yml")
    if "if: false" not in _workflow_job(src, "audit"):
        return "security.yml audit ishlaydi — Security run o'chiq bo'lishi kerak"
    triggers = _workflow_triggers(".github/workflows/security.yml")
    if "push" in triggers or "schedule" in triggers:
        return "security.yml push/cron da yuguradi — avtomatik ishga tushmasin"
    gate = read("tools/check_deploy_gate.py")
    if 'REQUIRED = ("CI",)' not in gate:
        return "check_deploy_gate.py Security ni talab qiladi — darvoza faqat CI"
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
    """Avtomatik deploy zanjiri — tartib buzilsa JIM buziladigan sakkiz joy.

    Saidakbar aka qarori (2026-09-19): deploy to'liq avtomatik bo'ladi —
    host watcher orqali (`tools/auto_deploy.sh` + `RankWant Auto Deploy`
    vazifasi). ⚠️ GitHub Actions'dagi `deploy` job ATAYLAB qo'lda qoladi
    (`deploy_manual_only`): o'lchandi — runner konteyneri jonli
    `.env.public` ni ko'rmaydi (u `/work` volume'ida) va unda `gh` yo'q,
    ya'ni u `check_deploy_gate.py` ni yurgiza olmaydi. Shuning uchun
    avtomatlashtirish Actions'ni yoqish bilan emas, watcher bilan qurildi.

    Beshta shart tartibga bog'liq: buzilganda kod ISHLAYDI, natija esa
    noto'g'ri bo'ladi — ya'ni xato faqat hodisa paytida bilinadi.
    Qolgan uchtasi (6–8) haqiqiy yurishda o'lchandi (6 va 7 — 2026-09-19,
    8 — 2026-09-20) va umumiy sababga ega: ular faqat zanjir BUTUN
    yurganda ko'rinadi, ya'ni unit darajasidagi tekshiruvlar ularni
    o'tkazib yuboradi.

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
    8. DARVOZA YOPIQ BO'LSA URINISH YOZILMAYDI. Darvoza — TAYYORLIK
       tekshiruvi, nosozlik emas. U yopiq bo'lganda `record_attempt`
       yozilsa, keyingi 30 daqiqa deploy umuman qilinmaydi va log yolg'on
       «deploy YIQILDI» deydi. O'lchandi 2026-09-20 (PR #192: merge
       18:09:36, yurish 18:10:06) — CI `main` da ~70 s yuguradi, yurish esa
       har daqiqada, ya'ni deyarli har merge shu yo'lga tushadi.
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
        return f"{AUTO_DEPLOY}: urinish yozilmaydi — yiqilgan deploy har daqiqada takrorlanadi"
    if deploy_at < 0:
        return f"{AUTO_DEPLOY}: `deploy.sh --yes` chaqirilmaydi"
    if attempt_at > deploy_at:
        return f"{AUTO_DEPLOY}: urinish deploy'dan KEYIN yoziladi — yiqilgan yurish takrorlanadi"

    # ⚠️ 8. Darvoza urinishdan OLDIN tekshiriladi. Yopiq darvoza — «hali
    # tayyor emas», nosozlik emas; `record_attempt` yozilsa SHA 30 daqiqa
    # bloklanadi va log yolg'on «deploy YIQILDI» deydi. O'lchandi
    # 2026-09-20 18:10:06Z: PR #192 18:09:36 da merge bo'ldi, CI hali
    # yugurar edi — yurish darvozada to'xtadi va «1800s to'siq» chiqdi.
    gate_at = position(auto, '"$GATE_PY" tools/check_deploy_gate.py')
    if gate_at < 0:
        return (
            f"{AUTO_DEPLOY}: darvoza oldindan tekshirilmaydi — yopiq darvoza "
            "urinish yozib 30 daqiqalik to'siq qo'yadi"
        )
    if gate_at > attempt_at:
        return (
            f"{AUTO_DEPLOY}: darvoza urinishdan KEYIN tekshiriladi — "
            "yopiq darvoza baribir to'siq qo'yadi"
        )

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

    # 9. OYNA OVERRIDE'I — QO'LDA BOR, AVTOMATIKDA YO'Q (2026-09-24,
    #    Saidakbar aka qarori). Qoida №1 («faol contest paytida deploy
    #    qilinmaydi») SAQLANADI, lekin endi odam qo'li bilan chetlab
    #    o'tilishi mumkin: `deploy.yml` → `allow_live_contest=yes`,
    #    `tools/deploy.sh` → `RANKWANT_ALLOW_LIVE_CONTEST`. Sabab: sayt
    #    contest paytida yiqilsa, tuzatishning YAGONA yo'li — deploy;
    #    yopiq darvoza tizimni qulflab qo'yardi.
    #
    #    ⚠️ AMMO avtomatik yo'lda odam YO'Q. Override u yerda bo'lsa
    #    watcher har daqiqada yuguradi va jonli musobaqa paytida o'zi
    #    deploy qilib verdikt va reytingni buzardi. Bu JIM buziladigan
    #    joy: override qo'shilsa hamma mavjud tekshiruv yashil qoladi,
    #    xato esa faqat keyingi musobaqada bilinadi.
    if "RANKWANT_ALLOW_LIVE_CONTEST" in auto:
        return (
            f"{AUTO_DEPLOY}: oyna override'i (`RANKWANT_ALLOW_LIVE_CONTEST`) "
            "avtomatik yo'lda — odam yo'q joyda qoida №1 chetlab o'tilardi"
        )
    if "RANKWANT_ALLOW_LIVE_CONTEST" not in deploy:
        return (
            "tools/deploy.sh: oyna override'i (`RANKWANT_ALLOW_LIVE_CONTEST`) "
            "yo'q — contest paytida shoshilinch tuzatish deploy'i qulflanadi"
        )
    if 'lock_hash "container:$name"' not in read("tools/check_deploy.sh"):
        return "check_deploy.sh: `requirements.lock` solishtirilmaydi — bog'liqlik yangilanishi deploy qilinmaydi"
    deploy_sh = read("tools/deploy.sh")
    watcher_sh = read("tools/auto_deploy.sh")
    if not re.search(r"check_deploy_gate\.py; then\n[^\n]*\n\s+exit 75\n", deploy_sh):
        return "deploy.sh: yopiq darvoza alohida kod (75) bermaydi — tarmoq uzilishi «yiqildi» bo'lib ko'rinadi"
    if not re.search(r'"\$deploy_rc" -eq 75 \]; then\n[^\n]*\n\s+rm -f "\$STATE"', watcher_sh):
        return "auto_deploy.sh: darvoza kodi (75) to'siqni olib tashlamaydi — 30 daqiqa bekor kutiladi"
    if "|| rotate_log\n" not in watcher_sh:
        return "auto_deploy.sh: log aylantirilmaydi — fayl cheksiz o'sadi"
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


def schema_change_wakes_web_job() -> str | None:
    """2026-10-04: a schema.yml change must run the web job's types check.

    `apps/web/src/lib/api/generated/schema.ts` is generated from
    `apps/api/openapi/schema.yml`. The path filter woke the web job only for
    `apps/web/**`, so #318 changed the schema, skipped the job, and left
    `main` green with types 226 lines stale. Four unrelated web PRs then
    failed on `openapi:check`.
    """
    ci = read(".github/workflows/ci.yml")
    line = next(
        (ln for ln in ci.splitlines() if ln.strip().startswith("web:") and "'apps/web/**'" in ln),
        "",
    )
    if "'apps/api/openapi/schema.yml'" not in line:
        return "ci.yml: schema.yml o'zgarsa Web job'i uyg'onmaydi"
    if "run: npm run openapi:check" not in ci:
        return "ci.yml: openapi:check qadami yo'q"
    return None


def sign_in_page_is_self_contained() -> str | None:
    """2026-10-04: `/login` is a two-column page without the site chrome.

    The site header and footer are not drawn on it, so `AuthShell` must carry
    what they carried: the language switch and the Terms/Privacy links
    (ADR-0016). Its brand panel must stay static — decision 18 dropped an
    earlier split screen because its panel rendered live API data and came
    up empty when the API was down.
    """
    shell = read("apps/web/src/layout/AppShell.tsx")
    full = re.search(r"const FULL = \[([^\]]*)\]", shell)
    if not full or '"/login"' not in full.group(1):
        return "AppShell.tsx: `/login` FULL ro'yxatida emas — sayt header/footer'i qaytadi"
    auth = read("apps/web/src/features/auth/components/AuthShell.tsx")
    if "lg:grid-cols-" not in auth:
        return "AuthShell.tsx: ikki ustunli tuzilma yo'q"
    if "<LocaleSwitch" not in auth:
        return "AuthShell.tsx: til tanlagich yo'q — header'siz sahifada til almashmaydi"
    if 'href="/terms"' not in auth or 'href="/privacy"' not in auth:
        return "AuthShell.tsx: Shartlar/Maxfiylik havolasi yo'q (ADR-0016)"
    if re.search(r"""from ["']@/lib/api["']""", auth) or "fetch(" in auth:
        return "AuthShell.tsx: brend paneli API'ga bog'liq — panel statik bo'lishi shart"
    return None


def clay_follows_dark_mode() -> str | None:
    """2026-10-05: the factory style has a dark palette and is marked dual.

    Clay is the default style and the default mode is `system`. Without a
    `[data-style="clay"].dark` block a dark-mode device got the `dark` class
    and `color-scheme: dark` on a page whose every surface stayed light. The
    two halves must move together: the block without `dual: true` leaves the
    mode switch hidden, `dual: true` without the block offers a switch that
    changes nothing.
    """
    css = read("apps/web/src/app/theme.css")
    if '[data-style="clay"].dark {' not in css:
        return "theme.css: `clay` uchun `.dark` palitra yo'q"
    styles = read("apps/web/src/layout/styles.ts")
    clay = re.search(r'id: "clay",(.*?)\},', styles, re.S)
    if not clay or "dual: true" not in clay.group(1):
        return "styles.ts: `clay` `dual: true` emas — rejim tugmasi ko'rinmaydi"
    return None


def signed_in_home_is_the_dashboard() -> str | None:
    """2026-10-05: a signed-in visitor gets the personal dashboard.

    The page returns `SignedInHome` before the guest markup, so the guest
    page (CDN-cached, guarded by the homepage decisions) is untouched. The
    dashboard keeps the homepage prefetch decision: links prefetch on
    intent, so it must not import `next/link` directly.
    """
    page = read("apps/web/src/app/(site)/page.tsx")
    if "if (me) {" not in page or "<SignedInHome" not in page:
        return "page.tsx: kirgan foydalanuvchi shaxsiy panelni olmaydi"
    # Every file of the dashboard, not only the entry: the lists of people
    # (top users, today's visitors) render dozens of links in sibling files.
    for name in ("SignedInHome.tsx", "Person.tsx", "TopUsers.tsx", "NewsCarousel.tsx"):
        source = read("apps/web/src/app/(site)/_home/" + name)
        if re.search(r"""from ["']next/link["']""", source):
            return f"{name}: `next/link` — havolalar ko'rinishi bilan prefetch qiladi"
    return None


def home_presence_reads_sessions() -> str | None:
    """2026-10-05: «bugun faol» ro'yxati shu saytdagi sessiyadan o'qiladi.

    `User.last_seen_at` ni Codeforces sinxronizatsiyasi ham yozadi (o'sha
    odamning CODEFORCES'ga oxirgi kirishi), ya'ni u ustundan o'qilsa
    saytni hech qachon ochmagan odamlar «bugun faol» bo'lib chiqardi.
    `online` ni yashirgan foydalanuvchi ro'yxatga kirmaydi — profil
    sahifasi bu tanlovga allaqachon rioya qiladi.
    """
    views = read("apps/api/core/views.py")
    match = re.search(r"^class PresenceView\(.*?(?=^class |^@extend_schema)", views, re.S | re.M)
    if not match:
        return "core/views.py: PresenceView topilmadi"
    body = match.group(0)
    if "UserSession.objects" not in body:
        return "PresenceView: `UserSession` o'qilmaydi — Codeforces tashrifi «bugun faol» bo'lib chiqadi"
    if '"online" not in' not in body:
        return "PresenceView: `online` maxfiylik tanlovi hisobga olinmaydi"
    return None


def settings_six_sections_and_grace() -> str | None:
    """2026-10-05: sozlamalar olti bo'lim, bitta saqlash paneli, 14 kunlik o'chirish.

    Uch narsa JIM qaytishi mumkin, shuning uchun qo'riqlanadi:

    - telefonda har bo'lim tepasidagi tanlash ro'yxati (`<Dropdown`) —
      o'lchangan nuqson shu edi: ro'yxat ham, select ham birga chiqardi;
    - `DELETE /me/` ning darhol anonimlashtirishi — amal qaytarilmaydi,
      egasi 14 kunlik kutishni tanlagan;
    - muddati o'tgan so'rovlarni bajaradigan beat vazifasi — usiz hisob
      «kutilmoqda» holatida abadiy qolardi.

    To'rtinchisi — migratsiya tuzog'i: `0028` `backfill_origin` buyrug'ini
    JONLI model bilan chaqiradi. So'rov ustunlarni cheklamasa, `User` ga
    qo'shilgan har yangi maydon bo'sh bazada migratsiyani sindiradi
    (o'lchandi: `no such column: core_user.deletion_requested_at`).
    """
    sections = read("apps/web/src/features/account/components/sections.ts")
    wanted = ("profil", "ommaviy", "malumotlar", "xavfsizlik", "bildirishnomalar", "hisob")
    found = tuple(re.findall(r'^    id: "(\w+)",', sections, re.M))
    if found != wanted:
        return f"sections.ts: bo'limlar {found} — kutilgan {wanted}"
    if "<Dropdown" in read("apps/web/src/features/account/components/SettingsShell.tsx"):
        return "SettingsShell.tsx: `<Dropdown` — telefonda bo'lim tanlash ro'yxati qaytgan"
    views = read("apps/api/core/views.py")
    match = re.search(r"def delete\(self, request: Request, \*args.*?(?=^class |^@extend_schema)", views, re.S | re.M)
    if not match:
        return "core/views.py: MeView.delete topilmadi"
    if "account.schedule_deletion(user)" not in match.group(0) or "anonymize(" in match.group(0):
        return "MeView.delete: hisob darhol anonimlashtiriladi — 14 kunlik kutish yo'q"
    if '"task": "core.finalize_deletions"' not in read("apps/api/config/settings.py"):
        return "settings.py: `core.finalize_deletions` beat jadvalida yo'q — o'chirish hech qachon bajarilmaydi"
    if ".only(" not in read("apps/api/core/management/commands/backfill_origin.py"):
        return "backfill_origin.py: so'rov barcha ustunlarni o'qiydi — yangi `User` maydoni 0028 ni sindiradi"
    return None


def signed_in_header_fits() -> str | None:
    """2026-10-05: kirgan foydalanuvchi header'i 320 px dan boshlab sig'adi.

    Kirgan odamning o'ng klasteri mehmonnikidan uzun (qo'ng'iroq, Qvant,
    streak, hisob tugmasi) va u QISQARMAYDI (`shrink-0`). O'lchandi
    (lokal, 2026-10-05): 390 px da 541 px kerak edi, 640 px da hujjat
    751 px, 768 px da 900 px; 1024 px da qidiruv maydoni Qvant ostida
    qolardi. Uch pog'ona shuni ushlab turadi — biri qaytsa toshish qaytadi.
    """
    if 'user ? "hidden xl:flex" : "flex"' not in read("apps/web/src/layout/HeaderActions.tsx"):
        return "HeaderActions.tsx: kirgan foydalanuvchida uch tugma `xl` dan oldin ko'rinadi — header toshadi"
    if read("apps/web/src/layout/HeaderStatus.tsx").count("hidden md:flex") != 2:
        return "HeaderStatus.tsx: Qvant/streak `md` dan oldin ko'rinadi — 640 px da header toshadi"
    if "truncate xl:inline" not in read("apps/web/src/layout/UserMenu.tsx"):
        return "UserMenu.tsx: ism `xl` dan oldin ko'rinadi — 768 px da header toshadi"
    return None


def secret_key_has_no_fallback() -> str | None:
    """2026-10-05 (ADR-0044, D5): `DJANGO_SECRET_KEY` siz Django ishga tushmaydi.

    Ma'lum standart sir bilan ko'tarilgan jarayon har sessiya, CSRF va PAT
    tokenni ommaviy kalit bilan imzolaydi. Qaror 2026-09-29 da qabul
    qilingan, testi kodga kirgan, qo'riqchining o'zi esa yo'q edi —
    Nightly shu sabab qizil turardi.

    Ikkinchi yarmi — image qurilishi: `collectstatic` sozlamalarni yuklaydi
    va `|| true` uning yiqilishini YUTADI, ya'ni kalitsiz qurilgan image
    statik fayllarsiz, lekin «muvaffaqiyatli» chiqardi.
    """
    settings = read("apps/api/config/settings.py")
    if 'SECRET_KEY = env("DJANGO_SECRET_KEY")\n' not in settings:
        return "settings.py: `SECRET_KEY` standart qiymatga ega — sirsiz ishga tushadi"
    if "raise ImproperlyConfigured(" not in settings:
        return "settings.py: `DJANGO_SECRET_KEY` yo'qligida xato ko'tarilmaydi"
    dockerfile = read("apps/api/Dockerfile")
    if not re.search(r"^RUN DJANGO_SECRET_KEY=\S+ python manage\.py collectstatic", dockerfile, re.M):
        return "apps/api/Dockerfile: `collectstatic` kalitsiz — image statik fayllarsiz quriladi"
    return None


SETTINGS_CONTROL_FILES = (
    "apps/web/src/features/account/components/CareerSection.tsx",
    "apps/web/src/features/account/components/SkillsSection.tsx",
    "apps/web/src/features/account/components/TeamsSection.tsx",
    "apps/web/src/features/account/components/ProfileSection.tsx",
    "apps/web/src/features/account/components/SecuritySection.tsx",
    "apps/web/src/features/account/components/SocialAccounts.tsx",
    "apps/web/src/features/account/components/AppearanceSection.tsx",
)


def settings_controls_are_44px() -> str | None:
    """2026-10-05: sozlamalar tablaridagi tugmalar 44 px dan kichik emas.

    Olti tab eski komponentlarda qolgan edi: 36 px li tugmalar (`h-9`) va
    32 px li «o'chirish» belgilari (`size-8`). Telefonda bular barmoq
    uchun kichik nishon (WCAG 2.5.8 — eng kami 24, tavsiya 44).
    """
    for rel in SETTINGS_CONTROL_FILES:
        source = read(rel)
        if re.search(r"\bh-9\b", source):
            return f"{rel}: `h-9` — 36 px li tugma qaytgan"
        if re.search(r"\bsize-8 (?:shrink-0 )?items-center", source):
            return f"{rel}: `size-8` — 32 px li belgi-tugma qaytgan"
    return None


def dependabot_locks_are_recompiled() -> str | None:
    """2026-10-05: Dependabot PR'ida API lock'lari avtomatik qayta yasaladi.

    Dependabot `requirements*.txt` ni tahrirlaydi, image esa
    `requirements.lock` dan quriladi (`uv pip compile`, u bu formatni
    bilmaydi) ⇒ PR yashil o'tadi, runtime esa o'zgarmaydi.

    Qo'riqlanadigan to'rt narsa:
    - yechish (resolve) bosqichi yozish huquqisiz: u manba paketni qurishi,
      ya'ni begona kodni bajarishi mumkin;
    - lock'lar image bilan bir xil Python uchun (3.12) yasaladi — boshqa
      versiyada shartli bog'liqliklar (`typing-extensions`) tushib qoladi;
    - push'dan keyin CI ochiq ishga tushiriladi: workflow tokeni bilan
      qilingan push CI'ni uyg'otmaydi va PR tekshiruvsiz qolardi.
    """
    workflow = read(".github/workflows/dependabot-locks.yml")
    match = re.search(r"^  compile:\n(.*?)^  commit:\n", workflow, re.S | re.M)
    if not match:
        return "dependabot-locks.yml: `compile` va `commit` job'lari topilmadi"
    if re.search(r"^\s+[a-z-]+: write\s*$", match.group(1), re.M):
        return "dependabot-locks.yml: `compile` job'ida yozish huquqi bor — begona kod token bilan ishlaydi"
    if workflow.count("--python-version 3.12") < 2:
        return "dependabot-locks.yml: lock'lar Python 3.12 uchun yasalmaydi"
    if read(".github/workflows/ci.yml").count("&& inputs.run_all)") < 6:
        return "ci.yml: `run_all` o'qilmaydi — qo'lda yurishda build o'tkazib yuboriladi"
    if '-m "[dependabot skip]"' not in workflow:
        return "dependabot-locks.yml: commit `[dependabot skip]` siz — Dependabot branch'ni rebase qilmay qo'yadi"
    if "/approve" not in workflow:
        return "dependabot-locks.yml: kutayotgan CI yurishi tasdiqlanmaydi — PR BLOCKED holatida qoladi"
    if "gh workflow run ci.yml" not in workflow:
        return "dependabot-locks.yml: push'dan keyin CI ishga tushirilmaydi — PR tekshiruvsiz qoladi"
    for name in ("requirements.lock", "requirements-dev.lock"):
        if "--python-version 3.12" not in read("apps/api/" + name).split("\n", 2)[1]:
            return f"apps/api/{name}: lock Python 3.12 uchun yasalmagan (sarlavhaga qarang)"
    return None


def customizer_reachable_on_a_phone() -> str | None:
    """2026-10-05: telefonda sozlagich yaqin, varaq ikki pog'onali, nishonlar 44 px.

    Kirgan foydalanuvchida header tugmasi `xl` dan, suzuvchi yorliq `lg`
    dan ko'rinadi ⇒ 1024 px dan torda panel faqat sozlamalar orqali, to'rt
    qadamda ochilardi; mavzu almashtirgich esa umuman yo'q edi.
    """
    menu = read("apps/web/src/layout/UserMenu.tsx")
    if "customizer.setOpen(true)" not in menu:
        return "UserMenu.tsx: hisob menyusida sozlagich qatori yo'q — telefonda panel to'rt qadamda"
    if '"flex min-h-11 w-full items-center' not in menu:
        return "UserMenu.tsx: hisob menyusi qatorlari 44 px emas"
    if "toggleTheme(" not in menu:
        return "UserMenu.tsx: hisob menyusida mavzu qatori yo'q — telefonda almashtirgich qolmaydi"
    shell = read("apps/web/src/components/customizer/Customizer.tsx")
    if 'tall ? "max-h-[90dvh]" : "max-h-[55dvh]"' not in shell:
        return "Customizer.tsx: mobil varaq ikki pog'onali emas (55% / 90%)"
    css = read("apps/web/src/app/globals.css")
    if not re.search(r"@media \(pointer: coarse\) \{\s*\[data-customizer\]", css):
        return "globals.css: sensorli qurilmada sozlagich nishonlari 44 px emas"
    if "data-customizer\n" not in shell:
        return "Customizer.tsx: `data-customizer` yo'q — 44 px qoidasi hech narsaga tegmaydi"
    return None


def editor_sheet_clears_the_side_menu() -> str | None:
    """2026-10-07: masala sahifasidagi muharrir varag'i yon menyu ostiga kirmaydi.

    `xl` dan pastda muharrir pastki varaqda, `lg` dan esa yon menyu ko'rinadi
    va varaqdan yuqorida turadi (z-50 > z-40). Varaq `fixed` — ustunning
    `margin` i uni surmaydi, shuning uchun 1024–1279 px da u oyna chetidan
    boshlanib, «Yuborish» tugmasi menyu havolasi ostida qolardi.
    """
    shell = read("apps/web/src/layout/AppShell.tsx")
    if 'const SHELL_INSET = "--rw-shell-inset"' not in shell:
        return "AppShell.tsx: `--rw-shell-inset` e'lon qilinmagan — fixed qutilar yon menyu kengligini bilmaydi"
    if '[SHELL_INSET]: sidenav ? (wide ? "260px" : "86px") : "0px"' not in shell:
        return "AppShell.tsx: `--rw-shell-inset` yon menyu holatiga (260 / 86 / 0 px) bog'lanmagan"
    side = read("apps/web/src/layout/AppSidebar.tsx")
    if '"w-[260px] px-4" : "w-[86px] px-2"' not in side:
        return "AppSidebar.tsx: yon menyu kengligi 260 / 86 px emas — `--rw-shell-inset` bilan ajralib ketadi"
    sheet = read("apps/web/src/features/problems/components/ProblemWorkspace.tsx")
    if "fixed inset-x-0 bottom-0 z-40" in sheet and "lg:left-[var(--rw-shell-inset,0px)]" not in sheet:
        return "ProblemWorkspace.tsx: muharrir varag'i `lg` dan yon menyu ostida boshlanadi — «Yuborish» bosilmaydi"
    return None


def customizer_quick_row_first() -> str | None:
    """2026-10-05: sozlagichda tez qator va shablonlar akkordeonlardan oldin.

    Eng ko'p ishlatiladigan to'rt boshqaruv (rejim, uslub, rang, matn
    o'lchami) har doim ko'rinadi; nozik sozlamalar (kit oilalari) oxirida.
    Sozlamalar sahifasi faqat xulosa ko'rsatadi — yozish yo'li bitta.
    """
    tab = read("apps/web/src/components/customizer/AppearanceTab.tsx")
    quick = tab.find("data-cz-quick")
    templates = tab.find("<TemplatesSection />")
    group = tab.find("<Group")
    if quick < 0 or not quick < templates < group:
        return "AppearanceTab.tsx: tez qator va shablonlar akkordeonlardan oldin emas"
    if tab.find('id="system"') < tab.find('id="look"'):
        return "AppearanceTab.tsx: «Kengaytirilgan» oxirida emas — nozik sozlamalar asosiy oqimga qaytgan"
    if "data-style={item.style}" not in tab:
        return "AppearanceTab.tsx: shablon preview'i uslub tokenlaridan chizilmaydi"
    if "let memory: GroupId | null = null;" not in read("apps/web/src/components/customizer/group-session.ts"):
        return "group-session.ts: yangi tab yopiq guruhlar bilan boshlanmaydi"
    settings = read("apps/web/src/features/account/components/AppearanceSection.tsx")
    if "data-appearance-summary" not in settings:
        return "AppearanceSection.tsx: sozlamalarda joriy ko'rinish xulosasi yo'q"
    if "{hydrated ? row.value : NBSP}" not in settings:
        return "AppearanceSection.tsx: xulosa serverda chiziladi — qurilma holati hisobdan farq qilsa gidratsiya xatosi"
    if "accentToHex" in settings:
        return "AppearanceSection.tsx: xulosa hex hisoblaydi — ekrandagi rangdan farq qiladigan kod ko'rsatiladi"
    if "writeLastTemplate(item.id)" not in tab:
        return "AppearanceTab.tsx: qo'llangan shablon eslab qolinmaydi — «shablonga qaytish» ishlamaydi"
    if "setAppearance" in settings or "applyTemplate" in settings:
        return "AppearanceSection.tsx: sozlamalar sahifasi ko'rinishni o'zi yozadi — ikkinchi yozish yo'li"
    return None


def failed_sign_ins_are_limited() -> str | None:
    """2026-10-05: noto'g'ri kirish urinishlari manzil va hisob bo'yicha cheklanadi.

    `LoginView` da alohida chegara yo'q edi: parolni terib ko'rishni faqat
    umumiy `anon` chegarasi (1500/soat) to'xtatardi. Faqat MUVAFFAQIYATSIZ
    urinish sanaladi (bitta manzil ortidagi sinf o'ttiz marta kiradi).
    Tekshiruv paroldan OLDIN turadi — aks holda to'g'ri taxmin baribir o'tardi.
    """
    views = read("apps/api/core/views.py")
    start = views.find("class LoginView(APIView):")
    block = views[start : views.find("\nclass ", start + 1)]
    check = block.find("login_guard.retry_after(request, identifier)")
    auth = block.find("django_authenticate(")
    if check < 0 or auth < 0 or check > auth:
        return "core/views.py: kirish chegarasi parol tekshiruvidan oldin emas — to'g'ri taxmin o'tib ketadi"
    if "login_guard.record_failure(request, identifier)" not in block:
        return "core/views.py: noto'g'ri urinish sanalmaydi — chegara hech qachon to'lmaydi"
    settings = read("apps/api/config/settings.py")
    for scope in ('"login_ip": os.environ.get("THROTTLE_LOGIN_IP"', '"login_account": os.environ.get("THROTTLE_LOGIN_ACCOUNT"'):
        if scope not in settings:
            return "config/settings.py: kirish chegarasining ikki idishidan biri yo'q (manzil va hisob)"
    return None


def guest_header_fits_every_locale() -> str | None:
    """2026-10-05: mehmon header'i 320 px dan boshlab o'nta tilda ham sig'adi.

    Nightly o'lchadi: 375 px da header 377 px (o'zbekcha). Jonli saytda
    inglizcha 385 px, tojikcha 320 px ekranda 352 px. «320 px ga sig'adi»
    qarori faqat o'zbekcha o'lchangan edi va mavzu almashtirgich undan
    keyin qo'shilgan.
    """
    actions = read("apps/web/src/layout/HeaderActions.tsx")
    if '<span className="hidden min-[390px]:contents">' not in actions:
        return "HeaderActions.tsx: sozlagich tugmasi 390 px dan oldin ko'rinadi — mehmon header'i toshadi"
    if '<span className="hidden md:contents">{!auth && <ThemeToggle />}</span>' not in actions:
        return "HeaderActions.tsx: mavzu almashtirgich `md` dan oldin ko'rinadi — mehmon header'i toshadi"
    if '<span className="max-w-[3.5rem] truncate md:max-w-none">' not in read("apps/web/src/layout/UserMenu.tsx"):
        return "UserMenu.tsx: kirish yorlig'i chegaralanmagan — eng uzun tarjima (tg) header'ni toshiradi"
    return None


def nightly_stack_matches_production() -> str | None:
    """2026-10-05: Nightly'ni qizartirgan uch nuqson qaytmasin.

    - A+B ga yozilgan bitta `ProblemLanguage` qatori (Julia xotira limiti)
      masalani FAQAT Julia'ga ochardi — jonli saytda ham;
    - namunalar jadvalidagi `sr-only` yorliq aylantirish qutisidan chiqib,
      sahifani telefonda 553 px ga kengaytirardi;
    - `tools/ci.Dockerfile` ildiz `.dockerignore` tufayli o'z yagona
      faylini topa olmasdi.
    """
    seed = read("apps/api/core/management/commands/seed_demo.py")
    if "for language in Language.objects.filter(is_active=True):" not in seed:
        return "seed_demo.py: A+B ga bitta til qatori yoziladi — masala faqat o'sha tilga ochiladi"
    if '<div className="relative min-w-0 rw-scroll-x">' not in read("apps/web/src/features/problems/components/SampleTests.tsx"):
        return "SampleTests.tsx: aylantirish qutisi `relative` emas — `sr-only` yorliq sahifani kengaytiradi"
    ignore = ROOT / "tools/ci.Dockerfile.dockerignore"
    if not ignore.exists() or "!apps/api/requirements-dev.lock" not in ignore.read_text(encoding="utf-8"):
        return "tools/ci.Dockerfile.dockerignore: dev lock kontekstga kirmaydi — Readiness obrazi qurilmaydi"
    return None


def public_stack_requires_its_secrets() -> str | None:
    """2026-10-05 (ADR-0044): ommaviy stack o'ziga berilmagan sir bilan ko'tarilmaydi.

    DB paroli (`dev`) va MinIO root paroli (`devdevdev`) compose'da qattiq
    yozilgan edi va `docker-compose.public.yml` ularni almashtirmasdi —
    ya'ni production ham o'sha qiymatlarda ishlardi. Endi qiymatlar env'dan
    keladi; lokal va CI stack bazaviy fayldagi dev qiymatga tushadi,
    ommaviy zanjirda esa `:?` bo'sh qiymatni xato qiladi.
    """
    base = read("docker-compose.yml")
    for literal in ("PASSWORD: dev\n", "rankwant:dev@", "PASSWORD: devdevdev", "S3_SECRET: devdevdev"):
        if literal in base:
            return f"docker-compose.yml: sir qattiq yozilgan (`{literal.strip()}`) — env orqali kelmaydi"
    public = read("docker-compose.public.yml")
    for name in ("POSTGRES_PASSWORD", "MINIO_ROOT_PASSWORD", "JUDGE_S3_SECRET"):
        if "${" + name + ":?" not in public:
            return f"docker-compose.public.yml: `{name}` majburiy emas — ommaviy stack standart sir bilan ko'tariladi"
    return None


def team_page_is_managed_data() -> str | None:
    """2026-10-05: «Jamoa» sahifasi admin paneldan boshqariladi.

    A'zolar, bo'limlar va lavozimlar bazada (`team` ilovasi); ommaviy
    endpoint faqat nashr qilinganini beradi, yozish faqat kontent xodimiga
    ochiq, rasm manzili esa brauzer bajaradigan narsa bo'la olmaydi.
    """
    views = read("apps/api/team/views.py")
    if views.count("is_published=True") < 3:
        return "team/views.py: ommaviy sahifa qoralamalarni ham beradi (a'zo, lavozim yoki bo'lim)"
    serializers = read("apps/api/team/serializers.py")
    if 'value.startswith("https://")' not in serializers or "return clean_photo(value)" not in serializers:
        return "team/serializers.py: rasm manzili tekshirilmaydi — `javascript:` yoki `http://` o'tib ketadi"
    if read("apps/api/team/staff_views.py").count("permission_classes = [StaffContent]") < 3:
        return "team/staff_views.py: jamoa ro'yxatlaridan biri kontent xodimi huquqisiz ochiq"
    page = read("apps/web/src/app/(site)/team/page.tsx")
    if "api.team().catch(() => null)" not in page:
        return "team/page.tsx: API yiqilsa sahifa xato ekraniga aylanadi"
    return None


def team_page_is_compact() -> str | None:
    """2026-10-06: «Jamoa» sahifasi ixcham ro'yxat (HITL: B varianti).

    O'lchandi (jonli sayt): telefonda 12 ekran; 24 ta bir xil `h2`; 48 ta
    havola ikki manzilga; yopishqoq panel jiddiy kartani yopardi; ulashilganda
    sayt nomi va bosh sahifa manzili chiqardi.
    """
    directory = read("apps/web/src/components/team/TeamDirectory.tsx")
    if 'if (!whole && index >= FIRST_WIDE) fold = "hidden";' not in directory:
        return "TeamDirectory.tsx: ro'yxat qisqartirilmagan yoki yashirin lavozimlar sahifadan chiqarilgan"
    if '{localized(role, "title", locale)}\n                          </h2>' not in directory:
        return "TeamDirectory.tsx: karta sarlavhasi lavozim emas - 24 ta bir xil `h2` qaytdi"
    if directory.count("<SocialLinks") != 1:
        return "TeamDirectory.tsx: havolalar yana har kartada (yoki jiddiy ko'rinishdan yo'qolgan)"
    if "sticky" in directory:
        return "TeamDirectory.tsx: boshqaruv paneli yana yopishqoq - jiddiy kartani yopadi"
    if "        {serious ? null : (\n          <>" not in directory:
        return "TeamDirectory.tsx: jiddiy ko'rinishda filtr va qidiruv chiziladi"
    page = read("apps/web/src/app/(site)/team/page.tsx")
    if "<div lang={locale}" not in page:
        return "team/page.tsx: matn tili aytilmagan - turkcha sahifada o'zbekcha «i» «İ» bo'ladi"
    if "url: alternates.canonical," not in page:
        return "team/page.tsx: ulashilganda sahifa o'z manzilini aytmaydi"
    return None


def about_page_is_one_searchable_page() -> str | None:
    """2026-10-07: «Qanday ishlaydi» - bitta sahifa, mundarija bilan (HITL: B).

    O'lchandi: 35 til `role="tab"` edi, tanlanmaganlari `tabIndex={-1}` va
    strelka tugmalari uchun kod yo'q - 34 til klaviaturaga yopiq; standart til
    alifbo bo'yicha birinchisi (Ada); bo'limlarda langar yo'q; ulashilganda
    sayt tavsifi va bosh sahifa manzili chiqardi.
    """
    languages = read("apps/web/src/features/about/components/LanguageGuide.tsx")
    if "useState(() => defaultLanguage(sorted))" not in languages:
        return "LanguageGuide.tsx: namuna alifbo bo'yicha birinchi tilda ochiladi (Ada), muharrir ochadigan tilda emas"
    if 'role="tab"' in languages or "aria-pressed={language.code === current.code}" not in languages:
        return "LanguageGuide.tsx: tillar yana `role=\"tab\"` - klaviatura bilan boshqa tilga o'tib bo'lmaydi"
    if '<details className="group">' not in read("apps/web/src/features/about/components/VerdictGuide.tsx"):
        return "VerdictGuide.tsx: yopiq kodlar sahifadan chiqarilgan - qidiruv tizimi va «sahifadan topish» ko'rmaydi"
    if "<section id={id} aria-labelledby={heading}" not in read("apps/web/src/features/about/components/GuideSection.tsx"):
        return "GuideSection.tsx: bo'limda langar yo'q - `/about#verdicts` havolasi ishlamaydi"
    sections = read("apps/web/src/features/about/sections.ts")
    for anchor in ("journey", "submit", "languages", "verdicts", "practices", "judge"):
        if f'{{ id: "{anchor}", ' not in sections:
            return f"about/sections.ts: `#{anchor}` langari o'zgargan - ulashilgan havolalar sinadi"
    if "url: alternates.canonical," not in read("apps/web/src/app/(site)/about/page.tsx"):
        return "about/page.tsx: ulashilganda sahifa o'z manzilini aytmaydi"
    return None


def site_search_is_one_engine() -> str | None:
    """2026-10-05: sayt qidiruvi — bitta dvigatel, bitta panel.

    Har tur bir xil katlanadi va tartiblanadi (`core.search`); foydalanuvchilar
    jadvali (~974k qator) hech qachon to'liq skanerlanmaydi; indeks jadvalni
    yozishga qulflamasdan quriladi; header yagona panelni ochadi.
    """
    if "site_search.search(" not in read("apps/api/core/views.py"):
        return "core/views.py: qidiruv endpoint'i `core.search` dvigatelidan o'tmaydi — bitta dvigatel qoidasi buzildi"
    engine = read("apps/api/core/search.py")
    if "        large=True,\n" not in engine:
        return "core/search.py: foydalanuvchilar manbasi `large` emas — qisqa so'rov ~974k qatorni to'liq skanerlaydi"
    if '_total=Window(Count("pk"))' not in engine:
        return "core/search.py: sanash sahifa so'rovidan ajraldi — alohida COUNT ketma-ket skanerga tushadi (o'lchandi: 320 ms)"
    migration = read("apps/api/core/migrations/0031_search_trigram.py")
    if "CREATE INDEX CONCURRENTLY" not in migration or "FOLD_PG.format(" not in migration:
        return "core/migrations/0031: trigram indeks CONCURRENTLY emas yoki ifodasi so'rovniki bilan bir manbadan emas"
    box = read("apps/web/src/layout/SearchBox.tsx")
    if "{open && <SearchPalette onClose={close} />}" not in box or "/search/?" in box:
        return "SearchBox.tsx: header yagona qidiruv panelini ochmaydi (yoki o'z so'rovini yuboradi)"
    return None


def notifications_inbox_contract() -> str | None:
    """2026-10-06: bildirishnomalar — ko'rildi/o'qildi, jonli kanal, bitta matn manbasi.

    Qo'ng'iroq ochilganda xabar «ko'rilgan» bo'ladi, «o'qilgan» emas; yangi
    xabar tranzaksiya commit bo'lgach e'lon qilinadi; oqimdagi jonli hodisa
    SSE ko'rinishida yuboriladi; yashirin tab oqim ushlamaydi; server
    matnlari web lug'atidan ko'chiriladi va CI ularning mosligini tekshiradi.
    """
    if "export_notification_messages.py --check" not in read(".github/workflows/ci.yml"):
        return "ci.yml: bildirishnoma matnlari tekshirilmaydi — server katalogi web lug'atidan ajralib ketadi"
    services = read("apps/api/notifications/services.py")
    if "    transaction.on_commit(publish)\n" not in services:
        return "notifications/services.py: e'lon commit'dan oldin ketadi — obunachi hali ko'rinmaydigan qatorni so'raydi"
    if "len(pointers) > ANNOUNCE_MAX" not in services:
        return "notifications/services.py: ommaviy jo'natma chegarasiz e'lon qilinadi — har qabul qiluvchiga bitta Redis so'rovi"
    asgi = read("apps/api/realtime/asgi.py")
    if "await write(raw)" in asgi or asgi.count("frame = _live_frame(raw)") != 2:
        return "realtime/asgi.py: jonli hodisa SSE ramkasisiz yuboriladi — brauzer uni hodisa deb tanimaydi"
    bell = read("apps/web/src/components/notifications/NotificationBell.tsx")
    if "if (summary.unseen > 0) markSeen();" not in bell or "readAll()" in bell:
        return "NotificationBell.tsx: panel ochilishi ko'rilgan deb belgilamaydi (yoki o'zi o'qilgan qilib qo'yadi)"
    if "enabled: signedIn && visible" not in read("apps/web/src/context/NotificationsContext.tsx"):
        return "NotificationsContext.tsx: yashirin tab ham oqim ushlaydi — foydalanuvchiga 5 ulanish chegarasi bor"
    return None


def site_search_is_bounded_and_exact() -> str | None:
    """2026-10-06: qidiruv — o'z chegarasi, aniq moslik, katta jadval himoyasi.

    Robocontest va KEP bilan taqqoslashda topilgan kamchiliklar: endpoint
    ochiq va chegarasiz edi; masala raqami bo'yicha topilmasdi; «eng mos
    natija» yo'q edi; tinish belgilaridan iborat so'rov ~974k qatorli
    foydalanuvchilar jadvalini skanerlardi.
    """
    views = read("apps/api/core/views.py")
    if "ResilientUserRateThrottle, SearchRateThrottle]" not in views:
        return "core/views.py: qidiruv endpoint'ida o'z tezlik chegarasi yo'q — har so'rov bazaga boradi"
    if '"search": os.environ.get("THROTTLE_SEARCH"' not in read("apps/api/config/settings.py"):
        return "config/settings.py: `search` throttle stavkasi yo'q — chegara ishga tushganda yiqiladi"
    engine = read("apps/api/core/search.py")
    if "        if not _askable(source, needle):\n            continue\n" not in engine:
        return "core/search.py: katta jadval himoyasi yo'q — `%%` kabi so'rov foydalanuvchilarni to'liq skanerlaydi"
    if "if rows and not fuzzy and offset == 0 and rows[0][0] <= 0:" not in engine:
        return "core/search.py: «eng mos natija» taxminiy mosdan ham olinadi — u faqat aniq moslik bo'lishi shart"
    if "        exact=by_number,\n" not in read("apps/api/problems/search.py"):
        return "problems/search.py: masala raqami bo'yicha topilmaydi (`1519`, `#1519`)"
    return None


def attempts_feed_is_the_shared_table() -> str | None:
    """2026-10-06: urinishlar lentasi — masala tabi bilan bitta jadval.

    Codeforces va KEP bilan taqqoslashda topilganlar: `/attempts` filtrsiz,
    sahifalashsiz xom jadval edi; til ichki kalit bilan ko'rsatilardi;
    «faqat meniki» SSR'da cookie'siz so'ralib, hammaning urinishlarini
    qaytarardi; mehmon oqimga ulanib 401 olardi.
    """
    feed = read("apps/web/src/app/(site)/attempts/page.tsx")
    if "            <AttemptTable rows={page.results} ordering={ordering} query={tableQuery} />\n" not in feed:
        return "attempts/page.tsx: lenta umumiy `AttemptTable` dan chizilmaydi — ikki jadval yana ajralib ketadi"
    if "      ? getWithSession<Paginated<Attempt>>(`/attempts/?${requestQuery}`)\n" not in feed:
        return "attempts/page.tsx: «mening urinishlarim» sessiyasiz so'raladi — hammaning urinishlari chiqadi"
    if "      ? await getWithSession<Paginated<Attempt>>(\n" not in read("apps/web/src/app/(site)/problems/[slug]/_panels/ProblemAttemptsPanel.tsx"):
        return "ProblemAttemptsPanel.tsx: «faqat meniki» sessiyasiz so'raladi — filtr jim e'tiborsiz qoladi"
    if "            qs = qs.filter(user=user) if user.is_authenticated else qs.none()\n" not in read("apps/api/judging/views.py"):
        return "judging/views.py: mehmonga `mine` filtri hammaning urinishlarini qaytaradi"
    if "    enabled: Boolean(user),\n" not in read("apps/web/src/features/submissions/components/AttemptLiveProvider.tsx"):
        return "AttemptLiveProvider.tsx: mehmon ham oqimga ulanadi — har tashrifda 401 va qayta urinish"
    if '"language_name",' not in read("apps/api/judging/serializers.py"):
        return "judging/serializers.py: urinish qatorida til nomi yo'q — sahifa ichki kalitni ko'rsatadi"
    return None


def side_menu_keeps_its_sections() -> str | None:
    """2026-10-06: yon menyu bo'sh joyni avval bo'limlar orasiga beradi.

    O'lchandi (jonli sayt): birinchi ixchamlash 1100 px dan past har ekranda
    hammasini birdan toraytirardi - 1080 px da 58 px yetishmovchilik uchun
    280 px olinardi, bo'limlar orasi 4-10 px, sarlavha ostida 2 px.
    """
    css = read("apps/web/src/app/theme.css")
    if "--rw-nav-spare: calc(100vh - 45.125rem);" not in css:
        return "theme.css: yon menyu ekran balandligiga moslashmaydi (`--rw-nav-spare` yo'q)"
    if "@media (min-width: 1024px) and (max-height: 1100px) and (pointer: fine)" in css:
        return "theme.css: yon menyu yana pog'onali ixchamlashda - bo'limlar yopishib qoladi"
    if "0.625rem + clamp(0rem, var(--rw-nav-spare) / 4, 0.375rem)" not in css:
        return "theme.css: bo'limlar orasi 10 px dan boshlanmaydi yoki bo'sh joyni birinchi olmaydi"
    return None


def side_menu_badges_are_one_request() -> str | None:
    """2026-10-06: yon menyu belgilari - bitta so'rov, to'rt tur.

    «O'zgarishlar» soni har o'qilgan yozuvga bitta qator saqlaydi; shu usul
    1 229 masala yoki har bo'limga yoyilsa jadval foydalanuvchilar soniga
    ko'paytiriladi. Shuning uchun: bitta endpoint, har bo'lim o'z
    hisoblagichini ro'yxatdan o'tkazadi, «yangi» turi bo'limga bitta vaqt
    belgisini saqlaydi.
    """
    if 'autodiscover_modules("nav_badges")' not in read("apps/api/core/apps.py"):
        return "core/apps.py: bo'limlarning `nav_badges.py` fayllari yuklanmaydi - belgilar bo'sh chiqadi"
    if 'name="uniq_nav_seen"' not in read("apps/api/core/models.py"):
        return "core/models.py: `NavSeen` bo'limga bitta qator emas - har yozuvga qator qaytdi"
    if "floor = max(EPOCH, user.date_joined)" not in read("apps/api/core/nav_badges.py"):
        return "core/nav_badges.py: boshlang'ich nuqta yo'q - eski hisob hamma narsani «yangi» deb ko'radi"
    if read("apps/web/src/context/NavBadgesContext.tsx").count("if (!signedIn) return;") < 2:
        return "NavBadgesContext.tsx: mehmon uchun ham so'rov ketadi (401 va keshlangan sahifada ortiqcha yuk)"
    lib = read("apps/web/src/lib/nav-badges.ts")
    start = lib.index("export const SEEN_ON_VISIT")
    seen = lib[start : lib.index("]);", start)]
    for section in ("duels", "classroom", "contests", "arena", "tournaments", "hackathons"):
        if f'"{section}"' in seen:
            return f"nav-badges.ts: `{section}` belgisi bo'limni ochish bilan o'chadi - u ish yoki holat, o'qilmagan emas"
    if '{said && <span className="sr-only">{said}</span>}' not in read("apps/web/src/layout/AppSidebar.tsx"):
        return "AppSidebar.tsx: belgi ekran o'quvchiga aytilmaydi (faqat son yoki nuqta)"
    return None


def scroll_is_one_vocabulary() -> str | None:
    """2026-10-06: scroll — bitta lug'at, bitta modul.

    O'lchandi: 33 faylda 44 ta scroll konteyner, har biri xom
    `overflow-*-auto` bilan; uchta qatlam sahifani uch nusxa kod bilan
    qulflardi; keng jadvalni klaviatura bilan surib bo'lmasdi; urinishlar
    filtri yopishmasdi; 404 sahifasi uslubsiz chiqardi.
    """
    if "        run: python3 tools/check_scroll.py\n" not in read(".github/workflows/ci.yml"):
        return "ci.yml: `check_scroll.py` yurmaydi — xom scroll konteyner jim qaytadi"
    if "    <div tabIndex={0} className=\"@container min-w-0 rw-scroll-x rw-focus-ring\">\n" not in read("apps/web/src/components/ui/Table.tsx"):
        return "Table.tsx: jadval qutisida tab to'xtash joyi yo'q — klaviatura bilan yon tomonga surilmaydi"
    if "        className=\"sticky top-16 z-20 -mx-1 -mt-4 space-y-1.5 px-1 py-2\"\n" not in read("apps/web/src/features/submissions/components/AttemptFilters.tsx"):
        return "AttemptFilters.tsx: filtr qatori sarlavha ostiga yopishmaydi (`sticky top-16`)"
    if "import \"./globals.css\";\n" not in read("apps/web/src/app/not-found.tsx"):
        return "not-found.tsx: 404 sahifasi uslub faylisiz chiziladi"
    return None


def evaluation_paths_are_proven() -> str | None:
    """2026-10-07: special checker, interactive va scorer haqiqiy judge'da isbotlangan.

    O'lchandi (haqiqiy stack, 12 yuborish): eski judge uchtasini noto'g'ri
    baholardi - boshqacha formatlangan to'g'ri javob `PE` (checker
    chaqirilmasdi), scorer'da 70 va 25 ball `AC`. Bu yo'llarni unit testlar
    ko'rmaydi: ular sandbox, checker jarayoni va pipe'larni almashtiradi.
    """
    judge = read("services/judge-go/judge.go")
    if "	return v == VAC || v == VWA || v == VPE\n" not in judge:
        return "judge.go: `PE` dastlabki verdikti checker'ga yetmaydi - boshqacha formatlangan to'g'ri javob rad etiladi"
    if "		worst = scorerVerdict(worst, res.Score)\n" not in judge:
        return "judge.go: scorer balli verdiktga aylanmaydi - 100 dan kam ball `AC` bo'lib qoladi"
    if "			cancel()\n" not in read("services/judge-go/interactive.go"):
        return "interactive.go: rad etilgan yechim to'xtatilmaydi - `WA` o'rniga `IDLENESS`"
    if "    evaluation_gate,\n" not in read("apps/api/problems/release.py"):
        return "release.py: tekshiruv turi darvozasi nashr zanjirida yo'q"
    if "evaluation.combination_error(io_mode, checker_type)" not in read("apps/api/problems/staff_serializers.py"):
        return "staff_serializers.py: yaroqsiz `io_mode` + `checker_type` birikmasi saqlashda rad etilmaydi"
    nightly = read(".github/workflows/nightly.yml")
    if (
        "            python manage.py seed_reference_problems\n" not in nightly
        or "            --profile evaluation run --rm evaluation\n" not in nightly
    ):
        return "nightly.yml: tekshiruv yo'llari haqiqiy judge'da yurmaydi (`evaluation` profili)"
    return None


def function_problems_are_composed() -> str | None:
    """2026-10-07: funksiya masalasi - yechim hakam dasturiga qo'yiladi (ADR-0053).

    Judge bu tur haqida hech narsa bilmaydi: API yechimni tilning hakam
    dasturiga qo'yib, oddiy dastur yuboradi. Shu uch joy tushsa, yechim
    hakam dasturisiz yuriladi - har yuborish kompilyatsiya xatosi bo'ladi va
    ayb yechuvchiga yoziladi.
    """
    if "        source = taskkinds.compose(harness, source)\n" not in read("apps/api/judging/services.py"):
        return "judging/services.py: funksiya yechimi hakam dasturiga qo'yilmaydi"
    if '            rows = rows.exclude(harness="")\n' not in read("apps/api/judging/serializers.py"):
        return "judging/serializers.py: hakam dasturi yo'q tilda yuborish qabul qilinadi"
    if "        or harnesses_error(problem)\n" not in read("apps/api/problems/evaluation.py"):
        return "evaluation.py: hakam dasturisiz funksiya masalasi nashr darvozasidan o'tadi"
    if "(PAIR, GUESS, COINS, MAXPAIR" not in read("apps/api/problems/reference_problems.py"):
        return "reference_problems.py: funksiya turining etalon masalasi ro'yxatda yo'q - haqiqiy judge'da sinalmaydi"
    return None


def answer_problems_run_no_code() -> str | None:
    """2026-10-07: «faqat javob» masalasi - kod yurmaydi, fayllarni checker baholaydi (ADR-0053).

    Uch joy birga ishlaydi: API ishga `task.kind = answer` ni qo'yadi, judge
    uni dasturdan ajratadi, va ikki eshik (manba kod / fayllar) bir-birini
    almashtirmaydi. Bittasi tushsa: javob arxivi dastur sifatida
    kompilyatsiya qilinadi yoki zip chegarasiz ochiladi.
    """
    judge = read("services/judge-go/judge.go")
    if "\tcase TaskAnswer:\n\t\tjudgeAnswers(ctx, work, job, tests, emit, res)\n" not in judge:
        return "judge.go: `answer` ishi dastur yo'lidan ketadi - javob fayllari kompilyatsiya qilinadi"
    if '\t\tres.CompileOutput = "unsupported task kind: " + job.Task.Kind\n' not in judge:
        return "judge.go: notanish `task.kind` rad etilmaydi (yopiq yiqilish yo'q)"
    if '        task = {"kind": "answer"}\n' not in read("apps/api/judging/services.py"):
        return "judging/services.py: `answer` masalasining ishida `task` yo'q - judge uni dastur deb o'qiydi"
    if '        if takes_files != bool(self.context.get("answer_files")):\n' not in read(
        "apps/api/judging/serializers.py"
    ):
        return "judging/serializers.py: manba kod va javob fayllari eshiklari aralashadi"
    if "        if sum(info.file_size for info in entries) > MAX_BYTES:\n" not in read(
        "apps/api/judging/answers.py"
    ):
        return "judging/answers.py: zip ochilgan hajmi bo'yicha cheklanmaydi (zip bomba)"
    if "MAXPAIR, PALS" not in read("apps/api/problems/reference_problems.py"):
        return "reference_problems.py: «faqat javob» etaloni ro'yxatda yo'q - haqiqiy judge'da sinalmaydi"
    return None


def two_pass_runs_share_nothing() -> str | None:
    """2026-10-07: ikki bosqichli masala - ikki yurish orasida faqat manager chiqishi o'tadi (ADR-0053).

    O'lchandi (bake-off `32-two-pass-no-carry`): ish katalogi sandbox'ga
    yoziladigan qilib ulanadi - birinchi yurish fayl yoza OLADI. Har yurish
    toza nusxada ishlamasa, o'sha fayl ikkinchi yurishga yetadi va masalaning
    butun ma'nosi (xabar faqat manager orqali o'tadi) yo'qoladi.
    """
    if "\t\tdir, err := cloneForRun(work)\n" not in read("services/judge-go/twopass.go"):
        return "twopass.go: yurishlar bitta katalogda ishlaydi - birinchisi qoldirgan fayl ikkinchisiga yetadi"
    if "\t\t\tout, decided, err = twoPass(ctx, work, runCmd, managerCmd, test, job.Limits, wallLimit)\n" not in read(
        "services/judge-go/judge.go"
    ):
        return "judge.go: `two_pass` ishi bir marta yuritiladi"
    if '            "kind": "two_pass",\n' not in read("apps/api/judging/services.py"):
        return "judging/services.py: `two_pass` masalasining ishida `task` yo'q - dastur bir marta yuradi"
    if "        or two_pass_error(problem)\n" not in read("apps/api/problems/evaluation.py"):
        return "evaluation.py: manager'siz ikki bosqichli masala nashr darvozasidan o'tadi"
    cases = ROOT / "services/bakeoff/cases/32-two-pass-no-carry.json"
    if not cases.exists():
        return "bake-off: `32-two-pass-no-carry` yo'q - yurishlar orasidagi izolyatsiya sinalmaydi"
    return None


def sql_queries_only_read() -> str | None:
    """2026-10-07: SQL masalasi - so'rov mavjud sandbox ichida, faqat o'qish (ADR-0053).

    So'rov Python dasturiga satr bo'lib joylanadi. Uch narsa uni xavfsiz
    ushlab turadi: `repr` (matn kodga aylanmaydi), authorizer (o'qishdan
    boshqa hamma narsa rad etiladi) va til eshigi (SQL faqat SQL masalasida).
    """
    runner = read("apps/api/problems/sqltasks.py")
    if '        _RUNNER.replace("__QUERY__", repr(query))\n' not in runner:
        return "sqltasks.py: so'rov dasturga `repr` siz joylanadi - matn Python kodiga aylanishi mumkin"
    if (
        "db.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in READS else sqlite3.SQLITE_DENY)\n"
        not in runner
    ):
        return "sqltasks.py: authorizer yo'q - so'rov ma'lumotni o'zgartira oladi yoki fayl ocha oladi"
    if "        source = sqltasks.compose(source)\n" not in read("apps/api/judging/services.py"):
        return "judging/services.py: SQL so'rovi judge'ga xom holda ketadi - Python dasturi deb yuritiladi"
    if '        if is_sql != (attrs["language"] == SQL_LANGUAGE):\n' not in read(
        "apps/api/judging/serializers.py"
    ):
        return "judging/serializers.py: SQL tili boshqa masalada (yoki boshqa til SQL masalasida) qabul qilinadi"
    return None


def dates_are_written_in_the_site_zone() -> str | None:
    """2026-10-06: sana yordamchilari standart holatda sayt zonasida yozadi.

    O'lchandi (jonli sayt): `dateTime` / `date` / `time` zonani belgilamasdi —
    web server (UTC) Toshkent vaqti bilan 14:56 da qilingan urinishni
    «9:56 AM» deb chizardi; klient komponentda brauzer uni qayta chizib,
    React gidratsiya xatosini (#418) berardi.
    """
    core = read("packages/shared/src/i18n/core.ts")
    if "  return { timeZone: DISPLAY_TIME_ZONE, ...options };\n" not in core:
        return "i18n/core.ts: sana yordamchilari zonasiz — server UTC vaqtini chizadi, klientda gidratsiya xatosi"
    if core.count("zoned(options)") != 3:
        return "i18n/core.ts: `dateTime`, `date` va `time` ning hammasi `zoned()` dan o'tmaydi"
    # A client component that is also server-rendered must not format a date
    # in the viewer's locale: Node has `uz` date data, the browser does not.
    table = read("apps/web/src/features/submissions/components/AttemptTable.tsx")
    if table.count("numericStamp(row.created_at)") != 2:
        return "AttemptTable.tsx: sana til bo'yicha formatlanadi — server va brauzer ICU'si har xil chizadi (gidratsiya xatosi)"
    return None


def docker_disk_stays_bounded() -> str | None:
    """2026-09-20: log 10m/3, builder GC, SHA teg yo'q, prune tasdiq'dan keyin.

    2026-10-06: GC chegarasi 10 GB, va deploy'dan keyin build cache TO'LIQ
    tozalanadi — chegaraning o'zi ushlab turmadi (69.6 GB, 36 soatda).

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
    if '"defaultKeepStorage": "10GB"' not in daemon:
        return "tools/docker-daemon.json: builder GC 10GB emas"
    if '"max-size": "10m"' not in daemon or '"max-file": "3"' not in daemon:
        return "tools/docker-daemon.json: json-file 10m/3 emas"

    prune = read("tools/prune_docker_disk.sh")
    if "docker image prune -f" not in prune:
        return "tools/prune_docker_disk.sh: `docker image prune -f` yo'q"
    if "\ndocker builder prune -af >/dev/null || true\n" not in prune:
        return "tools/prune_docker_disk.sh: build cache to'liq tozalanmaydi — `-f` ning o'zi 0 bayt bo'shatadi"
    if "docker volume prune" in prune:
        return "tools/prune_docker_disk.sh: volume prune — postgres/minio o'chadi"
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
SHARE_BUTTON = "apps/web/src/features/profile/components/ShareButton.tsx"


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
PROBLEM_SLUG_PAGE = "apps/web/src/app/(site)/problems/[slug]/page.tsx"
UPDATE_ID_PAGE = "apps/web/src/app/(site)/updates/[id]/page.tsx"
ROADMAP_ID_PAGE = "apps/web/src/app/(site)/platform-roadmap/[id]/page.tsx"


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


def judge_latency_gate_is_nightly() -> str | None:
    """Judge latency — launch gate (p50 < 5 s, p95 < 15 s) — Nightly'da.

    Ochiq band: `docs/09-development-plan/README.md` § "Launch gate"; mezon
    ADR-0004 da. Egasi 2026-09-21 da «doimiy Nightly job» ni tanladi — per-PR
    EMAS, chunki bu `pr_skips_heavy_ci` qarorini ag'darardi. Job ALOHIDA:
    E2E brauzer matritsasiga bog'langan darvoza aloqasiz sababdan qizarib,
    ayb noto'g'ri joyga yozilardi.

    ⚠️ Oxirgi ikki tekshiruv «darvoza o'likmi?» degan savolga javob beradi:
    byudjet taqqoslash o'chirilgan skript baribir `0` qaytaradi — ya'ni
    yashil, lekin o'lchov yo'q.
    """
    nightly = read(".github/workflows/nightly.yml")
    if "name: Latency — judge budget" not in nightly:
        return ".github/workflows/nightly.yml: `latency` jobi yo'q"
    if "--profile latency run --rm latency" not in nightly:
        return ".github/workflows/nightly.yml: latency jobi harness'ni yurgizmaydi"
    if "tests/latency" in read(".github/workflows/ci.yml"):
        return ".github/workflows/ci.yml: latency gate PR CI'ga qo'shilgan — qaror: faqat Nightly"
    compose = read("docker-compose.ci.yml")
    if "profiles: ['latency']" not in compose:
        return "docker-compose.ci.yml: latency `up -d` da ko'tariladi (profiles yo'q)"
    if "worker: { condition: service_started }" not in compose:
        return "docker-compose.ci.yml: latency `worker` ga bog'lanmagan — navbat bo'shamaydi"
    harness = read("tests/latency/check_judge_latency.py")
    if "if p50 > BUDGET_P50_MS:" not in harness:
        return "tests/latency/check_judge_latency.py: p50 byudjet taqqoslash yo'q"
    if "if p95 > BUDGET_P95_MS:" not in harness:
        return "tests/latency/check_judge_latency.py: p95 byudjet taqqoslash yo'q"
    return None


def security_boundary_is_loopback_only() -> str | None:
    """Chegara: hamma port loopback'da, judge hech narsa nashr etmaydi.

    `tools/deploy.sh` zanjiri `docker-compose.yml` + `docker-compose.public.yml`.
    Overlay `ports: !reset []` bilan bazaviy portni **o'chiradi** — shuning
    uchun bazaviy faylni yolg'iz o'qish MinIO'ni «9000:9000 da ochiq» deb
    ko'rsatadi, aslida unday emas (o'lchandi 2026-09-21: `curl
    127.0.0.1:9000/minio/health/live` → `HTTP 000`, `docker ps` → `9000/tcp`
    nashrsiz). Bu xato bir marta qilingan; qoida uni jimgina qaytarishning
    oldini oladi.

    ⚠️ Bu — QO'RIGCHI, o'lchov emas. To'liq tahlil (zanjirni birlashtirib
    haqiqiy port to'plamini hisoblash) `tools/check_security_boundary.py` da
    va o'sha CI job yurgizadi. Bu yerda uchta narsa tekshiriladi, chunki
    ularning har biri alohida jimgina yo'qolishi mumkin: darvoza CI'ga
    ulanganmi, overlay hali ham portlarni o'chiradimi, judge port e'lon
    qilmaganmi.

    Sana: 2026-09-21 — egasi «chegara bayonoti + dalillar to'plami» ni tanladi
    (audit oldidan). Yozuv: `docs/research/2026-09-21-security-boundary/`.
    """
    if "python3 tools/check_security_boundary.py" not in read(".github/workflows/ci.yml"):
        return ".github/workflows/ci.yml: chegara tekshiruvi CI'ga ulanmagan"
    overlay = read("docker-compose.public.yml")
    if overlay.count("ports: !reset []") < 3:
        return "docker-compose.public.yml: `!reset []` kamaygan — bazaviy portlar qaytadi"
    if "ports: !override ['127.0.0.1:" not in overlay:
        return "docker-compose.public.yml: loopback `!override` yo'q"
    judge = re.search(r"^  judge:\n(.*?)(?=^\w)", read("docker-compose.yml"), re.S | re.M)
    if judge is None:
        return "docker-compose.yml: `judge` servisi topilmadi"
    if re.search(r"^    ports:", judge.group(1), re.M):
        return "docker-compose.yml: judge port nashr etadi — 06-architecture: kiruvchi port yo'q"
    return None


THREAT_MODEL = "docs/10-operations/threat-model.md"
THREAT_MODEL_INDEX = "docs/10-operations/README.md"
THREAT_MODEL_RISKS = ("A-1", "A-2", "A-3", "A-4", "A-5", "A-6", "A-7", "A-8")


def threat_model_covers_the_platform() -> str | None:
    """Threat model bor, indeksdan topiladi va risk registri bo'sh emas.

    ADR-0004 tashqi auditni public launch oldidan majburiy qiladi; audit esa
    threat model'siz boshlanmaydi. Hujjatning O'ZI yetarli emas — uchta
    bo'lak jimgina yo'qolishi mumkin va har biri o'zicha yomon:

    - fayl o'chsa, audit oldidan hech kim sezmaydi;
    - `docs/10-operations/README.md` dan havola uzilsa, hujjat qoladi-yu
      keyingi o'quvchi uni topmaydi (10 ta hujjat ichida);
    - qabul qilingan risklar jadvali (A-1…A-8) bo'shasa, hujjat «hammasi
      nazoratda» deb o'qiladi — aslida esa egasi ularni ATAYLAB qabul qilgan.

    ⚠️ Bu — QO'RIGCHI, mazmun tekshiruvi emas: hujjat to'g'rimi — o'lchab
    bo'lmaydi; mavjudmi va muhim bo'laklari joyidami — mumkin.

    Sana: 2026-09-21 — egasi «threat model — butun platforma» variantini
    tanladi (audit yo'lida chegara bayonotidan keyingi qadam).
    """
    if not (ROOT / THREAT_MODEL).exists():
        return f"{THREAT_MODEL}: threat model yo'q — ADR-0004 auditdan oldin talab qiladi"
    if "](threat-model.md)" not in read(THREAT_MODEL_INDEX):
        return f"{THREAT_MODEL_INDEX}: threat model havolasi yo'q — hujjat indeksdan topilmaydi"
    model = read(THREAT_MODEL)
    missing = [risk for risk in THREAT_MODEL_RISKS if risk not in model]
    if missing:
        return f"{THREAT_MODEL}: qabul qilingan risklar yo'q — {', '.join(missing)}"
    if "privileged: true" not in model:
        return f"{THREAT_MODEL}: judge `privileged: true` xavfi yozilmagan (A-1)"
    return None


LICENCE_RECORD = "docs/research/2026-09-21-licence-inventory"


def licence_inventory_is_current() -> str | None:
    """Litsenziya inventari bor, CI'ga ulangan va muhim bo'laklari joyida.

    `docs/09-development-plan/README.md:81` — launch gate: «Huquqiy: litsenziya
    tahlili yurist tomonidan tasdiqlangan». Advokatga beriladigan narsa —
    inventar; u yo'qolsa yoki CI'dan uzilsa, gate **jimgina** bo'sh qoladi.

    ⚠️ Bu — QO'RIGCHI: haqiqiy drift o'lchovi
    (`tools/licence_inventory.py --check`, paket to'plamini lockfile'lar bilan
    taqqoslaydi) o'sha CI qadamida yuradi. Bu yerda faqat yo'qolishi mumkin
    bo'lgan uchta narsa: fayl, CI ulanishi, hujjatning risk bo'limlari.

    Sana: 2026-09-21 — egasi «Litsenziya inventari» ni tanladi (audit yo'lidan
    keyingi ikkinchi uzoq muddatli launch gate).
    """
    if not (ROOT / LICENCE_RECORD / "packages.tsv").exists():
        return f"{LICENCE_RECORD}/packages.tsv: inventar yo'q — 09:81 launch gate"
    if "python3 tools/licence_inventory.py --check" not in read(".github/workflows/ci.yml"):
        return ".github/workflows/ci.yml: inventar drift tekshiruvi CI'ga ulanmagan"
    readme = read(f"{LICENCE_RECORD}/README.md")
    for needed in ("## 4. Licences that could not be determined", "## 6. Copyleft register"):
        if needed not in readme:
            return f"{LICENCE_RECORD}/README.md: `{needed}` yo'q — hujjat qisqargan"
    if "go/judge-go" not in readme:
        return f"{LICENCE_RECORD}/README.md: Go qatori yo'q — Go qamrab olinmagan"
    return None


LATENCY_RECORD = "docs/research/2026-09-21-judge-latency"
LATENCY_HARNESS = "tests/latency/check_judge_latency.py"
LATENCY_SUMMARY = "tools/latency_summary.py"
NIGHTLY = ".github/workflows/nightly.yml"


def judge_latency_gate_is_recorded() -> str | None:
    """Latency o'lchovi bor, indeksdan topiladi va **qayd zanjiri** uzilmagan.

    `docs/09-development-plan/README.md` § "Launch gate":
    «Judge latency o'lchangan: p50 < 5s, p95 < 15s». Bu — launch gate'idagi
    agent yopa oladigan **yagona** band (qolgan ikkitasi egasining ishi:
    tashqi audit va yurist).

    ⚠️ Nega qo'riqchi kerak: job bor edi va **yashil** bo'lishi mumkin edi,
    lekin raqam faqat CI logiga tushardi — ya'ni gate katakchasi hech qachon
    o'zgarmasdi. O'lchov bor, **qayd** yo'q. Shuning uchun bu qoida
    zanjirning uzilishga moyil uch bo'g'inini qo'riqlaydi: yozuv fayli,
    mashina o'qiydigan belgi, va uni run sahifasiga olib chiqadigan qadam.

    Ataylab **talab qilinmaydi**: jadvalda raqam bo'lishi. 2026-09-21 holatida
    hech qanday raqam yo'q (job bir marta ham ishlamagan, production o'lchovi
    esa egasi qaroriga qoldirilgan). Raqam paydo bo'lgach qoida kuchaytiriladi
    — aks holda jadval jimgina bo'shab qolishi mumkin.
    """
    if not (ROOT / LATENCY_RECORD / "README.md").exists():
        return f"{LATENCY_RECORD}/README.md: latency yozuvi yo'q — 09 launch gate"
    if "](2026-09-21-judge-latency/README.md)" not in read("docs/research/README.md"):
        return "docs/research/README.md: latency yozuvi indeksda yo'q — topilmaydi"
    harness = read(LATENCY_HARNESS)
    if 'REPORT_MARKER = "LATENCY_JSON: "' not in harness:
        return f"{LATENCY_HARNESS}: mashina o'qiydigan belgi yo'q — raqam olinmaydi"
    if "emit_report(env, samples, p50, p95)" not in harness:
        return f"{LATENCY_HARNESS}: hisobot chiqarilmaydi — zanjir uzilgan"
    # Belgining IKKI nusxasi mos kelishi shart: harness chiqaradi, summary
    # o'qiydi. Biri o'zgarsa zanjir JIMGINA uziladi — summary belgini
    # topmaydi, exit 2 beradi, lekin sabab kodda ko'rinmaydi.
    if 'MARKER = "LATENCY_JSON: "' not in read(LATENCY_SUMMARY):
        return f"{LATENCY_SUMMARY}: `MARKER` harness belgisiga mos emas — zanjir uzilgan"
    nightly = read(NIGHTLY)
    if "tools/latency_summary.py" not in nightly:
        return f"{NIGHTLY}: latency raqami run sahifasiga yozilmaydi"
    # ⚠️ Langar ATAYLAB ikki qatorli: yalang `set -o pipefail` izohda ham
    # uchraydi (o'lchandi), ya'ni bunday tekshiruv haqiqiy qator o'chirilganda
    # ham o'tib ketardi — yolg'on yashil. Ikki qator birga esa faqat kodda
    # bo'ladi va `pipefail` aynan compose buyrug'iga qo'llanganini isbotlaydi.
    if "          set -o pipefail\n          docker compose" not in nightly:
        return f"{NIGHTLY}: `pipefail` compose buyrug'iga qo'llanmagan — byudjet buzilishi job'ni qizil qilmaydi"
    if "--profile latency run --rm latency" not in nightly:
        return f"{NIGHTLY}: harness umuman chaqirilmaydi"
    record = read(f"{LATENCY_RECORD}/README.md")
    if "Attempt.created_at" not in record:
        return f"{LATENCY_RECORD}/README.md: metrika ta'rifi yo'q — raqam nima ekani noaniq"
    if "API=https://rankwant.uz/api/v1" not in record:
        return f"{LATENCY_RECORD}/README.md: production buyrug'i yo'q — gate raqami yo'li yopilgan"
    return None


SECURITY_SUITE = "tests/security/run.sh"
SECURITY_SUITE_RECORD = "docs/research/2026-09-21-security-suite"


def security_suite_runs_automatically() -> str | None:
    """`tests/security` haqiqatan bir joyda avtomatik yuriydimi.

    O'lchandi 2026-09-21: `tests/security/run.sh` ning **yagona** chaqiruvchisi
    `.github/workflows/security.yml` (94–95-qatorlar) edi va u **o'chirilgan**
    (`on: workflow_dispatch` + job `if: false`, egasi qarori 2026-09-21).
    Ya'ni skript sarlavhasi «CI da har PR da ishlaydi» deb yozib turgan bo'lsa
    ham, uning statik yarmi — judge host qoidalari, IDOR, PAT hash, rate limit
    — **hech qayerda** avtomatik yurmasdi. Dinamik yarmining qamrovi bor edi:
    Nightly `e2e` job'idagi bake-off qadami ayni `runner.py` ni case-filtrisiz
    yurgizadi (`ISOLATION_CASES` o'sha yerda o'lchanadi).

    Egasi 2026-09-21 da «Nightly'ga ulaymiz» ni tanladi. Yechim — statik rejim:
    to'plam `SECURITY_STATIC_ONLY=1` bilan chaqiriladi, ya'ni allaqachon
    qoplangan dinamik yarmi **takrorlanmaydi**. Yozuv:
    `docs/research/2026-09-21-security-suite/`.

    ⚠️ Bu QO'RIGCHI, o'lchov emas: zanjirning uzilishga moyil bo'g'inlarini
    ushlaydi (chaqiruv, rejim, `pyyaml`, chegara, yozuv). Skriptning o'zi
    to'g'ri ishlashini faqat Nightly job'ining o'z yurishi o'lchaydi.
    """
    suite = read(SECURITY_SUITE)
    # Langar ATAYLAB to'liq kod qatori: yalang `SECURITY_STATIC_ONLY` izohlarda
    # ham uchraydi (o'lchandi), ya'ni shunday tekshiruv haqiqiy shox o'chirilganda
    # ham o'tib ketardi — yolg'on yashil.
    if 'if [ -n "${SECURITY_STATIC_ONLY:-}" ]; then' not in suite:
        return f"{SECURITY_SUITE}: statik rejim shoxi yo'q — dinamik yarmi takrorlanadi"
    # ⚠️ Eski sarlavha da'vosi qaytmasin. U noto'g'ri, va aynan shu yolg'on
    # ishonch tufayli bo'shliq sezilmay yotgan edi: fayl «har PR da ishlaydi»
    # deb yozardi, chaqiruvchi esa o'chirilgan edi.
    if "izolyatsiyasi — CI da har PR da ishlaydi" in suite:
        return f"{SECURITY_SUITE}: «har PR da ishlaydi» da'vosi qaytgan — chaqiruvchi o'chirilgan"
    nightly = read(NIGHTLY)
    # Ikki langar ham kod qatorlari: fayl nomi va rejim nomi izohlarda ham
    # uchraydi (o'lchandi), ya'ni yalang matn qidirish yolg'on yashil berardi.
    if "        run: tests/security/run.sh" not in nightly:
        return f"{NIGHTLY}: xavfsizlik to'plami hech qayerda yurmaydi — statik yarmi yopilmagan"
    if "          SECURITY_STATIC_ONLY: '1'" not in nightly:
        return f"{NIGHTLY}: to'plam statik rejimda chaqirilmaydi — bake-off bilan takrorlanadi"
    if "        run: pip install pyyaml" not in nightly:
        return f"{NIGHTLY}: `pyyaml` o'rnatilmaydi — `check_compose.py` yiqiladi"
    # Chegara MAJBURIY: self-hosted runner'da abadiy kutib qolgan job butun
    # navbatni ushlab turadi. Repo qoidasi — har job'da `timeout-minutes`.
    #
    # Job bloki ATAYLAB chegaralangan (`(?=^  \S)`): chegarasiz `.*?` keyingi
    # job'ning `timeout-minutes` ini topib qo'yardi, ya'ni bu tekshiruv hech
    # qachon yiqilmasdi — o'lchandi, aynan shu tuzoq bilan yozilgan edi.
    job = re.search(r"^  security:\n(.*?)(?=^  \S)", nightly, re.S | re.M)
    if job is None:
        return f"{NIGHTLY}: `security` job'i topilmadi"
    if not re.search(r"^    timeout-minutes: \d+", job.group(1), re.M):
        return f"{NIGHTLY}: `security` job'ida chegara yo'q — abadiy kutish mumkin"
    if not (ROOT / SECURITY_SUITE_RECORD / "README.md").exists():
        return f"{SECURITY_SUITE_RECORD}/README.md: yozuv yo'q — statik rejim sababi yo'qoladi"
    if "](2026-09-21-security-suite/README.md)" not in read("docs/research/README.md"):
        return "docs/research/README.md: xavfsizlik to'plami yozuvi indeksda yo'q — topilmaydi"
    record = read(f"{SECURITY_SUITE_RECORD}/README.md")
    # Sabab yozilmasa, keyingi o'quvchi `SECURITY_STATIC_ONLY` ni «tejash»
    # deb o'ylab, dinamik yarmini ikkinchi marta yoqib qo'yishi mumkin.
    if "ISOLATION_CASES" not in record:
        return f"{SECURITY_SUITE_RECORD}/README.md: dinamik yarmi qayerda qoplangani yozilmagan"
    return None


TOOLS_COMPOSE = "docker-compose.tools.yml"
BOUNDARY_RECORD = "docs/research/2026-09-21-security-boundary/README.md"
OPS_INDEX = "docs/10-operations/README.md"


def adminer_is_declared_outside_the_deploy_chain() -> str | None:
    """`adminer` e'lon qilingan, qadalgan, loopback'da — va zanjirdan TASHQARIDA.

    O'lchandi 2026-09-21: `rankwant-adminer` bir kundan ortiq **hech qanday
    compose faylisiz** ishladi — `Config.Labels` `{}`, obraz suzuvchi
    `adminer:4` tegi, `127.0.0.1:8081`, qo'lda `rankwant_default` tarmog'iga
    ulangan. Qo'lida DB credential bor, lekin uni hech bir tekshiruv
    ko'rmasdi: na `docker compose config`, na chegara qoidasi. Chegara yozuvi
    buni auditor uchun **1-divergensiya** deb qayd etgan.

    Egasi 2026-09-21 da «compose'ga qo'shamiz — profil bilan» ni tanladi.
    Yechim — ALOHIDA overlay: `docker-compose.tools.yml`. Sabab: u
    `docker-compose.yml` ga qo'shilsa `tools/deploy.sh` zanjiriga, demak
    ishlab chiqarish chegarasiga kirardi (`check_security_boundary.py` nashr
    etilgan portlarni aynan shu zanjirdan sanaydi). Pretsedent:
    `docker-compose.ci.yml`, `docker-compose.replicas.yml`.

    ⚠️ Bu QO'RIGCHI, o'lchov emas: e'lon qilishning shartlarini va faylning
    ko'rinadigan qolishini qo'riqlaydi. Fayl haqiqatan to'g'ri ekanini
    `check_security_boundary.py` o'lchaydi.
    """
    # ⚠️ Mavjudlik ALOHIDA tekshiriladi, `read()` dan oldin. `read()` yo'q
    # faylda `Unreadable` ko'taradi ⇒ exit 2, ya'ni «o'qilmadi». Bu to'g'ri
    # xatti-harakat, lekin **sababni aytmaydi**: fayl o'chirilganda qaysi qaror
    # buzilgani ko'rinmay qoladi. Pretsedent — `security_suite_runs_automatically`.
    if not (ROOT / TOOLS_COMPOSE).exists():
        return f"{TOOLS_COMPOSE}: fayl yo'q — vositalar yana e'lon qilinmagan"
    tools = read(TOOLS_COMPOSE)
    if "  adminer:" not in tools:
        return f"{TOOLS_COMPOSE}: `adminer` servisi yo'q — vosita yana e'lon qilinmagan"
    if "profiles: ['tools']" not in tools:
        return f"{TOOLS_COMPOSE}: `profiles` yo'q — `up -d` uni o'zi ko'tarib qo'yadi"
    # Digest, suzuvchi teg EMAS: `adminer:4` hech qachon o'z-o'zidan
    # yangilanmaydi, ya'ni «qaysi kod ishlayapti» degan savol javobsiz qoladi.
    if "image: adminer@sha256:" not in tools:
        return f"{TOOLS_COMPOSE}: obraz digest bilan qadalmagan — ishlayotgan kod noma'lum"
    if "ports: ['127.0.0.1:8081:8080']" not in tools:
        return f"{TOOLS_COMPOSE}: loopback porti yo'q — DB UI si LAN dan yetib bo'ladi"
    for chain in ("docker-compose.yml", "docker-compose.public.yml"):
        if "  adminer:" in read(chain):
            return f"{chain}: `adminer` deploy zanjiriga qo'shilgan — ishlab chiqarish chegarasida"
    # E'lon qilishning O'ZI yetarli emas: o'lchanmasa fayl yana ko'rinmas
    # bo'ladi — va bir kundan keyin kimdir uni qo'lda ishga tushirib qo'yadi.
    if TOOLS_COMPOSE not in read("tools/check_security_boundary.py"):
        return "tools/check_security_boundary.py: tools fayli o'lchanmaydi — yana ko'rinmas bo'ladi"
    if TOOLS_COMPOSE not in read(OPS_INDEX):
        return f"{OPS_INDEX}: `{TOOLS_COMPOSE}` indeksda yo'q — faylni topib bo'lmaydi"
    if not (ROOT / BOUNDARY_RECORD).exists():
        return f"{BOUNDARY_RECORD}: chegara yozuvi yo'q — divergensiya tarixi yo'qoladi"
    record = read(BOUNDARY_RECORD)
    if "Resolution, 2026-09-21" not in record:
        return f"{BOUNDARY_RECORD}: 1-divergensiyaning sanali yechimi yo'q — auditor ochiq bandni ko'radi"
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
    ("lug'at hook tartibi barqaror", locale_use_is_unconditional),
    ("User modeli tenglik maydonlari", user_parity_fields_kept),
    ("vaqt tamg'alari bazadan", timestamps_come_from_bases),
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
    ("sxema o'zgarsa web tiplari tekshiriladi", schema_change_wakes_web_job),
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
    ("bosh sahifa CSS inline", homepage_css_is_inlined),
    ("bosh sahifa CF email-decode yo'q", homepage_skips_cf_email_decode),
    ("login yupqa auth.css", login_uses_narrow_auth_css),
    ("kirgan foydalanuvchi bosh sahifasi — shaxsiy panel", signed_in_home_is_the_dashboard),
    ("bugun faol ro'yxati sessiyadan o'qiladi", home_presence_reads_sessions),
    ("sozlamalar: olti bo'lim va 14 kunlik o'chirish", settings_six_sections_and_grace),
    ("sozlamalar tugmalari 44 px", settings_controls_are_44px),
    ("sozlagich telefonda yaqin", customizer_reachable_on_a_phone),
    ("jamoa sahifasi boshqariladi", team_page_is_managed_data),
    ("jamoa sahifasi ixcham", team_page_is_compact),
    ("qanday ishlaydi sahifasi qidiriladigan", about_page_is_one_searchable_page),
    ("qidiruv bitta dvigatel", site_search_is_one_engine),
    ("bildirishnomalar shartnomasi", notifications_inbox_contract),
    ("qidiruv chegaralangan va aniq", site_search_is_bounded_and_exact),
    ("urinishlar lentasi umumiy jadvalda", attempts_feed_is_the_shared_table),
    ("scroll bitta lug'atda", scroll_is_one_vocabulary),
    ("yon menyu bo'limlari ajralib turadi", side_menu_keeps_its_sections),
    ("yon menyu belgilari bitta so'rovda", side_menu_badges_are_one_request),
    ("sanalar sayt zonasida", dates_are_written_in_the_site_zone),
    ("muharrir varag'i yon menyudan chetda", editor_sheet_clears_the_side_menu),
    ("SQL so'rovi faqat o'qiydi", sql_queries_only_read),
    ("ikki bosqichli yurishlar hech narsa bo'lishmaydi", two_pass_runs_share_nothing),
    ("faqat javob masalasida kod yurmaydi", answer_problems_run_no_code),
    ("funksiya masalasi hakam dasturi bilan yuriladi", function_problems_are_composed),
    ("tekshiruv yo'llari haqiqiy judge'da isbotlangan", evaluation_paths_are_proven),
    ("mehmon header'i har tilda sig'adi", guest_header_fits_every_locale),
    ("Nightly stendi production bilan mos", nightly_stack_matches_production),
    ("sozlagich: tez qator birinchi", customizer_quick_row_first),
    ("kirgan foydalanuvchi header'i sig'adi", signed_in_header_fits),
    ("SECRET_KEY standart qiymatsiz", secret_key_has_no_fallback),
    ("ommaviy stack sirlarini talab qiladi", public_stack_requires_its_secrets),
    ("noto'g'ri kirish urinishlari cheklangan", failed_sign_ins_are_limited),
    ("Dependabot lock'lari qayta yasaladi", dependabot_locks_are_recompiled),
    ("clay qorong'i rejimga ergashadi", clay_follows_dark_mode),
    ("kirish sahifasi o'z-o'ziga yetarli", sign_in_page_is_self_contained),
    ("customization invariantlari", customization_invariants_are_written),
    ("Security run o'chiq", security_run_is_disabled),
    ("judge latency Nightly'da", judge_latency_gate_is_nightly),
    ("chegara faqat loopback", security_boundary_is_loopback_only),
    ("threat model platformani qamraydi", threat_model_covers_the_platform),
    ("litsenziya inventari joriy", licence_inventory_is_current),
    ("judge latency gate qayd etiladi", judge_latency_gate_is_recorded),
    ("xavfsizlik to'plami avtomatik yuriydi", security_suite_runs_automatically),
    ("adminer e'lon qilingan, zanjirdan tashqarida", adminer_is_declared_outside_the_deploy_chain),
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
