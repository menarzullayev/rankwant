import { highlight, type TokenKind } from "@/lib/highlight";

const TOKEN_CLASS: Record<TokenKind, string> = {
  plain: "",
  comment: "rw-faint italic",
  string: "rw-ok-ink",
  number: "rw-warn-ink",
  keyword: "rw-accent-ink",
};

/** A short code block with the site's light highlighting (`lib/highlight`). */
export function CodeSnippet({ code, language }: { code: string; language: string }) {
  const tokens = highlight(code, language || "cpp");
  return (
    <pre
      className="rw-scroll-x rw-radius-sm border rw-line p-4 font-mono text-theme-xs leading-relaxed rw-strong"
      tabIndex={0}
    >
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
  );
}
