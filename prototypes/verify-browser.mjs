/**
 * Recharts prototip — haqiqiy brauzerda tekshirish (Chrome DevTools Protocol).
 *
 * NIMA UCHUN BU BOR
 * ─────────────────
 * HTML ichidagi JSX `type="text/babel"` bilan brauzerda kompilyatsiya
 * qilinadi. Ya'ni `tsc` tekshirmaydi, lint yo'q, build yo'q: sintaksis yoki
 * komponent nomi xatosi FAQAT brauzerda ko'rinadi — sahifa oq bo'lib qoladi,
 * hech qanday xato chiqarmaydi. Bu skript o'sha jim holatni ushlaydi.
 *
 * Nima tekshiriladi:
 *   1. Konsolda xato / sahifa istisnosi yo'q.
 *   2. `#root` ichida SVG bor va `<path>` lar soni kutilgan oraliqda
 *      (har bir diagramma o'z `path` ini chizadi — 0 bo'lsa Recharts
 *      yuklanmagan yoki ma'lumot bo'sh).
 *   3. Recharts haqiqatan global (`window.Recharts`) va unda
 *      `ResponsiveContainer` bor — UMD bundle ulanishini bildiradi.
 *   4. Mavzu almashtirgichi ishlaydi (`data-rw-theme` o'zgaradi).
 *
 * Ishlatish:
 *   node prototypes/verify-browser.mjs
 */

import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";

const require = createRequire(import.meta.url);

const PAGE = resolve("prototypes/recharts-contest-analytics.html");

/**
 * Chromium topish: avval o'rnatilgan Playwright nusxasi, keyin tizim
 * brauzerlari. Playwright nusxasi ATAYLAB birinchi — u ma'lum versiya,
 * ya'ni natija takrorlanadi.
 */
function findChrome() {
  const candidates = [
    join(homedir(), "AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe"),
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  throw new Error("Chromium topilmadi — tekshirilgan yo'llar: " + candidates.join(", "));
}

/** Bitta bo'sh port: brauzer `--remote-debugging-port` ni kutadi. */
const PORT = 9333 + Math.floor(Math.random() * 200);

const chrome = spawn(
  findChrome(),
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${join(tmpdir(), "rw-proto-profile-" + PORT)}`,
    "--allow-file-access-from-files",
    `--window-size=1400,2400`,
    "about:blank",
  ],
  { stdio: ["ignore", "ignore", "pipe"] },
);

let stderr = "";
chrome.stderr.on("data", (d) => (stderr += d.toString()));

/** CDP endpoint tayyor bo'lguncha kutamiz — brauzer darhol ochilmaydi. */
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
  throw new Error(
    `DevTools ${timeoutMs} ms ichida javob bermadi.\nchrome stderr:\n${stderr.slice(-1500)}`,
  );
}

/** Yupqa CDP klienti: `send` javobni kutadi, `on` hodisalarni yig'adi. */
class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.listeners = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
      } else if (msg.method) {
        for (const fn of this.listeners.get(msg.method) ?? []) fn(msg.params);
      }
    });
  }
  static async connect(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => {
      ws.addEventListener("open", res, { once: true });
      ws.addEventListener("error", () => rej(new Error("WebSocket ulanmadi")), { once: true });
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
      }, 30000);
    });
  }
  on(method, fn) {
    if (!this.listeners.has(method)) this.listeners.set(method, []);
    this.listeners.get(method).push(fn);
  }
}

const problems = [];
const consoleErrors = [];
const pageExceptions = [];

let cdp;
try {
  await waitForDevtools();

  const target = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })
    .then((r) => r.json());

  cdp = await Cdp.connect(target.webSocketDebuggerUrl);
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable");
  await cdp.send("Log.enable");

  cdp.on("Runtime.consoleAPICalled", (p) => {
    if (p.type === "error") {
      consoleErrors.push(p.args.map((a) => a.value ?? a.description ?? a.type).join(" "));
    }
  });
  cdp.on("Runtime.exceptionThrown", (p) => {
    const d = p.exceptionDetails;
    pageExceptions.push(d.exception?.description ?? d.text ?? JSON.stringify(d));
  });
  cdp.on("Log.entryAdded", (p) => {
    if (p.entry.level === "error") consoleErrors.push(p.entry.text);
  });

  // `file://` — CDN skriptlar tarmoqdan keladi, ya'ni internet kerak.
  await cdp.send("Page.navigate", { url: "file:///" + PAGE.replace(/\\/g, "/") });

  // Babel kompilyatsiyasi + Recharts chizishi + animatsiya: kutamiz.
  // Kutish ATAYLAB uzun (CDN sovuq keshda ~2-4 s) va tekshiruv tsiklda —
  // qat'iy `sleep` o'rniga SHART bajarilguncha.
  const evaluate = async (expr) => {
    const r = await cdp.send("Runtime.evaluate", {
      expression: expr,
      returnByValue: true,
      awaitPromise: true,
    });
    if (r.exceptionDetails) {
      throw new Error(
        "sahifada istisno: " + (r.exceptionDetails.exception?.description ?? r.exceptionDetails.text),
      );
    }
    return r.result.value;
  };

  // ⚠️ Boshlang'ich holat tozalanadi. Prototip mavzuni saqlaydi
  // (`rw-proto-theme`), ya'ni oldingi yurishdan qolgan qiymat keyingi
  // tekshiruvning BOSH holatini o'zgartirardi: bir marta `dark`, keyin
  // `light`. O'lchandi — shu sababli birinchi yurish `dark -> dark`
  // bo'lib, sababi noto'g'ri o'qilgan. Tekshiruv boshlang'ich holatdan
  // qat'i nazar bir xil bo'lishi kerak.
  await evaluate(
    `(() => { try { localStorage.removeItem("rw-proto-theme"); }
              catch (e) { /* file:// da ruxsat bo'lmasligi mumkin */ }
              return true; })()`,
  );
  await cdp.send("Page.reload", { ignoreCache: false });
  await new Promise((r) => setTimeout(r, 400));

  const deadline = Date.now() + 40000;
  let ready = null;
  while (Date.now() < deadline) {
    ready = await evaluate(`(() => {
      const root = document.getElementById("root");
      const charts = document.querySelectorAll(".recharts-wrapper").length;
      return { hasRecharts: typeof window.Recharts === "object" && window.Recharts !== null,
               rc: !!(window.Recharts && window.Recharts.ResponsiveContainer),
               charts, paths: root ? root.querySelectorAll("path").length : 0,
               svgs: root ? root.querySelectorAll("svg").length : 0,
               text: root ? root.innerText.length : 0 };
    })()`);
    if (ready.charts >= 8 && ready.paths > 40) break;
    await new Promise((r) => setTimeout(r, 700));
  }

  // ── 1. Recharts UMD ────────────────────────────────────────────────
  if (!ready.hasRecharts) problems.push("`window.Recharts` yo'q — UMD bundle ulanmagan");
  else if (!ready.rc) problems.push("`Recharts.ResponsiveContainer` yo'q — noto'g'ri bundle");

  // ── 2. Diagrammalar chizilgan ──────────────────────────────────────
  if (ready.charts < 8) {
    problems.push(`Recharts konteynerlari kam: ${ready.charts} (8 diagramma kutilgan)`);
  }
  if (ready.svgs < 8) problems.push(`SVG kam: ${ready.svgs}`);
  if (ready.paths < 40) problems.push(`chizilgan \`path\` kam: ${ready.paths}`);
  if (ready.text < 400) problems.push(`sahifa matni juda kam: ${ready.text} belgi`);

  // ── 3. Xato yo'q ───────────────────────────────────────────────────
  if (pageExceptions.length) {
    problems.push("sahifa istisnosi: " + pageExceptions.slice(0, 3).join(" | "));
  }
  if (consoleErrors.length) {
    problems.push("konsol xatosi: " + consoleErrors.slice(0, 3).join(" | "));
  }

  // ── 4. Mavzu almashtirgichi ────────────────────────────────────────
  //
  // ⚠️ `click()` dan keyin DARHOL o'qish xato beradi. `useThemeTokens`
  // mavzuni React EFFEKTIDA yozadi (`useEffect` -> setAttribute), ya'ni
  // DOM o'zgarishi keyingi renderdan keyin bo'ladi. Birinchi urinishda
  // sinxron o'qilgani uchun `dark -> dark` chiqdi va bu "tugma
  // ishlamayapti" deb noto'g'ri o'qildi (o'lchandi). Kutish shart.
  const theme = await evaluate(`(async () => {
    const before = document.documentElement.getAttribute("data-rw-theme");
    const btn = [...document.querySelectorAll("button")].find(b =>
      (b.getAttribute("aria-label") || "").includes("Mavzuni"));
    if (!btn) return { error: "mavzu tugmasi topilmadi" };
    const waitFor = async (want) => {
      for (let i = 0; i < 40; i++) {
        if (document.documentElement.getAttribute("data-rw-theme") === want) return true;
        await new Promise(r => setTimeout(r, 50));
      }
      return false;
    };
    const want = before === "dark" ? "light" : "dark";
    btn.click();
    const changed = await waitFor(want);
    const after = document.documentElement.getAttribute("data-rw-theme");
    btn.click();
    const restored = await waitFor(before);
    return { before, want, after, changed, restored,
             final: document.documentElement.getAttribute("data-rw-theme") };
  })()`);
  if (theme.error) problems.push(theme.error);
  else {
    if (!theme.changed) {
      problems.push(`mavzu almashmadi: ${theme.before} -> ${theme.after} (${theme.want} kutilgan)`);
    }
    if (!theme.restored) {
      problems.push(`mavzu qaytmadi: ${theme.before} kutilgan, ${theme.final} topildi`);
    }
  }

  console.log(`Recharts global: ${ready.hasRecharts}, ResponsiveContainer: ${ready.rc}`);
  console.log(`Diagramma konteynerlari: ${ready.charts}, SVG: ${ready.svgs}, path: ${ready.paths}`);
  console.log(`Sahifa matni: ${ready.text} belgi, konsol xatosi: ${consoleErrors.length}`);
  if (!theme.error) {
    console.log(`Mavzu: ${theme.before} -> ${theme.after} -> ${theme.final}`);
  }

  if (problems.length) {
    console.log("\nFAIL:");
    for (const p of problems) console.log("  - " + p);
  } else {
    console.log("\nOK: prototip haqiqiy brauzerda chizildi, xato yo'q");
  }
} finally {
  try {
    cdp?.ws.close();
  } catch {
    /* allaqachon yopilgan */
  }
  chrome.kill();
}

process.exit(problems.length ? 1 : 0);
