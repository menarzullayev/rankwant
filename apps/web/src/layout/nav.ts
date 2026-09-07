import {
  AlgorithmIcon,
  ArenaIcon,
  AttemptsIcon,
  BlogIcon,
  CalendarIcon,
  ClassroomIcon,
  ContestIcon,
  DuelIcon,
  FormulaIcon,
  HackathonIcon,
  InfoIcon,
  LeaderboardIcon,
  LearnIcon,
  ProblemsIcon,
  QuizIcon,
  RoadmapIcon,
  ShopIcon,
  TeamIcon,
  TournamentIcon,
} from "@/icons";

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
    | "/rating"
    | "/qvant"
    | "/about"
    | "/team";
  key: string;
  Icon: (props: { className?: string }) => React.JSX.Element;
};

export const NAV_GROUPS: { key: string; items: NavItem[] }[] = [
  {
    key: "navGroup.lab",
    items: [
      { href: "/problems", key: "nav.problems", Icon: ProblemsIcon },
      { href: "/attempts", key: "nav.attempts", Icon: AttemptsIcon },
      { href: "/quizzes", key: "nav.quizzes", Icon: QuizIcon },
    ],
  },
  {
    key: "navGroup.library",
    items: [
      { href: "/learn", key: "nav.articles", Icon: LearnIcon },
      { href: "/roadmaps", key: "nav.roadmap", Icon: RoadmapIcon },
      { href: "/algorithms", key: "nav.algorithms", Icon: AlgorithmIcon },
      { href: "/classroom", key: "nav.classroom", Icon: ClassroomIcon },
    ],
  },
  {
    key: "navGroup.compete",
    items: [
      { href: "/contests", key: "nav.contests", Icon: ContestIcon },
      { href: "/arena", key: "nav.arena", Icon: ArenaIcon },
      { href: "/duels", key: "nav.duels", Icon: DuelIcon },
      { href: "/tournaments", key: "nav.tournaments", Icon: TournamentIcon },
      { href: "/hackathons", key: "nav.hackathons", Icon: HackathonIcon },
      { href: "/calendar", key: "nav.calendar", Icon: CalendarIcon },
    ],
  },
  {
    key: "navGroup.campus",
    items: [
      { href: "/leaderboard", key: "nav.leaderboard", Icon: LeaderboardIcon },
      { href: "/blog", key: "nav.blog", Icon: BlogIcon },
    ],
  },
  {
    key: "navGroup.platform",
    items: [
      { href: "/rating", key: "nav.formulas", Icon: FormulaIcon },
      { href: "/qvant", key: "nav.shop", Icon: ShopIcon },
      { href: "/about", key: "nav.about", Icon: InfoIcon },
      { href: "/team", key: "nav.team", Icon: TeamIcon },
    ],
  },
];

/** Header sarlavhasi uchun tekis ro'yxat. */
export const NAV: NavItem[] = NAV_GROUPS.flatMap((group) => group.items);
