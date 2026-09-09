# ADR-0014: Codeforces handle'i — tavsiyani urug'lantirish

**STATUS:** rejected (2026-09-09)
**Ta'siri:** yo'q — [ADR-0005](0005-content-strategy-own-content.md) 🔒 kuchida qoladi

## Muammo

Arxivda 2089 masala bor, ya'ni «keyin qaysi masala?» degan savol endi
haqiqiy. Lekin `recommend.py` yangi foydalanuvchi haqida hech nima
bilmaydi va hammani 800 dan boshlaydi. Codeforces'da 1700 reytingli
odam bizga kelsa, unga bir hafta davomida `a+b` darajasidagi masalalar
tavsiya qilinadi va u ketib qoladi.

Bu **sovuq start** muammosi va uni ichki ma'lumot bilan yechib
bo'lmaydi: ma'lumot hali yo'q, chunki odam endi keldi.

Codeforces API si (kalitsiz, ochiq) buni yopadi. `user.status` har bir
urinishni **masalaning reytingi va teglari bilan** qaytaradi — o'lchab
ko'rildi: 200 ta urinishdan `greedy 50 · dp 45 · math 44 · trees 30`
chiqadi, ya'ni birinchi kundanoq ham maqsad qiyinlik, ham
[mavzu kesimidagi kuch](../../apps/api/problems/views.py) ma'lum bo'ladi.

## Ziddiyat

[ADR-0005](0005-content-strategy-own-content.md) «to'liq mustaqil» ni
tanlagan va sababi aniq edi: **siz nazorat qilmaydigan uchinchi tomon
differensiator bo'la olmaydi**, va `cp_uz_article_id` uchinchi tomon
nomini schema darajasiga kiritardi.

Bu taklif o'sha qarorga tegadi, shuning uchun ADR kerak.

## Variantlar

1. **Qilmaymiz.** Sovuq start qoladi; foydalanuvchi bir hafta o'zi
   sozlab yuradi (`?difficulty=` filtri bor).
2. **Bir martalik, YOPIQ urug'.** Foydalanuvchi handle'ini kiritadi,
   biz `user.status` dan uning darajasini hisoblaymiz va **faqat
   tavsiya dvigatelini** urug'lantiramiz. Handle hech qayerda
   ko'rsatilmaydi, `rating_skills` ga TEGMAYDI, leaderboardga ta'siri
   yo'q.
3. **To'liq bog'langan profil** — handle profilda ko'rinadi, CF
   reytingi ko'rsatiladi. Egalikni tasdiqlash shart bo'ladi (CF da
   odatiy usul: profilga vaqtinchalik kod, yoki maxsus masalaga
   compile error yuborish).

## Qaror: 1-variant — qilmaymiz

Egasi 2026-09-09 da 1-variantni tanladi: [ADR-0005](0005-content-strategy-own-content.md)
ning «to'liq mustaqil» qarori **o'zgarmaydi**. Codeforces integratsiyasi
qurilmaydi.

Sovuq start boshqa yo'l bilan yopiladi — arxiv endi 2089 masaladan
iborat va [mavzu kesimidagi kuch](../../apps/api/problems/views.py)
bloki foydalanuvchining O'Z urinishlaridan birinchi kunlardayoq signal
beradi. Qiyinlik filtri esa qo'lda sozlanadi.

Quyidagi tahlil qayta muhokamaning oldini olish uchun saqlanadi.

## Rad etilgan tavsiya: 2-variant

ADR-0005 uchinchi tomonni **differensiator** va **schema bog'liqligi**
sifatida rad etgan. 2-variant ikkalasi ham emas:

- Codeforces yo'qolsa RankWant'da hech narsa buzilmaydi — urug' bir
  marta ishlatiladi va bizning ma'lumotimizga aylanadi.
- Schema'ga uchinchi tomon nomi kirmaydi: saqlanadigan narsa
  «boshlang'ich maqsad qiyinlik», handle emas.
- Differensiator emas — bu bir martalik qulaylik, va'da emas.

Egalikni tasdiqlash 2-variantda **kerak emas**, chunki yolg'on handle
kiritishdan hech qanday foyda yo'q: u faqat o'zingizga noto'g'ri
tavsiya beradi. 3-variantda esa tasdiqlash SHART — u yerda handle
ommaviy da'voga aylanadi.

## Xavflar

| Xavf | Mitigatsiya |
| ---- | ----------- |
| CF limiti (1 so'rov / 2 s) va og'ir tarix (10k+ urinish) | Celery vazifasi, so'rov ichida emas |
| CF ishlamay qolsa | Urug'lantirish jimgina o'tkazib yuboriladi — bu majburiy qadam emas |
| Foydalanuvchi «RankWant CF ga bog'liq» deb o'ylashi | UI da «ixtiyoriy, bir martalik» deb ataladi |

## Ochiq savol

Xuddi shu narsani KEP.uz uchun ham qilish mumkinmi? Ularning ochiq API
si `user.status` ga o'xshash endpoint bermaydi
([kep-import](../../apps/api/problems/kep.py)), ya'ni hozircha yo'q.
