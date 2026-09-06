# ADR-0004: Judge engine — o'z engine'imiz, sandbox bake-off bilan

**STATUS:** proposed (2026-09-06) — bake-off natijasidan keyin `accepted` bo'ladi

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

## Bake-off — ikki nomzod sinaladi

Qaror **o'lchovga** qoldirildi. Ikkala nomzod ham `JudgeProvider` interfeysi ortida quriladi:

| # | Nomzod                 | Sandbox litsenziyasi | Izoh                                                          |
| - | ---------------------- | -------------------- | ------------------------------------------------------------- |
| **A** | **Go worker + nsjail** | **Apache-2.0** ✅    | Google saqlaydi; namespace + seccomp-bpf + cgroups; <20ms start; bitta binary deploy |
| **B** | **Python worker + isolate** | GPL-2.0+       | IOI va CMS ishlatadigan CP standarti, eng ko'p sinovdan o'tgan; backend bilan bitta til; cgroup v1 ga bog'liq |

### Baholash mezonlari

| Mezon                                        | Nega hal qiluvchi                                              |
| -------------------------------------------- | -------------------------------------------------------------- |
| cgroup v2 muvofiqligi                        | GRUB hack keraksiz bo'lsa — ops yuki keskin kamayadi           |
| Kerakli privilegiya darajasi                 | `--privileged` talab qilinmasa host xavfi tushadi              |
| Sandbox start latency (p50 / p95)            | PRD maqsadi: **p50 < 5s, p95 < 15s** — nomzod shu byudjetga sig'ishi kerak |
| CPU/wall time va peak memory o'lchash aniqligi | TLE/MLE adolatliligi — **reyting ishonchliligi** shunga bog'liq |
| Til konfiguratsiyasi qulayligi               | 20+ compiler saqlash narxi                                     |
| Interactive masala qo'llab-quvvatlashi       | ICPC formati uchun shart                                       |
| Kod hajmi va saqlash yuki                    | Kichik jamoa uchun hal qiluvchi                                |

Bake-off rejasi: [../09-development-plan/README.md](../09-development-plan/README.md) — Sprint 0.

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
