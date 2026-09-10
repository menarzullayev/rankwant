/**
 * Inline ikonkalar.
 *
 * TailAdmin `@svgr/webpack` bilan 58 ta SVG faylni import qiladi. Bu
 * yerda ishlatiladiganlari to'g'ridan-to'g'ri komponent — qo'shimcha
 * dependency ham, webpack/turbopack sozlamasi ham kerak emas
 * (TASK cheklovi #8).
 */

type IconProps = { className?: string };

const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function Icon({
  className,
  children,
}: IconProps & { children: React.ReactNode }) {
  return (
    <svg {...base} className={className ?? "size-5"} aria-hidden="true">
      {children}
    </svg>
  );
}

export const ProblemsIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H18a2 2 0 0 1 2 2v12.5" />
    <path d="M4 5.5V18a2 2 0 0 0 2 2h14" />
    <path d="M8 9h8M8 13h5" />
  </Icon>
);

export const LearnIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 4 2 9l10 5 10-5-10-5Z" />
    <path d="M5 11v5c0 1.1 3.1 3 7 3s7-1.9 7-3v-5" />
  </Icon>
);

export const ContestIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M8 4h8v5a4 4 0 0 1-8 0V4Z" />
    <path d="M8 5H5v2a3 3 0 0 0 3 3M16 5h3v2a3 3 0 0 1-3 3" />
    <path d="M12 13v4M9 20h6" />
  </Icon>
);

export const LeaderboardIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 20V11M12 20V5M19 20v-6" />
  </Icon>
);

export const QvantIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="8" />
    <path d="M12 8v8M9.5 10.5h5M9.5 13.5h5" />
  </Icon>
);

export const BlogIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 4h9l5 5v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" />
    <path d="M14 4v5h5M8 13h8M8 17h5" />
  </Icon>
);

export const BellIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6Z" />
    <path d="M10.3 20a2 2 0 0 0 3.4 0" />
  </Icon>
);

export const FormulaIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M6 20c2 0 2.5-1.5 3-4l2-9c.5-2.5 1-4 3-4" />
    <path d="M6 10h8M14 14l6 6M20 14l-6 6" />
  </Icon>
);

export const MenuIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 6h16M4 12h16M4 18h16" />
  </Icon>
);

export const CloseIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m6 6 12 12M18 6 6 18" />
  </Icon>
);

export const SunIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </Icon>
);

export const PaletteIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 3a9 9 0 1 0 0 18c.9 0 1.6-.7 1.6-1.6 0-.4-.2-.8-.5-1.1-.3-.3-.4-.6-.4-1 0-.9.7-1.6 1.6-1.6H16a5 5 0 0 0 5-5c0-4.1-4-7.7-9-7.7Z" />
    <circle cx="7.5" cy="11.5" r="1" />
    <circle cx="10.5" cy="7.5" r="1" />
    <circle cx="15.5" cy="8.5" r="1" />
  </Icon>
);

export const MoonIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z" />
  </Icon>
);

export const UserIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="8" r="4" />
    <path d="M5 20a7 7 0 0 1 14 0" />
  </Icon>
);

export const ChevronLeftIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m14 6-6 6 6 6" />
  </Icon>
);

export const CheckIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m5 13 4 4L19 7" />
  </Icon>
);

export const SearchIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.5-3.5" />
  </Icon>
);

export const CalendarIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path d="M3 10h18M8 3v4M16 3v4" />
  </Icon>
);

export const AttemptsIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 12h4l2-6 4 12 2-6h4" />
  </Icon>
);

export const QuizIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="4" y="3" width="16" height="18" rx="2" />
    <path d="m8 12 2 2 4-4M8 17h8" />
  </Icon>
);

export const RoadmapIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 19c4-1 4-6 8-7s4-6 8-7" />
    <circle cx="4" cy="19" r="1.5" />
    <circle cx="12" cy="12" r="1.5" />
    <circle cx="20" cy="5" r="1.5" />
  </Icon>
);

export const AlgorithmIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m8 7-4 5 4 5M16 7l4 5-4 5M14 4l-4 16" />
  </Icon>
);

export const ClassroomIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3" y="4" width="18" height="12" rx="2" />
    <path d="M8 20h8M12 16v4" />
  </Icon>
);

export const ArenaIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" />
  </Icon>
);

export const DuelIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m4 20 6-6M20 4l-6 6M4 20l-.5-4L14 5.5l1 1L20 4l.5 4L9.5 18.5l-1-1L4 20Z" />
  </Icon>
);

export const TournamentIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 5h5v4H3zM3 15h5v4H3zM16 10h5v4h-5zM8 7h4v10H8M12 12h4" />
  </Icon>
);

export const HackathonIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 19c0-3 1-5 3-7 2-3 6-5 11-7-2 5-4 9-7 11-2 2-4 3-7 3Z" />
    <path d="M9 15 5 19M14 6l4 4" />
  </Icon>
);

export const InfoIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5M12 8h.01" />
  </Icon>
);

export const TeamIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="9" cy="8" r="3.5" />
    <circle cx="17" cy="9" r="2.5" />
    <path d="M3 20a6 6 0 0 1 12 0M15 20a5 5 0 0 1 6-4.5" />
  </Icon>
);

export const ShopIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M4 8h16l-1.5 11a2 2 0 0 1-2 1.8h-9a2 2 0 0 1-2-1.8L4 8Z" />
    <path d="M9 8V6a3 3 0 0 1 6 0v2" />
  </Icon>
);

export const StarIcon = ({
  filled,
  ...p
}: IconProps & { filled?: boolean }) => (
  <Icon {...p}>
    <path
      fill={filled ? "currentColor" : "none"}
      d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.5 9.7l5.9-.9Z"
    />
  </Icon>
);

export const FlameIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 3c1 4 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3 1-6 1-9Z" />
  </Icon>
);

export const CopyIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="9" y="9" width="11" height="11" rx="2" />
    <path d="M15 5.5A1.5 1.5 0 0 0 13.5 4H6a2 2 0 0 0-2 2v7.5A1.5 1.5 0 0 0 5.5 15" />
  </Icon>
);

export const FlagIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 21V4M5 4h11l-1.5 3.5L16 11H5" />
  </Icon>
);

export const SettingsIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z" />
  </Icon>
);
