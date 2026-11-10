"use client";

import { Markdown } from "@/components/ui/Markdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

import type { MineProblem } from "../api/problems";

type Sections = Pick<
  MineProblem,
  "title" | "statement" | "input_format" | "output_format" | "note" | "time_limit_ms" | "memory_limit_kb"
>;

/** The draft as the problem page will draw it — same renderer, same
 *  sections. A draft does not open on the public page (404, even for its
 *  author, measured 2026-11-10), so this is the only place to see it. */
export function DraftPreview({ problem }: { problem: Sections }) {
  const locale = useLocale();
  return (
    <div className="space-y-4 rw-radius-sm border border-dashed rw-line rw-field-bg p-4">
      <div>
        <h2 className="text-theme-xl font-semibold rw-strong">{problem.title || "—"}</h2>
        <p className="mt-1 text-theme-xs rw-dim">
          {fill(t(locale, "studio.limits"), {
            time: problem.time_limit_ms / 1000,
            memory: Math.round(problem.memory_limit_kb / 1024),
          })}
        </p>
      </div>
      <Markdown>{problem.statement}</Markdown>
      {problem.input_format && (
        <section>
          <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
            {t(locale, "problem.inputFormat")}
          </h3>
          <Markdown>{problem.input_format}</Markdown>
        </section>
      )}
      {problem.output_format && (
        <section>
          <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
            {t(locale, "problem.outputFormat")}
          </h3>
          <Markdown>{problem.output_format}</Markdown>
        </section>
      )}
      {problem.note && (
        <section>
          <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
            {t(locale, "problem.comments")}
          </h3>
          <Markdown>{problem.note}</Markdown>
        </section>
      )}
    </div>
  );
}
