"use client";

import { useId, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import {
  reportTutorReply,
  type TutorMessage,
  type TutorReportReason,
} from "../api";

const REASONS: { value: TutorReportReason; key: string }[] = [
  { value: "wrong", key: "tutor.report.wrong" },
  { value: "solution", key: "tutor.report.solution" },
  { value: "harmful", key: "tutor.report.harmful" },
  { value: "other", key: "tutor.report.other" },
];

/** «Shikoyat» under a tutor reply (decision ⑦). Staff see a conversation
 *  only through such a report, and only the question and this reply. */
export function ReportReply({
  slug,
  message,
  onDone,
}: {
  slug: string;
  message: TutorMessage;
  onDone: () => void;
}) {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<TutorReportReason>("wrong");
  const [note, setNote] = useState("");
  const [sending, setSending] = useState(false);
  const [failed, setFailed] = useState(false);
  const noteId = useId();

  if (message.reported) {
    return (
      <p className="mt-1 text-theme-xs rw-faint">
        {t(locale, "tutor.report.sent")}
      </p>
    );
  }
  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="mt-1 min-h-11 rw-radius-sm px-1 text-theme-xs rw-faint rw-hover-bg rw-focus-ring"
      >
        {t(locale, "tutor.reportButton")}
      </button>
    );
  }

  async function send(event: React.FormEvent) {
    event.preventDefault();
    setSending(true);
    setFailed(false);
    try {
      await reportTutorReply(slug, { message: message.id, reason, note });
      onDone();
    } catch {
      setFailed(true);
    } finally {
      setSending(false);
    }
  }

  return (
    <form
      onSubmit={send}
      className="mt-2 space-y-2 rw-radius-sm rw-field-bg p-3"
    >
      <fieldset className="space-y-1">
        <legend className="text-theme-xs font-semibold rw-strong">
          {t(locale, "tutor.report.why")}
        </legend>
        {REASONS.map((r) => (
          <label
            key={r.value}
            className="flex min-h-11 items-center gap-2 text-theme-sm rw-dim-2"
          >
            <input
              type="radio"
              name={`reason-${message.id}`}
              value={r.value}
              checked={reason === r.value}
              onChange={() => setReason(r.value)}
            />
            {t(locale, r.key)}
          </label>
        ))}
      </fieldset>
      <label htmlFor={noteId} className="block text-theme-xs rw-faint">
        {t(locale, "tutor.report.note")}
      </label>
      <textarea
        id={noteId}
        rows={2}
        maxLength={500}
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-full resize-none rw-radius-sm border rw-line rw-surface px-3 py-2 text-theme-sm rw-strong rw-focus-ring"
      />
      <p className="text-theme-xs rw-faint">
        {t(locale, "tutor.report.privacy")}
      </p>
      {failed && (
        <p role="status" className="text-theme-xs rw-bad-ink">
          {t(locale, "tutor.fail.other")}
        </p>
      )}
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="min-h-11 rw-radius-sm px-3 text-theme-sm rw-dim rw-hover-bg rw-focus-ring"
        >
          {t(locale, "tutor.report.cancel")}
        </button>
        <button
          type="submit"
          disabled={sending}
          className="min-h-11 rw-radius-sm rw-accent-bg px-3 text-theme-sm font-semibold rw-btn-label rw-focus-ring disabled:opacity-50"
        >
          {t(locale, "tutor.report.send")}
        </button>
      </div>
    </form>
  );
}
