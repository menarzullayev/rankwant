# Theme Customizer

**STATUS:** shipped (2026-09-14)

Decisions: [research/2026-09-14-rankwant-theme-customizer-design/DECISION-SESSION.md](../research/2026-09-14-rankwant-theme-customizer-design/DECISION-SESSION.md) (D1–D54).
Entry points: the header icon, a floating tab on desktop, `Ctrl+.`, and
`/settings/korinish`.

## What it does

A user picks a style, a theme mode, a colour, a font, a size and a
density, and saves the result as a template. Eight team templates apply a
whole combination in one click. The result is stored on the account, so it
follows the user to another device, and on the device, so it applies before
hydration without a flash.

## Kit-family writer (D48)

Contestant **Appearance → Interfeys** is the only UI that writes kit-family
prefs: `verdictStyle`, `statusStyle`, `loadingStyle`, `overlayStyle`,
`formStyle`, `iconPack`. The list lives in
`apps/web/src/components/customizer/chrome.ts` as `KIT_FAMILY_KEYS`.

`/admin/kit` is the design-system lab (playground + icon gallery). It must
not call `setAppearance`. Applying a team template **does** write kit
families: all eight share `TEMPLATE_KIT_DEFAULTS` and `matchTemplate`
compares them (D49). A leftover circle verdict is no longer «Klassik».
Layout chrome (`navMode`, `navShape`, `card`, `pattern`, `fontHeading`,
`size`, `scale`, `lineHeight`, `tracking`, `width`) stays personal (D50)
— applying Klassik does not steal the sidenav.

Measured 2026-09-21: kit families were **50 chips**; D51 replaced them with
**six** `SelectField` controls (one tab stop each). Native `<select>` is
not used — the OS list paints white in dark mode. Closed accordion groups
still unmount (CUST-100). Layout families (`navMode`, `navShape`, `card`,
`pattern`) stay chips (D53) — two to five options, not a catalogue.

## The colour model

The user chooses a **hue and saturation**, never a hex (D42). The system
derives the lightness per environment.

That is not a stylistic preference. Measured on the default palette, a
light ground needs `L ≤ 0.1733` for accent-as-text to clear AA, while a
dark ground needs `L ≥ 0.2160`. **The ranges do not overlap**, so no single
colour can serve both — which is why `globals.css` declares a separate
accent per environment (`#476dc7` light, `#7ea4ff` dark).

Verified: 12 hues × 3 saturations × 2 environments = 72 cases, no failures.
Yellow at full saturation becomes olive in light mode, so the derived
result is shown before it is saved.

### Three pairs, not one

| Pair | Where | Derived from |
|---|---|---|
| `--rw-accent` + `--rw-accent-fg` | filled button | ink chosen by luminance |
| `--rw-accent-soft` + `--rw-accent-ink` | tinted chip | both from the hue |
| `--rw-accent-ink` on the page | link text | the band above |

`--rw-accent-ink` has to clear both the page backgrounds **and** the chip,
so it is derived against the union of the two.

### The guarantee has two layers

`tools/check_contrast.py` enumerates the eighteen palettes in CI. It cannot
enumerate user combinations, so the panel runs **the same arithmetic in the
browser** (`apps/web/src/lib/theme/color.ts`) and blocks saving a
combination that fails. Warning and allowing would produce unreadable
interfaces for the team to clean up later. The panel must not say «fails
AA (4.5:1)» when the ratio is unmeasured (D52 / APP-9): that sentence is
only for a computed ratio below the target.

Both implementations must be checked against known values before either is
trusted: `#000000`/`#ffffff` = 21.00, `#767676`/`#ffffff` = 4.54,
`#777777`/`#ffffff` = 4.48.

**Measure against every background the checker uses** — `ground`,
`surface`, `surface-2`, `chrome`, `chip`, `field`, `hover`. A hand-picked
subset under-reports: doing exactly that is how a defect in seven palettes
stayed hidden.

## Environment detection

Determine the environment from the **measured ground luminance**, never
from the `dark` class on `<html>`.

Six of the twelve styles are single-environment (`dual: false`), so they
have no `[data-style="x"].dark` block. On `clay` the `dark` class is
present while every background is light. Reading the class produced a dark
chip against light backgrounds, no ink could clear the set, and the
fallback silently collapsed `--rw-accent-ink` onto `--rw-accent` — links
rendered at 2.74:1.

## Colour vision

`protan` and `tritan` adapt the palette; they do not simulate it. A
colour-blind user already sees the page that way — what helps is a palette
whose states are distinguishable.

The values are derived at runtime against the measured backgrounds, the
same way the accent is. They cannot be written statically in CSS: every
semantic ink is declared per palette and `[data-style="x"].dark` outranks
any `[data-style]`-level `[data-vision]` rule, so a static block would lose
silently.

Shape and text remain the primary channel. Achromatopsia is handled by
those alone: on a light ground the adjacent lightness steps of three states
are only 1.63:1 apart, so colour cannot carry the meaning at all.

## Storage

`User.ui_prefs`, grouped and versioned (D33):

    {version: 2, appearance, tokens, a11y, templates, sound, effect}

Validation lives in `apps/api/core/prefs.py` so the panel, the migration
and any future CLI share one source. Unknown versions are **preserved but
not applied** — an older client must not erase what a newer one wrote.

The theme is **not** in `appearance`: `User.theme` already exists and is
canonical (D47). Storing it twice is the conflict that got a separate field
rejected in the first place.

`tools/.update-sync.json`-style device mirroring applies here too:
`localStorage` carries the choice for pre-hydration, the account is the
source of truth.

## Kill switch

`NEXT_PUBLIC_CUSTOMIZER=0` hides the floating tab, the header icon and the
panel. Saved settings stay in the database and on the device.

**Limitation:** `NEXT_PUBLIC_*` is baked into the bundle at build time, so
turning it off needs a rebuild (~40 s). A runtime switch would need an
API-side flag, which is separate work.

## Pitfalls worth keeping

- **Provider order matters.** `CustomizerProvider` calls `useSession()`, so
  it must sit *inside* `SessionProvider`. Inverted, React throws on the
  first render and the whole tree fails to mount — while `curl` returns 200
  and CI stays green, because the server-rendered shell is produced before
  the client tree runs. Verify client-side failures in a real browser.
- **Do not put side effects inside `setState` updaters.** React may call an
  updater more than once (StrictMode does), so DOM writes and network calls
  belong outside.
- **`react-hooks/set-state-in-effect`.** If the value lives in an external
  system (`localStorage`), `useSyncExternalStore` is the answer — not a
  suppressed lint rule.
- **Translucent overlays.** A background read as `rgba(255,255,255,.06)` is
  not white; composite it over the ground before measuring.
