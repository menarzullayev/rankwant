"use client";

import { useRef, useState } from "react";

import { CopyButton } from "@/components/kit/CopyControl";
import { useCustomizer } from "@/context/CustomizerContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { exportAppearance, importAppearance } from "@/lib/theme/share";
import { Icon } from "@/components/ui/Icon";

import { Section } from "./Group";

export function SavedTemplates() {
  const locale = useLocale();
  const {
    templates,
    saveTemplate,
    removeTemplate,
    applySaved,
    templateLimit,
    shareLink,
    appearance,
    a11y,
  } = useCustomizer();
  const { mode } = useTheme();
  const [name, setName] = useState("");
  const [importError, setImportError] = useState<string | null>(null);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const file = useRef<HTMLInputElement>(null);
  const full = templates.length >= templateLimit;

  function download() {
    const blob = new Blob([exportAppearance(appearance, a11y, mode)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "rankwant-appearance.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function upload(picked: File) {
    const result = importAppearance(await picked.text());
    if (!result.ok) {
      setImportError(result.error);
      return;
    }
    setImportError(null);
    applySaved(result);
  }

  return (
    <Section title={t(locale, "customizer.myTemplates")}>
      <CopyButton
        text={shareLink()}
        tone="text"
        label={t(locale, "customizer.copyLink")}
        copiedLabel={t(locale, "customizer.linkCopied")}
        className="mb-2 w-full justify-center"
      />

      <div className="mb-2 flex gap-2">
        <button
          type="button"
          onClick={download}
          className="min-w-0 flex-1 rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg"
        >
          {t(locale, "customizer.exportFile")}
        </button>
        <input
          ref={file}
          type="file"
          accept="application/json,.json"
          className="sr-only"
          tabIndex={-1}
          onChange={(event) => {
            const picked = event.target.files?.[0];
            if (picked) void upload(picked);
            event.target.value = "";
          }}
        />
        <button
          type="button"
          onClick={() => file.current?.click()}
          className="min-w-0 flex-1 rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg"
        >
          {t(locale, "customizer.importFile")}
        </button>
      </div>
      {importError && (
        <p role="alert" className="mb-2 rw-radius-sm rw-bad-soft px-2 py-1 text-theme-xs">
          {t(locale, `customizer.importError.${importError}`)}
        </p>
      )}

      {templates.length > 0 && (
        <ul className="mb-2 space-y-1">
          {templates.map((row) => (
            <li key={row.name} className="flex items-center gap-2">
              {pendingDelete === row.name ? (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      removeTemplate(row.name);
                      setPendingDelete(null);
                    }}
                    className="min-w-0 flex-1 rw-radius-sm border rw-line px-2.5 py-1.5 text-start text-theme-sm rw-bad-ink"
                  >
                    {t(locale, "customizer.deleteConfirm")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setPendingDelete(null)}
                    className="text-theme-sm rw-dim-2"
                  >
                    {t(locale, "customizer.cancel")}
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => applySaved(row)}
                    className="min-w-0 flex-1 truncate rw-radius-sm border rw-line px-2.5 py-1.5 text-start text-theme-sm rw-strong transition rw-hover-bg"
                  >
                    {row.name}
                  </button>
                  <button
                    type="button"
                    onClick={() => setPendingDelete(row.name)}
                    aria-label={`${t(locale, "customizer.delete")}: ${row.name}`}
                    className="flex size-8 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg"
                  >
                    <Icon name="nav.close" className="size-3.5" />
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}

      {full ? (
        <p className="text-theme-xs rw-faint">
          {t(locale, "customizer.templateLimit")} — {templateLimit}
        </p>
      ) : (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            saveTemplate(name);
            setName("");
          }}
          className="flex items-center gap-2"
        >
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={24}
            placeholder={t(locale, "customizer.templateName")}
            aria-label={t(locale, "customizer.templateName")}
            className="min-w-0 flex-1 rw-radius-sm border rw-line rw-field-bg px-2.5 py-1.5 text-theme-sm rw-strong rw-fm-inp"
          />
          <button
            type="submit"
            disabled={name.trim() === ""}
            className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg disabled:opacity-40"
          >
            {t(locale, "customizer.save")}
          </button>
        </form>
      )}
    </Section>
  );
}
