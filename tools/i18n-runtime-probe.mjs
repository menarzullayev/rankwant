/** `t()` zaxira yo'lini o'lchaydigan asosiy skript.
 *
 *  `tools/check_i18n_runtime.mjs` buni ikki marta ishga tushiradi:
 *  `NODE_ENV` dev va prod qiymatida. Har safar stdout'ga BITTA JSON
 *  qatori yoziladi; tekshiruvchi o'sha qatorni o'qiydi.
 *
 *  Bu fayl `apps/web` dan ishga tushiriladi (`cwd`), chunk esa
 *  `tools/` da turadi — import yo'li shunga qarab yozilgan.
 */

const t0 = Date.now();
void t0;

const messages = await import("../apps/web/src/i18n/messages.ts");
const { t, registerMessages, registrySize } = messages;

// `messages.server.ts` — SSR kirish nuqtasi. Uni import qilish
// o'nta tilning hammasini ro'yxatga oladi. `server-only` markeri
// hook orqali neytrallangan.
const serverMod = await import("../apps/web/src/i18n/messages.server.ts");
void serverMod;

const out = {};
const threw = (fn) => {
  try {
    fn();
    return false;
  } catch {
    return true;
  }
};

// ── A) server holati: o'nta lug'at ro'yxatda ────────────────────────────
out.realKey = t("ru", "nav.contests");
out.registrySize = registrySize();
out.missingThrew = threw(() => t("ru", "definitely.not.a.key"));
out.unregisteredThrew = threw(() => t("fr", "nav.contests"));

// ── B) `evict` bilan bir til qolgani (klient yo'li) ─────────────────────
const { kaa } = await import("../apps/web/src/i18n/locales/kaa.ts");
registerMessages("kaa", kaa, true);
out.evictRegistrySize = registrySize();
out.evictOtherThrew = threw(() => t("ru", "nav.contests"));

/** Dev katagi uchun yetarli. Prod katagi bundan keyingi qismni
 *  o'lchaydi, lekin ikkala jarayon bir xil faylni ishga tushiradi —
 *  ya'ni o'lchov bir xil sharoitda olinadi. */
if (process.env.NODE_ENV === "production") {
  registerMessages("uz", uzDict(await import("../apps/web/src/i18n/locales/uz.ts")), false);

  const logs = [];
  const original = console.error;
  console.error = (...args) => logs.push(args.join(" "));
  try {
    out.missingValue = t("uz", "definitely.not.a.key");
    out.missingThrew = false;
    // Ikkinchi chaqiruv jurnalga YOZILMASLIGI kerak.
    t("uz", "definitely.not.a.key");
    out.loggedCount = logs.length;
    t("uz", "second.missing.key");
    out.loggedCount2 = logs.length;
    out.loggedHasDetail = logs.some((l) => l.includes("missing from the"));
  } finally {
    console.error = original;
  }
}

function uzDict(mod) {
  return mod.uz;
}

console.log(JSON.stringify(out));
