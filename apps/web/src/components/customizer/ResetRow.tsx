"use client";

import { useState } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

export function ResetRow() {
  const locale = useLocale();
  // D67: Reset restores appearance/a11y prefs only — not rw:cz-tab / rw:cz-group.
  const { undo, canUndo, resetAll } = useCustomizer();
  const [confirming, setConfirming] = useState(false);
  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        disabled={!canUndo}
        onClick={undo}
        className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg disabled:opacity-40"
      >
        {t(locale, "customizer.undo")}
      </button>
      {confirming ? (
        <>
          <button
            type="button"
            onClick={() => {
              resetAll();
              setConfirming(false);
            }}
            className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-bad-ink"
          >
            {t(locale, "customizer.resetConfirm")}
          </button>
          <button
            type="button"
            onClick={() => setConfirming(false)}
            className="text-theme-sm rw-dim-2"
          >
            {t(locale, "customizer.cancel")}
          </button>
        </>
      ) : (
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg"
        >
          {t(locale, "customizer.reset")}
        </button>
      )}
    </div>
  );
}
