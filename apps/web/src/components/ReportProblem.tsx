"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { FlagIcon } from "@/icons";
import { REPORT_REASONS, reportProblem } from "@/lib/api";

/** Masaladagi nuqson haqida xabar.
 *
 * Arxivning katta qismi tashqi manbadan ko'chirilgan: matnda formatlash
 * buzilgan, tarjima xato yoki test noto'g'ri bo'lishi mumkin. Bularni
 * o'zimiz topib chiqa olmaymiz, yechayotgan odam esa darhol ko'radi —
 * xabar yo'li bo'lmasa nuqson bilan birga yo'qolardi.
 *
 * Mehmonga ko'rsatilmaydi: xabar kimdan kelganini bilmasak, uni
 * tekshirib ham bo'lmaydi.
 */
export function ReportProblem({ slug }: { slug: string }) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<string>(REPORT_REASONS[0][0]);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!ready || !user) return null;

  async function send() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await reportProblem(slug, reason, comment.trim());
      setDone(true);
      setOpen(false);
    } catch {
      setError(t(locale, "report.failed"));
    } finally {
      setBusy(false);
    }
  }

  if (done)
    return (
      <p className="text-theme-sm rw-ok-ink">{t(locale, "report.done")}</p>
    );

  if (!open)
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 rw-radius-sm px-2 py-1 text-theme-sm rw-faint transition rw-hover-bg"
      >
        <FlagIcon className="size-3.5" />
        {t(locale, "report.open")}
      </button>
    );

  return (
    <div className="rw-panel space-y-3 p-4">
      <p className="text-theme-sm font-medium rw-strong">
        {t(locale, "report.title")}
      </p>

      <div className="flex flex-wrap gap-1.5">
        {REPORT_REASONS.map(([value, labelKey]) => (
          <button
            key={value}
            type="button"
            onClick={() => setReason(value)}
            aria-pressed={reason === value}
            className={`rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
              reason === value
                ? "rw-accent-soft rw-accent-ink"
                : "rw-dim rw-hover-bg"
            }`}
          >
            {t(locale, labelKey)}
          </button>
        ))}
      </div>

      <label className="block">
        <span className="mb-1 block text-theme-xs rw-faint">
          {t(locale, "report.commentLabel")}
        </span>
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={3}
          maxLength={2000}
          className="w-full rw-radius-sm border rw-line rw-field-bg p-2.5 text-theme-sm rw-strong outline-none rw-focus-line"
        />
      </label>

      <div className="flex flex-wrap items-center gap-2">
        <Button onClick={send} disabled={busy}>
          {busy ? t(locale, "report.sending") : t(locale, "report.send")}
        </Button>
        <Button variant="outline" onClick={() => setOpen(false)}>
          {t(locale, "report.cancel")}
        </Button>
        {error && <span className="text-theme-sm rw-bad-ink">{error}</span>}
      </div>
    </div>
  );
}
