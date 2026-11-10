/** Names that are never translated — audit Q-15 (owner decisions, 2026-11-10).
 *
 * Two lists, both read by `tools/check_i18n.py` (it parses this file, so keep
 * every entry a plain string literal on its own line):
 *
 * - `SAME_IN_EVERY_LOCALE` — dictionary keys whose value is byte-identical in
 *   all ten locales. Tier names are English everywhere, Uzbek included (the
 *   owner chose this over translating them); interface style names are design
 *   terms people search by; the four rating names and Qvant are product
 *   names.
 * - `DO_NOT_TRANSLATE` — terms that must appear verbatim in a locale's value
 *   whenever the Uzbek source value contains them (brands, platforms and
 *   competition formats). Inflection after the term is fine: "Qvant'ga",
 *   "Qvant-қа" both keep "Qvant".
 *
 * Measured before this list existed: Russian and Kazakh wrote "Квант" and
 * Chinese "量子币" for the Qvant module, and three style names were
 * translated while nine were not.
 */

export const SAME_IN_EVERY_LOCALE = [
  // «DQ» — the referee's abbreviation for disqualified (ADR-0055, part 4).
  "standings.dq",
  // Tier names (ADR-0027 ladder) — English in every locale.
  "title.quark",
  "title.atom",
  "title.molecule",
  "title.droplet",
  "title.meteorite",
  "title.comet",
  "title.moon",
  "title.planet",
  "title.star",
  "title.supernova",
  "title.pulsar",
  "title.magnetar",
  "title.black_hole",
  "title.galaxy",
  "title.supercluster",
  "title.cosmos",
  // Interface style names — the hint under each name is translated.
  "style.dashboard.label",
  "style.swiss.label",
  "style.flat.label",
  "style.material.label",
  "style.editorial.label",
  "style.brutal.label",
  "style.terminal.label",
  "style.glass.label",
  "style.neu.label",
  "style.clay.label",
  "style.aurora.label",
  "style.skeu.label",
  // Rating and currency names.
  "leaderboard.skills",
  "leaderboard.contest",
  "leaderboard.activity",
  "leaderboard.challenges",
  "nav.qvant",
  "update.module.qvant",
  "admin.label.text.qvant",
  // A course price in Qvant (ADR-0056).
  "course.price.qvant",
] as const;

export const DO_NOT_TRANSLATE = [
  "RankWant",
  "Qvant",
  "Codeforces",
  "ACM/ICPC",
  "IOI",
  "Elo",
  "Telegram",
  "GitHub",
  "Google",
] as const;
