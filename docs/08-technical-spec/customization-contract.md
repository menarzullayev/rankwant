# Customization Contract

The rules an agent must follow before adding or changing a customization
setting. Everything here is **measured from the code**, not aspirational: each
row names the file that enforces it, and `tools/check_customization_contract.py`
fails when this document and the code disagree.

Why a single document: on 2026-09-24 the same defect landed twice in this area.
`themeToggle` reached the client in #244 but never reached the server's accepted
key set, so picking a theme-toggle style made the whole `appearance` write
`400` — the device showed the change, the account never got it. The guard that
should have caught it (`apps/api/tests/test_prefs.py`) had a hand-written key
list that had gone stale. Rules scattered across code comments and ADRs do not
stop that; a contract plus a gate does.

Related: `theme-customizer.md` (how the colour model and the panel work),
`i18n-precedence.md` (the locale chain in full), ADR-0008, ADR-0017, ADR-0024.

The block below is **machine-checked** against `apps/api/core/prefs.py` by
`tools/check_customization_contract.py`. Edit both together; the gate fails on
any disagreement, so this document cannot drift away from the code.

<!-- contract-constants -->
```contract
schema_version: 2
size: 75 150 5
scale: 0.9 1.15
line_height: 0.9 1.4
tracking: -0.02 0.06
width: 1000 1800 100
template_max: 5
template_name_max: 24
fonts: plex inter jakarta roboto dm-sans lexend
densities: compact comfortable spacious
visions: normal protan tritan
motions: system full mild off reduce
effects: none fade circle
```

## 1. Scope — customizable or invariant

**Customizable** (the user, on their own account or device):

    theme · locale · appearance · a11y · templates · problemset toggles

**Invariant** (never a customization setting; changing one is not a
preference, it is a policy change and needs its own decision record):

    security policy · authorization and roles · judge limits and sandboxing
    · contest rules and verdicts · rating model · content and editorial gates

The boundary is enforced where those things live: `apps/api/core/admin.py`
(staff-only surfaces), the role/group model (`roles_groups_and_object_authors`),
and the judge's own preflight. No customization setting may reach them.

## 2. Settings

Persisted per account in `User.ui_prefs`, grouped and versioned
(`SCHEMA_VERSION`, currently 2). Validation lives in `apps/api/core/prefs.py`
and is shared by the panel, the migration and any future CLI.

### 2.1 `appearance`

| key | type | default | allowed / bounds |
| --- | --- | --- | --- |
| `style` | slug | `clay` | client catalogue (`STYLE_IDS`, 12 styles) |
| `accent` | `{hue, sat}` or null | null | hue 0–360, sat 0–100 |
| `font` | enum or null | null | `FONTS` — plex, inter, jakarta, roboto, dm-sans, lexend |
| `fontHeading` | enum or null | null | `FONTS` |
| `size` | integer, step 5 | 100 | 75–150 (`SIZE_MIN/MAX/STEP`) |
| `scale` | float | 1 | 0.9–1.15 (`SCALE_MIN/MAX`) |
| `lineHeight` | float | — | 0.9–1.4 (`LINE_HEIGHT_MIN/MAX`) |
| `tracking` | float | — | −0.02–0.06 (`TRACKING_MIN/MAX`) |
| `width` | integer, step 100 | — | 1000–1800 (`WIDTH_MIN/MAX/STEP`) |
| `density` | enum | `comfortable` | `DENSITIES` — compact, comfortable, spacious |
| `navMode` | catalogue | `sidenav` | client catalogue |
| `navShape` | catalogue | `default` | client catalogue |
| `card` | catalogue | default | client catalogue |
| `pattern` | catalogue | none | client catalogue |
| `verdictStyle` | catalogue | auto | client catalogue |
| `statusStyle` | catalogue | auto | client catalogue |
| `loadingStyle` | catalogue | default | client catalogue |
| `iconPack` | catalogue | default | client catalogue |
| `overlayStyle` | catalogue | default | client catalogue |
| `formStyle` | catalogue | default | client catalogue |
| `themeToggle` | catalogue | `doira` | `THEME_TOGGLES` (7) |

**Catalogue keys validate their shape, not their list.** The allowed values live
in the client (`nav-config.ts`, `lib/theme/*.ts`) and grow often. A second copy
server-side rots silently and starts rejecting a newly added pack with `400` —
measured 2026-09-18 and again 2026-09-24. The server's job is to stop garbage
and unbounded strings (`_clean_slug`: `[a-zA-Z][a-zA-Z0-9-]*`, ≤ 24).

### 2.2 Outside `appearance`, on purpose

| setting | where | why not in `appearance` |
| --- | --- | --- |
| `theme` | `User.theme` | already canonical (D47); storing it twice is the conflict that got the duplicate field rejected |
| `locale` | `User.locale` + device cookie `rw_locale` | language is a device property, not an appearance value (§4) |
| `a11y` | `ui_prefs.a11y` | separate group: `vision` (normal/protan/tritan), `motion` (system/full/mild/off, plus legacy `reduce`), `bigTargets`, `strongFocus` |
| `templates` | `ui_prefs.templates` | `TEMPLATE_MAX` 5, `TEMPLATE_NAME_MAX` 24 |
| `problemset` | `ui_prefs.problemset` | `hideTags`, `hideSolved` (ADR-0024) |
| `sound`, `effect` | `ui_prefs` | v1 leftovers, kept so an old device copy and an old client do not break |
| `tokens` | `ui_prefs.tokens` | strong mode (D9), disabled by D43 |

## 3. Precedence

Per setting, not one global chain. The source of truth is **the account**;
the device copy exists only to paint before hydration reads the session.

    appearance · a11y · templates · problemset
        account (D4)  >  device cache (localStorage, first paint)  >  team default (D37)  >  hard fallback

    style
        account  >  device seeds the account when the account has none

    locale
        device cookie  >  account (a SEED, not an override)  >  Accept-Language

    theme
        account (`User.theme`)  >  device cache (first paint)  >  `system`

`locale` is a deliberate deviation from D4: one person may read Uzbek on a
phone and English on a work machine. `rw_locale=auto` is a marker meaning
"explicitly automatic", which is not the same as "no choice" — see
`i18n-precedence.md`.

An **unknown value** must never win: an unrecognised style falls back to
`clay`, an unrecognised mode to `system`, an unrecognised version is
**preserved but not applied** (D36) so a newer client's write survives an
older client.

## 4. Capability

| capability | Guest | User | Admin |
| --- | --- | --- | --- |
| theme, locale, appearance, a11y | yes (device-local) | yes (account-synced) | yes |
| templates | local only | up to `SIGNED_IN_TEMPLATE_LIMIT` | yes |
| icon gallery (226 keys) | — | — | lab/admin, closed by default |
| platform defaults (`SiteAppearance`) | — | — | Django admin only |
| invariants (§1) | — | — | — |

The panel is deliberately **not** role-gated: appearance is a personal
preference for everyone, including guests. What differs is where it is stored
and how many templates travel.

## 5. Runtime

    control → setAppearance / setMode
            → commit()                    applyAppearance + applyA11y + applyAndCacheAccent
            → rememberAppearance()        device cache (localStorage)
            → announcePrefs()             `PREFS_EVENT`
            → PrefsSync                   PATCH /me/  → prefs.validate → User.ui_prefs

    first paint (before hydration)
            layout.tsx inline bootstrap reads localStorage → sets `data-*`

There is exactly one path. A second mechanism (a new store, a direct DOM write
from a component, a second PATCH) is a defect, not a shortcut. `lib/theme/*` is
the only place that writes appearance to the DOM; `PrefsSync` is the only place
that writes it to the server.

The bootstrap must run **before** hydration and must not be blocked — the CSP
nonce on those inline tags is load-bearing (`tools/check_csp_nonce.py`).

## 6. Validation

Gates that already exist and must stay green:

| gate | covers |
| --- | --- |
| `tools/check_customization_contract.py` | this document vs the code |
| `tools/check_contrast.py` | 18 palettes, WCAG AA, accent-on-accent pairs |
| `tools/check_design_tokens.py` | no raw hex, no px font sizes |
| `tools/check_decisions.py` | 59 owner decisions, including the ones above |
| `tools/check_csp_nonce.py` | the pre-hydration bootstrap actually runs |
| `apps/api/tests/test_prefs.py` | schema, migration, bounds, the full customizer write |
| `apps/web/tests/unit/*` | clamp helpers, first paint, sync merge |
| visual regression + E2E | the painted result |

Acceptance for any appearance change: persists after reload · persists after
login · no flash of the wrong theme · every component honours the token layer ·
contrast stays AA · the auth tree keeps its narrow sheet · no SSR/hydration
mismatch.

## 7. Agent invariants

    An agent MUST NOT introduce a new customization setting without updating
    this contract AND the gate that checks it.

    An agent MUST NOT add a key to the client that the server's
    `APPEARANCE_KEYS` does not accept — the whole `appearance` write fails,
    not just that key.

    An agent MUST NOT change the precedence of an existing setting without a
    decision record.

    An agent MUST NOT introduce a second persistence mechanism, a second
    apply path, or a second PATCH for preferences.

    An agent MUST NOT bypass customization validation — no direct write to
    `ui_prefs`, no client-side-only value that the server rejects.

    Unknown values MUST have an explicit fallback, and an unknown schema
    version MUST be preserved rather than dropped.

These are recorded in `CLAUDE.md` and guarded by `check_decisions.py`, so they
are read by agents at the point of work, not only here.
