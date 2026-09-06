# ADR-0004: Judge engine — o'z engine'imiz, sandbox bake-off bilan

**STATUS:** accepted (2026-09-06) — bake-off o'tkazildi, g'olib: **Go + nsjail**

## Muammo

Kod ijro etish OJ ning yadrosi va eng xavfli qismi. Uch variant bor edi: tayyor Judge0 ni ishlatish, DMOJ engine'ini olish, yoki o'z engine'imizni qurish.

Vision principle #1 **«o'z engine va UX»** deydi; principle #6 esa **«DMOJ/custom yoki litsenziyali engine»** — ya'ni custom aynan ruxsat etilgan.

## Tanlov

**O'z judge engine'imizni quramiz** — lekin **sandbox primitivini o'zimiz yozmaymiz**.

### Qatlamlar va mas'uliyat

| Qatlam                                        | Kim         | Sabab                                                                                  |
| --------------------------------------------- | ----------- | -------------------------------------------------------------------------------------- |
| **1. Sandbox primitivi** (namespace, seccomp, cgroup) | ❌ tayyor olamiz | CVE'lar aynan shu yerda yashaydi — Judge0 ning o'zi 2024 da 3 ta escape → **host root** oldi (CVE-2024-29021 / 28185 / 28189, v1.13.1 da tuzatilgan) |
| **2. Judge worker / orchestrator**            | ✅ o'zimiz  | Queue → compile → N test → checker → verdict → resurs statistikasi. Biznes logika, ~3–6 hafta |
| **3. Til obrazlari** (20+ compiler)           | ✅ o'zimiz  | Versiyalar pin qilinadi, reproducible                                                  |

### Nega o'z engine — funksional sabab

Bu «mustaqillik» uchun emas, aniq talablar uchun:

- PRD [P0-3](../04-prd/README.md) dagi **20 verdict kodi** o'zimizniki
- **Partial scoring / IOI subtask** grading — Judge0 buni tabiiy qilmaydi
- **Interactive masalalar** (ICPC formatida uchraydi) — Judge0 da yo'q
- Judge0 ning `--privileged` + **cgroup v1** talabi yo'qoladi (zamonaviy Linux cgroup v2 da; Judge0 uchun GRUB'ga `systemd.unified_cgroup_hierarchy=0` yozish kerak)
- GPL masalasi butunlay tushadi (nsjail = Apache-2.0)

## Bake-off natijasi (2026-09-06)

Ikkala nomzod ham bir xil shartnoma, bir xil 14 case va bir xil host'da o'lchandi.
To'liq hisobotlar: [result-judge-go.md](../../services/bakeoff/result-judge-go.md) ·
[result-judge-py.md](../../services/bakeoff/result-judge-py.md)

**Ikkalasi ham O'TDI** — 13/13 bajarilgan case, 5 izolyatsiya sinovining hammasi.

| Case | A — Go + nsjail | B — Python + isolate |
| ---- | ---------------: | -------------------: |
| `01-aplusb` | 831 ms | 846 ms |
| `03-tle-cpu` | **1333 ms** | 1418 ms |
| `04-idleness` | 3003 ms | **2604 ms** |
| `08-ole` | **12 ms** | 14 ms |
| `09-fork-bomb` | 3004 ms | **2104 ms** |
| Yuklama p50 / p95 (30 parallel) | 836 / 839 ms | 825 / 833 ms |

Dastlabki o'lchovda A `08-ole` da 2007 ms va `03-tle-cpu` da 2818 ms ko'rsatgan
edi. Ikkalasi ham **implementatsiya nuqsoni** bo'lib chiqdi va tuzatildi
(pastga qarang) — shundan keyin A ikkala ko'rsatkichda ham B dan tezroq.

### Tuzatilgan taxmin — isolate cgroup v2 da ISHLAYDI

Bu ADR dastlab «isolate cgroup v1 talab qiladi, GRUB o'zgartirib reboot kerak»
deb yozgan edi. **Bu noto'g'ri.** isolate master cgroup v2 ni qo'llab-quvvatlaydi.

Haqiqiy muammo boshqa: isolate'ning standart konfiguratsiyasi
`cg_root = auto:/run/isolate/cgroup` systemd boshqaradigan cgroup'ni kutadi, va
uning `cg-keeper` i konteynerning **o'z** cgroup'ida `subtree_control` yoqmoqchi
bo'lib `Device or resource busy` oladi — cgroup v2 da jarayonlari bor cgroup
kontrollerlarni delegatsiya qila olmaydi.

Yechim judge-go dagi bilan bir xil: root ostida **toza** cgroup yaratib,
kontrollerlarni o'zimiz delegatsiya qilamiz va `cg_root` ni unga yo'naltiramiz.
Shundan keyin `cg-mem` limiti aniq majburlanadi (`cg-oom-killed:1`).

Ya'ni **litsenziya va ops jihatidan B ni chetlatadigan asos yo'q edi** —
qaror boshqa mezonlar bo'yicha qabul qilinishi kerak.

## Tanlov: A — Go + nsjail

B tezroq bo'lsa ham A tanlandi. Sabablari **performance emas**:

1. **Apache-2.0 vs GPL-2.0.** O'z-o'zini hosting qilishda ikkalasi ham muammosiz
   (tarqatish yo'q → copyleft majburiyati yo'q). Lekin PRD Phase 2 da
   **maktab/universitet judge rejasi** bor — agar judge appliance sifatida
   yetkazilsa, bu tarqatish bo'ladi. Apache-2.0 o'sha yo'lni ochiq qoldiradi.
2. **isolate — setuid root binary.** Eng yuqori xavfli host'da doimiy setuid
   root komponent qo'shimcha hujum yuzasi. nsjail setuid talab qilmaydi.
3. **Bitta binary deploy.** Judge hostlar gorizontal miqyoslanadi; Go binary
   uchun interpretator, paketlar yoki virtualenv kerak emas.

### B aniqlagan nuqsonlar — A da YOPILDI

Bake-off B ni tanlashga olib kelmadi, lekin A dagi **uchta haqiqiy nuqsonni**
ko'rsatdi. Bular nsjail kamchiligi emas, `judge-go` implementatsiyasiniki:

| Nuqson | Oldin → keyin | Tuzatish |
| ------ | ------------- | -------- |
| Chiqish chegarasida jarayon o'ldirilmasdi | 2007 → **12 ms** | `capBuffer` chegaraga yetganda kontekstni bekor qiladi |
| `--rlimit_cpu` faqat butun soniya | 2818 → **1333 ms** | cgroup `cpu.stat` ni 20 ms da pollovchi kuzatuvchi |
| Kompilyatsiya masalaning ish vaqti limitidan foydalanardi | har C++ submission CE | kompilyatsiya `compile_time_ms` byudjetidan foydalanadi |

Uchinchisi **yashirin buzilish** edi: CPU kuzatuvchisi qo'shilgunicha bilinmagan,
chunki `--rlimit_cpu` yaxlitlash tufayli g++ ga yetarli vaqt qolardi.

### O'tkazuvchanlik va sig'im

| Worker | O'tkazuvchanlik | p50 | p95 |
| ------ | --------------- | --- | --- |
| 1 | 2.4 submit/s | 848 ms | 857 ms |
| 2 | 3.3 submit/s | 867 ms | 882 ms |
| 4 | 5.4 submit/s | 899 ms | 952 ms |
| 8 | 8.0 submit/s | 984 ms | 1360 ms |

Miqyoslash **chiziqli emas** — 8 worker 8× emas, 3.3× beradi. Sabab: `total_ms`
ning ~830 ms i **kompilyatsiya**, u CPU-bound va bitta host yadrolari cheklangan.

PRD NFR contest spike'da 500 submit / 10 s (= 50 submit/s) talab qiladi. Bir
host'da bunga yetib bo'lmaydi — ikki richag bor:

1. **Ko'p judge host** — arxitektura bunga tayyor (pull protokoli, ADR-0004)
2. **Kompilyatsiya keshi** — bir xil manba qayta yuborilganda (rejudge, bir xil
   yechim) kompilyatsiya o'tkazib yuboriladi. Eng katta yutuq shu yerda.

Batafsil sig'im rejasi: [10-operations](../10-operations/README.md).

### judge-py taqdiri

Kod **saqlanadi** (`services/judge-py`), lekin faol emas. Sabab: `JudgeProvider`
shartnomasi ikkalasini ham qoplaydi, va yuqoridagi nuqsonlar A da yopilmasa
yoki litsenziya sharoiti o'zgarsa, B ga qaytish arzon bo'lib qoladi.

## Oraliq yechim

MVP submit oqimini erta ishga tushirish uchun **Judge0** (yoki managed sandbox) `JudgeProvider` ortida oraliq provider sifatida ishlatiladi. Mahsulot kodi engine almashganda **o'zgarmaydi**.

Judge0 ishlatilsa majburiy shartlar: **≥ v1.13.1**, default DB parolini almashtirish, `enable_network` o'chirilgan, API faqat o'z backend'imizdan chaqiriladi.

## Ish olish protokoli — PULL (2026-09-06)

O'z engine'imiz uchun **worker navbatdan ish tortib oladi**; API judge'ga hech qachon so'rov yubormaydi.

| | Pull (tanlandi) | Push (Judge0 modeli) |
| - | --------------- | -------------------- |
| Judge host'da kiruvchi port | **yo'q** | HTTP port ochiq |
| Hujum yuzasi | minimal | foydalanuvchi kodi ishlaydigan hostga kiruvchi yo'l |
| Miqyoslash | worker qo'shiladi | balanser kerak |

Sabab: sandbox escape tarixi (Judge0 da 3 ta CVE → host root) borligini hisobga olsak, eng xavfli mashinaga kiruvchi trafik yo'lini **umuman ochmaslik** eng arzon himoya.

Oqibat: judge host faqat **chiquvchi** ulanish qiladi (Redis navbat + S3 test data + natija yozish). Tarmoq qoidasi: judge → API/DB **yo'q**, judge → Redis/S3 **ha**.

Judge0 oraliq provider sifatida push bo'lib qoladi — `JudgeProvider` shartnomasi ikkalasini ham qoplaydi (`submit` = navbatga qo'yish yoki HTTP POST; `poll` = natija o'qish).

## JudgeProvider shartnomasi (draft)

```
submit(source, language, limits, testset)  -> job_id
poll(job_id)                                -> status | result
result: verdict, per_test[], time_ms, memory_kb, compile_output
cancel(job_id)
languages()                                 -> [{id, name, version, compile_cmd, run_cmd}]
```

## Xavfsizlik shartlari (muzokara qilinmaydi)

- Judge host **hech qachon** API/DB bilan bir serverda emas — alohida `judge.rankwant.uz`
- Judge hostdan tashqi tarmoqqa chiqish yopiq
- Foydalanuvchi kodi hech qachon API hostida ishlamaydi
- **Ommaviy launch oldidan tashqi xavfsizlik auditi majburiy**
- Til obrazlari va sandbox versiyalari pin qilinadi, CVE kuzatuvi yoqiladi

## Oqibatlar

- Sprint 0 ga bake-off spike'i kiradi (~1–2 hafta)
- O'z engine'i ~3–6 hafta boshlang'ich ish + doimiy til obrazlari xizmati
- Xavfsizlik mas'uliyati **bizda** — bu qabul qilingan narx, chunki u yadro kompetensiya
- Bake-off g'olibi aniqlangach bu ADR `accepted` ga o'tadi va yutgan variant yoziladi

## Bog'liq hujjatlar

- [0003-stack-django-next.md](0003-stack-django-next.md)
- [../06-architecture/README.md](../06-architecture/README.md)
