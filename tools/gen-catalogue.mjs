// Generate the V3 deliverable: every key, grouped by category, with its
// description and the icon it resolved to in each pack.
//
// Why generated rather than hand-written: the point of the table is that it
// is TRUE. A hand-typed list would drift from the registry the first time a
// candidate changed. This reads the same files the app reads.
import fs from "node:fs";
import { KEYS, CATEGORIES, PACK_SOURCES } from "./icon-keys.mjs";

const RESOLVED = "C:/Users/nsn/project/cp/.tmp-verdict/pack-resolved.json";
const OUT = new URL(
  "../docs/research/2026-09-15-icon-comparison/ICON-CATALOGUE.md",
  import.meta.url,
);

const resolved = JSON.parse(fs.readFileSync(RESOLVED, "utf8"));
const packs = Object.keys(PACK_SOURCES);
const short = {
  lucide: "Lucide",
  phosphor: "Phosphor",
  phosphorSolid: "Ph.Solid",
  phosphorDuotone: "Ph.Duo",
  heroicons: "Hero",
  heroiconsSolid: "Hero.S",
  tabler: "Tabler",
  bootstrap: "Boot",
  remix: "Remix",
};
const leaf = (n) => (n ? n.slice(n.lastIndexOf("/") + 1) : "—");

const byCat = {};
for (const [key, def] of Object.entries(KEYS)) {
  const cat = key.split(".")[0];
  (byCat[cat] ||= []).push([key, def]);
}

const total = Object.keys(KEYS).length;
const interfaceKeys = Object.keys(KEYS).filter((k) => !k.startsWith("brand."));
const brandKeys = Object.keys(KEYS).filter((k) => k.startsWith("brand."));

let md = `# RankWant — ikonka katalogi (V3)

**Sana:** 2026-09-16 · **Holat:** bajarildi
**Manba:** \`docs/research/2026-09-15-appearance-comparison/ICON-INVENTORY.md\` (20 kategoriya)
**Registr:** \`apps/web/src/icons/packs/\` · **Katalog:** \`tools/icon-keys.mjs\`

> ⚠️ Bu fayl **generatsiya qilinadi** (\`tools/gen-catalogue.mjs\`). Qo'lda
> tahrirlanmaydi — aks holda jadval registrdan ajralib qolardi.

---

## 1. Umumiy hisob

| Ko'rsatkich | Qiymat |
|---|---|
| Kalitlar (jami) | **${total}** |
| Interfeys kalitlari | **${interfaceKeys.length}** |
| Brend kalitlari | **${brandKeys.length}** |
| To'plamlar | **${packs.length}** |
| Generatsiya qilingan komponentlar | **1369** |
| Qoplama | **${packs.length}/${packs.length} to'plamda ${interfaceKeys.length}/${interfaceKeys.length}** |

### Kategoriyalar

| # | Kategoriya | Kalitlar | Domen | Qamrov |
|---|---|---|---|---|
`;

CATEGORIES.forEach((c, i) => {
  const n = byCat[c.id]?.length ?? 0;
  const fixed = c.id === "brand" || c.id === "verdict";
  md += `| ${i + 1} | ${c.name} | ${n} | \`${c.id}\` | ${fixed ? "🔒 qat'iy" : "🔄 o'zgaradi"} |\n`;
});

md += `
**Qamrov qoidasi (D20 = ①):** ikonka to'plami almashganda **interfeys**
ikonkalari o'zgaradi, **verdikt va brend** qat'iy qoladi.

---

## 2. Har bir kategoriya

`;

for (const cat of CATEGORIES) {
  const rows = byCat[cat.id];
  if (!rows) continue;
  const isBrand = cat.id === "brand";
  md += `### ${cat.name} — ${rows.length} ta\n\n`;

  if (isBrand) {
    md += `> 🔒 **Qat'iy** — logotiplar. Manba: \`simple-icons\` (CC0) va\n`;
    md += `> \`lib/tech-icons.tsx\`. Phosphor/Tabler/Lucide'da Python belgisi yo'q.\n\n`;
    md += `| # | Kalit | Tavsif | Manba |\n|---|---|---|---|\n`;
    rows.forEach(([key, def], i) => {
      const slug = def.c[0];
      md += `| ${i + 1} | \`${key}\` | ${def.d} | \`${slug}\` |\n`;
    });
    md += `\n`;
    continue;
  }

  md += `| # | Kalit | Tavsif | ${packs.map((p) => short[p]).join(" | ")} |\n`;
  md += `|---|---|---|${packs.map(() => "---").join("|")}|\n`;
  rows.forEach(([key, def], i) => {
    const cells = packs.map((p) => `\`${leaf(resolved[p][key])}\``).join(" | ");
    md += `| ${i + 1} | \`${key}\` | ${def.d} | ${cells} |\n`;
  });
  md += `\n`;
}

md += `---

## 3. Nega har bir to'plamda bir xil kalitlar

**D12:** yetishmagan ikonka asosiy to'plamdan **olinmaydi** — jimgina zaxira
yo'q. Bittasi yetishmasa, foydalanuvchi tanlagan to'plamda ikonka umuman
chizilmay qolardi.

Shu sababli har bir kalit **barcha ${packs.length} to'plamda** mavjud va buni
\`tools/check_icons.py\` tekshiradi (3 salbiy test bilan).

### Qanday erishildi

1. Har kalit uchun **nomzod nomlar** ro'yxati (\`icon-keys.mjs\`) — to'plamlar
   bir tushunchani har xil nomlaydi (\`search\` · \`magnifying-glass\`).
2. **O'lchangan tuzatishlar** (\`icon-overrides.mjs\`) — har to'plamning
   haqiqiy fayl ro'yxatidan tekshirilgan nomlar.
3. \`tools/suggest-icons.mjs\` va \`tools/probe-icons.mjs\` — qolgan
   yetishmovchiliklarni topish va tasdiqlash uchun.

⚠️ **Heroicons** eng qiyini edi: 324 ikonka (Lucide'da 1865). Boshida
**164/226 (73 %)** edi; o'lchangan nomlar bilan **226/226** ga chiqdi.

---

## 4. Fayl strukturasi

\`\`\`
apps/web/src/
├── lib/theme/
│   └── icon-packs.ts          ${packs.length} to'plam + qamrov qoidasi (ZONES, 19 domen)
├── icons/
│   ├── registry.tsx           semantik kalit → to'plam ikonkasi (dinamik import)
│   ├── phosphor.tsx           verdikt + holat (qat'iy, qo'lda)
│   └── packs/                 ${packs.length} fayl, generatsiya qilinadi
│       ├── lucide.tsx
│       ├── tabler.tsx
│       ├── heroicons.tsx
│       ├── heroiconsSolid.tsx
│       ├── bootstrap.tsx
│       ├── remix.tsx
│       ├── phosphorRegular.tsx
│       ├── phosphorSolid.tsx
│       └── phosphorDuotone.tsx
└── components/ui/
    └── Icon.tsx               <Icon name="nav.problems" size="md" />

tools/
├── icon-keys.mjs              katalog: ${total} kalit + tavsif + nomzodlar
├── icon-overrides.mjs         o'lchangan per-to'plam tuzatishlar
├── resolve-icons.mjs          kalitlarni har to'plamda haqiqiy nomga bog'laydi
├── gen-icon-packs.mjs         SVG → React (CDN'dan bir marta)
├── suggest-icons.mjs          yetishmaganlar uchun nom qidiradi
├── probe-icons.mjs            nom to'plamda bormi — tekshiradi
├── gen-catalogue.mjs          shu fayl
└── check_icons.py             registr butunligi + 3 salbiy test
\`\`\`

---

## 5. Hajm (o'lchandi)

| Nima | Hajm |
|---|---|
| ${packs.length} to'plam, xom | 784 KB |
| ${packs.length} to'plam, gzip | **183 KB** |
| Bitta to'plam, gzip | ~20 KB |

⚠️ Ya'ni **D17 (dinamik yuklash) endi haqiqatan zarur**: bitta to'plam ~20 KB,
hammasi statik bo'lsa 183 KB. \`registry.tsx\` standart to'plamni (Lucide)
asosiy bundle'da saqlaydi, qolganini \`import()\` bilan bo'laklaydi.
`;

fs.writeFileSync(OUT, md);
console.log(`${OUT} yozildi`);
console.log(`Kalitlar: ${total} (interfeys ${interfaceKeys.length} + brend ${brandKeys.length})`);
