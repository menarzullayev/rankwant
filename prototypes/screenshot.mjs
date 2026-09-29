/**
 * Prototipning skrinshotini oladi (yorug' va qorong'i mavzuda).
 *
 * Nima uchun: `verify-browser.mjs` "chizildi" ni isbotlaydi, lekin
 * "chiroyli chiqdi" ni emas. Skrinshot — yagona haqiqiy ko'z bilan
 * tekshirish yo'li. Fayllar `prototypes/shots/` ga tushadi.
 *
 * Ishlatish:  node prototypes/screenshot.mjs
 */

import { spawn } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";

const PAGE = resolve("prototypes/recharts-contest-analytics.html");
const OUT = resolve("prototypes/shots");

function findChrome() {
  const candidates = [
    join(homedir(), "AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe"),
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  throw new Error("Chromium topilmadi");
}

const PORT = 9700 + Math.floor(Math.random() * 200);

const chrome = spawn(
  findChrome(),
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--hide-scrollbars",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${join(tmpdir(), "rw-shot-" + PORT)}`,
    "--window-size=1400,2600",
    "about:blank",
  ],
  { stdio: ["ignore", "ignore", "ignore"] },
);

async function waitForDevtools(timeoutMs = 25000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (res.ok) return await res.json();
    } catch {
      /* hali tayyor emas */
    }
    await new Promise((r) => setTimeout(r, 350));
  }
  throw new Error("DevTools javob bermadi");
}

class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
      }
    });
  }
  static async connect(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => {
      ws.addEventListener("open", res, { once: true });
      ws.addEventListener("error", () => rej(new Error("WS ulanmadi")), { once: true });
    });
    return new Cdp(ws);
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.delete(id)) reject(new Error(`CDP timeout: ${method}`));
      }, 40000);
    });
  }
}

mkdirSync(OUT, { recursive: true });

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

let cdp;
try {
  await waitForDevtools();
  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })
    .then((r) => r.json());
  cdp = await Cdp.connect(target.webSocketDebuggerUrl);
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable");

  const evaluate = async (expr) => {
    const r = await cdp.send("Runtime.evaluate", {
      expression: expr, returnByValue: true, awaitPromise: true,
    });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
    return r.result.value;
  };

  const shoot = async (name) => {
    const { data } = await cdp.send("Page.captureScreenshot", {
      format: "png", captureBeyondViewport: true,
    });
    const file = join(OUT, name);
    writeFileSync(file, Buffer.from(data, "base64"));
    console.log("yozildi:", file);
  };

  for (const theme of ["dark", "light"]) {
    await cdp.send("Page.navigate", { url: "file:///" + PAGE.replace(/\\/g, "/") });
    await wait(500);
    await evaluate(`(() => { try { localStorage.setItem("rw-proto-theme", "${theme}"); }
                              catch (e) {} return true; })()`);
    await cdp.send("Page.reload", {});
    // CDN + Babel + Recharts animatsiyasi tugashini kutamiz.
    //
    // ⚠️ Faqat `.recharts-wrapper` paydo bo'lishini kutish YETARLI EMAS —
    // o'lchandi: konteyner darhol yaratiladi, lekin Recharts o'lchamni
    // `ResizeObserver` dan keyin oladi va animatsiya 900 ms davom etadi.
    // Shu sababli birinchi skrinshotda barcha diagrammalar bo'sh chiqdi,
    // holbuki diagnostika (12 s kutgandan keyin) ularni to'liq ko'rgan.
    // Shart: SVG HAQIQIY o'lchamga ega bo'lishi, `path` soni esa barqaror.
    const deadline = Date.now() + 45000;
    let ok = false;
    let stable = 0;
    let lastPaths = -1;
    while (Date.now() < deadline) {
      const state = await evaluate(`(() => {
        let real = 0, paths = 0;
        document.querySelectorAll(".recharts-wrapper").forEach((w) => {
          const svg = w.querySelector("svg");
          if (svg && +svg.getAttribute("width") > 60 && +svg.getAttribute("height") > 60) real++;
          paths += w.querySelectorAll("path").length;
        });
        return { real, paths };
      })()`);
      if (state.real >= 8) {
        stable = state.paths === lastPaths ? stable + 1 : 0;
        lastPaths = state.paths;
        if (stable >= 2) { ok = true; break; }
      }
      await wait(700);
    }
    // ⚠️ Kutish qondirilmasa — JIM o'tib ketmaymiz: bu holda skrinshot
    // bo'sh diagrammalarni "dalil" qilib ko'rsatardi.
    if (!ok) {
      throw new Error(`"${theme}" mavzuda diagrammalar tayyor bo'lmadi — skrinshot olinmadi`);
    }
    await wait(1400); // oxirgi render + shrift
    await shoot(`contest-analytics-${theme}.png`);
  }
} finally {
  try { cdp?.ws.close(); } catch { /* yopilgan */ }
  chrome.kill();
}
