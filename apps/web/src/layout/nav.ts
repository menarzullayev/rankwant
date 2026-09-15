
/**
 * Menyu — nomlash sessiyasida (2026-09-07) band-ma-band tanlangan.
 *
 * Guruhlar bitta institut binosi: Laboratoriya · Kutubxona · Auditoriya ·
 * Kampus. Bandlar esa deyarli hammasi ommaviy — GitHub yondashuvi
 * (Issues/Pull requests ommaviy, Actions/Copilot o'ziniki).
 * Qaror: docs/10-operations/menu.md
 */
type NavItem = {
  href:
    | "/problems"
    | "/attempts"
    | "/quizzes"
    | "/learn"
    | "/roadmaps"
    | "/algorithms"
    | "/classroom"
    | "/contests"
    | "/arena"
    | "/duels"
    | "/tournaments"
    | "/hackathons"
    | "/calendar"
    | "/leaderboard"
    | "/blog"
    | "/updates"
    | "/platform-roadmap"
    | "/rating"
    | "/qvant"
    | "/about"
    | "/team";
  key: string;
  iconKey: string;
};

export const NAV_GROUPS: { key: string; items: NavItem[] }[] = [
  {
    key: "navGroup.lab",
    items: [
      { href: "/problems", key: "nav.problems", iconKey: "nav.problems" },
      { href: "/attempts", key: "nav.attempts", iconKey: "ranking.chartBar" },
      { href: "/quizzes", key: "nav.quizzes", iconKey: "nav.quiz" },
    ],
  },
  {
    key: "navGroup.library",
    items: [
      { href: "/learn", key: "nav.articles", iconKey: "content.course" },
      { href: "/roadmaps", key: "nav.roadmap", iconKey: "content.roadmap" },
      { href: "/algorithms", key: "nav.algorithms", iconKey: "content.algorithm" },
      { href: "/classroom", key: "nav.classroom", iconKey: "content.course" },
    ],
  },
  {
    key: "navGroup.compete",
    items: [
      { href: "/contests", key: "nav.contests", iconKey: "ranking.trophy" },
      { href: "/arena", key: "nav.arena", iconKey: "contest.arena" },
      { href: "/duels", key: "nav.duels", iconKey: "contest.duel" },
      { href: "/tournaments", key: "nav.tournaments", iconKey: "ranking.trophy" },
      { href: "/hackathons", key: "nav.hackathons", iconKey: "contest.hackathon" },
      { href: "/calendar", key: "nav.calendar", iconKey: "contest.calendar" },
    ],
  },
  {
    key: "navGroup.campus",
    items: [
      { href: "/leaderboard", key: "nav.leaderboard", iconKey: "nav.leaderboard" },
      { href: "/blog", key: "nav.blog", iconKey: "content.article" },
      { href: "/updates", key: "nav.updates", iconKey: "notification.changelog" },
      // Yo'l xaritasi changelog yonida: ikkalasi bir savolga javob beradi —
      // "nima o'zgardi" (o'tmish) va "nima o'zgaradi" (kelajak).
      // ⚠️ `/roadmaps` (Traektoriya) BOSHQA narsa — ta'lim yo'li.
      { href: "/platform-roadmap", key: "nav.platformRoadmap", iconKey: "content.roadmap" },
    ],
  },
  {
    key: "navGroup.platform",
    items: [
      { href: "/rating", key: "nav.formulas", iconKey: "stats.chartBar" },
      { href: "/qvant", key: "nav.shop", iconKey: "shop.store" },
      { href: "/about", key: "nav.about", iconKey: "status.info" },
      { href: "/team", key: "nav.team", iconKey: "user.group" },
    ],
  },
];

/** Header sarlavhasi uchun tekis ro'yxat. */
export const NAV: NavItem[] = NAV_GROUPS.flatMap((group) => group.items);
