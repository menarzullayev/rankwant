"use client";

import { loader } from "@monaco-editor/react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { t } from "@/i18n/messages";
import { useLocale } from "@/i18n/LocaleProvider";

const Monaco = dynamic(() => import("@monaco-editor/react"), { ssr: false });

const HEIGHT = "clamp(280px, 46vh, 560px)";

/** Monaco o'z manbasini CDN dan yuklaydi. O'zbekistondagi aloqada bu
 * cho'zilishi yoki umuman yetib kelmasligi mumkin — o'shanda oddiy
 * `textarea` ga tushamiz, aks holda foydalanuvchi kod yoza olmay qolardi. */
const LOAD_TIMEOUT_MS = 8000;

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
  const [mode, setMode] = useState<"loading" | "monaco" | "plain">("loading");
  const [dark, setDark] = useState(true);

  useEffect(() => {
    let alive = true;
    const timer = setTimeout(() => {
      if (alive)
        setMode((current) => (current === "loading" ? "plain" : current));
    }, LOAD_TIMEOUT_MS);

    loader
      .init()
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
        style={{ height: HEIGHT }}
      >
        <Monaco
          language={language}
          value={value}
          onChange={(next) => onChange(next ?? "")}
          theme={dark ? "vs-dark" : "vs"}
          options={{
            automaticLayout: true,
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            tabSize: 4,
            renderLineHighlight: "none",
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    );

  if (mode === "loading")
    return (
      <div
        className="flex items-center justify-center rw-radius-sm border rw-line rw-field-bg text-theme-sm rw-faint"
        style={{ height: HEIGHT }}
      >
        {t(locale, "editor.loading")}
      </div>
    );

  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      spellCheck={false}
      autoCapitalize="off"
      autoCorrect="off"
      className="w-full rw-radius-sm border rw-line rw-field-bg p-3 font-mono text-theme-xs rw-strong outline-none rw-focus-line"
      style={{ height: HEIGHT }}
    />
  );
}
