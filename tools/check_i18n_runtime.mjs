/** `t()` ning zaxira yo'lini HAQIQIY modulda o'lchaydi — statik emas.
 *
 *  Nega kerak: `t()` da ikki xil shart bor — dev'da **otiladi**, prod'da
 *  **kalit qaytadi va bir marta jurnalga yoziladi**. Bu shartni
 *  `tools/check_i18n.py` ko'ra olmaydi: u faqat matnni o'qiydi. Ya'ni
 *  kod `throw` o'rniga `return key` qilib qo'yilsa ham yashil qoladi.
 *
 *  Bu skript modulni Node'da ishga tushirib, to'rt katakni o'lchaydi:
 *    A) server (o'nta lug'at, `evict` yo'q) — real kalit ishlaydi;
 *    B) dev — yetishmayotgan kalit OTILADI;
 *    C) prod — o'sha kalit QAYTADI va `console.error` FAQAT BIR MARTA;
 *    D) `evict` bilan bir til qolgani — boshqa til OTILADI.
 *
 *  Har katak uchun qiymat AYNAN tekshiriladi. Biror biri o'zgarsa —
 *  `exit 1`.
 *
 *  Ishlatish: node tools/check_i18n_runtime.mjs
 */

import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const WEB = path.resolve(import.meta.dirname, "..", "apps", "web");
const probe = path.join(import.meta.dirname, "i18n-runtime-probe.mjs");
const registerWrap = path.join(
  import.meta.dirname,
  "i18n-runtime-register.mjs",
);
const hook = path.join(import.meta.dirname, "i18n-runtime-hook.mjs");

const expect = [];
const problems = [];

/** Katakni alohida jarayonda ishga tushirish — `DEV` modul
 *  yuklanishida `NODE_ENV` dan o'qiladi, ya'ni uni keyin
 *  o'zgartirib bo'lmaydi. Shuning uchun prod katagi alohida
 *  jarayonda, `NODE_ENV=production` bilan. */
function runCell(mode) {
  const proc = spawnSync(
    process.execPath,
    // ⚠️ Windows'da `--import` ga MUTLAQ YO'L berib bo'lmaydi: Node
    // uni URL deb o'qiydi va `c:` sxemasini rad etadi
    // (`ERR_UNSUPPORTED_ESM_URL_SCHEME`). `file://` ko'rinishi shart.
    ["--import", pathToFileURL(registerWrap).href, probe],
    {
      cwd: WEB,
      env: { ...process.env, NODE_ENV: mode === "prod" ? "production" : "test" },
      encoding: "utf8",
    },
  );
  if (proc.status !== 0) {
    problems.push(
      `${mode} katagi ishga tushmadi (exit ${proc.status}): ` +
        `${(proc.stderr || "").split("\n").slice(0, 6).join(" | ")}`,
    );
    return null;
  }
  const line = proc.stdout.split("\n").filter((l) => l.startsWith("{")).pop();
  if (!line) {
    problems.push(`${mode} katagi JSON qaytarmadi`);
    return null;
  }
  return JSON.parse(line);
}

for (const p of [probe, registerWrap, hook]) {
  if (!existsSync(p)) problems.push(`yordamchi fayl topilmadi: ${p}`);
}
if (problems.length) {
  for (const p of problems) console.log(`  ✗ ${p}`);
  process.exit(1);
}

// ── dev kataklari ───────────────────────────────────────────────────────
const dev = runCell("dev");
if (dev) {
  expect.push(
    ["dev: real kalit (ru)", dev.realKey, "Соревнования"],
    ["dev: ro'yxatda 10 til", dev.registrySize, 10],
    ["dev: yetishmayotgan kalit otildi", dev.missingThrew, true],
    ["dev: ro'yxatga olinmagan til otildi", dev.unregisteredThrew, true],
    ["dev: `evict` bilan bir til qoldi", dev.evictRegistrySize, 1],
    ["dev: `evict`dan keyin boshqa til otildi", dev.evictOtherThrew, true],
  );
}

// ── prod katagi ─────────────────────────────────────────────────────────
const prod = runCell("prod");
if (prod) {
  expect.push(
    ["prod: yetishmayotgan kalit otilmadi", prod.missingThrew, false],
    ["prod: kalit qaytdi", prod.missingValue, "definitely.not.a.key"],
    ["prod: bir xil kalit bir marta yozildi", prod.loggedCount, 1],
    ["prod: ikkinchi kalit ham yozildi", prod.loggedCount2, 2],
    ["prod: jurnal matni", prod.loggedHasDetail, true],
  );
}

// ── solishtirish ────────────────────────────────────────────────────────
for (const [name, got, want] of expect) {
  if (got !== want) {
    problems.push(`${name}: kutilgan ${JSON.stringify(want)}, olingan ${JSON.stringify(got)}`);
  }
}

if (problems.length) {
  console.log("  ✗ i18n runtime:");
  for (const p of problems) console.log(`      ${p}`);
  process.exit(1);
}
console.log(
  `  ✓ i18n runtime: ${expect.length} ta o'lchov mos ` +
    `(dev otiladi, prod bir marta jurnalga yozadi)`,
);
