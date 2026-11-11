import { Children, createElement, type ReactNode } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

import { inReaderAlphabet } from "@/i18n/alphabet";

/**
 * Masala matni, maqola va blog uchun.
 *
 * Matn DB da Markdown + LaTeX sifatida saqlanadi (05-domain-model),
 * lekin xom holda ko'rsatilardi: `## Sarlavha` va formulalar shundayligicha
 * chiqib, masala matni o'qib bo'lmaydigan holga kelardi.
 *
 * HTML ATAYLAB o'chirilgan: matnni masala tuzuvchilar yozadi, ya'ni
 * `rehype-raw` qo'shilsa u XSS yo'liga aylanadi.
 */
/** `## Qidiruv {#binary-search}` — a heading anchor, as the algorithms library
 *  writes them (ADR-0062). Links inside the text point at the id. */
const HEADING_ANCHOR = /\s*\{#([\w-]+)\}\s*$/;

function anchored(tag: "h1" | "h2" | "h3" | "h4" | "h5" | "h6") {
  return function Heading({ children }: { children?: ReactNode }) {
    const parts = Children.toArray(children);
    const last = parts[parts.length - 1];
    let id: string | undefined;
    if (typeof last === "string") {
      const match = HEADING_ANCHOR.exec(last);
      if (match) {
        id = match[1];
        parts[parts.length - 1] = last.slice(0, match.index);
      }
    }
    // The root's scroll-padding keeps the heading below the sticky header.
    return createElement(tag, { id }, ...parts);
  };
}

const ANCHORED: Components = {
  h1: anchored("h1"),
  h2: anchored("h2"),
  h3: anchored("h3"),
  h4: anchored("h4"),
  h5: anchored("h5"),
  h6: anchored("h6"),
};

export function Markdown({
  children,
  lang,
  anchors = false,
}: {
  children: string;
  /** The text's own language. Uzbek is shown in the reader's alphabet
   *  (ADR-0059); code, formulas and links stay as written. */
  lang?: string | null;
  /** Turn a heading's trailing `{#id}` into its id (the algorithms library). */
  anchors?: boolean;
}) {
  return (
    <div className="rw-md leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={anchors ? ANCHORED : undefined}
      >
        {inReaderAlphabet(children, lang)}
      </ReactMarkdown>
    </div>
  );
}

/**
 * Markdown matnidan ro'yxat uchun bir qatorli parcha.
 *
 * NEGA KERAK: Updates arxivi va bosh sahifadagi ro'yxat matnni
 * `line-clamp` bilan qisqartiradi, ya'ni xom `##` va `**` belgilari
 * ko'rinib qolardi. Bu to'liq Markdown parseri EMAS — faqat eng ko'p
 * uchraydigan belgilar olib tashlanadi. To'liq matn baribir `Markdown`
 * bilan chiziladi, shuning uchun bu yerda aniqlik emas, o'qilish muhim.
 */
export function excerpt(text: string, limit = 160): string {
  const plain = text
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^\s{0,3}#{1,6}\s+/gm, "")
    .replace(/^\s{0,3}[-*+]\s+/gm, "")
    .replace(/^\s{0,3}>\s?/gm, "")
    .replace(/[*_]{1,3}([^*_\n]+)[*_]{1,3}/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
  return plain.length > limit
    ? `${plain.slice(0, limit - 1).trimEnd()}…`
    : plain;
}
