# RMQ — oraliqdagi eng kichik element {#range-minimum-query}

$A[1..N]$ massiv berilgan.
Siz $(L, R)$ ko‘rinishidagi so‘rovlarga javob berishingiz kerak: $A$ massivning $L$ va $R$ pozitsiyalari orasidagi (chegaralar ham kiradi) eng kichik elementini topish.

RMQ masalalarda bevosita uchrashi yoki boshqa vazifalarda qo‘llanishi mumkin, masalan, [eng yaqin umumiy ajdod](/algorithms/graph/lca) masalasida.

## Yechim {#solution}

RMQ masalasini yechish uchun ishlatish mumkin bo‘lgan ko‘plab yondashuvlar va ma’lumotlar tuzilmalari mavjud.

Ushbu saytda tushuntirilganlari quyida keltirilgan.

Avval so‘rovlarga javob berish orasida massivni o‘zgartirishga imkon beradigan yondashuvlar.

- [Kvadrat ildizli dekompozitsiya](/algorithms/data-structures/sqrt-decomposition) — har bir so‘rovga $O(\sqrt{N})$ da javob beradi, oldindan ishlov berish $O(N)$ da bajariladi.
  Afzalligi: juda sodda ma’lumotlar tuzilmasi. Kamchiligi: murakkabligi yomonroq.
- [Segment daraxti](/algorithms/data-structures/segment-tree) — har bir so‘rovga $O(\log N)$ da javob beradi, oldindan ishlov berish $O(N)$ da bajariladi.
  Afzalligi: yaxshi vaqt murakkabligi. Kamchiligi: boshqa ma’lumotlar tuzilmalariga nisbatan kod hajmi kattaroq.
- [Fenwick daraxti](/algorithms/data-structures/fenwick) — har bir so‘rovga $O(\log N)$ da javob beradi, oldindan ishlov berish $O(N \log N)$ da bajariladi.
  Afzalligi: eng qisqa kod, yaxshi vaqt murakkabligi. Kamchiligi: Fenwick daraxtini faqat $L = 1$ bo‘lgan so‘rovlar uchun ishlatish mumkin, shuning uchun u ko‘plab masalalarga mos kelmaydi.

Quyida esa faqat statik massivlar bilan ishlaydigan yondashuvlar keltirilgan, ya’ni butun ma’lumotlar tuzilmasini qayta hisoblamasdan massivdagi qiymatni o‘zgartirib bo‘lmaydi.

- [Siyrak jadval](/algorithms/data-structures/sparse-table) — har bir so‘rovga $O(1)$ da javob beradi, oldindan ishlov berish $O(N \log N)$ da bajariladi.
  Afzalligi: sodda ma’lumotlar tuzilmasi, a’lo vaqt murakkabligi.
- [Sqrt daraxti](/algorithms/data-structures/sqrt-tree) — so‘rovlarga $O(1)$ da javob beradi, oldindan ishlov berish $O(N \log \log N)$ da bajariladi. Afzalligi: tez. Kamchiligi: amalga oshirish murakkab.
- [Ajralgan to‘plamlar birlashmasi (DSU) / Arpa usuli](/algorithms/data-structures/disjoint-set-union#arpa) — so‘rovlarga $O(1)$ da javob beradi, oldindan ishlov berish $O(n)$ da bajariladi. Afzalligi: qisqa, tez. Kamchiligi: faqat barcha so‘rovlar oldindan ma’lum bo‘lganda ishlaydi, ya’ni so‘rovlarni faqat oflayn qayta ishlashni qo‘llab-quvvatlaydi.
- [Dekart daraxti](/algorithms/graph/rmq-linear) va [Farach-Colton va Bender algoritmi](/algorithms/graph/lca-farachcoltonbender) — so‘rovlarga $O(1)$ da javob beradi, oldindan ishlov berish $O(n)$ da bajariladi. Afzalligi: optimal murakkablik. Kamchiligi: kod hajmi katta.

Izoh: oldindan ishlov berish — berilgan massiv uchun mos ma’lumotlar tuzilmasini qurish orqali uni dastlabki qayta ishlashdir.

## Mashq masalalari {#practice-problems}

- [SPOJ — Range Minimum Query](http://www.spoj.com/problems/RMQSQ/)
- [CodeChef — Chef and Array](https://www.codechef.com/problems/FRMQ)
- [Codeforces 1454F — Array Partition](https://codeforces.com/contest/1454/problem/F)
