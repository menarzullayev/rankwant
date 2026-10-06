"use client";

import { useMemo, useState } from "react";

import { Card } from "@/components/ui/Card";
import { Verdict } from "@/components/ui/Verdict";
import {
  sampleEditorLanguage,
  sampleFileForLanguage,
  sampleForLanguage,
} from "@/content/about/language-samples";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import {
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { ABOUT_VERDICT_ORDER } from "@/content/about/verdict-guide-order";

export type GuideLanguage = { code: string; name: string; version: string };

const SUBMIT_STEPS: MessageKey[] = [
  "about.submit.pickProblem",
  "about.submit.pickLanguage",
  "about.submit.useStdio",
  "about.submit.sendForm",
  "about.submit.waitJudge",
  "about.submit.analyzeResult",
];

const PRACTICES: MessageKey[] = [
  "about.practices.samples",
  "about.practices.limits",
  "about.practices.algorithms",
  "about.practices.edges",
  "about.practices.format",
  "about.practices.fastIo",
  "about.practices.debug",
  "about.practices.readAll",
];

function verdictGuideKey(
  kind: "event" | "cause" | "example",
  code: (typeof ABOUT_VERDICT_ORDER)[number],
): MessageKey {
  return `about.verdicts.${kind}.${code.toLowerCase()}` as MessageKey;
}

function languageLabel(lang: GuideLanguage): string {
  const v = lang.version.trim();
  return v ? `${lang.name} ${v}` : lang.name;
}

function CodeBlock({ code, language }: { code: string; language: string }) {
  return (
    <pre
      className="rw-scroll-x rounded-md border rw-divider bg-[var(--rw-surface-2)] p-4 font-mono text-theme-xs leading-relaxed rw-strong"
      tabIndex={0}
    >
      <code className={`language-${language}`}>{code}</code>
    </pre>
  );
}

export function SystemGuide({ languages }: { languages: GuideLanguage[] }) {
  const locale = useLocale();
  const sorted = useMemo(
    () => [...languages].sort((a, b) => languageLabel(a).localeCompare(languageLabel(b), locale)),
    [languages, locale],
  );
  const [active, setActive] = useState(() => sorted[0]?.code ?? "");
  const [ioKind, setIoKind] = useState<"stdio" | "file">("stdio");

  const current = sorted.find((l) => l.code === active) ?? sorted[0];
  const sample =
    current && ioKind === "file"
      ? sampleFileForLanguage(current.code)
      : current
        ? sampleForLanguage(current.code)
        : null;
  const editorLang = sampleEditorLanguage(current?.code ?? "cpp23");

  return (
    <div className="space-y-6">
      <Card title={t(locale, "about.compilers.title")}>
        {sorted.length === 0 ? (
          <p className="text-theme-sm rw-dim">{t(locale, "about.compilers.empty")}</p>
        ) : (
          <>
            <div
              role="tablist"
              aria-label={t(locale, "about.compilers.tabsLabel")}
              className="flex max-h-48 flex-wrap gap-2 rw-scroll-y pb-1"
            >
              {sorted.map((lang) => {
                const selected = lang.code === (current?.code ?? "");
                return (
                  <button
                    key={lang.code}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    id={`about-lang-${lang.code}`}
                    aria-controls="about-lang-panel"
                    tabIndex={selected ? 0 : -1}
                    onClick={() => setActive(lang.code)}
                    className={`rounded-full border px-3 py-1.5 text-theme-xs font-medium rw-focus-ring ${
                      selected
                        ? "border-transparent rw-accent-soft rw-accent-ink"
                        : "rw-divider rw-dim rw-hover-bg"
                    }`}
                  >
                    {languageLabel(lang)}
                  </button>
                );
              })}
            </div>
            <div
              id="about-lang-panel"
              role="tabpanel"
              aria-labelledby={current ? `about-lang-${current.code}` : undefined}
              className="mt-4 space-y-3"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-theme-xs rw-dim">{t(locale, "about.io.tabsLabel")}</span>
                <div
                  role="group"
                  aria-label={t(locale, "about.io.tabsLabel")}
                  className="inline-flex rounded-full border rw-divider p-0.5"
                >
                  {(["stdio", "file"] as const).map((kind) => {
                    const selected = ioKind === kind;
                    return (
                      <button
                        key={kind}
                        type="button"
                        aria-pressed={selected}
                        onClick={() => setIoKind(kind)}
                        className={`rounded-full px-3 py-1 text-theme-xs font-medium rw-focus-ring ${
                          selected
                            ? "rw-accent-soft rw-accent-ink"
                            : "rw-dim rw-hover-bg"
                        }`}
                      >
                        {t(locale, kind === "stdio" ? "about.io.kind.stdio" : "about.io.kind.file")}
                      </button>
                    );
                  })}
                </div>
              </div>
              <h3 className="text-theme-sm font-semibold rw-strong">
                {t(
                  locale,
                  ioKind === "file" ? "about.io.file.title" : "about.io.title",
                )}
              </h3>
              <p className="text-theme-xs rw-dim">
                {t(locale, ioKind === "file" ? "about.io.file.hint" : "about.io.hint")}
              </p>
              {sample ? (
                <CodeBlock code={sample} language={editorLang} />
              ) : (
                <p className="text-theme-sm rw-dim">{t(locale, "about.sampleMissing")}</p>
              )}
            </div>
          </>
        )}
      </Card>

      <Card title={t(locale, "about.judge.title")}>
        <p className="text-theme-sm rw-dim whitespace-pre-line">
          {t(locale, "about.judge.body")}
        </p>
      </Card>

      <Card title={t(locale, "about.notes.title")}>
        <ul className="list-disc space-y-2 pl-5 text-theme-sm rw-dim">
          <li>{t(locale, "about.notes.io")}</li>
          <li>{t(locale, "about.notes.cpp")}</li>
          <li>{t(locale, "about.notes.java")}</li>
        </ul>
      </Card>

      <Card title={t(locale, "about.submit.title")}>
        <ol className="list-decimal space-y-2 pl-5 text-theme-sm rw-dim">
          {SUBMIT_STEPS.map((key) => (
            <li key={key}>{t(locale, key)}</li>
          ))}
        </ol>
      </Card>

      <Card title={t(locale, "about.practices.title")}>
        <ul className="list-disc space-y-2 pl-5 text-theme-sm rw-dim">
          {PRACTICES.map((key) => (
            <li key={key}>{t(locale, key)}</li>
          ))}
        </ul>
      </Card>

      <Card title={t(locale, "about.verdicts.title")}>
        <p className="mb-4 text-theme-sm rw-dim">{t(locale, "about.verdicts.intro")}</p>
        <div className="rw-scroll-x">
        <Table>
          <THead>
            <TH className="w-10">{t(locale, "about.verdicts.col.num")}</TH>
            <TH className="min-w-[8rem]">{t(locale, "about.verdicts.col.status")}</TH>
            <TH className="min-w-[12rem]">{t(locale, "about.verdicts.col.event")}</TH>
            <TH className="min-w-[12rem]">{t(locale, "about.verdicts.col.cause")}</TH>
            <TH className="min-w-[14rem]">{t(locale, "about.verdicts.col.example")}</TH>
          </THead>
          <TBody>
            {ABOUT_VERDICT_ORDER.map((key, i) => (
                <TR key={key}>
                  <TD className="rw-faint align-top">{i + 1}</TD>
                  <TD className="align-top">
                    <Verdict verdict={key} variant="full" />
                  </TD>
                  <TD className="text-theme-sm rw-dim align-top">
                    {t(locale, verdictGuideKey("event", key))}
                  </TD>
                  <TD className="text-theme-sm rw-dim align-top">
                    {t(locale, verdictGuideKey("cause", key))}
                  </TD>
                  <TD className="text-theme-sm rw-faint align-top">
                    {t(locale, verdictGuideKey("example", key))}
                  </TD>
                </TR>
              ))}
          </TBody>
        </Table>
        </div>
      </Card>
    </div>
  );
}
