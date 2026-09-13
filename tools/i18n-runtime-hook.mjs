/** Node loader: `.ts` ni topib, joyida kompilyatsiya qiladi.
 *
 *  `i18n-runtime-probe.mjs` HAQIQIY manba fayllarni import qiladi
 *  (`messages.ts`, `messages.server.ts`, o'nta lug'at). Node `.ts` ni
 *  o'zi o'qimaydi, TypeScript ham `esbuild` kabi bog'liqlikni talab
 *  qiladi — shuning uchun bu yerda `typescript` paketining API'si
 *  ishlatiladi (u allaqachon `apps/web` da bor).
 *
 *  Ikki ish qilinadi:
 *   1) `resolve` — kengaytmasiz nisbiy yo'lni (`.ts`/`.tsx`) topadi;
 *   2) `load`  — `.ts` ni kompilyatsiya qilib beradi.
 *
 *  `server-only` markeri ham shu yerda neytrallanadi: uning haqiqiy
 *  `index.js` i `throw` qiladi (u brauzer uchun mo'ljallangan), bizga
 *  esa faqat modul kerak.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import { createRequire } from "node:module";

/** `tools/` → repo ildizi → `apps/web`.
 *
 *  `process.cwd()` ga TAYANMAYMIZ: hook ikki xil joydan ishga
 *  tushirilishi mumkin (repo ildizidan va `apps/web` dan), `cwd` esa
 *  o'shanga qarab o'zgaradi. Faylning o'z joyidan hisoblash — bir xil
 *  natija beradi. */
const REPO = path.resolve(import.meta.dirname, "..");
const WEB = path.join(REPO, "apps", "web");

/** `typescript` `apps/web` da o'rnatilgan, `tools/` da emas.
 *  Shuning uchun `require` nuqtasini `apps/web` ga ko'rsatamiz — aks
 *  holda Node `tools/` dan qidiradi va topmaydi. */
const require = createRequire(path.join(WEB, "package.json"));
const ts = require("typescript");

function compile(file) {
  const source = readFileSync(file, "utf8");
  return ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ESNext,
      target: ts.ScriptTarget.ES2022,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
    fileName: file,
  }).outputText;
}

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "server-only") {
    return nextResolve(
      pathToFileURL(path.join(WEB, "node_modules/server-only/empty.js")).href,
      context,
    );
  }

  try {
    return await nextResolve(specifier, context);
  } catch (err) {
    if (!specifier.startsWith(".") && !specifier.startsWith("/")) throw err;
    const parent = context.parentURL
      ? path.dirname(fileURLToPath(context.parentURL))
      : WEB;
    for (const ext of [".ts", ".tsx", "/index.ts", "/index.tsx"]) {
      const candidate = path.resolve(parent, specifier + ext);
      try {
        readFileSync(candidate);
        return { url: pathToFileURL(candidate).href, shortCircuit: true };
      } catch {
        /* keyingi kengaytmani sina */
      }
    }
    throw err;
  }
}

export async function load(url, context, nextLoad) {
  if (url.endsWith(".ts") || url.endsWith(".tsx")) {
    return {
      format: "module",
      source: compile(fileURLToPath(url)),
      shortCircuit: true,
    };
  }
  return nextLoad(url, context);
}
