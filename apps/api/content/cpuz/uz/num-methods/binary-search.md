# Ikkilik qidiruv {#binary-search}

**Ikkilik qidiruv** qidiruv oralig‘ini ikki qismga bo‘lish orqali biror narsani tezroq topish imkonini beradigan usuldir. Uning eng keng tarqalgan qo‘llanishi tartiblangan massivlarda qiymat qidirish, biroq oraliqni bo‘lish g‘oyasi boshqa ko‘plab odatiy masalalarda ham hal qiluvchi ahamiyatga ega.

## Tartiblangan massivda qidirish {#search-in-sorted-arrays}

Ikkilik qidiruvga olib keladigan eng odatiy masala quyidagicha. Sizga tartiblangan $A_0 \leq A_1 \leq \dots \leq A_{n-1}$ massiv berilgan; $k$ soni ketma-ketlikda bor-yo‘qligini tekshirish kerak. Eng sodda yechim — har bir elementni birma-bir tekshirib, $k$ bilan solishtirish (bu chiziqli qidiruv deyiladi). Bu yondashuv $O(n)$ vaqtda ishlaydi, ammo massiv tartiblanganidan foydalanmaydi.

![Massivdan 7 qiymatini ikkilik qidiruv bilan topish](https://upload.wikimedia.org/wikipedia/commons/8/83/Binary_Search_Depiction.svg)

*Massivda $7$ qiymatini ikkilik qidiruv bilan topish*.

*[Tasvir](https://commons.wikimedia.org/wiki/File:Binary_Search_Depiction.svg) muallifi [AlwaysAngry](https://commons.wikimedia.org/wiki/User:AlwaysAngry), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en) litsenziyasi ostida tarqatiladi.*

Endi $A_L \leq k \leq A_R$ bo‘ladigan ikkita $L < R$ indeks ma’lum deb faraz qilaylik. Massiv tartiblangani uchun $k$ yo $A_L, A_{L+1}, \dots, A_R$ orasida uchraydi, yo massivda umuman yo‘q, deb xulosa qilish mumkin. Agar $L < M < R$ shartni qanoatlantiradigan ixtiyoriy $M$ indeksni tanlab, $k$ ning $A_M$ dan kichik yoki katta ekanini tekshirsak, ikki mumkin bo‘lgan holat yuzaga keladi:

1. $A_L \leq k \leq A_M$. Bu holda masalani $[L, R]$ dan $[L, M]$ ga keltiramiz;
1. $A_M \leq k \leq A_R$. Bu holda masalani $[L, R]$ dan $[M, R]$ ga keltiramiz.

$M$ ni tanlashning iloji bo‘lmasa, ya’ni $R = L + 1$ bo‘lsa, $k$ ni to‘g‘ridan-to‘g‘ri $A_L$ va $A_R$ bilan solishtiramiz. Aks holda $M$ ni faol kesmani _eng yomon holatda_ ham imkon qadar tez bitta elementgacha qisqartiradigan qilib tanlagan bo‘lardik.

Eng yomon holatda biz doim $[L, M]$ va $[M, R]$ dan kattasiga o‘tamiz. Demak, eng yomon holatda kesma $R-L$ dan $\max(M-L, R-M)$ gacha qisqaradi. Bu qiymatni minimallashtirish uchun $M \approx \frac{L+R}{2}$ ni tanlash kerak, shunda

$$
M-L \approx \frac{R-L}{2} \approx R-M.
$$

Boshqacha aytganda, eng yomon holat nuqtai nazaridan $M$ ni doim $[L, R]$ ning o‘rtasidan olib, uni teng ikkiga bo‘lish optimal. Shunda faol kesma o‘lchami $1$ ga yetguncha har qadamda ikki barobar qisqaradi. Demak, jarayon $h$ qadam talab qilsa, oxirida $R$ va $L$ orasidagi farq $R-L$ dan $\frac{R-L}{2^h} \approx 1$ gacha kamayadi va $2^h \approx R-L$ tenglama hosil bo‘ladi.

Ikkala tomondan $\log_2$ olsak, $h \approx \log_2(R-L) \in O(\log n)$ ni olamiz.

Qadamlarning logarifmik soni chiziqli qidiruvdagidan keskin yaxshi. Masalan, $n \approx 2^{20} \approx 10^6$ uchun chiziqli qidiruvda taxminan million amal bajarish kerak, ikkilik qidiruvda esa atigi taxminan $20$ amal.

### Quyi va yuqori chegara {#lower-bound-and-upper-bound}

Ko‘pincha elementning aniq o‘rnini emas, $k$ dan katta yoki unga teng birinchi element o‘rnini (massivda $k$ ning **quyi chegarasi** deyiladi) yoki $k$ dan katta birinchi element o‘rnini ($k$ ning **yuqori chegarasi** deyiladi) topish qulay bo‘ladi.

Quyi va yuqori chegaralar birgalikda massivdagi $k$ ga teng elementlardan iborat, bo‘sh bo‘lishi ham mumkin bo‘lgan yarim intervalni beradi. $k$ massivda borligini tekshirish uchun uning quyi chegarasini topib, mos element $k$ ga tengligini tekshirish yetarli.

### Implementatsiya {#implementation}

Yuqoridagi tushuntirish algoritmning taxminiy tavsifini beradi. Implementatsiya tafsilotlari uchun aniqroq bo‘lishimiz kerak.

$A_L \leq k < A_R$ bo‘ladigan $L < R$ juftligini saqlab boramiz. Ya’ni faol qidiruv oralig‘i $[L, R)$. Bu yerda $[L, R]$ kesma o‘rniga yarim intervaldan foydalanamiz, chunki u chekka holatlar bilan kamroq ishlashni talab qilishi ma’lum bo‘ladi.

$R = L+1$ bo‘lganda, yuqoridagi ta’riflardan $R$ — $k$ ning yuqori chegarasi ekani kelib chiqadi. $R$ ni oxiridan keyingi indeks, ya’ni $R=n$, $L$ ni esa boshidan oldingi indeks, ya’ni $L=-1$ bilan boshlash qulay. Algoritmda $A_L$ va $A_R$ ni hech qachon to‘g‘ridan-to‘g‘ri hisoblamasak va ularni formal ravishda $A_L = -\infty$ hamda $A_R = +\infty$ deb qarasak, bu to‘g‘ri bo‘ladi.

Nihoyat, tanlanadigan $M$ qiymatini aniq belgilash uchun $M = \lfloor \frac{L+R}{2} \rfloor$ ni tanlaymiz.

U holda implementatsiya quyidagicha ko‘rinishi mumkin:

```cpp
... // tartiblangan massiv a[0], a[1], ..., a[n-1] ko‘rinishida saqlanadi
int l = -1, r = n;
while (r - l > 1) {
    int m = (l + r) / 2;
    if (k < a[m]) {
        r = m; // a[l] <= k < a[m] <= a[r]
    } else {
        l = m; // a[l] <= a[m] <= k < a[r]
    }
}
```

Algoritm bajarilishi davomida $L < M < R$ bo‘lgani uchun $A_L$ ham, $A_R$ ham hech qachon hisoblanmaydi. Oxirida $L$ — $k$ dan katta bo‘lmagan oxirgi element indeksi (bunday element bo‘lmasa $-1$), $R$ esa $k$ dan katta birinchi element indeksi (bunday element bo‘lmasa $n$) bo‘ladi.

**Eslatma.** `m = (r + l) / 2` deb hisoblash `l` va `r` ikkita musbat butun son bo‘lsa, toshib ketishga olib kelishi mumkin; bu xato JDK da taxminan 9 yil saqlanib qolgan, bu [blog yozuvida](https://ai.googleblog.com/2006/06/extra-extra-read-all-about-it-nearly.html) tasvirlangan. Muqobil yondashuvlardan biri — `m = l + (r - l) / 2` deb yozish: u musbat butun `l` va `r` uchun doim ishlaydi, lekin `l` manfiy son bo‘lsa, baribir toshib ketishi mumkin. C++20 dan foydalansangiz, u `m = std::midpoint(l, r)` ko‘rinishida muqobil yechim taklif qiladi, u doim to‘g‘ri ishlaydi.

## Ixtiyoriy predikat bo‘yicha qidirish {#search-on-arbitrary-predicate}

$f : \{0,1,\dots, n-1\} \to \{0, 1\}$ — $0,1,\dots,n-1$ da aniqlangan, monoton o‘suvchi, ya’ni

$$
f(0) \leq f(1) \leq \dots \leq f(n-1).
$$

bo‘lgan mantiqiy funksiya bo‘lsin.

Yuqorida tasvirlangan ikkilik qidiruv massivni $k < A_M$ ifodaning mantiqiy qiymatini saqlovchi $f(M)$ predikat bo‘yicha ajratadi.
$k < A_M$ o‘rniga ixtiyoriy monoton predikatdan foydalanish mumkin. Bu, ayniqsa, $f(k)$ ni hisoblash har bir mumkin bo‘lgan qiymat uchun amalda hisoblab bo‘lmaydigan darajada ko‘p vaqt talab qilganda foydali.
Boshqacha aytganda, ikkilik qidiruv, agar shunday _o‘tish nuqtasi_ mavjud bo‘lsa, $f(L) = 0$ va $f(R)=f(L+1)=1$ bo‘ladigan yagona $L$ indeksni topadi; agar $f(0) = \dots = f(n-1) = 0$ bo‘lsa, $L = n-1$ ni, agar $f(0) = \dots = f(n-1) = 1$ bo‘lsa, $L = -1$ ni beradi.

To‘g‘rilik isboti (o‘tish nuqtasi mavjud, ya’ni $f(0)=0$ va $f(n-1)=1$ deb faraz qilamiz): implementatsiya _sikl invarianti_ $f(l)=0, f(r)=1$ ni saqlaydi. $r - l > 1$ bo‘lganda $m$ ning tanlanishi $r-l$ ning doim kamayishini bildiradi. Sikl $r - l = 1$ bo‘lganda tugaydi va bu bizga kerakli o‘tish nuqtasini beradi.

```cpp
... // f(i) — f(0) <= ... <= f(n-1) bo‘ladigan mantiqiy funksiya
int l = -1, r = n;
while (r - l > 1) {
    int m = (l + r) / 2;
    if (f(m)) {
        r = m; // 0 = f(l) < f(m) = 1
    } else {
        l = m; // 0 = f(m) < f(r) = 1
    }
}
```

### Javob bo‘yicha ikkilik qidiruv {#binary-search-on-the-answer}

Bunday holat ko‘pincha biror qiymatni hisoblash so‘ralganda, lekin biz faqat shu qiymat kamida $i$ ekanini tekshira olgandagina uchraydi. Masalan, sizga $a_1,\dots,a_n$ massiv berilgan va $r-l \geq x$ bo‘ladigan barcha mumkin bo‘lgan $l,r$ juftliklari orasida pastga yaxlitlangan eng katta o‘rtacha yig‘indini topish so‘ralgan:

$$
\left \lfloor \frac{a_l + a_{l+1} + \dots + a_r}{r-l+1} \right\rfloor
$$

Bu masalani yechishning sodda usullaridan biri — javob kamida $\lambda$ ekanini, ya’ni quyidagi tengsizlik o‘rinli bo‘ladigan $l, r$ juftligi mavjudligini tekshirish:

$$
\frac{a_l + a_{l+1} + \dots + a_r}{r-l+1} \geq \lambda.
$$

Unga teng kuchli ravishda, uni quyidagicha qayta yozish mumkin:

$$
(a_l - \lambda) + (a_{l+1} - \lambda) + \dots + (a_r - \lambda) \geq 0,
$$

demak, endi yangi $a_i - \lambda$ massivda uzunligi kamida $x+1$ va yig‘indisi manfiy bo‘lmagan qism massiv bor-yo‘qligini tekshirish kerak, buni prefiks yig‘indilari yordamida bajarish mumkin.

## Uzluksiz qidiruv {#continuous-search}

$f : \mathbb R \to \mathbb R$ funksiya $[L, R]$ kesmada uzluksiz haqiqiy qiymatli funksiya bo‘lsin.

Umumiylikni yo‘qotmasdan $f(L) \leq f(R)$ deb faraz qilamiz. [Oraliq qiymatlar teoremasidan](https://en.wikipedia.org/wiki/Intermediate_value_theorem) har bir $y \in [f(L), f(R)]$ uchun $f(x) = y$ bo‘ladigan $x \in [L, R]$ mavjudligi kelib chiqadi. E’tibor bering: oldingi paragraflardan farqli o‘laroq, funksiyaning monoton bo‘lishi _shart emas_.

$x$ qiymatini istalgan aniq $\delta$ uchun $\pm\delta$ aniqlikda $O\left(\log \frac{R-L}{\delta}\right)$ vaqtda yaqinlashtirish mumkin. G‘oya asosan bir xil: $M \in (L, R)$ ni olsak, $f(M)$ ning $y$ dan katta-kichikligiga qarab qidiruv oralig‘ini $[L, M]$ yoki $[M, R]$ gacha qisqartira olamiz. Bu yerda keng tarqalgan misollardan biri — toq darajali ko‘phadlarning ildizlarini topish.

Masalan, $f(x)=x^3 + ax^2 + bx + c$ bo‘lsin. U holda $L \to -\infty$ va $R \to +\infty$ da $f(L) \to -\infty$ va $f(R) \to +\infty$. Bu $f(L) < 0$ va $f(R) > 0$ bo‘ladigan yetarlicha kichik $L$ va yetarlicha katta $R$ ni har doim topish mumkinligini bildiradi. Shundan keyin ikkilik qidiruv yordamida $f(x)=0$ bo‘ladigan $x$ ni o‘z ichiga olgan istalgancha kichik oraliqni topish mumkin.

## Ikkining darajalari bilan qidirish {#search-with-powers-of-2}

Ikkilik qidiruvni bajarishning yana bir e’tiborga loyiq usuli — faol kesmani saqlash o‘rniga joriy $i$ ko‘rsatkichni va joriy $k$ darajani saqlash. Ko‘rsatkich $i=L$ dan boshlanadi, keyin har iteratsiyada predikat $i+2^k$ nuqtada tekshiriladi. Agar predikat hamon $0$ bo‘lsa, ko‘rsatkich $i$ dan $i+2^k$ ga suriladi, aks holda o‘z joyida qoladi; so‘ng $k$ daraja $1$ ga kamaytiriladi.

Bu paradigma daraxtlar bilan bog‘liq masalalarda, masalan, ikki tugunning eng yaqin umumiy ajdodini yoki ma’lum tugunning muayyan balandlikdagi ajdodini topishda keng qo‘llanadi. Uni, masalan, Fenwick daraxtida $k$-noldan farqli elementni topish uchun ham moslashtirish mumkin.

## Mashq masalalari {#practice-problems}

- [LeetCode — Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/)
- [LeetCode — Search Insert Position](https://leetcode.com/problems/search-insert-position/)
- [LeetCode — First Bad Version](https://leetcode.com/problems/first-bad-version/)
- [LeetCode — Valid Perfect Square](https://leetcode.com/problems/valid-perfect-square/)
- [LeetCode — Find Peak Element](https://leetcode.com/problems/find-peak-element/)
- [LeetCode — Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)
- [LeetCode — Find Right Interval](https://leetcode.com/problems/find-right-interval/)
- [Codeforces 706B — Interesting Drink](https://codeforces.com/problemset/problem/706/B/)
- [Codeforces 670D1 — Magic Powder 1](https://codeforces.com/problemset/problem/670/D1)
- [Codeforces 165C — Another Problem on Strings](https://codeforces.com/problemset/problem/165/C)
- [Codeforces 760B — Frodo and Pillows](https://codeforces.com/problemset/problem/760/B)
- [Codeforces 551C — GukiZ Hates Boxes](https://codeforces.com/problemset/problem/551/C)
- [Codeforces 645C — Enduring Exodus](https://codeforces.com/problemset/problem/645/C)
- [Codeforces 590B — Chip ’n Dale Rescue Rangers](https://codeforces.com/problemset/problem/590/B)
- [Codeforces 251A — Points on Line](https://codeforces.com/problemset/problem/251/A)
