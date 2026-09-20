import next from "eslint-config-next";
import tseslint from "typescript-eslint";

// eslint-config-next 16 native flat config beradi — FlatCompat kerak emas.
//
// ESLint 10: Next compiled babel parser eski ScopeManager beradi —
// `addGlobals` yo'q, lint `TypeError` bilan yiqiladi. typescript-eslint
// parser ESLint 10 ScopeManager'ini beradi (`.mts` ham shu yerda).
const config = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  ...next,
  {
    languageOptions: { parser: tseslint.parser },
    settings: { react: { version: "19.3.0" } },
  },
  {
    rules: {
      // `rehype-raw` masala matnidagi xom HTML ni JONLANTIRADI. Matn tashqi
      // manbadan import qilinadi (KEP.uz, 2000+ masala), ya'ni bu to'g'ridan
      // to'g'ri saqlanadigan XSS bo'lardi. O'lchandi: usiz `<script>`,
      // `onerror`, `javascript:` havola va KaTeX `\href` — hammasi zararsiz.
      "no-restricted-imports": [
        "error",
        {
          paths: [
            {
              name: "rehype-raw",
              message:
                "Masala matni tashqi manbadan keladi — xom HTML jonlantirilmaydi (Markdown.tsx izohiga qarang).",
            },
          ],
        },
      ],
    },
  },
];

export default config;
