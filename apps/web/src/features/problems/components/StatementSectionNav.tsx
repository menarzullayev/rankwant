"use client";

import { revealElement } from "@/lib/scroll";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const JUMPS = [
  { id: "problem-statement", key: "problem.sectionNav.statement" as const },
  { id: "problem-input-format", key: "problem.sectionNav.input" as const },
  { id: "problem-output-format", key: "problem.sectionNav.output" as const },
  { id: "problem-samples", key: "problem.sectionNav.samples" as const },
  { id: "problem-notes", key: "problem.sectionNav.notes" as const },
  { id: "problem-editorial", key: "problem.sectionNav.editorial" as const },
] as const;

type SectionJump = (typeof JUMPS)[number];

/** Prototip M4 — tor ekranda bo‘limlar orasida sakrash. */
export function StatementSectionNav({
  showEditorial = false,
  showNotes = false,
}: {
  showEditorial?: boolean;
  showNotes?: boolean;
}) {
  const locale = useLocale();

  function scrollTo(id: string) {
    revealElement(id, { smooth: true, block: "start" });
  }

  let jumps: SectionJump[] = [...JUMPS];
  if (!showEditorial) jumps = jumps.filter((j) => j.id !== "problem-editorial");
  if (!showNotes) jumps = jumps.filter((j) => j.id !== "problem-notes");

  return (
    <p
      role="group"
      aria-label={t(locale, "problem.sectionNav.label")}
      className="sticky top-16 z-10 -mx-1 mb-3 flex gap-1.5 rw-scroll-x rw-snap-x border-b rw-divider bg-[var(--rw-ground)] py-2 xl:hidden"
    >
      {jumps.map(({ id, key }) => (
        <button
          key={id}
          type="button"
          onClick={() => scrollTo(id)}
          className="shrink-0 rw-radius-full border rw-divider rw-panel-bg px-2.5 py-1 text-theme-xs font-semibold rw-dim rw-hover-bg rw-focus-ring"
        >
          {t(locale, key)}
        </button>
      ))}
    </p>
  );
}
