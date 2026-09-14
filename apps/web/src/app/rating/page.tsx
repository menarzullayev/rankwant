import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "nav.ratingInfo"),
    description: t(locale, "rating.description"),
  };
}

/**
 * Launch gate sharti: 4 reyting formulasi UI da OCHIQ bo'lishi kerak
 * (09-development-plan). Vision principle #2 — «yashirin algoritm emas».
 *
 * Formulalar 04-prd 🔒 dan; kod `apps/api/ratings/formulas.py` da.
 *
 * The formulas themselves are mathematics: `Skills = Σ pᵢ × 0.95^(i−1)`
 * reads the same in all ten languages, so they are module constants rather
 * than dictionary entries. Only the prose around them is translated.
 */
const FORMULA_SKILLS = "Skills = Σ pᵢ × 0.95^(i−1)  (p₁ ≥ p₂ ≥ … , pᵢ = qiyinlik)";

const FORMULA_CONTESTS = [
  "P(i,j) = 1 / (1 + 10^((Rⱼ − Rᵢ) / 400))",
  "seedᵢ = 1 + Σ P(j, i)      kutilgan o'rin",
  "mᵢ = √(seedᵢ × rankᵢ)      kutilgan va haqiqiy o'rin o'rtachasi",
  "dᵢ = (R*ᵢ − Rᵢ) / 2         R*ᵢ — mᵢ ga mos reyting",
  "soʻng: barcha dᵢ dan Σd/n ayiriladi (musobaqa reytingni shishirmaydi)",
].join("\n");

const FORMULA_ACTIVITY =
  "Activity = 10 × faol_kun + 5 × bajarilgan_quest + min(2 × streak_kun, 60)";

const FORMULA_CHALLENGES = [
  "E = 1 / (1 + 10^((R_raqib − R) / 400))",
  "R' = R + K × (S − E)       S ∈ {1 = g'alaba, 0.5 = durang, 0}",
  "K = 32 (birinchi 10 duel), keyin 16",
].join("\n");

function Section({
  title,
  phase,
  active,
  children,
}: {
  title: string;
  phase: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className="rw-radius border rw-line rw-surface rw-shadow">
      <div className="flex items-center justify-between gap-3 border-b rw-divider px-5 py-4">
        <h2 className="text-theme-xl font-semibold rw-strong">{title}</h2>
        <Badge color={active ? "brand" : "neutral"}>{phase}</Badge>
      </div>
      <div className="space-y-2 px-5 py-4 text-theme-sm rw-dim">{children}</div>
    </section>
  );
}

function Formula({ children }: { children: React.ReactNode }) {
  return (
    <pre
      className="overflow-x-auto rounded p-3 text-xs"
      style={{ background: "var(--bg)", color: "var(--text)" }}
    >
      <code>{children}</code>
    </pre>
  );
}

export default async function RatingPage() {
  const locale = await getLocale();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.ratingInfo")}
        </h1>
        <p className="mt-2 max-w-3xl text-theme-sm rw-dim">
          {t(locale, "rating.intro")}
        </p>
      </header>

      <Section title="Skills" phase={t(locale, "rating.phase.active")} active>
        <p>{t(locale, "rating.skills.summary")}</p>
        <Formula>{FORMULA_SKILLS}</Formula>
        <ul className="list-disc space-y-1 pl-5">
          <li>{t(locale, "rating.skills.noDecrease")}</li>
          <li>{t(locale, "rating.skills.cap")}</li>
          <li>{t(locale, "rating.skills.saturation")}</li>
          <li>{t(locale, "rating.skills.revaluation")}</li>
        </ul>
        <p className="text-xs">{t(locale, "rating.skills.example")}</p>
      </Section>

      <Section title="Contests" phase={t(locale, "rating.phase.active")} active>
        <p>{t(locale, "rating.contests.summary")}</p>
        <Formula>{FORMULA_CONTESTS}</Formula>
        <ul className="list-disc space-y-1 pl-5">
          <li>{t(locale, "rating.contests.start")}</li>
          <li>{t(locale, "rating.contests.provisional")}</li>
          <li>{t(locale, "rating.contests.floor")}</li>
        </ul>
      </Section>

      <Section title="Activity" phase={t(locale, "rating.phase.active")} active>
        <p>{t(locale, "rating.activity.window")}</p>
        <Formula>{FORMULA_ACTIVITY}</Formula>
        <p>{t(locale, "rating.activity.qvant")}</p>
      </Section>

      <Section
        title="Challenges"
        phase={t(locale, "rating.phase.phase3")}
        active={false}
      >
        <p>{t(locale, "rating.challenges.summary")}</p>
        <Formula>{FORMULA_CHALLENGES}</Formula>
      </Section>

      <p className="text-xs" style={{ color: "var(--muted)" }}>
        {t(locale, "rating.adr")}
      </p>
    </div>
  );
}
