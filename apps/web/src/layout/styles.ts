/** Foydalanuvchi tanlaydigan vizual uslublar.
 *
 * CSS tomoni — `globals.css` dagi `[data-style="..."]` bloklari; bu yerda
 * faqat ro'yxat va yorug'/qorong'u qo'llab-quvvatlashi turadi. `dual: false`
 * uslublar bitta muhitga mo'ljallangan (terminal qorong'u, gil yorug'), shu
 * sababli ularda tema tugmasi ko'rsatilmaydi.
 *
 * ⚠️ `label` va `hint` EMAS, `labelKey`/`hintKey`: ilgari bu yerda tayyor
 * o'zbekcha matn turardi va 9 tilda ham o'zbekcha chiqardi. Uslub nomi
 * (Dashboard, Terminal, Aurora) — atoqli ot, tarjima qilinmaydi, shuning
 * uchun ba'zi kalitlarning qiymati barcha tillarda bir xil; bu ataylab
 * shunday va `tools/check_i18n.py` dagi `UNTRANSLATED_OK` ga yozilgan.
 */
export type StyleId =
  | "dashboard"
  | "swiss"
  | "flat"
  | "material"
  | "editorial"
  | "brutal"
  | "terminal"
  | "glass"
  | "neu"
  | "clay"
  | "aurora"
  | "skeu";

export type StyleDef = {
  id: StyleId;
  labelKey: string;
  hintKey: string;
  dual: boolean;
};

export const STYLES: StyleDef[] = [
  {
    id: "dashboard",
    labelKey: "style.dashboard.label",
    hintKey: "style.dashboard.hint",
    dual: true,
  },
  {
    id: "swiss",
    labelKey: "style.swiss.label",
    hintKey: "style.swiss.hint",
    dual: true,
  },
  {
    id: "flat",
    labelKey: "style.flat.label",
    hintKey: "style.flat.hint",
    dual: true,
  },
  {
    id: "material",
    labelKey: "style.material.label",
    hintKey: "style.material.hint",
    dual: true,
  },
  {
    id: "editorial",
    labelKey: "style.editorial.label",
    hintKey: "style.editorial.hint",
    dual: true,
  },
  {
    id: "brutal",
    labelKey: "style.brutal.label",
    hintKey: "style.brutal.hint",
    dual: true,
  },
  {
    id: "terminal",
    labelKey: "style.terminal.label",
    hintKey: "style.terminal.hint",
    dual: false,
  },
  {
    id: "glass",
    labelKey: "style.glass.label",
    hintKey: "style.glass.hint",
    dual: false,
  },
  {
    id: "neu",
    labelKey: "style.neu.label",
    hintKey: "style.neu.hint",
    dual: false,
  },
  {
    id: "clay",
    labelKey: "style.clay.label",
    hintKey: "style.clay.hint",
    dual: false,
  },
  {
    id: "aurora",
    labelKey: "style.aurora.label",
    hintKey: "style.aurora.hint",
    dual: false,
  },
  {
    id: "skeu",
    labelKey: "style.skeu.label",
    hintKey: "style.skeu.hint",
    dual: false,
  },
];

export const DEFAULT_STYLE: StyleId = "clay";

export const STYLE_IDS: StyleId[] = STYLES.map((s) => s.id);

export const isDual = (id: StyleId) =>
  STYLES.find((s) => s.id === id)?.dual ?? true;
