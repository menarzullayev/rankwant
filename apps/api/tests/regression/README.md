# Regression — bir marta sodir bo'lgan xatolar

Bu papka **xususiyat** emas, **xulq-atvor** testlarini saqlaydi. Har bir test
shu repoda o'lchangan, haqiqiy xatoni qaytadan paydo bo'lishidan himoya
qiladi. Bittasi qizil bo'lsa — eski xato qaytgan.

## Nega alohida papka

`tests/` dagi testlar «funksiya ishlaydimi?» degan savolga javob beradi.
Bu yerdagilar esa «ilgari buzilgan narsa buzilmaganmi?» savoliga. Ularni
aralashtirish xato qidirishni qiyinlashtiradi: xususiyat testi qulaganda
yangi kod aybdor, regressiya testi qulaganda esa **eski xato qaytgan**.

## Hozirgi to'plam

| Test | Xato | Qayerda o'lchangan |
|---|---|---|
| `test_sample_echo_is_not_ac` | Namunaviy javobni chop etgan dastur `AC` olgan | `3-ta-son` — `print('3 2 1')` qabul qilingan |
| `test_reference_solution_is_ac` | Etalon yechim tekshirilmagan, holat oldinga yurgan | `readiness` holat-mashinasi (D8) |
| `test_reference_solution_not_ac_blocks` | Etalon yechim o'tmasa ham masala ochiq qolgan | D8 · S3 |
| `test_no_hidden_test_keeps_the_state` | Yashirin testsiz masala tekshirilgandek ko'ringan | D8 · S1 |

## Qo'shish tartibi

1. Xatoni **o'lchang** — qaysi masala, qaysi so'rov, qanday natija.
2. Testni shu papkaga yozing: avval qizil bo'lishi shart (tuzatishdan oldin).
3. `tools/check_negative.py` ga salbiy test qo'shing: test qizil berishini
   isbotlang. «Hech qachon yiqilmaydigan tekshiruv qabul qilinmaydi.»

## Ishlatish

```bash
python -m pytest tests/regression -v
```

Judge kerak emas: `conftest.py` dagi `ScriptedJudge` navbatni almashtiradi va
`submit()` ga zahoti javob qaytaradi — sandbox'siz, lekin zanjirning o'zi
(ish qurish · navbat · holat-mashinasi) haqiqiy.

**STATUS:** Regression to'plami — tayyor. WP1 (D8) bo'yicha 5 test; R6 va R7
shu yerda.
