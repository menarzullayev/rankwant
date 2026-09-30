# AI agentlarining korxona ilovalaridagi rivojlanish tendentsiyalari va ularning RankWant platformasi talablariga ta'siri

**Sana:** 2026-09-29
**Til:** o'zbek (lotin)
**Ijro rejimi:** To'liq tadqiqot (6 bo'lim, har biri ko'rikdan o'tgan)
**Auditoriya:** RankWant loyihasi egasi (texnik asoschi)

> **Yozuv maqomi:** bu `docs/research/` dagi sanali yozuv — **tirik hujjat emas**,
> 2026-09-29 holatidagi tahlil. Amaldagi qoidalar `docs/01`–`docs/10` va
> [ADR](../../07-adr/) larda; bu matn ular bilan zid kelsa, o'sha bo'limlar ustun.
> Hujjat ataylab **o'zbek tilida** (loyihaning boshqa `docs/` hujjatlari
> inglizcha) — shu sababli alohida `research/` yozuvi sifatida saqlanadi.
> 6-bo'limdagi RankWant faktlari loyiha hujjatlaridan olingan va tashqi
> tekshiruvdan o'tmagan; qolgan bo'limlar havola qilingan manbalarga tayanadi.

---

## Mundarija

- [Kirish](#kirish)
- [1. Korxonalarda AI agentlarini joriy etishning asosiy omillari](#1-korxonalarda-ai-agentlarini-joriy-etishning-asosiy-omillari)
- [2. Sohalar kesimida AI agentlarining eng keng tarqalgan qo'llanish holatlari](#2-sohalar-kesimida-ai-agentlarining-eng-keng-tarqalgan-qollanish-holatlari)
- [3. Korxona AI agentlarining texnik va tashkiliy muammolari](#3-korxona-ai-agentlarining-texnik-va-tashkiliy-muammolari)
- [4. Yetakchi platformalar va sotuvchilarning raqobat manzarasi](#4-yetakchi-platformalar-va-sotuvchilarning-raqobat-manzarasi)
- [5. AI agentlar tendentsiyalarining keyingi 3–5 yildagi rivojlanish bashoratlari](#5-ai-agentlar-tendentsiyalarining-keyingi-35-yildagi-rivojlanish-bashoratlari)
- [6. RankWant platformasiga bog'liqlik: arxitektura, foydalanuvchi ehtiyojlari va raqobat tahlili](#6-rankwant-platformasiga-bogliqlik-arxitektura-foydalanuvchi-ehtiyojlari-va-raqobat-tahlili)
- [Xulosa](#xulosa)
- [Adabiyotlar](#adabiyotlar)
- [Metodologiya va cheklovlar](#metodologiya-va-cheklovlar)

---

## Kirish

Sun'iy intellekt (SI) agentlari — o'z-o'zidan rejalashtiruvchi, tashqi vositalarni chaqiruvchi va ko'p bosqichli vazifalarni avtonom bajaruvchi katta til modellariga (LLM) asoslangan tizimlar — 2024–2026 yillarda korxona IT kun tartibining markaziga ko'tarildi. Bu siljish tasodifiy emas: model inferensiyasi narxining bir necha yuz baravar arzonlashuvi ([Stanford HAI, AI Index 2025](https://hai.stanford.edu/ai-index/2025-ai-index-report)), tayyor vendor platformalarining yetilishi va Model Context Protocol (MCP) kabi ochiq standartlarning shakllanishi ([Model Context Protocol](https://modelcontextprotocol.io/)) agentlarni tajribadan amaliyotga o'tkazdi. Shu bilan birga bozor jiddiy ikkilanishni boshdan kechirmoqda: bir tomondan korxonalarning aksariyati agentlarni joriy qilmoqda va byudjetlarini oshirmoqda ([PwC, AI Agent Survey](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html)), ikkinchi tomondan esa sinov loyihalarining katta qismi kutilgan moliyaviy natijani bermayapti ([MIT NANDA, GenAI Divide](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf)).

RankWant — o'zbek tilidagi raqobatbardosh dasturlash (CP) va olimpiada platformasi — uchun bu tendentsiyalar bevosita strategik ahamiyatga ega. Platforma hozircha SI/LLM funksiyalaridan foydalanmaydi, bu esa mahsulot rivojlanishidagi eng katta bo'shliqlardan biri hisoblanadi. Shu bois ushbu hisobot AI agentlar bozorining joriy holatini, texnik va tashkiliy to'siqlarini hamda kelgusi 3–5 yillik bashoratlarini RankWant nuqtai nazaridan tahlil qiladi.

Hisobot olti bo'limdan iborat. Birinchi bo'lim agentlar joriy etilishini tezlashtirgan asosiy omillarni (narx, standartlar, raqobat va rahbariyat bosimi) ko'rib chiqadi. Ikkinchi bo'lim sohalar kesimida eng keng tarqalgan qo'llanish holatlarini tizimlashtiradi. Uchinchi bo'lim korxona agentlarining ishonchlilik, integratsiya, xavfsizlik va governance bilan bog'liq muammolarini ochib beradi. To'rtinchi bo'lim yetakchi platformalar va sotuvchilar raqobat manzarasini, beshinchi bo'lim esa kelgusi bashoratlarni taqdim etadi. Oltinchi bo'lim barcha topilmalarni RankWant platformasi uchun amaliy tavsiyalarga aylantiradi.

Dastlabki topilmalar uch nuqtada jamlanadi. Birinchidan, agentlar tez sur'atda korxona jarayonlariga kirib bormoqda — Gartner korxona ilovalarining 40% 2026-yilga kelib vazifaga xos agentlarga ega bo'lishini prognoz qilmoqda ([Gartner, 2025-08-26](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)), LangChain ma'lumotlariga ko'ra esa respondentlarning 57,3% agentlarni productionda ishlatmoqda ([LangChain, State of Agent Engineering](https://www.langchain.com/state-of-agent-engineering)). Ikkinchidan, muvaffaqiyat texnologiyaning o'ziga emas, balki ma'lumot sifati, integratsiya va governance yetukligiga bog'liq. Uchinchidan, RankWant uchun eng istiqbolli nisha — o'zbek tilidagi CP platformasi uchun AI mentor va lokal AI feedback kabi hali egallanmagan yo'nalishlardir.

---

## 1. Korxonalarda AI agentlarini joriy etishning asosiy omillari

**Tezis.** 2024–2026-yillarda korxonalarning AI agentlarini joriy etish sur'ati keskin tezlashdi. Bu "texnologiya qiziqarli bo'lgani uchun" emas, balki bir necha o'lchanadigan iqtisodiy va tashkiliy omilning bir vaqtda pishib yetilishi natijasidir: model narxining keskin pasayishi, tayyor platformalarning paydo bo'lishi, integratsiya standartlashuvi (xususan MCP), raqobat va rahbariyat bosimi hamda bozor hajmining tez o'sishi. Shu bilan birga, omillar mavjud bo'lsa-da, loyihalarning katta qismi hali productionga chiqmayapti — bu qarama-qarshilikni 3-bo'lim batafsil ochadi.

### 1.1. Nima uchun aynan hozir — makro sabablar

Bozor hajmining o'zi asosiy makro signaldir. [MarketsandMarkets](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp) hisobiga ko'ra, global AI agentlar bozori 2025-yildagi 7,84 mlrd AQSh dollaridan 2030-yilga kelib 52,62 mlrd dollargacha o'sadi, ya'ni yillik o'sish sur'ati (CAGR) 46,3%. Bu shunchaki katta raqam emas — u investorlar va sotuvchilar uchun "endi kirish vaqti" degan signal bo'lib xizmat qiladi.

Ikkinchi makro omil — AI'ning biznesga kirib borishining umumiy tezlashuvi. [Stanford AI Index 2025](https://hai.stanford.edu/ai-index/2025-ai-index-report) ma'lumotlariga ko'ra, 2024-yilda korxonalarning 78%i AI'dan foydalangan, bu 2023-yildagi 55%ga nisbatan sezilarli sakrash. Ya'ni agentlar allaqachon "iliq" muhitga — AI infratuzilmasi, ma'lumot va tajriba mavjud bo'lgan korxonalarga kirmoqda.

Uchinchi omil — talab tomonidagi bosim. [Deloitte](https://www.deloitte.com/us/en/about/press-room/deloitte-technology-media-telecom-2025-predictions.html) prognoziga ko'ra, GenAI'dan foydalanuvchi korxonalarning 25%i 2025-yilda AI agentlarini joriy etadi, bu ko'rsatkich 2027-yilga kelib 50%ga yetadi. Bu — "kutish va ko'rish" strategiyasining iqtisodiy jihatdan qimmatlashib borishini anglatadi.

### 1.2. Asosiy joriy etish omillari (drivers)

**1.2.1. Model narxining keskin pasayishi.** Bu, ehtimol, eng fundamental texnik-iqtisodiy omildir. Stanford AI Index 2025 ma'lumotiga ko'ra, GPT-3.5 darajasidagi tizim uchun inference narxi 2022-yil noyabrdan 2024-yil oktabrgacha **280 martadan ortiq** arzonlashdi ([Stanford AI Index 2025](https://hai.stanford.edu/ai-index/2025-ai-index-report)). LangChain so'rovida ham "xarajat" to'sig'i o'tgan yilga nisbatan pasaygani qayd etilgan ([LangChain](https://www.langchain.com/state-of-agent-engineering)). Ya'ni agentlarni keng ko'lamda ishlatish iqtisodiy jihatdan endi mumkin bo'ldi.

**1.2.2. Xarajat tejamkorligi va mehnat unumdorligi.** [PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html) 2025-yil may oyida 300 dan ortiq AQSh rahbarini so'rov qilib, agentlarni joriy qilayotganlarning **66%i unumdorlik o'sishini**, **57%i xarajat tejamkorligini**, 55%i tezroq qaror qabul qilishni qayd etgan. Bu — agentlar "va'da" emas, o'lchanadigan natija bera boshlaganini ko'rsatadi.

**1.2.3. Vendor tayyorligi (tayyor platformalar).** Endi korxonalar agentlarni noldan qurishi shart emas. [Salesforce](https://www.salesforce.com/news/press-releases/2026/02/25/fy26-q4-earnings/) hisobotiga ko'ra, Agentforce ARR 800 mln dollarga yetdi (+169% yillik o'sish) va 29 000 dan ortiq kelishuv yopildi. [Microsoft](https://www.microsoft.com/investor/reports/ar25/index.html) esa 2025-moliya yilida Copilot oilasi bo'ylab 100 milliondan ortiq oylik faol foydalanuvchiga erishdi. Tayyor mahsulotlar "vaqt-to-qiymat" masofasini qisqartirdi.

**1.2.4. Integratsiya osonlashuvi (MCP va protokollar).** [Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) 2025-yil 9-dekabrda Model Context Protocol (MCP)ni Linux Foundation qoshidagi Agentic AI Foundation'ga o'tkazdi. O'sha paytda ekotizimda **10 000 dan ortiq faol ommaviy MCP server** va **oyiga 97 mln dan ortiq SDK yuklab olish** mavjud edi. MCP'ni ChatGPT, Gemini, Microsoft Copilot va VS Code qabul qilgani uni de-fakto standartga aylantirdi — bu esa agentlarni korporativ tizimlarga ulash xarajatini keskin kamaytiradi.

**1.2.5. Raqobat bosimi va rahbariyat talabi.** PwC so'rovida respondentlarning **46%i** agentlarni joriy etishda raqobatchilardan orqada qolishdan xavotir bildirgan; 73%i agentlardan foydalanish 12 oy ichida "sezilarli raqobat ustunligi" berishiga ishonadi ([PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html)). Ya'ni joriy etish ko'pincha "imkoniyat" emas, "majburiyat" sifatida qaraladi.

**1.2.6. Ishchi kuchi va tashkiliy omillar.** [BCG va MIT Sloan Management Review](https://www.bcg.com/press/18november2025-agentic-ai-blurs-line-tool-teammate) 2025-yil noyabrdagi 2 102 rahbarni qamrab olgan tadqiqotida rahbarlarning **76%i** agentik AI'ni "vosita"dan ko'ra ko'proq "hamkasb" sifatida ko'rishini qayd etdi; 44%i uni yaqin orada joriy etishni rejalashtirmoqda.

### 1.3. Joriy etish darajasi va byudjet dinamikasi

Joriy etish darajasi bo'yicha eng ishonchli raqamlar:

- [LangChain](https://www.langchain.com/state-of-agent-engineering) (1 340 respondent, 2025-yil noyabr–dekabr): respondentlarning **57,3%i** agentlarni productionda ishlatadi (o'tgan yili 51%), yana 30,4%i faol ishlab chiqmoqda. 10 000+ xodimli tashkilotlarda bu ko'rsatkich **67%**ga yetadi.
- [PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html): rahbarlarning **79%i** agentlar allaqachon joriy qilinayotganini aytdi; **88%i** agentik AI tufayli AI byudjetlarini oshirishni rejalashtirmoqda (to'rtdan biri 26%dan ko'proq o'sishni ko'zlaydi).
- [BCG/MIT SMR](https://www.bcg.com/press/18november2025-agentic-ai-blurs-line-tool-teammate): kompaniyalarning **35%i** allaqachon agentik AI'dan foydalanmoqda, yana **44%i** yaqin orada joriy etishni rejalashtirmoqda.

> **Izoh:** bu uch raqam bir-biriga zid emas — ular turli namuna va turli savolga asoslanadi ("productionda ishlatadi" ≠ "joriy qilmoqda" ≠ "foydalanmoqda").

### 1.4. Qaysi omillar eng kuchli

Mavjud dalillar asosida ustuvorlikni quyidagicha tartiblash mumkin:

1. **Model narxining pasayishi** — eng fundamental, chunki qolgan barcha omillarning iqtisodiy asosini yaratadi (280 martalik arzonlashuv, [Stanford AI Index](https://hai.stanford.edu/ai-index/2025-ai-index-report)).
2. **Vendor tayyorligi va integratsiya standartlashuvi** — MCP va tayyor platformalar "vaqt-to-qiymat" masofasini qisqartirdi ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), [Salesforce](https://www.salesforce.com/news/press-releases/2026/02/25/fy26-q4-earnings/)).
3. **Raqobat va rahbariyat bosimi** — joriy etishni tezlashtiruvchi "majburiyat" omili ([PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html)).

Bu — tahliliy tartiblash (fikr), chunki manbalar omillarni alohida-alohida o'lchaydi, yagona reyting bermaydi.

### 1.5. "Nima ishlamayapti" — 3-bo'limga ko'prik

Omillar kuchli bo'lsa-da, qiymatga aylanish darajasi past. [MIT NANDA "GenAI Divide"](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf) hisobotiga ko'ra, korxonalar GenAI'ga 30–40 mlrd dollar sarflagan bo'lsa-da, **95% tashkilot o'lchanadigan P&L natijasiga erishmadi**. [Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) esa 2027-yil oxirigacha agentik loyihalarning **40%dan ortig'i** bekor qilinishini prognoz qiladi. [VentureBeat Pulse Research](https://venturebeat.com/resources/agentic-orchestration-enterprise-ai-organizations-have-a-deployment-problem-not-a-platform-problem-and-most-are-calling-chatbots-agents) (n=101) so'rovida respondentlarning **71%i** "agentlar"ning to'rtdan bir qismi yoki undan kami haqiqiy orkestratsiya ekanini tan oladi ("chatbot tuzog'i"). Bu ziddiyat — **joriy etish omillari** kuchli, lekin **qiymatga aylantirish** zaif ekanini ko'rsatadi.

**Kichik xulosa.** Korxonalar agentlarni aynan hozir joriy qilmoqda, chunki (a) iqtisodiy to'siq — model narxi — keskin tushdi, (b) sotuvchilar tayyor va integratsiyalanuvchi platformalarni yetkazib berdi, (c) raqobat va rahbariyat bosimi "kutish"ni qimmatlashtirdi. Bu omillar joriy etish **sur'atini** tushuntiradi, lekin **muvaffaqiyatini** kafolatlamaydi — bu bo'linish 3-bo'limning predmeti.

---

## 2. Sohalar kesimida AI agentlarining eng keng tarqalgan qo'llanish holatlari

**Tezis.** Qo'llanish holatlarining taqsimoti tasodifiy emas: agentlar birinchi navbatda **yuqori hajmli, takrorlanuvchi va aniq tekshiriladigan** vazifalarga jalb qilinmoqda.

### 2.1. Umumiy reyting

[LangChain](https://www.langchain.com/state-of-agent-engineering) (1 340 respondent): eng keng tarqalgan — **mijozlarga xizmat (26,5%)**, **tadqiqot/ma'lumot tahlili (24,4%)**, **ichki ish oqimlari (18%)**. 10 000+ xodimli yirik korxonalarda birinchi o'rinda **ichki samaradorlik (26,8%)** turadi.

### 2.2. Sohalar kesimi

**Moliya va bank.** JPMorgan kuniga **450 dan ortiq AI agent/use-case** ishlatadi, o'rtacha **171% ROI** (12 keys) ([AI Intel Report](https://www.aiintelreport.com/ai-agents/jpmorgan-chase-ai-agents-171-roi) — *ikkilamchi manba, sanoat blogi*). COiN platformasi yiliga **12 000 kredit shartnomasini** qayta ishlab, **360 000 advokat-soatini** bo'shatadi, xatoni **80%ga** kamaytiradi. Yillik texnologiya byudjeti ~18 mlrd dollar (kompaniya ma'lumotlariga asosan; [JPMorganChase — Annual Report](https://www.jpmorganchase.com/ir/annual-report)).

**Chakana savdo va e-commerce.** Klarna'ning OpenAI asosidagi yordamchisi murojaatlarning **~2/3 qismini** hal qiladi ([Klarna rasmiy press-relizi](https://www.klarna.com/international/press/klarna-ai-assistant-handles-two-thirds-of-customer-service-chats-in-its-first-month/)). O'sha press-relizda yordamchi **700 ta to'liq stavkali agent** ishini bajarishi va 2024-yilda foydani ~$40 mln yaxshilashi kutilgani qayd etilgan; ba'zi ikkilamchi manbalarda **$60 mln / 853 FTE** raqamlari uchraydi — farq hisobot davri va metodologiyaga bog'liq ([AI Intel Report](https://aiintelreport.com/enterprise-ai/klarna-ai-agent-853-ftes-savings) — *ikkilamchi manba*). Oyiga **2,3 mln suhbat**, hal qilish vaqti **11→2 daqiqa**, takroriy murojaat **-25%** ([cc4.life](https://cc4.life/ai-stories/the-support-replacement/) — *ikkilamchi manba*). **Muhim nuance:** Klarna keyinchalik **gibrid modelga** qaytgan; bosh direktor "xarajat asosiy mezon bo'lgani sifatni pasaytirdi" deb tan olgan. [Salesforce](https://www.salesforce.com/agentforce/agentic-enterprise-index/) Agentic Enterprise Index ma'lumotiga ko'ra, **bayram mavsumidagi cho'qqilarda iste'mol sohasida** agentlardan foydalanish **4 baravar yuqori o'sish sur'atini** ko'rsatdi.

**Ishlab chiqarish va sanoat.** General Mills Palantir bilan qurgan ELF platformasi orqali **$20 mln+ tejash** qildi; tizim kuniga **5 000+ yukni** real vaqtda optimallashtiradi, tavsiyalarning **70% avtomatik qabul** qilinadi ([AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/24/general-mills-always-on-supply-chain-ai-5000-daily-shipments) — *ikkilamchi manba*). Marshrutlarni optimallashtirish hisobiga **15 000 tonnadan ortiq CO₂** kamaytirilgan.

**IT va dasturiy ta'minot.** [GitHub/Accenture tadqiqotida](https://github.blog/news-insights/research/research-quantifying-github-copilots-impact-in-the-enterprise-with-accenture/) 1 000+ dasturchi ishtirokida Copilot vazifalarni **55% tezroq** bajardi, PR sikli **9,6→2,4 kun (-75%)** qisqardi, muvaffaqiyatli build'lar **+84%** oshdi. Duolingo muhandislari yangi kod bazasiga **25% tezroq** moslashdi (yangi repo/framework'ga kirishganlarda; tajribalilarida ~10%) va code review turnaround **3 soat→1 soat (-67%)** ([GitHub rasmiy customer story](https://github.com/customer-stories/duolingo)).

**Sog'liqni saqlash.** 180+ tibbiyot tashkiloti ma'lumotlariga ko'ra, AI asosidagi **oldindan tasdiqlash** jarayonida vaqt **61% qisqardi** (4,2→1,6 soat); hujjatlarni ko'rib chiqish **83%**, so'rov loyihalash **73%** tezlashdi; birinchi urinishda tasdiqlash darajasi **64%→72%** ([Cevi](https://cevi.ai/blog/prior-auth-industry-data) — *vendor hisoboti*). Har 1 000 so'rov/oy uchun **2,1 FTE** tejaladi, o'rtacha qoplanish muddati — **18 oy**. Salesforce ma'lumotlarida sog'liqni saqlash sohasida agentlardan foydalanish hajmi yillik **19 baravar** oshgan ([Salesforce Agentic Enterprise Index](https://www.salesforce.com/agentforce/agentic-enterprise-index/)).

**Xizmat ko'rsatish va ITSM.** ServiceNow AI yordamida tashkilotlar tiketlarning **30–60%ini** odamga yetmasdan hal qilishi mumkin; real misollarda moliyaviy firma **50%**, tibbiyot provayderi **40%**, ishlab chiqarish kompaniyasi **30%** kamaytirgan ([Rede Consulting](https://www.rede-consulting.com/post/unlocking-servicenow-ai-strategies-to-deflect-30-60-of-support-tickets)). **2026-yilgi "State of AI in IT" hisobotida tashkilotlarning 74%i** kamida bitta xizmat boshqaruvi jamoasida AI ishlatadi ([ITSM.tools](https://itsm.tools/state-of-ai-in-it-2026/)). ServiceNow o'zining ichki qo'llab-quvvatlashida ish oqimining **37%ini** avtomatlashtirgan ([ServiceNow](https://www.servicenow.com/customers/now-on-now-support-ai.html)). Salesforce Agentforce mijozlarida suhbatlarning **7/10 qismi avtonom** hal qilinadi, eskalatsiya **32%**.

**Ta'lim.** *Scientific Reports* jurnalida 2025-yil iyun oyida chop etilgan Harvard randomizatsiyalangan nazorat tadqiqoti AI repetitorni jonli faol o'qitish bilan solishtirib, AI guruhi **0,73–1,3 standart og'ish** darajasida yuqori natija berganini va materialni **18% tezroq** (60→49 daqiqa) tugatganini ko'rsatdi ([AgentMarketCap — Education](https://agentmarketcap.ai/blog/2026/04/06/education-ai-agents-khanmigo-chegg-edtech-agentic-learning)). Khanmigo Nyu-Hempshir'da **40 000 o'quvchi va 5 000 o'qituvchi**ga yetib bordi; Duolingo bir yilda **148 yangi til kursini** yaratib, **$1,04 mlrd** daromadga (+39% YoY) erishdi. Muhim xulosa: **inson+AI gibrid** modeli faqat-AI modelidan yaxshiroq ishlaydi.

**Huquq.** A&O Shearman 43 yurisdiksiyada Harvey AI'ni joriy etib, xodimlar haftasiga **2–3 soat** tejaydi, shartnomalarni ko'rib chiqish **30%** tezlashdi, **2 000 advokat** undan kunlik foydalanadi ([Velocity AI Partners](https://insights.velocityaipartners.co/case-studies/ao-shearman-harvey-ai-legal)).

**Telekom.** Oliver Wyman ma'lumotlariga ko'ra, telekomda AI xarajatlarni **30–40%** kamaytiradi, qo'ng'iroqdan keyingi ish **40–50%** qisqaradi; AI chatbot muloqoti narxi **$0,25–$0,50**, inson bilan esa **$3–$6** ([Kommunicate](https://www.kommunicate.io/blog/ai-customer-service-in-telecom/)).

### 2.3. Umumiy naqshlar

Agentlar birinchi navbatda **4 mezonga** javob beradigan vazifalarga beriladi: **takrorlanadi, bir nechta tizimni qamraydi, aniq qadamlarga bo'linadi va o'lchanadigan natijaga ega** ([Coworker AI](https://coworker.ai/blog/ai-agent-use-cases)). Aksincha, har safar o'zgaradigan qadamlar, qoidaga sig'maydigan mulohaza, qaytarib bo'lmaydigan yuqori xatar yoki agent yeta olmaydigan ma'lumotlar — agentga berilmaydi. [AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/11/gartner-15-percent-agent-autonomy-forecast-2026): 2028-yilga kunlik ish qarorlarining **15%i** avtonom qabul qilinadi; xarid jarayonlarining **60–70%i** avtomatlashtirilishi mumkin.

**Kichik xulosa.** Sohalar kesimida agentlar eng avval **chegaralangan xatarlik va yuqori chastotali qarorlar** sohasida ildiz otmoqda: ITSM, xarid, kod review va mijoz xizmati. Bu yerda ular o'lchanadigan natija beradi; murakkab mulohaza, empatiya va qaytarib bo'lmaydigan qarorlar esa odamda qolmoqda.

---

## 3. Korxona AI agentlarining texnik va tashkiliy muammolari

**Tezis.** Korxonalarda AI agentlarning joriy etilishini to'sib turgan asosiy omil — model "aqli" emas, balki ishonchlilik, baholash metodologiyasi, integratsiya va boshqaruv (governance) yetukligidir. Dalillar shuni ko'rsatadiki, aksariyat loyihalar texnik jihatdan ishga tushsa-da, ishlab chiqarish bosqichida barqaror ishlamaydi. 1-bo'lim **nima uchun** joriy qilinishini ko'rsatgan bo'lsa, bu bo'lim **nima to'sqinlik qilishini** ochib beradi.

### 3.1. Texnik muammolar

**Ishonchlilik va xatolar to'planishi (error accumulation).** Ko'p bosqichli oqimlarda har bir qadamning kichik xatosi to'planib boradi. [AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/14/agent-compound-reliability-problem-multi-step-error-rates) hisob-kitobiga ko'ra, har bir qadam 95% aniqlikda bajarilsa, 20 bosqichli oqimning yakuniy muvaffaqiyati 0,95²⁰ ≈ **36%** ni tashkil etadi. Ya'ni "95% aniqlik" ishonchli tuyuladi, ammo amalda har uchinchi ishga tushirish muvaffaqiyatsiz bo'ladi. Bu nazariy emas: "Measuring Agents in Production" tadqiqoti ([arXiv:2512.04123](https://arxiv.org/abs/2512.04123)) 20 ta keys-stadi va 86 ta production tizimni o'rganib, **production agentlarining 68% inson aralashuvidan oldin ko'pi bilan 10 bosqich** bajarishini aniqladi.

**Kechikish (latency) va xarajat.** [LangChain](https://www.langchain.com/state-of-agent-engineering)ning 1 340 nafar mutaxassis ishtirokidagi so'roviga ko'ra, sifat (32%) productionga chiqishdagi eng katta to'siq bo'lsa, kechikish ikkinchi o'ringa ko'tarilib (20%) xarajatdan o'zib ketdi. Bu sifat-tezlik almashinuvi (trade-off) agentlar mijoz bilan bevosita ishlaganda keskinlashadi.

**Baholash (evaluation) muammosi.** Agentni "to'g'ri o'lchash" usuli hali yetuk emas. "Survey on Evaluation of LLM-based Agents" maqolasi ([arXiv:2503.16416](https://arxiv.org/abs/2503.16416)) baholashning beshta qatlamini tahlil qilib, asosiy bo'shliqlar **xarajat-samaradorlik, xavfsizlik va mustahkamlik (robustness)**ni baholashda hamda **mayda donador, miqyoslanuvchi** metodlarni ishlab chiqishda ekanini ko'rsatadi. Amalda production agentlarning **74% asosan inson baholashiga** tayanadi.

**Integratsiya murakkabligi.** [CIO.com / Tray.ai](https://www.cio.com/article/3829261/what-gives-it-leaders-pause-as-they-look-to-integrate-agentic-ai-with-legacy-infrastructure.html) so'roviga ko'ra, **42% korxona** agentlarni muvaffaqiyatli ishga tushirish uchun **8 yoki undan ortiq ma'lumot manbasiga** ulanishi kerak; 38% integratsiya murakkabligini kengaytirishdagi eng katta to'siq deb ataydi; 86% korxona mavjud texnologik stekini yangilashi kerak. Legacy tizimlarning deterministik va partiyaviy (batch) ishlashi agentlarning real vaqtli kutilmalariga ziddir.

**Xavfsizlik.** Agentga berilgan avtonomiya yangi hujum yuzasini yaratadi: prompt injection, asboblarni suiiste'mol qilish (tool abuse), ma'lumot sizib chiqishi, ruxsatlar va audit izi. Katta korxonalarda (2k+ xodim) xavfsizlik sifatdan keyin ikkinchi eng katta to'siq bo'lib, **24,9%** buni qayd etgan ([LangChain](https://www.langchain.com/state-of-agent-engineering)). *(Izoh: turli so'rovlarda bu ko'rsatkich farq qiladi — 24,9% LangChain, 28% VentureBeat, 34% PwC; uchta raqam ham turli savol va namunalarga tegishli.)*

**Kuzatuv (observability) va debugging.** LangChain'da 89% korxona kuzatuvni joriy qilgan, 62% to'liq tracing imkoniga ega; production agentlari bo'lganlarda bu 94%gacha chiqadi. Ammo kuzatuv baholashdan (evals) ancha oldinda — bu "ko'ramiz, lekin tizimli o'lchamaymiz" muammosini ko'rsatadi.

**Model lock-in va narx o'zgarishi.** Vendor boshqaruv qatlamini egallashidan qo'rqish kuchli: [VentureBeat](https://venturebeat.com/resources/agentic-orchestration-enterprise-ai-organizations-have-a-deployment-problem-not-a-platform-problem-and-most-are-calling-chatbots-agents) so'rovida **vendor lock-in eng katta xavotir (35%)** bo'lib, xavfsizlik va ruxsat cheklovlaridan (28%) o'zib ketdi; faqat 6% korxona nazoratni to'liq provayderga topshirishni kutadi, 88% esa nazoratni kamida qisman o'zida saqlashni istaydi.

### 3.2. Tashkiliy muammolar

**Governance yetukligi.** Bir nechta tahlilga ko'ra, **korxonalarning faqat ozchilik qismida (taxminan beshdan biri) avtonom agentlar uchun yetuk boshqaruv modeli** mavjud ([Imperialis Tech](https://imperialis.tech/en/blog/ai-governance-agentic-ai-maturity-gap-2026) — *sanoat tahlili, birlamchi so'rov emas*). Umumiy yetuklik bo'shlig'i mustaqil institutsional so'rovlarda ham tasdiqlanadi: [Gartner (2025-06-30)](https://www.gartner.com/en/newsroom/press-releases/2025-06-30-gartner-survey-finds-forty-five-percent-of-organizations-with-high-artificial-intelligence-maturity-keep-artificial-intelligence-projects-operational-for-at-least-three-years) va [Grant Thornton 2026 AI Impact Survey](https://www.grantthornton.com/services/advisory-services/artificial-intelligence/2026-ai-impact-survey).

**ROI isboti.** [MIT NANDA](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf): korxonalarning **95% generativ AI pilotlari** o'lchanadigan moliyaviy natija bermagan — bu $30–40 mlrd investitsiyaga qaramay. Uzilish pilot va production o'rtasida yaqqol ko'rinadi: **38% korxona pilot o'tkazayotgan bo'lsa-da, faqat 11% productionga chiqqan** (*ikkilamchi manbalar orqali; asli Deloitte 2025 tadqiqotiga borib taqaladi*) ([HumansAreObsolete](https://humansareobsolete.com/articles/agentic-ai-production-gap-11-percent-deployment-despite-38-percent-pilots-december-17-2025), [byteiota](https://byteiota.com/agentic-ai-production-gap-why-89-of-pilots-fail/)).

**Kadrlar va ko'nikma tanqisligi.** [PwC](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html) so'rovida rahbarlar eng katta to'siq sifatida kiberxavfsizlik va xarajatni (har biri 34%) ko'rsatadi; agentlarni ilovalar orasida ulash 19%, tashkiliy o'zgarish 17% va xodimlarning qabul qilishi 14% ro'yxatning quyi qismida. PwC buni "texnologiya emas, tafakkur va o'zgarishga tayyorlik to'sqinlik qilmoqda" deb izohlaydi. 67% rahbar agentlar 12 oy ichida mavjud rollarni tubdan o'zgartirishini aytadi.

**Mas'uliyat (accountability).** Aksariyat korxonalarda har bir agent uchun nomlangan "AI System Owner" yo'q, avtonomiya chegaralari va audit izi aniqlanmagan; bu mas'uliyatning tarqoqligi amalda javobgarlikning yo'qligiga olib keladi ([Imperialis Tech](https://imperialis.tech/en/blog/ai-governance-agentic-ai-maturity-gap-2026)).

**Regulyatsiya va compliance.** EU AI Act (Regulation (EU) 2024/1689) yuqori xavfli AI tizimlari uchun asosiy talablarni **2026-yil 2-avgustdan** to'liq kuchga kiritadi: xavfni boshqarish tizimi, texnik hujjatlar, inson nazorati, jurnal (log) yozuvi; buzilish uchun jarima **€15 mln yoki global aylanmaning 3%gacha** ([Hufeld](https://www.hufeld.com/en-gb/blog/eu-ai-act-august-2026-high-risk-ai-obligations)). Bu, xususan, HR, kredit va moliya kabi sohalarda agentlarni joriy etishga qo'shimcha yuklama qo'yadi.

**"Agent washing".** Bozor shov-shuvi haqiqiy imkoniyatni ko'mib tashlaydi. [Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) hisobicha, "agentic AI" taklif qilayotgan **minglab vendordan atigi ~130 tasi** haqiqiy agent qobiliyatiga ega (*Gartner hisoboti asosida; [Paperclipped](https://www.paperclipped.de/en/blog/agent-washing-agentic-ai-vendors/) — ikkilamchi sharh*). [VentureBeat](https://venturebeat.com/resources/agentic-orchestration-enterprise-ai-organizations-have-a-deployment-problem-not-a-platform-problem-and-most-are-calling-chatbots-agents) so'rovida korxonalarning **71%i** o'z "agentlarining" to'rtdan bir qismi yoki undan kami haqiqiy ko'p bosqichli oqim ekanini tan oladi — "chatbot tuzog'i".

**Loyihalarni bekor qilish.** Yuqoridagi omillar natijasida Gartner 2027-yil oxirigacha agentic AI loyihalarining **40%dan ortig'i** bekor qilinishini bashorat qiladi — sabablari: xarajatning nazoratdan chiqishi, noaniq biznes qiymati va zaif xavf nazorati ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)).

**Kichik xulosa.** Korxona agentlarini to'sib turgan muammolar model aqlining yetishmasligida emas, balki muhandislik ishonchliligi, o'lchash metodologiyasi, integratsiya va tashkiliy boshqaruv yetukligida jamlangan. Bu shuni anglatadiki, 40%lik bekor qilish to'lqini — mag'lubiyat emas, balki g'alla-kepakni ajratuvchi filtr: ishonchlilik va governance asoslarini bugun qurayotgan korxonalar keyingi bosqichda raqobat ustunligiga ega bo'ladi.

---

## 4. Yetakchi platformalar va sotuvchilarning raqobat manzarasi

**Tezis.** 2026-yilda korxona AI-agentlarini orkestratsiya qilish platformalari model-provayderlari atrofida jadal konsolidatsiyalashmoqda. Biroq bu hali barqaror oligopoliya emas: rekord darajadagi almashtirish (switching) niyati, vendor lock-in qo'rquvi, protokol standartlari uchun kurash va narxlash modellarining parchalanishi bozor tuzilmasi hali shakllanish bosqichida ekanini ko'rsatadi.

### 4.1. Bozor tuzilishi: model-provayder platformalari hukmron

[VentureBeat Pulse Research](https://venturebeat.com/resources/agentic-orchestration-enterprise-ai-organizations-have-a-deployment-problem-not-a-platform-problem-and-most-are-calling-chatbots-agents) 2026-yil iyun to'lqinida 100+ xodimli 101 korxonani so'rov qildi. Natijalar shuni ko'rsatadiki, korxonalar orkestratsiyani asosan model-provayder platformalarida quryapti: Anthropic'ning Claude platformasi respondentlarning **40%**ida asosiy platforma bo'lib, eng yaqin raqibdan ikki baravardan ko'proq; Microsoft **18%**, OpenAI **13%**, Google **8%**, Amazon Bedrock Agents **2%**. Ochiq freymvorklardan LangChain/LangGraph **6%**, o'z ichida qurish (custom in-house) **5%**, hali orkestratsiya qilmayotganlar 3% (qolgan ~5% — boshqa/javob bermaganlar). Beshta yirik model-provayder birgalikda **~80%** deployni qamrab oladi.

Platforma tanlovidagi asosiy omil "model gravitatsiyasi" — eng zamonaviy bazaviy model bilan native moslik (21%); muvaffaqiyat mezoni esa ishonchli ko'p bosqichli ijro (vazifani bajarish ishonchliligi 32%, ko'p bosqichli workflow boshqaruvi 28%). Muhim tafsilot: korxonalar o'z portfelini halol baholaganda, **71%** "deploy qilingan agentlarning to'rtdan bir qismi yoki undan kami haqiqiy ko'p bosqichli orkestrlangan workflow, qolgani esa chatbot qobig'i" deb tan oldi.

### 4.2. Asosiy o'yinchilar guruhlari

Bozorni to'rt guruhga ajratish mumkin.

**1) Model-provayderlari va ularning agent platformalari.** OpenAI (Agents SDK, Responses API), Anthropic (Claude Agent SDK, MCP ixtirochisi), Google (Gemini Enterprise, ADK, A2A protokoli), Microsoft (Copilot Studio, Agent 365, Azure AI Foundry). VentureBeat ma'lumotlariga ko'ra, aynan shu to'rtlik orkestratsiya bozorining asosiy qismini egallaydi.

**2) Korxona dasturiy ta'minot gigantlari.** Salesforce Agentforce, ServiceNow (AI Control Tower), SAP, Oracle. [AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/13/salesforce-agentforce-vs-microsoft-copilot-enterprise-agent-platform-war-2026) ma'lumotiga ko'ra, Salesforce Agentforce **18 500 mijozga** yetgan va **$800 mln ARR** (yillik o'sish 169%) haqida xabar bergan; Microsoft Copilot esa **70 mln pullik o'rindiq** (seat) da. **Bu raqamlar vendorning o'z hisoboti bo'lib, mustaqil audit bilan tasdiqlanmagan** — ehtiyotkorlik bilan ishlatilishi kerak (Copilot'da aktivatsiya darajasi ~35,8% deb qayd etilgan, ya'ni "seat" soni haqiqiy foydalanishni ko'rsatmaydi).

**3) Freymvork va orkestratsiya qatlami.** LangChain/LangGraph, CrewAI, Microsoft AutoGen, LlamaIndex, Semantic Kernel. Muhim dinamika: 2026-yil aprelda Microsoft Agent Framework 1.0 GA chiqdi va AutoGen'ni Semantic Kernel bilan birlashtirdi, AutoGen esa maintenance mode'ga o'tdi ([LearnAgent](https://learnagent.org/library/compare/agent-framework-comparison-2026/) — *sanoat blogi, rasmiy tasdiq yo'q*).

**4) Bulut infratuzilmasi.** AWS Bedrock Agents, Azure AI Foundry, Google Cloud Vertex — agentlar uchun hisoblash va xavfsizlik infratuzilmasini taqdim etadi.

### 4.3. Protokollar va standartlar kurashi

Interoperability — bu bo'limning eng muhim strategik jihati. Anthropic yaratgan **MCP (Model Context Protocol)** agentlarni vositalar va ma'lumotlarga ulashning universal standartiga aylandi: 10 000+ faol ommaviy MCP server va Python/TypeScript SDK'lar uchun oyiga **97 mln+ yuklab olish**. 2025-yil 9-dekabrda Anthropic MCP'ni Linux Foundation qoshidagi yangi **Agentic AI Foundation (AAIF)**ga xayriya qildi; AAIF'ga Anthropic, Block va OpenAI asos solgan, Google, Microsoft, AWS, Cloudflare va Bloomberg qo'llab-quvvatlaydi ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)). AAIF platinum a'zolariga AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft va OpenAI kiradi, gold a'zolar qatorida esa Salesforce, SAP, ServiceNow va Oracle bor ([Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)).

Ikkinchi standart — Google'ning **A2A (Agent2Agent)** protokoli — agentlararo gorizontal aloqa uchun. 2025-yil iyun oyida Google uni Linux Foundation'ga xayriya qildi; 100+ kompaniya qo'llab-quvvatlaydi, asoschilari qatorida AWS, Cisco, Google, Microsoft, Salesforce, SAP va ServiceNow bor ([Google Developers Blog](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/)). Uchinchi qatlam — **AG-UI (Agent–User Interaction)** — agentlar va foydalanuvchi interfeysi o'rtasidagi ochiq, event-ga asoslangan protokol ([CopilotKit / AG-UI](https://www.copilotkit.ai/ag-ui)). Uchovi birgalikda "MCP — vositalar, A2A — agentlararo, AG-UI — frontend" arxitekturasini shakllantiradi. Bu nega muhim? Chunki bitta model-provayderga bog'lanib qolmaslik (lock-in) aynan protokollarning vendor-neytral bo'lishiga tayanadi.

### 4.4. Narxlash modellari

Narxlash 2026-yilda uchga bo'lindi: **per-seat**, **per-task/per-action** va **outcome-based**. Salesforce Agentforce bir vaqtda bir necha modelni yuritadi: $2/suhbat, Flex Credits **$0,10/harakat**, va $125/foydalanuvchi/oy ([AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/25/ai-agent-pricing-model-divergence-per-seat-per-task-outcome-based)). Microsoft per-seat modelida: **$30–99/foydalanuvchi/oy**. Intercom Fin esa outcome-based modelda har bir hal qilingan ticket uchun **$0,99** oladi ([AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/11/outcome-based-ai-agent-pricing-2026)). IDC prognoziga ko'ra, **2028-yilga kelib sof per-seat narxlash eskirib qoladi** — agentlar qo'l mehnatini almashtirgani uchun vendorlarning 70% o'z qiymat taklifini yangi modellarga qayta qurishga majbur bo'ladi ([IDC FutureScape 2026](https://my.idc.com/getdoc.jsp?containerId=prUS53883425)).

### 4.5. Raqobat dinamikasi, lock-in va ochiq kod

Har bir o'yinchining ustunligi har xil: Anthropic — model sifati va native orkestratsiya muhiti; Microsoft — korxona integratsiyasi va M365 ekotizimi; Google — protokol va ochiqlik; Salesforce — CRM-native workflow; ServiceNow — ko'p-vendorli AI Control Tower governance. Lock-in eng katta xavf: respondentlarning **35%** uni eng katta xavf deb atadi, 51% esa 2026-yil oxiriga kelib **gibrid boshqaruv tekisligi** (provider-native + tashqi orkestratsiya) kutmoqda. Bu "build vs buy" savolini ham qo'zg'aydi: 5% o'z ichida quradi, 68% esa bir yil ichida platformani almashtirish yoki qo'shishni rejalashtirmoqda — bu VentureBeat kuzatgan barcha qatlamlar orasida eng yuqori almashtirish niyati.

Ochiq kod muqobillari bu manzarada muhim rol o'ynaydi: LangChain/LangGraph orkestratsiya bozorida 6% ulushga ega, ammo Gartner'ning "agent washing" ogohlantirishi bozorni chalg'itadi — Gartner minglab "agentic AI" sotuvchisidan faqat **~130 tasi haqiqiy** deb hisoblaydi ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)). Bu esa xaridorlar uchun vendor tanlashni yanada qiyinlashtiradi.

**Kichik xulosa.** Korxona agent platformalari bozori model-provayderlari atrofida konsolidatsiyalashmoqda, ammo uchta kuch bu konsolidatsiyani mo'rt qiladi: (1) protokollarning vendor-neytral fondga o'tishi (MCP, A2A) lock-in'ni pasaytiradi; (2) narxlash modellarining parchalanishi va IDC'ning per-seat "o'limi" prognozi qiymat olish nuqtasini qayta belgilaydi; (3) 68% almashtirish niyati bozorni hali "hal bo'lmagan" qiladi. Shu sababli 2026-yil "platforma urushi" emas, balki **joylashish nuqtasi uchun kurash** yili.

---

## 5. AI agentlar tendentsiyalarining keyingi 3–5 yildagi rivojlanish bashoratlari

> **Muhim eslatma:** quyidagi barcha raqamlar — **bashorat/prognoz**, **fakt emas**. Har bir da'vo uchun kim aytgani va qachon aytgani ko'rsatilgan. Prognozlar bir-biriga zid bo'lganda, ziddiyat ochiq ko'rsatilgan.

**Tezis.** 2026–2030-yillar oralig'ida yirik tahlil markazlari bir yo'nalishda yakdil: agentik AI alohida pilot loyihalardan korporativ miqyosdagi orkestratsiyaga o'tadi. Biroq ular **sur'at va aniq raqamlar bo'yicha keskin ajralib turadi** — bu esa har qanday prognozga ehtiyotkorlik bilan yondashish zarurligini ko'rsatadi.

### 5.1. Rasmiy prognozlar: raqamlar ortidagi ziddiyat

**Gartner.** Gartner 2025-yil 25-iyundagi press-relizida uchta bashoratni e'lon qildi: 2027-yil oxirigacha agentik AI loyihalarining **40%dan ortig'i bekor qilinadi** (xarajatlar o'sishi, noaniq biznes qiymati va risk nazoratining yetarli emasligi sababli); 2028-yilga kunlik ish qarorlarining **kamida 15%i** agentik AI orqali avtonom qabul qilinadi (2024-yilda deyarli nol); korxona dasturiy ta'minot ilovalarining **33%i** agentik AI funksiyalarini o'z ichiga oladi (2024-yilda 1%dan kam) ([Gartner, 2025-06-25](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)). O'sha relizda Gartner minglab "agentik AI" vendorlaridan faqat **~130 tasini haqiqiy** deb hisoblashini ta'kidlaydi.

2025-yil 26-avgustda Gartner yana bir bashorat e'lon qildi: 2026-yil oxiriga korxona ilovalarining **40%i** "vazifaga xos" (task-specific) AI agentlarni o'z ichiga oladi (2025-yilda <5%) ([Gartner, 2025-08-26](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)). O'sha relizda Gartner 2027-yilga agentik AI joriy etishlarining **uchdan biri** turli ko'nikmali agentlarni birlashtirishini, 2028-yilga foydalanuvchi tajribalarining uchdan biri ilovalardan agentik "front end"ga o'tishini prognoz qiladi.

> **Izoh (raqamlar orasidagi nomuvofiqlik):** 2028-yilga "33% ilovalar" va 2026-yilga "40% ilovalar" raqamlari **turli ko'rsatkichlarni** o'lchaydi (agentik AI funksiyalari ↔ vazifaga xos agentlar) va turli qamrovga ega. Shuning uchun ularni qat'iy "ziddiyat" deb emas, **turli qamrovdagi prognozlar** deb o'qish aniqroq bo'ladi.

**IDC.** IDC FutureScape 2026 hisobotida (2025-yil 23-oktabr) bashorat qiladi: 2030-yilga **45% tashkilot** agentlarni keng miqyosda orkestrlaydi; 2026-yilga G2000 kompaniyalaridagi **ish rollarining 40%i** agentlar bilan ishlashni o'z ichiga oladi; 2028-yilga sof "o'rindiq" (seat-based) narxlash eskiradi va **70% vendor** o'z qiymat taklifini yangi modellarga qayta qurishga majbur bo'ladi ([IDC FutureScape 2026](https://www.hpcwire.com/off-the-wire/idc-futurescape-2026-predictions-reveal-the-rise-of-agentic-ai-and-a-turning-point-in-enterprise-transformation/)). Alohida blogida IDC 2027-yilga G2000 agentlardan foydalanish **10 baravar**, token va API yuklamasi **1000 baravar** oshishini, 2029-yilga esa **1 milliarddan ortiq** faol agent ishga tushishini (kuniga 217 mlrd harakat) bashorat qiladi ([IDC, 2025-12-10](https://www.idc.com/resource-center/blog/agent-adoption-the-it-industrys-next-great-inflection-point/)).

**Deloitte.** Deloitte 2025-yilda GenAI ishlatuvchi korxonalarning **25%i** agentik AI pilotini boshlashini, **2027-yilga 50%ga** yetishini prognoz qiladi ([Deloitte / TechGig](https://www.techgig.com/news/ai/deloitte-50-of-generative-ai-users-to-pilot-agentic-ai-by-2027/132007614)). Deloitte Tech Trends 2026 hisobotida agentlarni "silikon ishchi kuchi" deb tavsiflab, avtonomiya spektrini (augmentation → automation → true autonomy) va "agent supervisor" rolini ta'kidlaydi ([Deloitte Tech Trends 2026](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)).

**Boshqalar.** Forrester 2026-yil prognozida korxonalar AI xarajatlarining **25%ini 2027-yilga kechiktirishini** ta'kidlaydi, chunki AI qaror qabul qiluvchilarning atigi **15%i** so'nggi 12 oyda EBITDA o'sishini qayd etgan ([Forrester, 2025-10-08](https://www.forrester.com/blogs/predictions-2026-ai-moves-from-hype-to-hard-hat-work/)). MarketsandMarkets AI agentlar bozorini 2025-yildagi 7,84 mlrd dollardan 2030-yilga **52,62 mlrd dollargacha** (CAGR 46,3%) o'sishini prognoz qiladi ([MarketsandMarkets](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp)).

### 5.2. Sifat o'zgarishlari (raqamlardan tashqari)

**Chatbotdan haqiqiy agentga o'tish.** [VentureBeat](https://venturebeat.com/technology/venturebeat-research-where-enterprise-ai-agent-governance-hasnt-caught-up) tadqiqoti ko'rsatadi: korxonalarning **71%i** o'z "agentlar"ining to'rtdan bir qismi yoki undan kami mustaqil ko'p qadamli ishni bajara olishini aytdi; faqat **10%i** haqiqiy agentlar ko'pchilikni tashkil etishini bildirdi. Ya'ni bozor "agent" atamasini haddan tashqari keng qo'llamoqda.

**Multi-agent orkestratsiya va agentlararo muloqot (A2A).** Google yaratgan A2A protokoli 2025-yil 23-iyunda Linux Foundation qoshidagi loyihaga aylandi; uni AWS, Cisco, Salesforce, SAP, Microsoft va ServiceNow qo'llab-quvvatlaydi ([Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)).

**Standartlashtirish va protokol konsolidatsiyasi.** 2025-yil 9-dekabrda Anthropic MCP'ni Linux Foundation ostidagi **AAIF**ga o'tkazdi; MCP allaqachon ChatGPT, Cursor, Gemini, Microsoft Copilot va VS Code tomonidan qo'llaniladi; 10 000dan ortiq faol MCP server mavjud ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).

**Agent governance va observability mahsulotlari.** Microsoft 2025-yil 18-noyabrda **Agent 365**ni e'lon qildi — agentlarni "odamlarni boshqargandek" boshqarish uchun yagona nazorat tekisligi: agent ID, reyestr, ruxsatlar, kuzatuv (observability) va xavfsizlik ([Microsoft](https://www.microsoft.com/en-us/copilot/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/)).

**Human-in-the-loop → human-on-the-loop.** Deloitte "agent supervisor"larni tavsiya qiladi; AgentMarketCap risk darajasiga qarab bosqichli avtonomiya (yuqori xatarlilarda human-in-the-loop, muntazamlarida human-on-the-loop) modelini ta'kidlaydi ([AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/11/gartner-15-percent-agent-autonomy-forecast-2026)).

**Narxlash modeli.** IDC 2028-yilga seat-based narxlash eskirishini va vendorlar **natijaga asoslangan (outcome-based)** modelga o'tishini prognoz qiladi ([IDC FutureScape 2026](https://www.hpcwire.com/off-the-wire/idc-futurescape-2026-predictions-reveal-the-rise-of-agentic-ai-and-a-turning-point-in-enterprise-transformation/)).

**Kichik til modellari (SLM).** Xarajat optimizatsiyasi uchun korxonalar barcha vazifalar uchun yirik LLM o'rniga kichikroq, vazifaga xos modellarni tanlamoqda ([Joget](https://joget.com/ai-agent-adoption-in-2026-what-the-analysts-data-shows/)).

**Regulyatsiya.** EU AI Act'ning **14-moddasi** yuqori xatarlil AI tizimlari uchun "samarali inson nazorati"ni talab qiladi — jumladan avtomatlashtirish xatosi (automation bias)dan xabardor bo'lish hamda tizim natijasini bekor qilish yoki "to'xtatish" qobiliyati; talablar 2027–2028-yillarda kuchga kiradi ([EU AI Act, 14-modda](https://artificialintelligenceact.eu/article/14/)).

**Agentlar "xodim" sifatida.** Microsoft Agent 365 va Deloitte hisoboti agentlarga alohida nom, identifikatsiya va ruxsatlar berilishini, kelajakda ular "soliqqa tortilishi" mumkinligini ham eslatadi ([Microsoft](https://www.microsoft.com/en-us/copilot/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/), [Deloitte](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)).

### 5.3. Optimistik va konservativ stsenariylar

Optimistik stsenariy (IDC 45%/2030, Gartner 15%/2028) texnologiyaning tez tarqalishiga tayanadi. Konservativ dalillar sezilarli: **MIT NANDA** hisoboti (2025-yil avgust) korporativ GenAI pilotlarining **95%i** o'lchanadigan moliyaviy natija bermaganini ko'rsatadi ([MIT NANDA, 2025](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf)); Gartner 40%+ loyiha bekor qilinishini, Forrester 25% xarajat kechiktirilishini bashorat qiladi. Gartner o'zining Hype Cycle for AI 2025 hisobotida generativ AI cho'qqidan tushayotganini ko'rsatadi ([Gartner Hype Cycle for AI](https://www.gartner.com/en/articles/hype-cycle-for-artificial-intelligence)).

**Ehtimoliy real stsenariy:** agentlar tez o'sadi, lekin 2028-yilga "15% avtonom qarorlar" kabi raqamlarga erishish emas, balki boshqaruv (governance), ma'lumot sifati va integratsiya muammolarini hal qilgan korxonalargina muvaffaqiyat qozonadi. VentureBeat anketasi shuni ko'rsatadiki, korxonalarning **uchdan ikki qismi** agentga avtomatik baholash natijalarigagina tayanib ishlab chiqarishga o'zgarish kiritishga ruxsat beradi, ammo faqat **5%i** bu baholashlarga to'liq ishonadi ([VentureBeat](https://venturebeat.com/technology/venturebeat-research-where-enterprise-ai-agent-governance-hasnt-caught-up)).

### 5.4. Nima o'zgarmaydi

Uch narsa tendentsiyalardan qat'i nazar doimiy qoladi: **inson nazorati** (EU AI Act 14-moddasi talabi; Deloitte "agent supervisor" modeli), **ma'lumot sifati** (IDC ma'lumotlarga tayyor bo'lmagan korxonalar 2027-yilga 15% unumdorlik yo'qotishini prognoz qiladi; VentureBeat anketasida 57% korxona noto'g'ri javobni biznes kontekstining yetishmasligidan topgan), va **integratsiya qiyinligi** (Gartner eski tizimlarni integratsiya qilish texnik jihatdan murakkab va qimmat ekanini ta'kidlaydi).

**Kichik xulosa.** Keyingi 3–5 yil agentik AI uchun "shovqindan amaliyotga" o'tish davri bo'ladi. Barcha yirik prognozlar bir yo'nalishni ko'rsatadi — korporativ miqyosdagi agent orkestratsiyasi, standartlashtirish va governance mahsulotlari — ammo sur'at bo'yicha ular keskin ajralib turadi. Shu sababli prognozlarni "ajralmas haqiqat" sifatida emas, balki yo'nalish ko'rsatkichi sifatida qabul qilish, muvaffaqiyatni esa boshqaruv hamda ma'lumot tayyorligi bilan o'lchash maqsadga muvofiqdir.

---

## 6. RankWant platformasiga bog'liqlik: arxitektura, foydalanuvchi ehtiyojlari va raqobat tahlili

> **Izoh:** bu bo'limda RankWant haqidagi faktlar loyihaning o'z hujjatlaridan (arxitektura, domain model, texnik spetsifikatsiya, ADR'lar) olingan — ular uchun tashqi manba talab qilinmaydi. Tashqi faktlar havola bilan berilgan.

### 6.1. RankWant'da AI agent qanday ishlashi kerak (arxitektura darajasida)

RankWant bugungi holatida AI/LLM funksiyasiga ega emas: na masala generatsiyasi, na AI mentor, na kod bo'yicha avtomatik fikr-mulohaza. Bu — platformaning eng katta strategik bo'shlig'i, chunki global raqobatchilar aynan shu yo'nalishda jadal harakatlanmoqda.

**Nomzod funksiyalar va ularning AI'ga mosligi:**

| Funksiya | AI'ga mosligi | Sabab |
|---|---|---|
| Masala va test generatsiyasi | Yuqori (qoralama) | Yuqori hajm, takrorlanuvchi, lekin inson tekshiruvi shart |
| Kod bo'yicha AI feedback (WA/TLE sababi) | Yuqori | Har bir urinishda kerak, matnli izoh beriladi |
| AI mentor/repetitor | Yuqori | Kontent tanqisligini to'ldiradi |
| Kontent tarjimasi (10 til) | Yuqori | Mexanik, tekshiriladigan |
| Masala tavsiyasi (recommendation) | O'rta | Mavjud reyting ma'lumoti bilan gibrid yaxshi ishlaydi |
| Editorial yozishga yordam | O'rta | Inson muharriri zarur |
| Anti-cheat (plagiat, AI-kod aniqlash) | O'rta | HackerRank tajribasi ko'rsatadi — ishlaydi, lekin xato pozitiv bor |
| Moderatorlik (spam, report) | O'rta | Yuqori hajm, lekin qaror insonda qolishi kerak |
| Musobaqa ichida yordam | **Mos emas** | Adolat buziladi |

**Kritik arxitektura chegarasi.** RankWant judge'i alohida hostda, DB credential'siz va kiruvchi portsiz ishlaydi — bu "eng kam imtiyoz" (least privilege) tamoyilining namunasi. AI agent ham xuddi shu mantiqda qurilishi kerak: u judge hostiga **kirmasligi**, testlar bazasiga to'g'ridan-to'g'ri **ulanmasligi** va faqat ruxsatlar bilan cheklangan interfeys orqali ishlashi lozim. Lekin bu yerda ikki jiddiy qarama-qarshilik bor:

1. **Maxfiylik.** Foydalanuvchi yechimini uchinchi tomon modeliga (OpenAI/Anthropic) yuborish — bu kod egasining intellektual mulkini tashqi serverga chiqarish demakdir. Xalqaro tajribada bu muammo real: ko'plab AI coding-agent'lar standart holatda kodni bulutga yuboradi va ko'plab kompaniyalar uchun bu "dealbreaker" ([AIMadeTools](https://www.aimadetools.com/blog/best-ai-coding-agents-privacy-2026/)). Asosiy model provayderlarining ma'lumot siyosati ham shu xavotirni asoslaydi: masalan, Anthropic API standart holatda ma'lumotni 30 kun saqlaydi va (kelishuvsiz) mijoz ma'lumotlarida o'qitmaydi ([Anthropic Privacy Center](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)); "nol saqlash" (zero data retention) alohida shartnoma talab qiladi ([Anthropic](https://privacy.claude.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to)). RankWant'da bu masala yanada o'tkir, chunki musobaqa ishtirokchisining yechimi — uning shaxsiy aktivi.
2. **Musobaqa adolati.** [Codeforces](https://codeforces.com/blog/entry/133941) 2024-yil sentabrdan boshlab AI'dan musobaqa ichida foydalanishni **ataylab taqiqlagan** — hatto AI orqali xatoni tuzatishni ham ("Runtime error on test 1" kabi verdictdan keyin AI'dan yordam so'rash mumkin emas). Sabab — 2024-yilda ChatGPT o1 kabi modellarning paydo bo'lishi bilan firibgarlik "o'n barobar, balki yuz barobar" ko'paygan ([Codeforces](https://codeforces.com/blog/entry/141199)).

**Texnik variantlar (trade-off):**

- **Self-hosted (o'z joyida):** Ollama + vLLM orqali ochiq kodli coding-model — masalan, **Qwen2.5-Coder-32B** ([Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct), [Ollama](https://ollama.com/library/qwen2.5-coder)) yoki **Codestral-22B** ([Hugging Face](https://huggingface.co/mistralai/Codestral-22B-v0.1)). Kod tashqariga chiqmaydi, lekin sifat farqi murakkab vazifalarda sezilarli. RankWant hozir bitta mashinada ishlaydi — bu real boshlanish nuqtasi.
- **API (OpenAI/Anthropic):** eng yuqori sifat, lekin har bir so'rov uchun to'lov + ma'lumot tashqariga chiqadi. Azure OpenAI yoki AWS Bedrock "nol saqlash" siyosati bilan kelishish mumkin.
- **Gibrid (tavsiya):** yuqori hajmli, takrorlanuvchi vazifalar (tarjima, moderatorlik, tavsiya) — lokal kichik model; kam hajmli, yuqori mantiqiy vazifalar (editorial, murakkab feedback) — bulutli API, **faqat foydalanuvchi roziligi bilan**.

**Xulosa:** AI agentni "yuqori hajm + takrorlanuvchi + tekshiriladigan" funksiyalarga bog'lash, yakuniy hukmni (judge) esa **deterministik va izolyatsiyalangan** holida saqlash kerak. Anti-cheat va moderatsiya qarorlari doimo inson nazoratida qolishi (human-in-the-loop) lozim.

### 6.2. Foydalanuvchi ehtiyojlari

RankWant'ning beshta asosiy roli bor va har biri uchun AI agent aniq ehtiyojni qondiradi:

- **O'rta maktab o'quvchisi.** Eng katta to'siq — "yolg'iz qolish" va xatoni tushunmaslik. AI mentor WA sababini o'zbek tilida tushuntirsa, o'quvchi mustaqil davom eta oladi. Boshlang'ich darajadagi (800–1200) masalalarda AI feedback ayniqsa foydali.
- **Universitet talabasi.** Musobaqa va intervyu tayyorgarligi. Bu yerda LeetCode'ning "Ask Leet" tajribasi o'rnak: brainstorming, kodni optimallashtirish, test generatsiyasi va debug ([LeetCode Premium](https://leetcode.com/subscribe/)).
- **O'qituvchi/murabbiy.** Topshiriq tuzish, baholash va tahlil — bu takroriy yuk. AI buni avtomatlashtirsa, o'qituvchi pedagogikaga vaqt ajratadi. Bu global tendentsiya: "AI tizimlari test topshiriqlari, baholash jarayonlarini avtomatlashtiradi... baholash inson omilidan kamroq ta'sirlanadi" ([uzmarkaz](https://uzmarkaz.uz/en/news/talimda-suniy-intellekt-imkoniyatlar-muammolar-va-istiqbollar)).
- **Mustaqil o'rganuvchi.** Roadmap, editorial va mavzuli tavsiyalar kerak. RankWant'da editorial allaqachon bor — AI uni kengaytirib, har bir masalaga individual tushuntirish bera oladi.
- **Tashkilot (B2B).** Classroom va maktab katalogi ustiga AI analitika (kim qayerda qoqilyapti) qo'shilsa, B2B qiymat sezilarli oshadi.

**O'zbekiston konteksti.** AI'ni ta'limga joriy etish davlat darajasida ustuvor yo'nalish sifatida belgilangan: O'zbekiston Prezidentining **2024-yil 14-oktyabrdagi PQ-358-son qarori** bilan **Sun'iy intellekt texnologiyalarini 2030-yilga qadar rivojlantirish strategiyasi** tasdiqlangan ([gov.uz — Raqamli texnologiyalar vazirligi](https://gov.uz/digital/news/view/24510)). Ikki asosiy muammo bor: (1) **o'zbek tilidagi kontent tanqisligi** — RankWant buni o'z kontenti va 10 tilli i18n bilan qisman hal qilgan; (2) **mentor tanqisligi** — malakali CP murabbiyini topish qiyin. Aynan shu bo'shliqni AI mentor to'ldiradi.

Nima uchun AI mentor muhim? Chunki CP o'rganishdagi eng katta to'siq texnik emas, psixologik: odam yolg'iz qoladi va xatosini tushunmaydi. Lokal OJ'lar (KEP, RoboContest) bu bo'shliqni to'ldirmaydi — ular faqat verdict beradi, izoh bermaydi. Bu RankWant uchun asosiy differensiatsiya imkoniyati.

### 6.3. Raqobatchilar bilan taqqoslash

| Platforma | Asosiy auditoriya | AI funksiyalari | RankWant'ga nisbatan ustunlik/kamchilik |
|---|---|---|---|
| **Codeforces** | Sport dasturchilar, global | **Yo'q (ataylab)** — AI musobaqada taqiqlangan ([manba](https://codeforces.com/blog/entry/133941)) | Ustunlik: hamjamiyat, contest sifati. Kamchilik: AI yo'q, o'zbek tili yo'q |
| **LeetCode** | Intervyu tayyorgarligi | **Ask Leet** (brainstorm, optimizatsiya, test, debug), Interview Simulations ([manba](https://leetcode.com/subscribe/)) | Ustunlik: AI agent + kompaniya savollari. Kamchilik: CP/OI emas, o'zbek tili yo'q |
| **KEP.uz** | O'zbekiston OJ | **Aniqlanmadi** — saytda AI haqida ma'lumot topilmadi ([manba](https://kep.uz/)) | Ustunlik: mahalliy auditoriya. Kamchilik: AI yo'q (aniqlanmagan) |
| **RoboContest** | O'zbekiston OJ | **Aniqlanmadi** — 200 615 foydalanuvchi, 1 477 ochiq masala; AI funksiyasi ko'rsatilmagan ([manba](https://robocontest.uz/)) | Ustunlik: katta foydalanuvchi bazasi. Kamchilik: AI yo'q (aniqlanmagan) |
| **cp.uz** | O'zbek CP hamjamiyati | **Aniqlanmadi** — ochiq kutubxona, roadmap, lug'at; AI tilga olinmagan ([manba](https://cp.uz/)) | Hamjamiyat/kontent resursi, lekin OJ emas |
| **CodeChef** | DSA/CP o'rganuvchilar | AI mentor — "24/7 AI yordam", "har bir kodga intellektual feedback", roadmap'lar ([manba](https://www.codechef.com/pro)) | Ustunlik: o'quv roadmap + AI. Kamchilik: o'zbek tili yo'q |
| **AtCoder** | Yaponiya/global CP | AI mahsulot emas, **AI o'qitish uchun dataset** (30M+ yechim, 5 000+ masala) ([manba](https://datasets.atcoder.jp/)) | Ma'lumot boyligi, lekin o'quvchi uchun AI yo'q |
| **HackerRank** | Ishga yollash/assessment | **AI Plagiarism Detection**, AI Assistant, **AI Tutor**, Mock AI Interviewer, Interview Creator Agent ([manba](https://support.hackerrank.com/articles/9416207922-hackerrank%27s-ai-features)) | Ustunlik: AI to'plami juda boy. Kamchilik: CP emas, korporativ |
| **CodeSignal** | Texnik yollash | **Cosmo** AI co-pilot, Full/Guided AI rejimlari ([manba](https://codesignal.com/newsroom/press-releases/codesignal-launches-ai-assisted-coding-assessments-and-interviews-redefining-technical-hiring-in-the-ai-era/)) | Ustunlik: "AI bilan ishlashni baholash". Kamchilik: CP emas |

**Asosiy xulosa:** global platformalar AI'ni ikki yo'nalishda qo'llaydi — (1) **yollash/assessment** (HackerRank, CodeSignal) va (2) **o'quv/intervyu** (LeetCode, CodeChef). Mahalliy platformalar (KEP, RoboContest, cp.uz) AI'dan deyarli foydalanmaydi. RankWant uchun "o'zbek tilidagi CP platformasi + AI mentor" kombinatsiyasi bozorda deyarli egallanmagan nisha hisoblanadi.

> **Metodik izoh:** KEP, RoboContest va cp.uz bo'yicha "AI aniqlanmadi" xulosasi ularning ochiq (ommaviy) sahifalarini ko'zdan kechirishga asoslangan. Bu — salbiy dalil: AI funksiyasi mavjud bo'lmasligini isbotlamaydi, faqat ommaviy manbalarda topilmaganini ko'rsatadi.

### 6.4. Yetishmayotgan funksiyalar va tavsiyalar

**Yetishmayotgan funksiyalar (ustuvorlik/murakkablik):**

| # | Funksiya | Nima uchun kerak | Ustuvorlik | Murakkablik |
|---|---|---|---|---|
| 1 | AI feedback (WA/TLE sababi, o'zbek tilida) | Eng katta ehtiyoj, differensiator | Yuqori | O'rta |
| 2 | AI mentor/repetitor (suhbatli) | Mentor tanqisligini to'ldiradi | Yuqori | O'rta-yuqori |
| 3 | Kontent tarjimasi (10 til) | i18n allaqachon bor, kontent kerak | Yuqori | Past-o'rta |
| 4 | Masala/test generatsiyasi (qoralama) | Kontent hajmini oshiradi | O'rta | Yuqori |
| 5 | Anti-cheat (AI-kod, plagiat) | Musobaqa adolatini himoya qiladi | O'rta | Yuqori |
| 6 | Moderatorlik (spam/report) | Jamoa kichik (1 kishi) | O'rta | Past |
| 7 | AI tavsiya (recommendation) | Retensiyani oshiradi | O'rta | O'rta |
| 8 | O'qituvchi uchun topshiriq generatori | B2B qiymati | O'rta | O'rta |
| 9 | Editorial draft yordamchisi | Kontent tezligi | Past-o'rta | O'rta |

**5-bo'lim tendentsiyalari bilan bog'lash.** AI funksiyalarini joriy etishda "agent governance", **MCP** va **human-in-the-loop** tamoyillariga tayanish kerak. MCP — AI agentni tashqi asbob-uskunalarga ulashni standartlashtiruvchi ochiq standart ([MCP rasmiy spetsifikatsiyasi](https://modelcontextprotocol.io/)). RankWant uchun bu degani: AI agent judge, DB va kontent tizimlariga to'g'ridan-to'g'ri emas, **standartlashtirilgan, ruxsatlar bilan cheklangan interfeys** orqali ulanishi kerak. Human-in-the-loop esa anti-cheat va moderatsiya qarorlarida majburiy bo'lishi lozim.

**Amaliy tavsiyalar (ketma-ketlik bilan):**

1. **1-bosqich — Lokal AI feedback MVP.** Bitta self-hosted kichik coding-model (masalan, **Qwen2.5-Coder-7B** — [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct), [Ollama](https://ollama.com/library/qwen2.5-coder)) bilan WA/TLE sababini o'zbek tilida tushuntiruvchi funksiya. Faqat **practice rejimida**, musobaqa ichida o'chirilgan. Xarajat past, maxfiylik saqlanadi.
2. **2-bosqich — AI mentor + tarjima.** Mentor suhbat interfeysini qo'shish va mavjud kontentni 10 tilga tarjima qilishni avtomatlashtirish. Bu eng ko'p ko'rinadigan qiymat beradi.
3. **3-bosqich — Anti-cheat (gibrid).** AI-kod aniqlashni joriy etish (HackerRank tajribasi asosida), lekin har bir flag **inson tekshiruvidan** o'tishi shart.
4. **4-bosqich — O'qituvchi paneli + masala generatsiyasi.** B2B va kontent hajmini oshirish. Bu bosqichda bulutli API'ga ehtiyotkorlik bilan o'tish mumkin.
5. **Butun jarayon davomida** — barcha AI o'zgarishlarini audit jurnaliga yozish (RankWant'da `RatingHistory` allaqachon shu tamoyilda).

**Risklar:** (1) **Adolat** — AI musobaqa ichida ishlasa, contest integrity buziladi; shuning uchun contest rejimida qat'iy o'chirish kerak. (2) **Xarajat** — API'ga to'liq o'tish kutilmagan xarajat keltiradi; gibrid model eng optimal. (3) **Maxfiylik** — foydalanuvchi kodini bulutga yuborishda ochiq rozilik va nol-saqlash siyosatli provayderlar (Azure/Bedrock) talab qilinadi.

---

## Xulosa

Ushbu hisobot korxona AI agentlari bozorining 2024–2026-yillardagi holatini olti bo'limda tahlil qilib, ularning RankWant platformasi uchun strategik ahamiyatini baholadi. Markaziy xulosa shuki, agentlar endi texnologik eksperiment bosqichidan chiqdi, ammo haqiqiy qiymat model kuchida emas, balki governance, ma'lumot sifati va integratsiya yetukligida shakllanadi. Bu RankWant kabi nisbatan kichik, lekin aniq nishaga ega platformalar uchun ham imkoniyat, ham ogohlantirishdir.

**Asosiy topilmalar:**

1. **Joriy etish tez o'smoqda, muvaffaqiyat esa orqada qolmoqda.** Gartner korxona ilovalarining 40% 2026-yilga kelib vazifaga xos agentlarga ega bo'lishini prognoz qiladi ([Gartner, 2025-08-26](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)), biroq MIT NANDA tadqiqoti sinov loyihalarining 95% moliyaviy natija bermaganini ko'rsatadi ([MIT NANDA, GenAI Divide](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf)).
2. **Qiymat aniq turdagi vazifalarda to'planadi.** Agentlar takrorlanuvchi, ko'p tizimli, qadamlarga bo'linadigan va o'lchanadigan vazifalarda eng yaxshi natija beradi — mijozlarga xizmat, tadqiqot/tahlil, ichki oqimlar va ITSM shundan dalolat beradi.
3. **Asosiy to'siqlar texnik va tashkiliy.** Ishonchlilik (ko'p bosqichli oqimlarda aniqlik tez pasayadi), integratsiya, xavfsizlik, governance yetukligi va ROI isboti asosiy muammolar bo'lib qolmoqda ([VentureBeat Research](https://venturebeat.com/technology/venturebeat-research-where-enterprise-ai-agent-governance-hasnt-caught-up)).
4. **Platformalar model-provayderlar atrofida konsolidatsiyalashmoqda, protokollar neytrallashdi.** Anthropic, Microsoft, OpenAI, Google va Amazon birgalikda bozorning ~80%ini egallaydi; MCP va A2A Linux Foundation fondiga o'tdi ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).
5. **Barcha prognozlar bir yo'nalishda — korporativ miqyosdagi orkestratsiya.** IDC 2030-yilga 45% tashkilot agentlarni orkestrashini, Gartner esa 2028-yilga kunlik qarorlarning 15% avtonom bo'lishini kutmoqda ([IDC FutureScape 2026](https://www.hpcwire.com/off-the-wire/idc-futurescape-2026-predictions-reveal-the-rise-of-agentic-ai-and-a-turning-point-in-enterprise-transformation/)).

**RankWant uchun amaliy xulosalar:**

1. **Lokal AI feedback MVP bilan boshlash.** Practice rejimida foydalanuvchi kodiga AI feedback (WA/TLE sabablari) — eng past xavfli va tez qaytim beradigan birinchi qadam.
2. **"O'zbek tilidagi CP platformasi + AI mentor" nishasini egallash.** Global raqobatchilar (HackerRank, CodeSignal, LeetCode) AI'ni qo'llaydi, mahalliy platformalar (KEP.uz, RoboContest, cp.uz) esa deyarli foydalanmaydi — bu egallanmagan nisha.
3. **Arxitektura chegarasini saqlash.** Judge alohida hostda va DB credential'siz ishlaganidek, AI agent ham faqat ruxsatlar bilan cheklangan interfeys orqali ishlashi kerak (MCP tamoyili) ([Model Context Protocol](https://modelcontextprotocol.io/)).
4. **Maxfiylik uchun gibrid joylashtirishni tanlash.** Kodni uchinchi tomonga yuborish xavfini kamaytirish uchun self-hosted modellar (Qwen2.5-Coder, Codestral) va API kombinatsiyasi tavsiya etiladi ([Qwen2.5-Coder-32B](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct)).
5. **Anti-cheat'ni inson nazorati bilan joriy etish.** Musobaqa ichida AI yordami mos emas — Codeforces AI'ni ataylab taqiqlagan; anti-cheat faqat gibrid yondashuv va inson tekshiruvi bilan ishlatilishi kerak ([Codeforces](https://codeforces.com/blog/entry/133941)).
6. **Governance va o'lchovni birinchi kundan o'rnatish.** "Agent washing" tuzog'iga tushmaslik uchun har bir AI funksiyaning ROI ko'rsatkichlarini oldindan belgilash zarur.
7. **4 bosqichli yo'l xaritasiga amal qilish.** (1) lokal AI feedback MVP, (2) AI mentor + tarjima, (3) gibrid anti-cheat, (4) o'qituvchi paneli va masala generatsiyasi.

**Shartli tavsiya:** Agar RankWant birinchi navbatda AI mentor va lokal feedback funksiyalarini o'zbek tilida joriy qilsa, unda u mintaqada yagona AI-yetakchi CP platformasiga aylanishi va foydalanuvchi bazasini mustahkamlashi mumkin; aks holda, global platformalar o'zbek tilini qo'llab-quvvatlashni boshlaguncha kutish strategik bo'shliqni yanada chuqurlashtiradi.

**Kelgusi yo'nalishlar:** Ma'lumot sifati va governance'ga investitsiya qilgan tashkilotlar g'olib bo'ladi. RankWant uchun keyingi tadqiqot yo'nalishi — lokal modellarning o'zbek tilidagi kod-feedback sifatini va anti-cheat aniqligini eksperimental baholash.

---

## Adabiyotlar

### Bozor va joriy etish

- Agent adoption: the IT industry's next great inflection point, 2025, IDC — [havola](https://www.idc.com/resource-center/blog/agent-adoption-the-it-industrys-next-great-inflection-point/)
- Agentic AI blurs the line between tool and teammate, 2025, BCG & MIT Sloan Management Review — [havola](https://www.bcg.com/press/18november2025-agentic-ai-blurs-line-tool-teammate)
- Agentic Enterprise Index, 2025, Salesforce — [havola](https://www.salesforce.com/agentforce/agentic-enterprise-index/)
- AI agent survey, 2025, PwC — [havola](https://www.pwc.com/us/en/tech-effect/ai-analytics/ai-agent-survey.html)
- AI agents market, 2025, MarketsandMarkets — [havola](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp)
- AI Index 2025, 2025, Stanford HAI — [havola](https://hai.stanford.edu/ai-index/2025-ai-index-report)
- Annual Report 2025, 2025, Microsoft — [havola](https://www.microsoft.com/investor/reports/ar25/index.html)
- Duolingo customer story, 2024, GitHub — [havola](https://github.com/customer-stories/duolingo)
- FY26 Q4 earnings, 2026, Salesforce — [havola](https://www.salesforce.com/news/press-releases/2026/02/25/fy26-q4-earnings/)
- Klarna AI assistant handles two-thirds of customer service chats in its first month, 2024, Klarna — [havola](https://www.klarna.com/international/press/klarna-ai-assistant-handles-two-thirds-of-customer-service-chats-in-its-first-month/)
- Now on Now: Support AI, 2024, ServiceNow — [havola](https://www.servicenow.com/customers/now-on-now-support-ai.html)
- Quantifying GitHub Copilot's impact in the enterprise with Accenture, 2024, GitHub — [havola](https://github.blog/news-insights/research/research-quantifying-github-copilots-impact-in-the-enterprise-with-accenture/)
- State of Agent Engineering, 2025, LangChain — [havola](https://www.langchain.com/state-of-agent-engineering)
- State of AI in IT 2026, 2026, ITSM.tools — [havola](https://itsm.tools/state-of-ai-in-it-2026/)
- Survey finds forty-five percent of organizations with high AI maturity keep AI projects operational for at least three years, 2025, Gartner — [havola](https://www.gartner.com/en/newsroom/press-releases/2025-06-30-gartner-survey-finds-forty-five-percent-of-organizations-with-high-artificial-intelligence-maturity-keep-artificial-intelligence-projects-operational-for-at-least-three-years)
- Ta'limda sun'iy intellekt: imkoniyatlar, muammolar va istiqbollar, 2025, uzmarkaz — [havola](https://uzmarkaz.uz/en/news/talimda-suniy-intellekt-imkoniyatlar-muammolar-va-istiqbollar)

### Platformalar va protokollar

- Agent 365: the control plane for AI agents, 2025, Microsoft — [havola](https://www.microsoft.com/en-us/copilot/blog/2025/11/18/microsoft-agent-365-the-control-plane-for-ai-agents/)
- Donating the Model Context Protocol and establishing the Agentic AI Foundation, 2025, Anthropic — [havola](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- Google Cloud donates A2A to Linux Foundation, 2025, Google Developers Blog — [havola](https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/)
- Linux Foundation announces the formation of the Agentic AI Foundation, 2025, Linux Foundation — [havola](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- Linux Foundation launches the Agent2Agent Protocol Project, 2025, Linux Foundation — [havola](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)
- Worldwide agentic AI pricing and consumption forecast, 2025, IDC — [havola](https://my.idc.com/getdoc.jsp?containerId=prUS53883425)

### Muammolar va governance

- Agentic orchestration: enterprise AI organizations have a deployment problem, not a platform problem, 2026, VentureBeat Pulse Research — [havola](https://venturebeat.com/resources/agentic-orchestration-enterprise-ai-organizations-have-a-deployment-problem-not-a-platform-problem-and-most-are-calling-chatbots-agents)
- A survey on evaluation of LLM-based agents (arXiv:2503.16416), 2025, Yehudai va boshq. — [havola](https://arxiv.org/abs/2503.16416)
- Measuring agents in production (arXiv:2512.04123), 2025, Pan va boshq. — [havola](https://arxiv.org/abs/2512.04123)
- GenAI Divide: state of AI in business 2025, 2025, MIT NANDA — [havola](https://www.artificialintelligence-news.com/wp-content/uploads/2025/08/ai_report_2025.pdf)
- What gives IT leaders pause as they look to integrate agentic AI with legacy infrastructure, 2025, CIO.com / Tray.ai — [havola](https://www.cio.com/article/3829261/what-gives-it-leaders-pause-as-they-look-to-integrate-agentic-ai-with-legacy-infrastructure.html)
- Where enterprise AI agent governance hasn't caught up, 2026, VentureBeat Research — [havola](https://venturebeat.com/technology/venturebeat-research-where-enterprise-ai-agent-governance-hasnt-caught-up)

### Bashoratlar va regulyatsiya

- 50% of generative AI users to pilot agentic AI by 2027, 2025, Deloitte / TechGig — [havola](https://www.techgig.com/news/ai/deloitte-50-of-generative-ai-users-to-pilot-agentic-ai-by-2027/132007614)
- AI strategy of Uzbekistan (PQ-358), 2024, gov.uz — [havola](https://gov.uz/digital/news/view/24510)
- Deloitte Technology, Media & Telecom 2025 predictions, 2024, Deloitte — [havola](https://www.deloitte.com/us/en/about/press-room/deloitte-technology-media-telecom-2025-predictions.html)
- EU AI Act, Article 14 — Human oversight, 2024, EU AI Act — [havola](https://artificialintelligenceact.eu/article/14/)
- EU AI Act: high-risk AI obligations from August 2026, 2026, Hufeld — [havola](https://www.hufeld.com/en-gb/blog/eu-ai-act-august-2026-high-risk-ai-obligations)
- FutureScape 2026 predictions reveal the rise of agentic AI, 2025, IDC — [havola](https://www.hpcwire.com/off-the-wire/idc-futurescape-2026-predictions-reveal-the-rise-of-agentic-ai-and-a-turning-point-in-enterprise-transformation/)
- Gartner predicts 40 percent of enterprise apps will feature task-specific AI agents by 2026, 2025, Gartner — [havola](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)
- Gartner predicts over 40 percent of agentic AI projects will be canceled by end of 2027, 2025, Gartner — [havola](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)
- Hype Cycle for Artificial Intelligence, 2025, Gartner — [havola](https://www.gartner.com/en/articles/hype-cycle-for-artificial-intelligence)
- Predictions 2026: AI moves from hype to hard-hat work, 2025, Forrester — [havola](https://www.forrester.com/blogs/predictions-2026-ai-moves-from-hype-to-hard-hat-work/)
- Tech Trends 2026: agentic AI strategy, 2025, Deloitte — [havola](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)

### Raqobatchi platformalar

- AI rule, 2024, Codeforces — [havola](https://codeforces.com/blog/entry/133941)
- AtCoder Datasets, 2025, AtCoder — [havola](https://datasets.atcoder.jp/)
- CodeChef Pro, 2025, CodeChef — [havola](https://www.codechef.com/pro)
- CodeSignal launches AI-assisted coding assessments and interviews, 2024, CodeSignal — [havola](https://codesignal.com/newsroom/press-releases/codesignal-launches-ai-assisted-coding-assessments-and-interviews-redefining-technical-hiring-in-the-ai-era/)
- cp.uz platformasi, 2025, cp.uz — [havola](https://cp.uz/)
- HackerRank's AI features, 2025, HackerRank — [havola](https://support.hackerrank.com/articles/9416207922-hackerrank%27s-ai-features)
- KEP.uz platformasi, 2025, KEP.uz — [havola](https://kep.uz/)
- LeetCode Premium, 2025, LeetCode — [havola](https://leetcode.com/subscribe/)
- Mass cheating using AI, 2024, Codeforces — [havola](https://codeforces.com/blog/entry/141199)
- RoboContest platformasi, 2025, RoboContest — [havola](https://robocontest.uz/)

### Texnik resurslar

- Codestral-22B-v0.1, 2024, Mistral AI — [havola](https://huggingface.co/mistralai/Codestral-22B-v0.1)
- Is my data used for model training?, 2024, Anthropic Privacy Center — [havola](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)
- Model Context Protocol specification, 2024, Anthropic / MCP — [havola](https://modelcontextprotocol.io/)
- Qwen2.5-Coder-32B-Instruct, 2024, Qwen — [havola](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct)
- Qwen2.5-Coder-7B-Instruct, 2024, Qwen — [havola](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- Zero data retention agreement, 2024, Anthropic Privacy Center — [havola](https://privacy.claude.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to)

---

## Metodologiya va cheklovlar

**Ishlab chiqarish jarayoni.** Hisobot 6 bosqichli tadqiqot jarayonida tayyorlandi: dastlabki razvedka → reja tuzish → har bir bo'lim bo'yicha chuqur tadqiqot (mustaqil manba izlash) → har bir bo'limni 6 mezon bo'yicha ko'rikdan o'tkazish → tuzatish va qayta ko'rik → yakuniy yig'ish. Har bir bo'lim kamida bitta mustaqil ko'rikdan o'tgan; qaytarilgan bo'limlar (2, 3, 6) tuzatilib, ikkinchi bosqichda qayta tekshirilgan va PASS olgan.

**Manbalar.** Hisobot 55 ta manbaga tayanadi (6 guruh). Manba turlari: analitik hisobotlar (Gartner, IDC, Forrester, Deloitte), konsalting so'rovlari (PwC, BCG/MIT SMR, Grant Thornton), rasmiy vendor va institut e'lonlari (Anthropic, Microsoft, Linux Foundation, Google, Salesforce, Klarna, ServiceNow), akademik maqolalar (arXiv, *Scientific Reports*), nufuzli texnologiya nashrlari (VentureBeat, CIO.com), platforma rasmiy sahifalari va model kartalari.

**Cheklovlar (ochiq aytilishi shart):**

1. **Ikkilamchi manbalar.** Bir qator raqamlar (JPMorgan 171% ROI, Klarna $60 mln/853 FTE, General Mills, Cevi prior-auth, telekom) faqat sanoat bloglari/agregatorlari orqali keltirilgan va birlamchi manbada tasdiqlanmagan. Ular matnda shunday belgilangan. Klarna misolida rasmiy press-reliz boshqa raqam beradi (700 FTE, ~$40 mln) — farq matnda ochiq ko'rsatilgan.
2. **Vendor hisobotlari.** Salesforce Agentforce, Microsoft Copilot, ServiceNow raqamlari vendorning o'z e'lonlari bo'lib, mustaqil audit bilan tasdiqlanmagan. Ular "vendor ma'lumotiga ko'ra" kontekstida o'qilishi kerak.
3. **Prognozlar — fakt emas.** 5-bo'limdagi barcha raqamlar bashorat. Gartner ichida ham turli qamrovdagi raqamlar uchraydi (33%/2028 vs 40%/2026) — bu matnda izohlangan.
4. **Production darajasi bo'yicha ziddiyat.** LangChain 57,3% "productionda" deydi, boshqa manbalar 11% productionda deydi. Farq tanlov (sample) tarkibida: LangChain so'rovi texnologiya/developer auditoriyasiga moyil. Raqamlar to'g'ridan-to'g'ri solishtirilmasligi kerak.
5. **Raqobatchilar bo'yicha salbiy dalil.** KEP, RoboContest va cp.uz bo'yicha "AI aniqlanmadi" xulosasi faqat ommaviy sahifalarga asoslangan — AI funksiyasi yo'qligini isbotlamaydi.
6. **RankWant bo'limi.** 6-bo'limdagi RankWant faktlari loyihaning o'z hujjatlaridan olingan va tashqi tekshiruvdan o'tmagan. Bu bo'lim — tavsiya xarakterida, qaror emas.

**Ochiq qolgan savollar (keyingi tadqiqot uchun):**

- Lokal modellarning (Qwen2.5-Coder-7B/32B) o'zbek tilidagi kod-feedback sifati qanday? Eksperimental o'lchov kerak.
- RankWant'ning hozirgi apparat quvvati (bitta mashina) 7B modelni production yuklamasida ko'tara oladimi?
- Anti-cheat uchun AI-kod aniqlashning aniqligi qanday — xato pozitiv darajasi qabul qilinadimi?
- O'zbek tilidagi CP kontentini AI bilan generatsiya qilish sifati va huquqiy tomoni (mualliflik) qanday?
- Contest rejimida AI'ni texnik jihatdan qanday ishonchli o'chirish mumkin (foydalanuvchi tashqi AI'dan foydalanishini aniqlash mumkinmi)?

---

> **Ogohlantirish:** ushbu hisobot AI tadqiqot jamoasi tomonidan tayyorlangan. Muhim qarorlar qabul qilishdan oldin asosiy raqamlar va manbalar mutaxassis tomonidan qayta tekshirilishi kerak. Ayniqsa ikkilamchi manbalarga tayangan raqamlar (2-bo'limdagi korporativ keyslar) va barcha prognozlar (5-bo'lim) — ehtiyotkorlik bilan ishlatilsin.
