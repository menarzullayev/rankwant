# Visual Gate Debugging Plan

## Muammo tavsifi

| | Qiymat |
|---|---|
| **Lokal** | 7/7 test yashil |
| **CI** | Pixel diff bilan yiqiladi |
| **maxDiffPixelRatio** | 1% → 5% (yordam bermadi) |
| **Snapshot oxirgi yangilanish** | PR #249 (eski) |

## 1. Ildiz sabab (tahmin, tekshirish kerak)

**Snapshotlar eskirgan.** Baseline'lar PR #249 da CI muhitida (Linux) olingan va commit qilingan. O'shandan beri:
- UI komponentlari o'zgargan
- CSS/styling yangilangan
- Masala seed ma'lumotlari o'zgargan (jadval ko'rinishi)
- CSP tuzatildi (skriptlar endi yuklanadi → sahifa to'liq render bo'ladi)

Playwright config izohi (line 25-34):
> "Linux konteynerida 6/6 sahifa 3–4% farq berdi. Diff rasmda butun matn qizil."

**Kritik:** 5% threshold ham yordam bermadi ⇒ farq **5% dan katta** yoki umuman **boshqa muammo** (masalan, sahifa o'zidan boshqacha ko'rinadi).

## 2. Tizimli debugging reja

### Phase 1: Ma'lumotlarni to'plash (1-2 soat)

**1.1. CI artifacts ni yoqish**

`nightly.yml` da `e2e` job (visual gate) artifacts saqlanmayapti. `failure()` bo'lganda diff rasmlarini saqlash kerak:

```yaml
- name: Upload visual diffs
  if: ${{ failure() }}
  uses: actions/upload-artifact@v7
  with:
    name: visual-diffs
    path: |
      tests/e2e/test-results/
      tests/e2e/visual/**/*-diff.png
      tests/e2e/visual/**/*-actual.png
    if-no-files-found: ignore
    retention-days: 7
```

**1.2. CI'da `--update-snapshots` bilan ishga tushirish**

Yangi workflow yaratish (yoki `workflow_dispatch` qo'shish):

```yaml
# .github/workflows/update-visual-baselines.yml
name: Update Visual Baselines
on:
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - name: Stack + visual tests
        env:
          COMPOSE_PROJECT_NAME: rw-visual-update
          E2E_BASE_URL: http://web:3000
          E2E_API_BASE: http://api:8000/api/v1
        run: |
          bash tools/ci_stack.sh
          bash tools/ci_playwright.sh -- npx playwright test --project=visual --update-snapshots
      - name: Commit new baselines
        run: |
          git config user.name "CI Bot"
          git config user.email "ci@rankwant.uz"
          git add tests/e2e/visual/visual.spec.ts-snapshots/
          git diff --cached --quiet || git commit -m "chore: update visual baselines"
          git push
```

**1.3. Diff hajmini o'lchash**

CI'da `--reporter=html` bilan ishga tushirish va report'ni artifacts qilish:

```yaml
- name: Visual regression with HTML report
  run: bash tools/ci_playwright.sh -- npx playwright test --project=visual --reporter=html,list
- name: Upload HTML report
  if: ${{ failure() }}
  uses: actions/upload-artifact@v7
  with:
    name: visual-report
    path: tests/e2e/playwright-report/
```

### Phase 2: Farqni tahlil qilish (1 soat)

**2.1. Diff rasmlarini ko'rish**

Artifacts'dan `-diff.png` fayllarini yuklab:
- **Butun matn qizil** → shrift anti-aliasing (yangi baseline kerak)
- **Ma'lum bir qism qizil** → o'sha komponent o'zgargan (fix yoki baseline yangilash)
- **Butun sahifa farq qiladi** → container/iframe/muhit muammosi

**2.2. Sahifa holatini tekshirish**

CI'da `page.content()` va `page.screenshot()` ni probe test orqali olish:

```typescript
// zz-visual-debug.spec.ts
import { test } from "@playwright/test";

test("debug visual page", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  const html = await page.content();
  console.log("HTML length:", html.length);
  console.log("HTML hash:", require("crypto").createHash("md5").update(html).digest("hex"));
  await page.screenshot({ path: "/tmp/debug-home.png", fullPage: true });
});
```

### Phase 3: Doimiy yechim (2-3 soat)

**3.1. Snapshotlarni CI'da yangilash**

`workflow_dispatch` bilan workflow yaratish va ishga tushirish:

```bash
gh workflow run update-visual-baselines.yml
```

**3.2. Baseline yangilanishini avtomatlashtirish**

Har haftalik (yoki har deploy'dan keyin) avtomatik yangilash:

```yaml
on:
  schedule:
    - cron: "0 3 * * 1"  # Har dushanba 03:00
```

**3.3. `maxDiffPixelRatio` ni qayta 1-2% ga tushirish**

Yangi baseline'lar bilan threshold qayta toraytiriladi.

### Phase 4: Tekshirish (1 soat)

**4.1. Yangi baseline bilan nightly ishga tushirish**

**4.2. 3 ta ketma-ket run'da barqarorlikni tekshirish**

## 3. Muammoli qismlar va yechimlari

| Muammo | Sabab | Yechim |
|---|---|---|
| Artifacts yo'q | `e2e` job'da `failure()` sharti noto'g'ri | Phase 1.1 |
| Snapshotlar eskirgan | PR #249 dan beri UI o'zgargan | Phase 3.1 |
| Lokal/CI farqi | Lokal Windows, CI Linux (lekin baseline Linux) | Baseline'lar faqat CI'da olinadi |
| CSP fix'dan keyin | Sahifa endi to'liq render bo'ladi (avval bo'sh) | Yangi baseline zarur |
| maxDiffPixelRatio 5% | Threshold'ni ko'tarish haqiqiy regressiyani yutadi | Phase 3.3 |

## 4. Qisqa yo'l (agarda vaqt cheklangan bo'lsa)

1. **Snapshotlarni CI'da yangilash** — `workflow_dispatch` bilan workflow
2. **Commit qilish** — yangi PNG'lar
3. **Threshold'ni qayta 2% ga tushirish**
4. **Nightly tekshirish**

Bu 1-2 soat ichida hal bo'ladi.

## 5. Uzoq muddatli yechim

| | Tavsif |
|---|---|
| **Avtomatik baseline** | Har deploy'dan keyin CI'da snapshot yangilash |
| **Threshold monitoring** | Diff foizini CI'da o'lchab, threshold'dan katta bo'lsa alarm |
| **Cross-platform** | Windows/Mac/Linux baseline'lari alohida (hozir faqat Linux) |
