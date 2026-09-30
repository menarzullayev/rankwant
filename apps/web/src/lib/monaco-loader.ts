"use client";

import { loader } from "@monaco-editor/react";

let prepared: Promise<void> | null = null;

/**
 * Worker yo'llari `esm/vs/` ni O'Z ICHIGA OLMAYDI.
 *
 * `monaco-editor` 0.57 da `exports` xaritasi o'zgardi:
 *
 *   0.55:  "./*": "./*"            -> `monaco-editor/esm/vs/x.js` = `<pkg>/esm/vs/x.js`
 *   0.57:  "./*": "./esm/vs/*"     -> `monaco-editor/x.js`       = `<pkg>/esm/vs/x.js`
 *
 * Ya'ni prefiksni endi XARITA qo'shadi. Eski shakl yozilsa u
 * `<pkg>/esm/vs/esm/vs/x.js` bo'lib qoladi va Turbopack
 * `Module not found` beradi (o'lchandi 2026-09-30, 10 xato).
 */
function installMonacoWorkers(): void {
  if (typeof globalThis.MonacoEnvironment?.getWorker === "function") return;
  globalThis.MonacoEnvironment = {
    getWorker(_workerId, label) {
      switch (label) {
        case "json":
          return new Worker(
            new URL("monaco-editor/language/json/json.worker.js", import.meta.url),
          );
        case "css":
        case "scss":
        case "less":
          return new Worker(
            new URL("monaco-editor/language/css/css.worker.js", import.meta.url),
          );
        case "html":
        case "handlebars":
        case "razor":
          return new Worker(
            new URL("monaco-editor/language/html/html.worker.js", import.meta.url),
          );
        case "typescript":
        case "javascript":
          return new Worker(
            new URL(
              "monaco-editor/language/typescript/ts.worker.js",
              import.meta.url,
            ),
          );
        default:
          return new Worker(
            new URL("monaco-editor/editor/editor.worker.js", import.meta.url),
          );
      }
    },
  };
}

/** Client-only: `monaco-editor` faqat `prepareMonaco()` ichida yuklanadi (SSR xavfsiz). */
export function prepareMonaco(): Promise<void> {
  if (prepared) return prepared;
  prepared = (async () => {
    installMonacoWorkers();
    const monaco = await import("monaco-editor");
    loader.config({ monaco });
  })();
  return prepared;
}
