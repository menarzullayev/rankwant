import { fill, t, type Locale } from "@/i18n/messages";
import type { Achievement, AchievementTier } from "@/lib/api";

const ACHIEVEMENT_TEXT: Record<Achievement["group"], string> = {
  solve: "profile.achSolve",
  streak: "profile.achStreak",
  contest: "profile.achContest",
  profile: "profile.achProfile",
};

export const achievementLabel = (row: Pick<Achievement, "group" | "target">, locale: Locale) =>
  fill(t(locale, ACHIEVEMENT_TEXT[row.group]), { n: row.target });

/** Medal — bezak; daraja nomi yonida matn bo'lib ham yoziladi. */
export function MedalDot({ tier, muted = false }: { tier: AchievementTier; muted?: boolean }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-block size-4 shrink-0 rounded-full ${muted ? "rw-medal-none" : `rw-medal-${tier}`}`}
    />
  );
}

/** Profil kartasidagi tanlangan yutuq. */
export function Medal({
  tier,
  label,
  locale,
}: {
  tier: AchievementTier;
  label: string;
  locale: Locale;
}) {
  return (
    <span
      title={t(locale, `tier.${tier}`)}
      className="inline-flex items-center gap-1.5 rounded-full border rw-line px-2.5 py-1 text-theme-xs font-medium rw-strong"
    >
      <MedalDot tier={tier} />
      <span className="sr-only">{t(locale, `tier.${tier}`)}: </span>
      {label}
    </span>
  );
}
