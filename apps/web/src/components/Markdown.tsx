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
