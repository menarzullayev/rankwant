"use client";

import { Markdown } from "@/components/ui/Markdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type Locale, type MessageKey } from "@/i18n/messages";

import type { TutorMessage } from "../api";

/** Where the server's guard cut a code block (ADR-0065 § 2.4). */
const REMOVED = "[[code-removed]]";

/** Why a reply did not come — the codes `tutor.answer` writes. */
const FAILURES: Record<string, MessageKey> = {
  busy: "tutor.fail.busy",
  unavailable: "tutor.fail.unavailable",
  ai_unavailable: "tutor.fail.unavailable",
  tutor_busy: "tutor.thinking",
  timeout: "tutor.fail.timeout",
  ai_off_in_contest: "tutor.contest",
};

export function failureText(locale: Locale, code: string): string {
  return t(locale, FAILURES[code] ?? "tutor.fail.other");
}

/** One tutor reply: pending, failed, or the answer as Markdown. */
export function TutorReply({ message }: { message: TutorMessage }) {
  const locale = useLocale();
  if (message.status === "pending") {
    return (
      <p
        className="text-theme-sm rw-dim motion-safe:animate-pulse"
        role="status"
      >
        {t(locale, "tutor.thinking")}
      </p>
    );
  }
  if (message.status === "failed") {
    return (
      <p className="text-theme-sm rw-bad-ink">
        {failureText(locale, message.error)}
      </p>
    );
  }
  const text = message.text
    .split(REMOVED)
    .join(`*${t(locale, "tutor.codeRemoved")}*`);
  return (
    <div className="text-theme-sm rw-dim-2">
      <Markdown lang={locale}>{text}</Markdown>
    </div>
  );
}
