"use client";

import { useMemo, useState } from "react";

import { CodeCopy } from "@/components/kit/CopyControl";
import { Dropdown } from "@/components/ui/Dropdown";
import {
  sampleEditorLanguage,
  sampleFileForLanguage,
  sampleForLanguage,
} from "@/content/about/language-samples";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { PREFERRED_LANGUAGES, defaultLanguage } from "@/lib/editor-language";
import { highlight, type TokenKind } from "@/lib/highlight";

export type GuideLanguage = { code: string; name: string; version: string };

/** Token colours come from the theme's own inks (as on the attempt page),
 *  so the sample reads in every style and in both modes. */
const TOKEN_CLASS: Record<TokenKind, string> = {
  plain: "",
  comment: "rw-faint italic",
  string: "rw-ok-ink",
  number: "rw-warn-ink",
  keyword: "rw-accent-ink",
};

function languageLabel(language: GuideLanguage): string {
  const version = language.version.trim();
  return version ? `${language.name} ${version}` : language.name;
}

const pick = (active: boolean) =>
  `inline-flex h-11 items-center rounded-full border px-4 text-theme-sm font-medium rw-focus-ring ${
    active ? "border-transparent rw-accent-soft rw-accent-ink" : "rw-divider rw-dim-2 rw-hover-bg"
  }`;

/** The A+B sample in a language of the reader's choice.
 *
 *  The languages used to be thirty-five tabs: the first one alphabetically
 *  (Ada) was selected, and the other thirty-four could not be reached from
 *  a keyboard — the tab role with a negative tab index and no arrow-key
 *  handling. Now the three most used are buttons, the rest a searchable
 *  list, and the page opens on the language the editor opens on. */
export function LanguageGuide({ languages }: { languages: GuideLanguage[] }) {
  const locale = useLocale();
  const sorted = useMemo(
    () => [...languages].sort((a, b) => languageLabel(a).localeCompare(languageLabel(b), locale)),
    [languages, locale],
  );
  const popular = useMemo(
    () =>
      PREFERRED_LANGUAGES.map((code) => sorted.find((language) => language.code === code)).filter(
        (language): language is GuideLanguage => Boolean(language),
      ),
    [sorted],
  );
  const others = useMemo(
    () => sorted.filter((language) => !popular.includes(language)),
    [sorted, popular],
  );
  const [active, setActive] = useState(() => defaultLanguage(sorted));
  const [ioKind, setIoKind] = useState<"stdio" | "file">("stdio");

  if (sorted.length === 0) {
    return <p className="text-theme-sm rw-dim">{t(locale, "about.compilers.empty")}</p>;
  }

  const current = sorted.find((language) => language.code === active) ?? sorted[0];
  const sample =
    ioKind === "file" ? sampleFileForLanguage(current.code) : sampleForLanguage(current.code);
  const tokens = sample ? highlight(sample, sampleEditorLanguage(current.code)) : [];
  const isOther = others.some((language) => language.code === current.code);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-end gap-2">
        <div role="group" aria-label={t(locale, "about.compilers.tabsLabel")} className="flex flex-wrap gap-2">
          {popular.map((language) => (
            <button
              key={language.code}
              type="button"
              aria-pressed={language.code === current.code}
              onClick={() => setActive(language.code)}
              className={pick(language.code === current.code)}
            >
              {language.name}
            </button>
          ))}
        </div>
        {others.length > 0 ? (
          <div className="min-w-0 flex-1 basis-48 sm:max-w-xs">
            <Dropdown
              label={fill(t(locale, "about.lang.other"), { count: others.length })}
              options={others.map((language) => ({
                value: language.code,
                label: languageLabel(language),
              }))}
              value={isOther ? current.code : ""}
              onChange={(value) => {
                if (value) setActive(value);
              }}
            />
          </div>
        ) : null}
        <div
          role="group"
          aria-label={t(locale, "about.io.tabsLabel")}
          className="inline-flex rounded-full border rw-divider p-0.5"
        >
          {(["stdio", "file"] as const).map((kind) => (
            <button
              key={kind}
              type="button"
              aria-pressed={ioKind === kind}
              onClick={() => setIoKind(kind)}
              className={`inline-flex h-10 items-center rounded-full px-3 text-theme-xs font-medium rw-focus-ring ${
                ioKind === kind ? "rw-accent-soft rw-accent-ink" : "rw-dim rw-hover-bg"
              }`}
            >
              {t(locale, kind === "stdio" ? "about.io.kind.stdio" : "about.io.kind.file")}
            </button>
          ))}
        </div>
      </div>

      <h3 className="text-theme-sm font-semibold rw-strong">
        {languageLabel(current)} — {t(locale, ioKind === "file" ? "about.io.file.title" : "about.io.title")}
      </h3>
      <p className="text-theme-xs rw-dim">
        {t(locale, ioKind === "file" ? "about.io.file.hint" : "about.io.hint")}
      </p>
      {sample ? (
        <CodeCopy text={sample} filename={languageLabel(current)}>
          <pre className="rw-scroll-x p-4 font-mono text-theme-xs leading-relaxed rw-strong" tabIndex={0}>
            <code>
              {tokens.map((token, index) =>
                token.kind === "plain" ? (
                  token.text
                ) : (
                  <span key={index} className={TOKEN_CLASS[token.kind]}>
                    {token.text}
                  </span>
                ),
              )}
            </code>
          </pre>
        </CodeCopy>
      ) : (
        <p className="text-theme-sm rw-dim">{t(locale, "about.sampleMissing")}</p>
      )}
    </div>
  );
}
