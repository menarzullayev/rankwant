# GitHub Free + private repository — to‘liq imkoniyatlar va cheklovlar

**Sana:** 2026-09-17 (Toshkent)  
**Maqsad:** Free reja, xususan **private repo**da nima ishlaydi, nima ishlamaydi, 2025–2026 da nima o‘zgardi.  
**Usul:** faqat rasmiy GitHub Docs, Pricing va Changelog. Eski xotira (2020 FAQ, “Windows 2× / macOS 10×”) yangi hujjat bilan solishtirilgan.

> Bu tirik hujjat emas. Limitlar o‘zgarishi mumkin. Har raqam ostida manba bor.

---

## 1. Eng muhim xulosa — 30 soniyada

GitHub Free **cheksiz private repo** va **cheksiz collaborator** beradi. Kod, issue, PR, Actions, Packages, Dependabot — ishlaydi. Lekin private repo **cheklangan funksiya to‘plami**: branch protection, required reviewers, Pages, wiki, environment secret, CodeQL, secret scanning **yo‘q**.

**Amaliy qoida:**

| Vazifa | Free private yetadimi? |
|---|---|
| Yopiq kod, cheksiz odam, issue/PR | **Ha** |
| CI/CD (Linux, o‘z runner) | **Ha** — o‘z runner da daqiqalar cheksiz |
| CI/CD (GitHub-hosted, private) | **Ha, lekin** 2000 daqiqa/oy, OS narxi farq qiladi |
| `main`ni majburiy review + required check | **Yo‘q** — Pro (shaxsiy) yoki Team (org) |
| Private repodan sayt (Pages) | **Yo‘q** |
| Secret/environment gate (prod deploy) | **Yo‘q** — faqat repo secret |
| CodeQL / secret push-protection | **Yo‘q** (public da bepul) |

**Eng katta “yashirin” imkoniyat:** self-hosted runner. GitHub-hosted daqiqalar tugaydi; o‘z mashinangizda ishlagan job **0 daqiqa** hisoblanadi.

---

## 2. Ikki qatlam — reja va ko‘rinish

GitHub “Free”ni ikki o‘qda kesadi. Ikkalasini aralashtirish — asosiy tuzoq.

```
Hisob turi          ×          Repo ko‘rinishi
Free shaxsiy                    public  → to‘liq to‘plam
Free tashkilot                  private → cheklangan to‘plam
Pro / Team / Enterprise
```

- **Public repo + Free** ≈ deyarli to‘liq: Pages, branch protection/rulesets, environment, CodeQL, secret scanning, cheksiz standard Actions daqiqalari.
- **Private repo + Free** = kod yopiq, lekin “professional” gate’lar o‘chiq.
- **Private + Pro** (shaxsiy, ~$4/oy) yoki **Team** (org, ~$4/user/oy): review, protection, Pages (sayt baribir ochiq), wiki, environment.

Manba: [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans), [FAQ 2020 o‘zgarishlari](https://docs.github.com/en/get-started/learning-about-github/faq-about-changes-to-githubs-plans).

**Free shaxsiy vs Free tashkilot**

| | Free shaxsiy | Free tashkilot |
|---|---|---|
| Cheksiz public/private repo | Ha | Ha |
| Cheksiz collaborator | Ha | Ha |
| Team (guruh ruxsati) | Yo‘q | Ha — `Read/Triage/Write/Maintain/Admin` |
| Codespaces kvotasi | 120 core-soat, 15 GB | **Yo‘q** (org Codespaces — Team+ va to‘lov) |
| Actions daqiqa / Packages | 2000 / 500 MB | 2000 / 500 MB |
| Issue fields (2026-07) | — | **Ha** (org, Free ham) |

---

## 3. Collaborator va ruxsatlar

**Cheklov yo‘q.** 2020-04-14 dan Free da private repoga cheksiz odam. Bu doimiy. ([FAQ](https://docs.github.com/en/get-started/learning-about-github/faq-about-changes-to-githubs-plans))

**Shaxsiy private repo:** collaborator = `Read` yoki `Write` (klassik). Organizing teams yo‘q.

**Org private repo (Free org):**

| Rol | Nima qiladi | Qachon beriladi |
|---|---|---|
| Read | Ko‘radi, issue ochadi, fork qiladi | Kuzatuvchi, auditor |
| Triage | Label, assign, PR review so‘raydi — push yo‘q | PM / triager |
| Write | Push, merge, Actions, secret yozish | Dasturchi |
| Maintain | Sozlama (wiki, merge usuli) — o‘chirish/visibility yo‘q | Texnik rahbar |
| Admin | Odam, webhook, visibility, o‘chirish | Egasi |

Custom rol — faqat Enterprise Cloud.

**Amaliy:** org oching, hatto Free bo‘lsa ham. Team orqali “faqat `apps/web` ga yozadiganlar”ni guruhlay olmaysiz (CODEOWNERS private Free da **majburiy emas**), lekin `Write` vs `Triage` ni ajratasiz. Tashqi odamni **outside collaborator** qilib, butun org a’zoligisiz bitta repoga qo‘shasiz.

**2FA:** Free hisobda 2FA ni majburiy qilish mumkin ([plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans)). Org da ham yoqing.

---

## 4. Actions (CI/CD)

### 4.1 Nima bepul, nima hisoblanadi

| Holat | Hisob |
|---|---|
| Public repo + **standard** GitHub-hosted runner | **0** |
| GitHub Pages workflow | **0** |
| Dependabot workflow | **0** |
| **Self-hosted** runner (private ham) | **0 daqiqa** |
| Private + GitHub-hosted standard | Kvotadan |
| **Larger runner** (public ham) | **Har doim pullik**; kvotaga kirmaydi |

Manba: [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

**Free kvota (private, hosted):**

| | Free | Pro | Team | Enterprise Cloud |
|---|---|---|---|---|
| Daqiqa / oy | **2000** | 3000 | 3000 | 50 000 |
| Artifact + Packages saqlash (umumiy) | **500 MB** | 1 GB / 2 GB pkg | 2 GB | 50 GB |
| Cache / repo | **10 GB** | 10 GB | 10 GB | 10 GB |
| Parallel job (hosted) | **20** (macOS max 5) | 40 | 60 | 500 |

Manba: [Product usage](https://docs.github.com/en/billing/reference/product-usage-included), [Actions limits](https://docs.github.com/en/actions/reference/limits).

Karta yo‘q bo‘lsa kvota tugagach ish **to‘xtaydi** (overage yo‘q). Karta bo‘lsa budget qo‘ying: “limitga yetganda to‘xta”.

### 4.2 2026: “multiplier” o‘rniga to‘g‘ridan-to‘g‘ri narx

Eski qoida (Linux 1×, Windows 2×, macOS 10×) **endi rasmiy jadval emas**. 2026 da GitHub per-minute USD beradi. Nisbat saqlanadi, lekin hisob boshqacha.

Standard hosted (2026 hujjat):

| Runner | SKU | USD / daqiqa | ~ nisbat (Linux 2-core) |
|---|---|---|---|
| Linux 1-core | `actions_linux_slim` | $0.002 | ~0.3× |
| Linux 2-core ARM | `actions_linux_arm` | $0.005 | ~0.8× |
| **Linux 2-core x64** | `actions_linux` | **$0.006** | 1× |
| Windows 2-core | `actions_windows` | $0.010 | ~1.7× |
| macOS 3/4-core | `actions_macos` | $0.062 | ~10.3× |

Har job **yuqoriga butun daqiqaga** yaxlitlanadi. ([Actions runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing))

**Amaliy:** private Free da `runs-on: ubuntu-latest` (yoki ARM linux). Windows/macOS kvotani tez yeydi. iOS/Windows test kerak bo‘lsa — self-hosted yoki pullik.

**Copilot code review** private da **Actions daqiqasini** ham yeydi. Public da bepul. ([billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions))

### 4.3 Saqlash tuzog‘i

- Artifact va Packages **bitta 500 MB hovuz**.
- Cache **alohida**: repo uchun 10 GB; oshig‘i $0.07/GB-oy.
- Artifact o‘chirish **joriy** joyni bo‘shatadi, shu oyda yig‘ilgan GB-hour ni qaytarmaydi.

**Amaliy:** `actions/upload-artifact` retention ni 1–3 kun qiling. Katta wheel/image ni Packages yoki R2 ga qo‘ying, artifactda saqlamang.

### 4.4 Private da bor / yo‘q

| | Free private |
|---|---|
| Workflow, reusable workflow, composite action | Ha |
| Repo/org secret va variable | Ha |
| Environment + environment secret | **Yo‘q** |
| Required reviewers / wait timer | **Yo‘q** (public da bor) |
| Deployment branch policy | **Yo‘q** |
| Action allowlist (2026-02) | **Ha — barcha rejalar** |
| Cron + IANA timezone (2026-03) | Ha |
| `deployment: false` environment (2026-03) | Environment o‘zi yo‘q private Free da |
| Same-repo `$/` action (2026-07) | Ha |
| Concurrent 20 / job 6 soat hosted / 35 kun run | Ha |

Environment: Free foydalanuvchi **faqat public** da sozlaydi. Private qilsangiz, oldingi environment secret/rule **e’tiborsiz** qoladi. ([Managing environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments))

**Amaliy o‘rinbosar:** `ENVIRONMENT=prod` repo secret + job `if: github.ref == 'refs/heads/main'`. Bu gate emas — yozish huquqi bor odam secretni o‘qiydi. Haqiqiy gate uchun Pro/Team.

### 4.5 Self-hosted — Free private ning asosiy quroli

Rasmiy: self-hosted **barcha rejalarda daqiqa hisoblanmaydi**.

Cheklovlar (hosted emas):

- Job 5 kun, navbat 24 soat
- Runner ro‘yxati: 1500 / 5 daqiqa
- Xavfsizlik: self-hosted **izolyatsiya qilinmagan** — fork PR ni o‘z runner da ishlatish xavfli (private da fork kamroq, lekin `pull_request_target` + secret = xavf)
- Docker Hub limit self-hosted da **ishlaydi** (hosted public image da yo‘q)

2026-02: **Runner Scale Set Client** (Go, Kubernetes shart emas) — o‘z avtoscaling. ARC Kubernetes uchun qoladi.

**Amaliy (RankWant tipidagi stack):** CI ni o‘z runner ga qo‘ying. 2000 daqiqa “zaxira” yoki oddiy lint uchun qolsin. Fork PR ni hosted da, yoki `pull_request` ni secret’siz ishlating.

---

## 5. Packages

| | Free | Izoh |
|---|---|---|
| Public paket | **Bepul**, cheksiz oqilish | |
| Private saqlash | 500 MB — **Actions artifact bilan umumiy** | |
| Private transfer / oy | **1 GB** | Oy boshida 0 |
| Kirish (download) | Har qanday manbadan **bepul** | |
| Actions + `GITHUB_TOKEN` bilan yuklash | **Bepul** (hosted va self-hosted) | |
| Self-hosted + **PAT** bilan yuklash | **Pullik** transfer | |

Manba: [Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages).

**Amaliy:**

1. Private image/npm ni Actions da `GITHUB_TOKEN` bilan oling — 1 GB ni yemaysiz.
2. Odatiy `docker pull` ni PAT bilan self-hosted da qilmang.
3. 500 MB tez to‘ladi: eski version `untagged` ni o‘chiring.
4. Public package (docs site image) — kvotaga kirmaydi.

Registry: `ghcr.io` (container), npm, Maven, NuGet, RubyGems — bir hisob.

---

## 6. Pages

| Savol | Javob |
|---|---|
| Free + **public** repo | Ha. 1 user/org site (`user.github.io`) + har repo uchun project site |
| Free + **private** repo | **Yo‘q.** Repo public bo‘lishi shart |
| Pro/Team + private repo | Sayt chiqadi, lekin **internetga ochiq** |
| Saytni login orqasida yashirish | Faqat **org + Enterprise Cloud** |

Limitlar (barcha rejalar): tavsiya 1 GB manba, 1 GB published, 100 GB/oy bandwidth (yumshoq), 10 build/soat (Actions bilan publish qilsangiz bu limit yo‘q), build 10 daqiqa. ([Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits))

**Amaliy:** private kod + ochiq docs kerak bo‘lsa — **ikki repo**: `app` private, `docs` public. Yoki Cloudflare Pages / Netlify. “Private Pages” = Enterprise, Pro emas.

---

## 7. Branch protection va rulesets

Bu private Free dagi **eng og‘riqli** cheklov.

### 7.1 Branch protection (klassik)

[Plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans) Pro/Team “private dagi advanced” ro‘yxatiga **Protected branches** va **Required pull request reviewers** ni qo‘yadi. [FAQ](https://docs.github.com/en/get-started/learning-about-github/faq-about-changes-to-githubs-plans): Team/Pro dan Free ga tushsangiz private da shular yo‘qoladi.

**Free private da yo‘q:**

- Required reviewers
- Required status checks (CI o‘tmasa merge yopiladi)
- CODEOWNERS ni majburiy qilish
- Restrict who can push (bu hatto public Free org da bor; private Team+)
- Merge queue (protection ostida)

**Free public da** protection va rulesets ishlaydi.

### 7.2 Rulesets

[About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets): org-wide ruleset — Team/Enterprise. Eski server hujjati aniqroq: rulesets **public + Free**; private uchun **Pro/Team/Enterprise**.

Push ruleset (fayl kengaytmasi, yo‘l, hajm) — private/internal, pullik rejalar.

### 7.3 Free private da nima qilish mumkin

Majburiy emas, lekin foydali:

1. **Ijtimoiy qoida** + PR template: “`main`ga to‘g‘ridan-to‘g‘ri push yo‘q”.
2. Default branch ni `main` qilib, write huquqini kam odamga bering. Admin o‘zi push qila oladi.
3. Actions: `on: push` da `main`ga to‘g‘ridan-to‘g‘ri commitni aniqlab issue ochish — **to‘xtatmaydi**.
4. Public “gate” repo: kod private, CI public mirror da — odatda arzimaydi.
5. Kerak bo‘lsa **Pro $4** — bitta shaxsiy repo uchun eng arzon “required review + required check”.

`CODEOWNERS` faylini yozish mumkin; Free private da u **avtomatik required review bermaydi**.

---

## 8. Xavfsizlik

| Funksiya | Public Free | Private Free | Qayerda pullik |
|---|---|---|---|
| Dependabot alerts | Ha | **Ha** | — |
| Dependabot security + version updates | Ha | **Ha** (pricing) | — |
| Dependency graph | Ha | Yoqish mumkin (Admin) | — |
| Dependency review (PR diff) | Ha | Yo‘q | Code Security |
| CodeQL / code scanning | Ha | Yo‘q | Team/Enterprise + Code Security |
| Secret scanning + push protection | Ha | Yo‘q | Secret Protection |
| Security overview | — | Yo‘q | Team+ |
| Custom Dependabot triage | — | Yo‘q | Code Security |

Manba: [plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans), [Cannot enable CodeQL in private](https://docs.github.com/en/code-security/reference/code-scanning/troubleshoot-analysis-errors/private-repository-enablement), [About Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security).

**Amaliy Free private:**

1. Dependabot alerts + security updates ni yoqing.
2. Secret ni GitHub secret scanning o‘rniga **pre-commit** (`gitleaks`) + Actions job — merge ni yopmaydi, lekin signal beradi.
3. `.env`, kalit, dump ni repo ga umuman qo‘ymang; history dan `git filter-repo`.
4. Public qilishni rejalashtirsangiz — secret scanning o‘sha zahoti yoqiladi. Private → public qilishdan oldin `gitleaks` o‘tkazing.

---

## 9. Codespaces, Copilot, “AI” mahsulotlar

### Codespaces

| | Free shaxsiy |
|---|---|
| Core-soat / oy | 120 |
| Saqlash / oy | 15 GB |
| Free org | **Kiritilmagan** |

Private repo da Read ham codespace ochishi mumkin; secretli codespace — Write+.

**Amaliy:** 120 soat ≈ 2 vCPU da ~60 soat. Og‘ir image tez yeydi. Org Free da Codespaces umuman kvotasiz — shaxsiy hisobda ochiladi yoki Team.

### Copilot Free (GitHub rejasidan alohida)

[Plans for Copilot](https://docs.github.com/en/copilot/get-started/plans), [licenses](https://docs.github.com/en/billing/concepts/product-billing/github-copilot-licenses):

- ~**2000 completion** / oy + cheklangan chat/agent
- Model: faqat **auto**
- Org/enterprise a’zosiga berilmaydi (ularning Copilot’i boshqacha)
- Policy, audit, file exclusion, indemnification — **yo‘q**
- Cloud agent — asosan **pullik** Copilot
- Code review private da Actions daqiqasini yeydi

**2026-04-24:** Copilot Free/Pro/Pro+ o‘zaro ta’sir ma’lumoti (prompt, snippet, output) default da treningga ketishi mumkin — **opt-out** kerak: Copilot settings → “Allow GitHub to use my data for AI model training” = Disabled. Private repo **diskdagi** kod treningga kirmaydi; siz yuborgan kontekst kirishi mumkin. ([changelog 2026-03-25](https://github.blog/changelog/2026-03-25-updates-to-our-privacy-statement-and-terms-of-service-how-we-use-your-data/))

### GitHub Models — o‘lik

**2026-07-30** playground, catalog, inference API, BYOK **butunlay yopilgan**. O‘rniga Microsoft Foundry yoki Copilot. ([changelog](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/))

Eski maqola “GitHub Models bepul API” desа — **eskirgan**.

---

## 10. Issues, Projects, Discussions, wiki, insights

| | Free private |
|---|---|
| Issues, PR, draft PR | Ha (draft pricing da Team ostida marketing; downgrade yo‘qotish ro‘yxatida yo‘q) |
| Bir nechta assignee | **Yo‘q** |
| Bir nechta required reviewer | **Yo‘q** |
| Autolink (Jira) | **Yo‘q** |
| Projects (v2) | Ha |
| Discussions | Ha |
| Wiki | **Yo‘q** (public da bor) |
| Insights: Pulse, traffic, contributors… | **Yo‘q** |
| Releases + binary | Ha (katta fayl LFS limiti bilan) |
| Issue fields (org, 2026-07 GA) | Free **org** da ha; `Priority`, `Effort`, sanalar |

Issue/PR edit tarixi: 100 yozuv (2026-07, barcha rejalar).

**Amaliy:** wiki o‘rniga `docs/` + public docs repo yoki Notion. Bir nechta assignee o‘rniga `Triage` + comment. Autolink o‘rniga PR template da ticket URL.

---

## 11. Git, LFS, hajm

Barcha rejalar (repo health):

| Cheklov | Qiymat |
|---|---|
| Brauzerdan fayl | 25 MiB |
| `git push` ogohlantirish | 50 MiB |
| Blok | **100 MiB** |
| Tavsiya repo | < 1 GB (5 GB dan oshmasin) |

**Git LFS (Free):** 10 GB saqlash + 10 GB bandwidth / oy. ([usage](https://docs.github.com/en/billing/reference/product-usage-included))

**Amaliy:** video, dump, model ni LFS/git ga qo‘ymang — R2/S3/Release. SQL dump Git uchun mos emas (rasmiy ogohlantirish).

---

## 12. Kam ma’lum, lekin Free private da foydali

1. **Self-hosted runner = cheksiz CI** — kvotani aylanib o‘tishning rasmiy yo‘li.
2. **Action allowlist (2026-02)** — `actions/*` va o‘z org actionlarigina. Supply-chain uchun bepul.
3. **`$/` same-repo action (2026-07)** — private action ni alohida public qilmasdan chaqirish.
4. **Cron `timezone:` (2026-03)** — `Asia/Tashkent`. UTC hisoblamang.
5. **Budget + 90%/100% email** — karta bo‘lsa ham “stop at limit”.
6. **Packages + `GITHUB_TOKEN`** — transfer 1 GB ni yemaydi.
7. **Cache 10 GB / repo** — artifact hovuzidan alohida; dependency cache shu yerda.
8. **Dependabot private da** — ko‘pchilik “faqat public” deb o‘ylaydi; alerts Free private da bor.
9. **Public + private juftlik:** ochiq docs/CI kvotasiz, yopiq kod.
10. **Outside collaborator** — org a’zoligisiz bitta repo.
11. **Fine-grained PAT** — repo + ruxsat kesimi; classic `repo` o‘rniga.
12. **2FA enforcement** + deploy key ogohlantirishi: kalit egasi org dan chiqsa ham repo ochiq qoladi.
13. **Student Developer Pack** — shaxsiy Pro (protection, Pages private repodan, wiki).
14. **Issue fields (Free org, 2026)** — label o‘rniga typed `Priority`.
15. **AGENTS.md** — Copilot review o‘qiydi (2026-06); review o‘zi pullik/daqiqa yeyishi mumkin.
16. **Repo secret vs environment:** Free private da faqat repo/org secret — prod kalitini `Write` dan yashira olmaysiz. Kam odamga `Write` bering.
17. **GitHub Community Support** — ticket emas, forum. Account/abuse — [support.github.com](https://support.github.com/).
18. **Trade controls:** AQSh sanksiya mintaqasida private repo xizmati cheklanishi mumkin; public qoladi.

---

## 13. 2025–2026 da eski xotira adashtiradigan narsalar

| Eski tasavvur | 2026 holat |
|---|---|
| Private collaborator ≤ 3 | **Cheksiz** (2020, hali ham) |
| Actions: Windows 2×, macOS 10× | **USD/daqiqa**; nisbat ~1.7× / ~10.3× |
| GitHub Models bepul API | **2026-07-30 yopilgan** |
| Rulesets hamma joyda | Private da **Pro/Team+** |
| Environment secret private Free da | **Yo‘q** |
| Pages private repo + sayt yopiq | Repo Pro+; **sayt ochiq**; yopiq sayt = Enterprise |
| CodeQL private Free | **Yo‘q** |
| Copilot interaction xususiy | 2026-04-24 dan Free/Pro **opt-out** |
| Allowlist faqat Enterprise | **2026-02 dan barcha rejalar** |
| Secret scanning private “end i bepul” | **Yo‘q** — Secret Protection |

---

## 14. Amaliy playbook — Free + private

**Minimal (bitta odam yoki 2–3 kishi):**

1. Private repo, 2FA, Dependabot yoqilgan.
2. CI: `ubuntu-latest` yoki self-hosted; artifact retention qisqa.
3. Secret: faqat repo secrets; `.env` gitignore.
4. `main`ga to‘g‘ridan-to‘g‘ri push — kelishuv; Admin kam.
5. Budget: Actions/Packages “stop at included”.

**Kichik jamoa (org Free):**

1. Org oching, team + outside collaborator.
2. Base permission `Read` yoki `None`; Write ni team orqali.
3. Issue fields: Priority / Target date.
4. Docs ni **public** repo yoki tashqi host.
5. CI og‘ir bo‘lsa — self-hosted (RankWant allaqachon shu yo‘lda).

**Qachon Pro ($4) yoki Team ($4/user):**

- `main`ga required review + required CI **shart**
- Private repodan Pages (sayt ochiq qoladi)
- Environment secret (staging/prod ajratish)
- Wiki, traffic insights, bir nechta assignee
- CODEOWNERS ni **majburiy** qilish

**Qachon Team + Code/Secret Protection:**

- Private da CodeQL, push protection, dependency review

**Qilmang:**

- Private repo ni “CI bepul bo‘lsin” deb public qilish — secret tarixi ochiladi
- macOS hosted ni Free kvotada default qilish
- PAT bilan self-hosted dan Packages yutish
- GitHub Models endpointiga tayanib qolish

---

## 15. Tezkor matritsa: private Free

| Funksiya | Holat |
|---|---|
| Cheksiz repo / collaborator | ✅ |
| Issues, PR, Projects, Discussions, Releases | ✅ |
| Actions hosted | ✅ 2000 daq, 20 parallel |
| Actions self-hosted | ✅ cheksiz daqiqa |
| Packages private | ✅ 500 MB + 1 GB out |
| Dependabot alerts/updates | ✅ |
| Repo secrets/variables | ✅ |
| Action allowlist | ✅ (2026) |
| Codespaces (shaxsiy) | ✅ 120 soat / 15 GB |
| Copilot Free | ✅ cheklangan |
| Branch protection / required review | ❌ |
| Rulesets / push rules | ❌ |
| Pages | ❌ |
| Wiki / insights | ❌ |
| Environment + env secret | ❌ |
| CodeQL / secret scanning | ❌ |
| Multiple assignee / autolink | ❌ |
| Email support | ❌ (Community) |

---

## Manbalar

- [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans) — tekshirilgan 2026-09-17
- [Product usage included](https://docs.github.com/en/billing/reference/product-usage-included)
- [FAQ about changes to GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/faq-about-changes-to-githubs-plans) (2020 asos, collaborator)
- [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Actions runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)
- [Actions limits](https://docs.github.com/en/actions/reference/limits)
- [Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages)
- [What is GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) · [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Managing environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [Repository roles](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-repository-roles/repository-roles-for-an-organization)
- [About GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)
- [Cannot enable CodeQL in a private repository](https://docs.github.com/en/code-security/reference/code-scanning/troubleshoot-analysis-errors/private-repository-enablement)
- [Plans for GitHub Copilot](https://docs.github.com/en/copilot/get-started/plans)
- [About large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- Changelog: [Actions 2026-02-05](https://github.blog/changelog/2026-02-05-github-actions-early-february-2026-updates/), [Actions 2026-03-19](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/), [Privacy/Copilot 2026-03-25](https://github.blog/changelog/2026-03-25-updates-to-our-privacy-statement-and-terms-of-service-how-we-use-your-data/), [Issue fields GA 2026-07-02](https://github.blog/changelog/2026-07-02-issue-fields-are-now-generally-available/), [Models retired 2026-07-30](https://github.blog/changelog/2026-07-30-github-models-is-now-retired/)
- [github.com/pricing](https://github.com/pricing) — marketing; reja farqi uchun Docs ustun
