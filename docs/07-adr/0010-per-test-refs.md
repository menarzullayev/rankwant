# ADR-0010: Job da har test uchun alohida S3 havolasi

**STATUS:** accepted (2026-09-06)
**Ta'siri:** [08-technical-spec](../08-technical-spec/README.md) 🔒 dagi `testset_ref` maydoni almashtiriladi

## Muammo

Qulflangan spesifikatsiya job'da bitta katalog havolasini belgilaydi:

```json
"testset_ref": "s3://…/problem-42/tests/"
```

Amalga oshirishda ikkita to'siq chiqdi:

1. **Subtask'lar.** `TestCase` har testni `subtask` va `points` bilan
   bog'laydi ([05-domain-model](../05-domain-model/README.md)). Katalog
   havolasi bu bog'lanishni tashiy olmaydi — judge katalogdagi fayllarni
   qaysi subtask'ga tegishli ekanini bilmaydi.
2. **Katalog ro'yxatlash.** Bitta havola judge'ni S3 `ListObjects` ga
   majbur qiladi va tartibni fayl nomidan taxmin qilishga qoldiradi.
   Har test uchun aniq havola bunga o'rin qoldirmaydi.

## Qaror

Job testlarni ro'yxat sifatida yuboradi, har birida aniq havola:

```json
"tests": [{"index": 1, "input_ref": "s3://…/1.in", "output_ref": "s3://…/1.out"}]
```

Ma'lumot oqimi o'zgarmaydi: test DB da emas, S3 da; judge S3 dan o'qiydi,
API/DB ga ulanmaydi ([08-technical-spec](../08-technical-spec/README.md)
xavfsizlik chegarasi buzilmaydi).

## Oqibatlar

- Judge S3 mijoziga muhtoj (`minio-go`), kredensiallar `S3_*` orqali.
- Testlar takror so'ralgani uchun worker'da xotira keshi bor.
- Inline `input`/`expected` maydonlari saqlanadi: bake-off harness'i
  S3'siz ishlaydi.
- Shartnoma `tools/check_contract.py` orqali CI da tekshiriladi.
