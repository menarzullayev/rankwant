import Link from "next/link";

import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

const STEPS: { title: MessageKey; body: MessageKey }[] = [
  { title: "about.journey.solveTitle", body: "about.journey.solveBody" },
  { title: "about.journey.measureTitle", body: "about.journey.measureBody" },
  { title: "about.journey.competeTitle", body: "about.journey.competeBody" },
  { title: "about.journey.qvantTitle", body: "about.journey.qvantBody" },
  { title: "about.journey.transparencyTitle", body: "about.journey.transparencyBody" },
];

/** The platform in five steps, before the reference below it.
 *
 *  Five full-width cards were a screen and a half on a phone for five
 *  sentences. They are one row from `xl` and a compact list under it; the
 *  section has a heading of its own, which the cards never had. */
export async function AboutJourney() {
  const locale = await getLocale();
  return (
    <section id="journey" aria-labelledby="about-journey-title" className="scroll-mt-16 space-y-3 xl:scroll-mt-2">
      <h2 id="about-journey-title" className="text-theme-xl font-semibold rw-strong">
        {t(locale, "about.journey.title")}
      </h2>
      <ol className="grid gap-2 xl:grid-cols-5">
        {STEPS.map(({ title, body }, index) => (
          <li key={title} className="flex gap-3 rw-panel p-3 xl:flex-col xl:gap-2">
            <span
              aria-hidden="true"
              className="grid size-7 shrink-0 place-items-center rounded-full rw-accent-soft text-theme-sm font-bold rw-accent-ink"
            >
              {index + 1}
            </span>
            <div className="min-w-0">
              <h3 className="text-theme-sm font-semibold rw-strong">{t(locale, title)}</h3>
              <p className="mt-0.5 text-theme-xs rw-dim">{t(locale, body)}</p>
            </div>
          </li>
        ))}
      </ol>
      <p className="flex flex-wrap gap-2 pt-1">
        <Link
          href="/problems"
          className="inline-flex h-11 items-center rw-radius-sm rw-accent-bg px-5 text-theme-sm font-semibold rw-focus-ring"
        >
          {t(locale, "about.cta.solve")}
        </Link>
        <a
          href="#verdicts"
          className="inline-flex h-11 items-center rw-radius-sm border rw-divider px-5 text-theme-sm font-medium rw-dim-2 rw-hover-bg rw-focus-ring"
        >
          {t(locale, "about.toc.verdicts")}
        </a>
      </p>
    </section>
  );
}
