export type BadgeColor = "brand" | "success" | "error" | "warning" | "info" | "neutral";

const COLORS: Record<BadgeColor, string> = {
  brand: "bg-brand-50 text-brand-600 dark:bg-brand-500/12 dark:text-brand-400",
  success: "bg-success-50 text-success-600 dark:bg-success-500/12 dark:text-success-400",
  error: "bg-error-50 text-error-600 dark:bg-error-500/12 dark:text-error-400",
  warning: "bg-warning-50 text-warning-600 dark:bg-warning-500/12 dark:text-warning-400",
  info: "bg-blue-light-50 text-blue-light-500 dark:bg-blue-light-500/12 dark:text-blue-light-400",
  neutral: "bg-gray-100 text-gray-600 dark:bg-white/5 dark:text-gray-300",
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
      className={`level-${level} inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5
        text-theme-xs font-semibold dark:bg-white/5`}
    >
      {value}
    </span>
  );
}
