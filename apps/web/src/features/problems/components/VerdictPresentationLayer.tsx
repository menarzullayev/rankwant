"use client";

import { useEffect } from "react";

import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { isPendingVerdict } from "@/lib/theme/verdict";

import { AttemptVerdictPanel } from "./AttemptVerdictPanel";
import {
  useProblemSolve,
  useVerdictLayoutMode,
} from "./problem-solve-context";

/** Ustun / toast / modal rejimlarida statement ustunida yoki overlay’da. */
export function VerdictPresentationLayer({
  placement,
}: {
  placement: "column" | "toast" | "modal";
}) {
  const locale = useLocale();
  const [layout] = useVerdictLayoutMode();
  const ctx = useProblemSolve();

  useEffect(() => {
    if (!ctx || placement !== "modal") return;
    if (layout !== "modal") ctx.setModalOpen(false);
  }, [ctx, layout, placement]);

  useEffect(() => {
    if (!ctx || placement !== "modal" || layout !== "modal") return;
    if (ctx.submitBusy || ctx.attempt) ctx.setModalOpen(true);
  }, [ctx, layout, placement]);

  if (!ctx || layout !== placement) return null;

  const { attempt, submitBusy, modalOpen, setModalOpen } = ctx;
  const pending =
    submitBusy || (attempt !== null && isPendingVerdict(attempt.verdict));

  const panel = (
    <AttemptVerdictPanel
      attempt={attempt}
      pending={pending}
      locale={locale}
    />
  );

  if (placement === "column") {
    return (
      <Card bodyClassName="p-4" className="mb-4">
        {panel}
      </Card>
    );
  }

  if (placement === "toast" && (attempt || pending)) {
    return (
      <div className="pointer-events-none sticky bottom-4 z-20 flex justify-center px-2">
        <div className="pointer-events-auto max-w-md rw-radius-sm border rw-divider rw-panel-bg px-4 py-3 shadow-lg">
          <AttemptVerdictPanel
            attempt={attempt}
            pending={pending}
            locale={locale}
            compact
          />
        </div>
      </div>
    );
  }

  if (placement === "modal" && modalOpen) {
    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-5"
        role="dialog"
        aria-modal="true"
        aria-label={t(locale, "submit.tabVerdict")}
      >
        <div className="max-h-[min(520px,90vh)] w-full max-w-lg overflow-auto rw-radius-md border rw-divider rw-panel-bg p-4 shadow-xl">
          <div className="mb-3 flex justify-end">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="rw-radius-sm px-2 py-1 text-theme-sm rw-dim rw-hover-bg rw-focus-ring"
            >
              {t(locale, "problem.closeEditor")}
            </button>
          </div>
          {panel}
        </div>
      </div>
    );
  }

  return null;
}
