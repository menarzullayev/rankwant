// Semantic keys and the icon names to look for in each pack.
//
// Why a candidate LIST per key rather than one name: icon libraries name
// the same concept differently (`search` in Lucide, `magnifying-glass` in
// Phosphor, `search` in Tabler). Listing the plausible names in order lets
// the fetcher resolve automatically and report only the genuine misses,
// which is far less work than 44 keys × 9 packs typed by hand.
//
// D18 naming: `domain.object.state`. The first segment decides the zone,
// and the zone decides whether the pack applies at all (D20 = ①):
// nav / action / status change with the pack, verdict / brand never do.

export const KEYS = {
  // ── nav ────────────────────────────────────────────────────────────
  "nav.problems": ["book-open", "book", "notebook", "file-text", "books"],
  "nav.learn": ["graduation-cap", "academic-cap", "book", "book-open", "school", "student"],
  "nav.contest": ["trophy", "award", "medal", "ranking"],
  "nav.leaderboard": ["chart-no-axes-column", "bar-chart", "chart-bar", "ranking", "podium"],
  "nav.qvant": ["coins", "coin", "wallet", "currency-dollar", "money"],
  "nav.blog": ["newspaper", "news", "article", "file-text"],
  "nav.formula": ["function", "sigma", "square-function", "square-root", "calculator", "math"],
  "nav.menu": ["menu", "bars-3", "bars", "list", "hamburger", "align-justify"],
  "nav.attempts": ["history", "clock-rotate-left", "clock-history", "clock", "rotate-left", "undo"],
  "nav.quiz": ["circle-help", "question-mark-circle", "question-circle", "help-circle", "question", "quiz"],
  "nav.roadmap": ["map", "route", "signpost", "map-pin"],
  "nav.algorithm": ["route", "git-branch", "hdd-network", "flow-chart", "network", "share", "share-2", "waypoints", "sitemap"],
  "nav.classroom": ["presentation", "presentation-chart-bar", "easel", "chalkboard", "dashboard", "academic-cap", "school", "blackboard"],
  "nav.arena": ["swords", "sword", "crosshair", "crosshair-2", "target", "bolt", "thunderbolt", "zap"],
  "nav.duel": ["users", "group", "group-2", "user-group", "people", "swords"],
  "nav.tournament": ["trophy", "medal", "crown", "award"],
  "nav.hackathon": ["code", "code-bracket", "command", "terminal", "rocket", "rocket-launch", "lightbulb"],
  "nav.team": ["users", "group", "team", "user-group", "people", "users-round"],
  "nav.shop": ["shopping-bag", "shopping-cart", "store", "bag"],
  "nav.updates": ["bell", "megaphone", "rss", "newspaper"],
  "nav.user": ["user", "person", "circle-user", "user-circle"],
  "nav.notifications": ["bell", "bell-ring", "bell-dot"],
  "nav.calendar": ["calendar", "calendar-days", "calendar-dots"],
  "nav.language": ["globe", "language", "translate", "languages", "world"],
  "nav.settings": ["settings", "cog", "gear", "sliders", "sliders-horizontal"],
  "nav.info": ["info", "information-circle", "information", "circle-info", "info-circle"],

  // ── action ─────────────────────────────────────────────────────────
  "action.search": ["search", "magnifying-glass"],
  "action.close": ["x", "x-mark", "x-lg", "close", "xmark", "cross", "multiply"],
  "action.confirm": ["check", "checkmark", "tick", "check-lg"],
  "action.copy": ["copy", "clipboard", "duplicate", "files"],
  "action.report": ["flag", "triangle-alert", "exclamation-triangle"],
  "action.favourite": ["star", "star-filled", "bookmark"],
  "action.up": ["arrow-up", "arrow-up-right", "chevron-up", "caret-up"],
  "action.expand": ["chevron-down", "arrow-down-s", "caret-down", "chevron-right", "angle-down"],
  "action.back": ["chevron-left", "caret-left", "arrow-left", "angle-left"],
  "action.logout": ["log-out", "arrow-right-on-rectangle", "box-arrow-right", "logout-box", "logout", "sign-out", "exit"],
  "action.theme": ["palette", "paint-brush", "paintbrush", "brush", "swatch", "droplet"],
  "action.light": ["sun", "sun-bright", "sun-medium", "brightness"],
  "action.dark": ["moon", "moon-stars", "moon-fill"],
  "action.loading": ["loader", "arrow-path", "arrow-clockwise", "loader-circle", "spinner", "circle-notch", "refresh", "spinner-gap"],

  // ── status ─────────────────────────────────────────────────────────
  "status.warning": ["triangle-alert", "error-warning", "alert-triangle", "alert", "warning", "exclamation-triangle"],
  "status.ok": ["circle-check", "checkbox-circle", "check-circle", "check-circle-2", "circle-check-big"],
  "status.bad": ["circle-x", "close-circle", "x-circle", "circle-xmark", "forbid", "alert-octagon"],
  "status.info": ["circle-info", "information", "info-circle", "information-circle", "info"],
};

/** Packs that need a generated subset. Verdict and brand are fixed
 *  (D20 ①), so they are not listed here — they keep the Phosphor set. */
export const PACK_SOURCES = {
  lucide: {
    list: "https://data.jsdelivr.com/v1/packages/npm/lucide-static@0.544.0?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/lucide-static@0.544.0/icons/${n}.svg`,
  },
  tabler: {
    list: "https://data.jsdelivr.com/v1/packages/npm/@tabler/icons@3.34.1?structure=flat",
    prefix: "/icons/outline/",
    url: (n) => `https://cdn.jsdelivr.net/npm/@tabler/icons@3.34.1/icons/outline/${n}.svg`,
  },
  heroicons: {
    list: "https://data.jsdelivr.com/v1/packages/npm/heroicons@2.2.0?structure=flat",
    prefix: "/24/outline/",
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/outline/${n}.svg`,
  },
  heroiconsSolid: {
    list: "https://data.jsdelivr.com/v1/packages/npm/heroicons@2.2.0?structure=flat",
    prefix: "/24/solid/",
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/solid/${n}.svg`,
  },
  bootstrap: {
    list: "https://data.jsdelivr.com/v1/packages/npm/bootstrap-icons@1.13.1?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/icons/${n}.svg`,
  },
  remix: {
    list: "https://data.jsdelivr.com/v1/packages/npm/remixicon@4.6.0?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/remixicon@4.6.0/icons/${n}.svg`,
  },
};

/** ⚠️ Phosphorning uch uslubi — haqiqiy uch xil fayl to'plami
 *  (`assets/regular`, `assets/fill`, `assets/duotone`). Ilgari uchtasi
 *  bitta xaritaga ulangan edi va tanlov **hech narsani o'zgartirmasdi** —
 *  o'lchandi: brauzerda «Phosphor Solid» ni bosganda ikonkalar bir xil
 *  qoldi. */
const PHOSPHOR_LIST =
  "https://data.jsdelivr.com/v1/packages/npm/@phosphor-icons/core@2.1.1?structure=flat";
const phosphorUrl = (style, n) =>
  `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/${style}/${n}${style === "regular" ? "" : "-" + style}.svg`;

PACK_SOURCES.phosphor = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/regular/",
  url: (n) => phosphorUrl("regular", n),
};
PACK_SOURCES.phosphorSolid = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/fill/",
  url: (n) => phosphorUrl("fill", n),
};
PACK_SOURCES.phosphorDuotone = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/duotone/",
  url: (n) => phosphorUrl("duotone", n),
};

/** Simple Icons is a brand set only — it has no interface icons. It is
 *  kept in the list for brand marks, which D20 ① keeps fixed anyway. */
export const SIMPLE_ICONS_ONLY = true;
