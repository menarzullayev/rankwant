import {
  BellIcon,
  BlogIcon,
  ContestIcon,
  FormulaIcon,
  LeaderboardIcon,
  LearnIcon,
  ProblemsIcon,
  QvantIcon,
} from "@/icons";

/**
 * Sidebar guruhlari.
 *
 * Guruhlash foydalanuvchi niyati bo'yicha: mashq qilish, musobaqalashish,
 * jamiyat. Route yo'llari TASK cheklovi bo'yicha o'zgarmaydi.
 */
type NavItem = {
  href: "/problems" | "/learn" | "/rating" | "/contests" | "/leaderboard" | "/blog"
    | "/qvant" | "/notifications";
  key: string;
  Icon: (props: { className?: string }) => React.JSX.Element;
};

export const NAV_GROUPS: { key: string; items: NavItem[] }[] = [
  {
    key: "navGroup.practice",
    items: [
      { href: "/problems", key: "nav.problems", Icon: ProblemsIcon },
      { href: "/learn", key: "nav.learn", Icon: LearnIcon },
      { href: "/rating", key: "nav.ratingInfo", Icon: FormulaIcon },
    ],
  },
  {
    key: "navGroup.compete",
    items: [
      { href: "/contests", key: "nav.contests", Icon: ContestIcon },
      { href: "/leaderboard", key: "nav.leaderboard", Icon: LeaderboardIcon },
    ],
  },
  {
    key: "navGroup.community",
    items: [
      { href: "/blog", key: "nav.blog", Icon: BlogIcon },
      { href: "/qvant", key: "nav.qvant", Icon: QvantIcon },
      { href: "/notifications", key: "nav.notifications", Icon: BellIcon },
    ],
  },
];

/** Header sarlavhasi uchun tekis ro'yxat. */
export const NAV: NavItem[] = NAV_GROUPS.flatMap((group) => group.items);
