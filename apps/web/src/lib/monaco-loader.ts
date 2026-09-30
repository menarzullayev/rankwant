"use client";

import { loader } from "@monaco-editor/react";

let prepared: Promise<void> | null = null;

function installMonacoWorkers(): void {
  if (typeof globalThis.MonacoEnvironment?.getWorker === "function") return;
  globalThis.MonacoEnvironment = {
    getWorker(_workerId, label) {
      switch (label) {
        case "json":
          return new Worker(
            new URL("monaco-editor/esm/vs/language/json/json.worker.js", import.meta.url),
          );
        case "css":
        case "scss":
        case "less":
          return new Worker(
            new URL("monaco-editor/esm/vs/language/css/css.worker.js", import.meta.url),
          );
        case "html":
        case "handlebars":
        case "razor":
          return new Worker(
            new URL("monaco-editor/esm/vs/language/html/html.worker.js", import.meta.url),
          );
        case "typescript":
        case "javascript":
          return new Worker(
            new URL(
              "monaco-editor/esm/vs/language/typescript/ts.worker.js",
              import.meta.url,
            ),
          );
        default:
          return new Worker(
            new URL("monaco-editor/esm/vs/editor/editor.worker.js", import.meta.url),
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
