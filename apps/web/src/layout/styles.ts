/** Foydalanuvchi tanlaydigan vizual uslublar.
 *
 * CSS tomoni — `globals.css` dagi `[data-style="..."]` bloklari; bu yerda
 * faqat ro'yxat va yorug'/qorong'u qo'llab-quvvatlashi turadi. `dual: false`
 * uslublar bitta muhitga mo'ljallangan (terminal qorong'u, gil yorug'), shu
 * sababli ularda tema tugmasi ko'rsatilmaydi.
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
  label: string;
  hint: string;
  dual: boolean;
};

export const STYLES: StyleDef[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    hint: "Hozirgi — yumshoq kartalar",
    dual: true,
  },
  { id: "swiss", label: "Shveycha", hint: "Chiziq va tipografika", dual: true },
  { id: "flat", label: "Flat", hint: "Soyasiz, toza ranglar", dual: true },
  {
    id: "material",
    label: "Material",
    hint: "Balandlik va soyalar",
    dual: true,
  },
  {
    id: "editorial",
    label: "Editorial",
    hint: "Serif, jurnal ko'rinishi",
    dual: true,
  },
  {
    id: "brutal",
    label: "Neo-brutalizm",
    hint: "Qalin chegara, qattiq soya",
    dual: true,
  },
  { id: "terminal", label: "Terminal", hint: "Monospace, konsol", dual: false },
  {
    id: "glass",
    label: "Glassmorphism",
    hint: "Shaffof, xiralashgan",
    dual: false,
  },
  { id: "neu", label: "Neumorphism", hint: "Yumshoq bo'rtma", dual: false },
  { id: "clay", label: "Claymorphism", hint: "Gil, hajmli", dual: false },
  { id: "aurora", label: "Aurora", hint: "Gradient fon", dual: false },
  { id: "skeu", label: "Skeuomorfizm", hint: "Metall va relyef", dual: false },
];

export const DEFAULT_STYLE: StyleId = "clay";

export const STYLE_IDS: StyleId[] = STYLES.map((s) => s.id);

export const isDual = (id: StyleId) =>
  STYLES.find((s) => s.id === id)?.dual ?? true;
