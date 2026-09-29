/**
 * Diagnostika: qaysi diagramma bo'sh chizilyapti?
 *
 * `verify-browser.mjs` "8 ta konteyner bor, `path` bor" ni tekshiradi,
 * lekin QAYSI diagramma bo'sh ekanini aytmaydi. Skrinshotda uchta
 * diagramma bo'sh ko'rindi va sabab noma'lum edi — bu skript har biri
 * uchun o'lcham, SVG `viewBox` va chizilgan elementlarni sanaydi.
 *
 * Ishlatish: node prototypes/diagnose.mjs
 */

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";

const PAGE = resolve("prototypes/recharts-contest-analytics.html");
const CHROME = join(
  homedir(),
  "AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe",
);
if (!existsSync(CHROME)) throw new Error("Chromium topilmadi: " + CHROME);

const PORT = 9911 + Math.floor(Math.random() * 100);
const chrome = spawn(
  CHROME,
  [
    "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
    "--remote-debugging-port=" + PORT,
    "--user-data-dir=" + join(tmpdir(), "rw-diag-" + PORT),
    "--window-size=1400,2600", "about:blank",
  ],
  { stdio: ["ignore", "ignore", "ignore"] },
);

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

for (let i = 0; i < 90; i++) {
  try {
    await fetch("http://127.0.0.1:" + PORT + "/json/version");
    break;
  } catch {
    await wait(300);
  }
}

const target = await fetch("http://127.0.0.1:" + PORT + "/json/new?about:blank", {
  method: "PUT",
}).then((r) => r.json());

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));

let id = 0;
const pend = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) {
    const p = pend.get(m.id);
    pend.delete(m.id);
    m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
  }
});
const send = (method, params = {}) =>
  new Promise((res, rej) => {
    const i = ++id;
    pend.set(i, { res, rej });
    ws.send(JSON.stringify({ id: i, method, params }));
    setTimeout(() => {
      if (pend.delete(i)) rej(new Error("timeout " + method));
    }, 30000);
  });

await send("Page.enable");
await send("Runtime.enable");
await send("Page.navigate", { url: "file:///" + PAGE.replace(/\\/g, "/") });
await wait(9000);

const EXPR = [
  "(() => {",
  "  const out = [];",
  "  document.querySelectorAll('.recharts-wrapper').forEach((w) => {",
  "    const svg = w.querySelector('svg');",
  "    const box = w.getBoundingClientRect();",
  "    const panel = w.closest('.rw-panel');",
  "    out.push({",
  "      chart: (panel && panel.querySelector('.rw-panel__title') || {}).innerText || '?',",
  "      boxW: Math.round(box.width), boxH: Math.round(box.height),",
  "      svgW: svg && svg.getAttribute('width'), svgH: svg && svg.getAttribute('height'),",
  "      viewBox: svg && svg.getAttribute('viewBox'),",
  "      bars: w.querySelectorAll('.recharts-bar-rectangle').length,",
  "      barPaths: w.querySelectorAll('.recharts-bar-rectangle path').length,",
  "      areas: w.querySelectorAll('.recharts-area-area').length,",
  "      lines: w.querySelectorAll('.recharts-line-curve').length,",
  "      radial: w.querySelectorAll('.recharts-radial-bar-sector').length,",
  "      sectors: w.querySelectorAll('.recharts-pie-sector').length,",
  "    });",
  "  });",
  "  return JSON.stringify(out, null, 1);",
  "})()",
].join("\n");

const r = await send("Runtime.evaluate", { expression: EXPR, returnByValue: true });
if (r.exceptionDetails) {
  console.error("sahifada istisno:", JSON.stringify(r.exceptionDetails, null, 1));
}
console.log(r.result.value);

ws.close();
chrome.kill();
