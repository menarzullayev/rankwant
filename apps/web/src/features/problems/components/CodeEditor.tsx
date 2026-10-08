"use client";

import { t } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";

import { loader } from "@monaco-editor/react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const Monaco = dynamic(() => import("@monaco-editor/react"), { ssr: false });

// `--rw-editor-h` is set by a layout that knows how much room is left
// (the sticky submit panel); everywhere else the editor is about half
// the screen.
const HEIGHT = "var(--rw-editor-h, clamp(320px, min(52vh, 640px), 640px))";
const LOAD_TIMEOUT_MS = 3500;

const monacoOptions = {
  automaticLayout: true,
  fontSize: 14,
  lineNumbers: "on" as const,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  tabSize: 4,
  wordWrap: "off" as const,
  renderLineHighlight: "line" as const,
  padding: { top: 12, bottom: 12 },
};

/** Muharrir mavzusi 12 ta uslub va ikkala temaga mos kelishi kerak.
 * Har biri uchun ro'yxat yuritish o'rniga `--rw-text` yorqinligiga
 * qaraymiz: matn och bo'lsa fon qorong'u. */
function prefersDarkEditor(): boolean {
  const probe = document.createElement("span");
  probe.style.color = "var(--rw-text)";
  probe.style.display = "none";
  document.body.appendChild(probe);
  const rgb = getComputedStyle(probe).color.match(/\d+/g);
  probe.remove();
  if (!rgb) return true;
  const [r, g, b] = rgb.map(Number);
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.5;
}

export default function CodeEditor({
  language,
  value,
  onChange,
}: {
  language: string;
  value: string;
  onChange: (next: string) => void;
}) {
  const locale = useLocale();
  const [mode, setMode] = useState<"plain" | "monaco">("plain");
  const [dark, setDark] = useState(true);

  useEffect(() => {
    let alive = true;
    const timer = setTimeout(() => alive && setMode("plain"), LOAD_TIMEOUT_MS);

    void import("@/lib/monaco-loader")
      .then(({ prepareMonaco }) => prepareMonaco())
      .then(() => loader.init())
      .then(() => alive && setMode("monaco"))
      .catch(() => alive && setMode("plain"))
      .finally(() => clearTimeout(timer));

    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, []);

  useEffect(() => {
    const sync = () => setDark(prefersDarkEditor());
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "data-style"],
    });
    return () => observer.disconnect();
  }, []);

  if (mode === "monaco")
    return (
      <div
        className="overflow-hidden rw-radius-sm border rw-line"
        style={{ height: HEIGHT, minHeight: 240 }}
      >
        <Monaco
          language={language}
          value={value}
          //: ⚠️ Aniq tip — `next` 16.3.6 dan keyin inferensiya `any` ga
          //: tushdi (TS7006). Monaco `undefined` ham beradi.
          onChange={(next: string | undefined) => onChange(next ?? "")}
          theme={dark ? "vs-dark" : "vs"}
          options={monacoOptions}
        />
      </div>
    );

  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      spellCheck={false}
      autoCapitalize="off"
      autoCorrect="off"
      aria-label={t(locale, "submit.solution")}
      className="w-full rw-radius-sm border rw-line rw-field-bg p-3 font-mono text-theme-sm leading-relaxed rw-strong outline-none rw-focus-line"
      style={{ height: HEIGHT, minHeight: 240, tabSize: 4 }}
    />
  );
}
