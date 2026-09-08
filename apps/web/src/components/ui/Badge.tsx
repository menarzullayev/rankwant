export type BadgeColor =
  "brand" | "success" | "error" | "warning" | "info" | "neutral";

const COLORS: Record<BadgeColor, string> = {
  brand: "rw-accent-soft rw-accent-ink ",
  success: "rw-ok-soft rw-ok-ink ",
  error: "rw-bad-soft rw-bad-ink ",
  warning: "rw-warn-soft rw-warn-ink ",
  info: "rw-chip rw-accent-ink",
  neutral: "rw-chip rw-dim-2 ",
};

export function Badge({
  color = "neutral",
  children,
}: {
  color?: BadgeColor;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center justify-center gap-1 rounded-full px-2.5 py-0.5
 text-theme-xs font-medium ${COLORS[color]}`}
    >
      {children}
    </span>
  );
}

/** Qiyinlik — 04-prd shkalasi. Rang `.level-*` bilan bir xil mantiqda. */
export function DifficultyBadge({ value }: { value: number }) {
  const level =
    value < 1200
      ? "beginner"
      : value < 1600
        ? "intermediate"
        : value < 2100
          ? "hard"
          : value < 2600
            ? "expert"
            : "master";
  return (
    <span
      className={`level-${level} inline-flex items-center rounded-full rw-chip px-2.5 py-0.5
 text-theme-xs font-semibold `}
    >
      {value}
    </span>
  );
}
