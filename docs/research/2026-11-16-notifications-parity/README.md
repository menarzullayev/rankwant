# Bildirishnomalar: Robocontest bilan solishtirma va qarorlar

**Sana:** 2026-11-16. **Manba:** Saidakbar aka keltirgan Robocontest yangilanishi (49 tur, 14 guruh)
va RankWant kodi (`apps/api/notifications/`, `tools/notification-codes.json`).
**Holat:** qarorlar qabul qilingan, kod hali yozilmagan (ikki katta PR rejalashtirilgan).

Robocontest tomonida kanallar va tur bo'yicha sozlama ro'yxatdan ko'rinmaydi, shuning uchun u tomon
faqat **tur** bo'yicha solishtirilgan.

## RankWant bugun (kodda tekshirilgan)

- 35 ta kod (`message_catalog.py`), 8 ta umumiy tur (`Notification.Kind`); sozlama **8 tur × 3 kanal**.
- Kanallar: sayt (standart yoqiq), Telegram va email (standart o'chiq, 2026-11-10 qarori).
- Sayt: qo'ng'iroq paneli, `/notifications`, SSE orqali jonli, «ko'rildi ≠ o'qildi», 10 tilda matn.
- `rating_changed`, `quest_awarded`, `system` turlari bor, lekin ularga kod yozilmagan.
- Vaqtga bog'liq xabar yo'q (beat bor, vazifa yozilmagan); xavfsizlik xabarlari faqat tasdiqlash,
  tiklash va «email o'zgardi» xatlari (bildirishnoma emas).

## Robocontest turi → RankWant

✅ bor · 🟡 qisman · ❌ yo'q · ➖ funksiyaning o'zi yo'q

| Guruh | Tur | RankWant |
|---|---|---|
| Jamoalar | taklif, javob, sardor, bekor (4) | ➖ |
| Sinflar | sinfga taklif | 🟡 |
| | taklif bekor | ➖ |
| Musobaqalar | e'lonlar | ✅ `contest_announcement` |
| | hakam savolimga javob berdi | ✅ `contest_answer` |
| | natijalar va reyting | ✅ `contest_result` |
| | ishtirokim o'zgarishi | 🟡 `contest_disqualified` |
| | moderatorlikka taklif | 🟡 `contest_tester` |
| | moderatorlikdan chiqarish, musobaqaga taklif, 1 kun / 1 soat qoldi (2), reyting bekor | ❌ |
| | sovrin kuponi | ➖ |
| Yangi musobaqalar | e'lon | ❌ |
| Testlar | testga taklif | ❌ |
| Urinishlar | natijasi o'zgardi | ❌ |
| Seriya | natijalar | 🟡 `streak` |
| | uzilish arafasida, uzildi | ❌ |
| Shikoyatlar | 3 tur | ❌ |
| Tarif | 3 tur | ➖ (`billing` bayrog'i o'chiq) |
| Hisob xavfsizligi | email o'zgardi, parol tiklandi | 🟡 (xat bor, bildirishnoma yo'q) |
| | yangi qurilma, Telegram ulandi, parol o'zgardi, o'chirish rejasi / bekor | ❌ |
| Men o'tkazayotgan | qatnashchidan savol | ✅ `contest_question` |
| | 1 soat qoldi, tugadi, moderator javobi, antiplagiat | ❌ |
| Mening sinflarim | qo'shilish so'rovi | ✅ `classroom_join_requested` |
| | taklifimga javob, o'quvchi chiqdi | ❌ |
| Masalalarim va testlarim | masala arxivga, test ommaviy | ❌ |
| Hakam ruxsati va limitlar | 3 tur | ➖ |

Hisob: 49 turdan ✅ 6, 🟡 6, ➖ ≈10, ❌ ≈27.
RankWant'da bo'lib Robocontest ro'yxatida yo'qlari (≈28): duel (5), hack (6), murabbiylik (4),
izoh javobi va @eslatma (2), blog, kurslar (3), masala qayta baholandi, masala ko'rigi,
hackathon bahosi, AI ustoz byudjeti, sinfga qo'shilish tasdig'i va rad etilishi.

## Qarorlar (egasi, 2026-11-16, AskUserQuestion)

1. **Qamrov:** to'rt bo'shliq guruhining hammasi — hisob xavfsizligi, vaqt xabarlari, tashkilotchi
   vositalari, sinf/shikoyat/test/masalam. Hamma 49 tur uchun kod va matn oldindan qo'shiladi.
2. **Funksiyasi yo'q turlar «uxlab yotadi»:** kod, 10 tilda matn va test bor; chiqaruvchi (emitter)
   yo'q va sozlamalarda ko'rinmaydi (hero qarori: tayyor bo'lmagan narsa ko'rsatilmaydi).
   Sabab: `check_notification_codes.py` kodni o'chirishga yo'l qo'ymaydi, shuning uchun har kod doimiy.
3. **Sozlama granulyarligi:** 8 tur o'rniga ~14 guruh (guruh × 3 kanal).
4. **Kanallar:** sayt, Telegram, email. Yangi kanal (web push, digest) hozir yo'q.
5. **Hisob xavfsizligi:** sayt kanali majburiy (o'chirib bo'lmaydi); email va Telegram ixtiyoriy,
   standart o'chiq (2026-11-10 email qarori o'zgarmaydi).
6. **Vaqt:** musobaqa — 24 soat va 1 soat oldin (faqat ro'yxatdan o'tganlarga); seriya —
   Toshkent 20:00, uzilishga 4 soat qolganda; har tur bir marta, beat har 5 daqiqada tekshiradi.
7. **Tartib:** ikkita katta PR.

## Guruhlar (taklif)

| # | Guruh | Ichida |
|---|---|---|
| 1 | Hisob xavfsizligi | yangi qurilma, parol o'zgardi / tiklandi, email o'zgardi, Telegram ulandi, o'chirish rejasi / bekor |
| 2 | Musobaqa (ishtirokchi) | e'lon, hakam javobi, natija, ishtirok o'zgarishi, 1 kun / 1 soat, reyting bekor, taklif |
| 3 | Yangi musobaqalar | yangi musobaqa e'loni |
| 4 | Musobaqa tashkilotchisi | savol, 1 soat qoldi, tugadi, antiplagiat, moderator javobi |
| 5 | Moderatorlik | taklif, chiqarilish, tester |
| 6 | Sinf (o'quvchi) | taklif, bekor, qo'shilish tasdig'i / rad |
| 7 | Mening sinflarim | so'rov, taklifga javob, o'quvchi chiqdi |
| 8 | Test va urinishlar | testga taklif, urinish natijasi, masala qayta baholandi |
| 9 | Seriya | yutuq, uzilish arafasida, uzildi |
| 10 | Shikoyat va mening kontentim | 3 shikoyat turi, masala arxivga, test ommaviy, ko'rik so'rovi |
| 11 | Raqobat | duel, hack, hackathon |
| 12 | Hamjamiyat va ustozlik | izoh, @eslatma, blog, murabbiy, kurslar |
| 13 | Tarif va limitlar | tarif (3), hakam ruxsati (3), AI ustoz byudjeti |
| 14 | Jamoa va sovrinlar | jamoa (4), sovrin kuponi |

## Ochiq

- «Yangi qurilmadan kirish» qurilmani tanishga muhtoj; hozir sessiya jadvalida qurilma belgisi bormi
  — kodda aniqlanadi. Yo'q bo'lsa, bu tur birinchi PR'da uxlab yotganlar qatoriga o'tadi.
- Mavjud `notify_prefs` (tur bo'yicha) yangi guruhlarga ko'chiriladi; eski kalitlar o'qiladi.
