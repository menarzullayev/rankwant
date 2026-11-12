"use client";

import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

import { useTutor } from "../useTutor";
import { TutorReply, failureText } from "./TutorReply";

/** Verdicts that are the student's to fix — the same set the API takes
 *  (`tutor/services.py` → `EXPLAINABLE`). A judge fault has nothing in
 *  the code to explain. */
export const EXPLAINABLE = new Set([
  "WA", "TLE", "MLE", "OLE", "RE", "RE_SIGNAL", "RE_EXIT", "CE", "PE", "HACKED", "PARTIAL",
  "COMPILE_TIMEOUT", "IDLENESS",
]); // prettier-ignore

/** «Nega xato?» under the student's own attempt (owner choice 2026-11-12).
 *  The tutor reads the code, the verdict and the failing test's number —
 *  never a hidden test. An explanation already given is shown again
 *  instead of asking (and counting) twice. */
export function WhyWrong({ slug, attempt }: { slug: string; attempt: number }) {
  const locale = useLocale();
  const { conversation, problem, sending, pending, ask } = useTutor(slug, true);

  const reply = conversation?.messages
    .filter(
      (m) =>
        m.role === "tutor" && m.kind === "why_wrong" && m.attempt === attempt,
    )
    .at(-1);
  const refused = (() => {
    if (problem?.code === "tutor_limit") {
      return fill(t(locale, "tutor.limit"), {
        limit: String(problem.details.limit ?? ""),
      });
    }
    if (
      problem?.code === "ai_off_in_contest" ||
      conversation?.reason === "ai_off_in_contest"
    ) {
      return t(locale, "tutor.contest");
    }
    if (conversation && !conversation.available)
      return failureText(locale, "unavailable");
    if (problem) return failureText(locale, problem.code);
    return null;
  })();
  const canAsk = Boolean(conversation?.available) && !pending && !sending;

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-theme-base font-semibold rw-strong">
          {t(locale, "tutor.whyWrongTitle")}
        </h2>
        {(!reply || reply.status === "failed") && (
          <button
            type="button"
            disabled={!canAsk}
            onClick={() => void ask({ kind: "why_wrong", attempt })}
            className="min-h-11 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-semibold rw-btn-label rw-focus-ring disabled:opacity-50"
          >
            {t(locale, "tutor.whyWrong")}
          </button>
        )}
      </div>
      <div className="mt-3 space-y-2">
        {reply ? (
          <TutorReply message={reply} />
        ) : (
          <p className="text-theme-sm rw-dim">
            {t(locale, "tutor.whyWrongHint")}
          </p>
        )}
        {refused && (
          <p role="status" className="text-theme-sm rw-dim-2">
            {refused}
          </p>
        )}
      </div>
    </Card>
  );
}
