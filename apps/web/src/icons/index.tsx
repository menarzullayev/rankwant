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

function Icon({ className, children }: IconProps & { children: React.ReactNode }) {
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
