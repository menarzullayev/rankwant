import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

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
export function Markdown({ children }: { children: string }) {
  return (
    <div className="rw-md leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
      >
        {children}
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
