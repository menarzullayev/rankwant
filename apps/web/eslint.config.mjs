import next from "eslint-config-next";

// eslint-config-next 16 native flat config beradi — FlatCompat kerak emas.
const config = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  ...next,
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
