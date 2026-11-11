# Uchlik qidiruv {#ternary-search}

Bizga $[l, r]$ oraliqda **unimodal** bo‘lgan $f(x)$ funksiya berilgan. Unimodal funksiya deganda funksiyaning ikki xatti-harakatidan biri tushuniladi:

1. Funksiya avval qat’iy o‘sadi, maksimumga erishadi (bitta nuqtada yoki oraliqda), so‘ng qat’iy kamayadi.

2. Funksiya avval qat’iy kamayadi, minimumga erishadi, so‘ng qat’iy o‘sadi.

Ushbu maqolada birinchi holatni nazarda tutamiz.
Ikkinchi holat birinchisiga to‘liq simmetrik.

Vazifa — $f(x)$ funksiyaning $[l, r]$ oraliqdagi maksimumini topish.

## Algoritm {#algorithm}

Shu oraliqdagi ixtiyoriy 2 ta $m_1$ va $m_2$ nuqtani ko‘rib chiqamiz: $l < m_1 < m_2 < r$. Funksiyani $m_1$ va $m_2$ nuqtalarda hisoblaymiz, ya’ni $f(m_1)$ va $f(m_2)$ qiymatlarini topamiz. Endi uch variantdan biri chiqadi:

-   $f(m_1) < f(m_2)$

    Izlanayotgan maksimum $m_1$ ning chap tomonida, ya’ni $[l, m_1]$ oraliqda bo‘la olmaydi, chunki yo $m_1$ va $m_2$ nuqtalarning ikkalasi, yo faqat $m_1$ funksiya o‘suvchi sohaga tegishli. Har ikki holatda ham maksimumni $[m_1, r]$ kesmada izlash kerak bo‘ladi.

-   $f(m_1) > f(m_2)$

    Bu vaziyat avvalgisiga simmetrik: maksimum $m_2$ ning o‘ng tomonida, ya’ni $[m_2, r]$ oraliqda bo‘la olmaydi va qidiruv sohasi $[l, m_2]$ kesmagacha qisqaradi.

-   $f(m_1) = f(m_2)$

    Ko‘rish mumkinki, yo bu ikki nuqtaning ikkalasi funksiya qiymati maksimal bo‘lgan sohaga tegishli, yo $m_1$ qiymatlar o‘sayotgan, $m_2$ esa kamayayotgan sohada (bu yerda funksiyaning qat’iy o‘sishi/kamayishidan foydalandik). Demak, qidiruv sohasi $[m_1, m_2]$ gacha qisqaradi. Kodni soddalashtirish uchun bu holatni oldingi holatlarning biri bilan birlashtirish mumkin.

Shunday qilib, ikkita ichki nuqtadagi qiymatlarni taqqoslash asosida joriy $[l, r]$ oraliqni yangi, qisqaroq $[l^\prime, r^\prime]$ oraliq bilan almashtirishimiz mumkin. Tavsiflangan jarayonni oraliqqa qayta-qayta qo‘llab, ixtiyoriy darajada qisqa oraliq hosil qilish mumkin. Oxir-oqibat uning uzunligi oldindan belgilangan biror o‘zgarmasdan (aniqlikdan) kichik bo‘ladi va jarayonni to‘xtatish mumkin. Bu sonli usul, shuning uchun shundan keyin funksiya oxirgi $[l, r]$ oraliqning barcha nuqtalarida o‘zining maksimumiga erishadi deb hisoblash mumkin. Umumiylikni yo‘qotmasdan, qaytariladigan qiymat sifatida $f(l)$ ni olish mumkin.

Biz $m_1$ va $m_2$ nuqtalarni tanlashga hech qanday cheklov qo‘ymadik. Bu tanlov implementatsiyaning yaqinlashish tezligi va aniqligini belgilaydi. Eng keng tarqalgan usul — nuqtalarni $[l, r]$ oraliqni uchta teng qismga bo‘ladigan qilib tanlash. Shunda

$$
m_1 = l + \frac{(r - l)}{3}
$$

$$
m_2 = r - \frac{(r - l)}{3}
$$

Agar $m_1$ va $m_2$ bir-biriga yaqinroq tanlansa, yaqinlashish tezligi biroz oshadi.

### Ishlash vaqtini tahlil qilish {#run-time-analysis}

$$
T(n) = T({2n}/{3}) + O(1) = \Theta(\log n)
$$

Buni quyidagicha tasavvur qilish mumkin: funksiyani $m_1$ va $m_2$ nuqtalarda hisoblagandan so‘ng har safar oraliqning taxminan uchdan birini, chap yoki o‘ng qismini, e’tiborga olmaymiz. Shunday qilib, qidiruv sohasi o‘lchami asl o‘lchamning ${2n}/{3}$ qismiga teng bo‘ladi.

[Master teoremasini](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms)) qo‘llab, kerakli murakkablik bahosini olamiz.

### Butun argumentli holat {#the-case-of-the-integer-arguments}

Agar $f(x)$ butun parametr qabul qilsa, $[l, r]$ oraliq diskret bo‘ladi. $m_1$ va $m_2$ nuqtalarni tanlashga hech qanday cheklov qo‘ymaganimiz uchun algoritmning to‘g‘riligiga ta’sir qilmaydi. $m_1$ va $m_2$ ni baribir $[l, r]$ ni taxminan teng 3 qismga bo‘ladigan qilib tanlash mumkin.

Farq algoritmning to‘xtash shartida yuzaga keladi. Uchlik qidiruv $(r - l) < 3$ bo‘lganda to‘xtashi kerak, chunki bu holda $m_1$ va $m_2$ ni bir-biridan hamda $l$ va $r$ dan farqli qilib tanlab bo‘lmaydi, bu esa cheksiz siklga olib kelishi mumkin. $(r - l) < 3$ bo‘lgach, $f(x)$ ning maksimal qiymatini beradigan nuqtani topish uchun nomzod nuqtalarning qolgan to‘plamini $(l, l + 1, \ldots, r)$ tekshirish kerak.

### Oltin kesim bo‘yicha qidiruv {#golden-section-search}

Ba’zi hollarda $f(x)$ ni hisoblash ancha sekin bo‘lishi mumkin, lekin aniqlik muammolari tufayli iteratsiyalar sonini kamaytirib bo‘lmaydi. Yaxshiyamki, $f(x)$ ni har bir iteratsiyada (birinchisidan tashqari) faqat bir marta hisoblash mumkin.

Buni qanday qilishni ko‘rish uchun $m_1$ va $m_2$ ni tanlash usuliga qaytamiz. Faraz qilaylik, $m_1$ va $m_2$ ni $[l, r]$ da shunday tanlaymizki, $\frac{r - l}{r - m_1} = \frac{r - l}{m_2 - l} = \varphi$ bo‘lsin, bu yerda $\varphi$ — qandaydir o‘zgarmas. Hisoblashlar hajmini kamaytirish uchun keyingi iteratsiyada yangi hisoblanadigan $m_1'$, $m_2'$ nuqtalardan biri $m_1$ yoki $m_2$ bilan ustma-ust tushadigan $\varphi$ ni tanlamoqchimiz, shunda allaqachon hisoblangan funksiya qiymatidan qayta foydalanish mumkin bo‘ladi.

Endi joriy iteratsiyadan keyin $l = m_1$ deb o‘rnatdik deylik. Unda $m_1'$ nuqta $\frac{r - m_1}{r - m_1'} = \varphi$ ni qanoatlantiradi. Biz bu nuqta $m_2$ bilan ustma-ust tushishini istaymiz, ya’ni $\frac{r - m_1}{r - m_2} = \varphi$ bo‘lishi kerak.

$\frac{r - m_1}{r - m_2} = \varphi$ tenglikning ikkala tomonini $\frac{r - m_2}{r - l}$ ga ko‘paytirib, $\frac{r - m_1}{r - l} = \varphi\frac{r - m_2}{r - l}$ ni olamiz. Shunga e’tibor bering: $\frac{r - m_1}{r - l} = \frac{1}{\varphi}$ va $\frac{r - m_2}{r - l} = \frac{r - l + l - m_2}{r - l} = 1 - \frac{1}{\varphi}$. Buni o‘rniga qo‘yib va $\varphi$ ga ko‘paytirib, quyidagi tenglamani olamiz:

$\varphi^2 - \varphi - 1 = 0$

Bu mashhur oltin kesim tenglamasi. Uni yechsak, $\frac{1 \pm \sqrt{5}}{2}$ chiqadi. $\varphi$ musbat bo‘lishi kerakligi uchun $\varphi = \frac{1 + \sqrt{5}}{2}$ ni olamiz. Xuddi shu mulohazani $r = m_2$ deb o‘rnatib, $m_2'$ ning $m_1$ bilan ustma-ust tushishini istagan holatga qo‘llasak, $\varphi$ ning aynan shu qiymati chiqadi. Demak, $m_1 = l + \frac{r - l}{1 + \varphi}$ va $m_2 = r - \frac{r - l}{1 + \varphi}$ ni tanlasak, har iteratsiyada oldingi iteratsiyada hisoblangan $f(x)$ qiymatlaridan birini qayta ishlatish mumkin.

## Implementatsiya {#implementation}

```cpp
double ternary_search(double l, double r) {
	double eps = 1e-9;				//xato chegarasini shu yerda belgilang
	while (r - l > eps) {
		double m1 = l + (r - l) / 3;
		double m2 = r - (r - l) / 3;
		double f1 = f(m1);		//funksiyani m1 nuqtada hisoblaydi
		double f2 = f(m2);		//funksiyani m2 nuqtada hisoblaydi
		if (f1 < f2)
			l = m1;
		else
			r = m2;
	}
	return f(l);					//[l, r] dagi f(x) maksimumini qaytaradi
}
```

Bu yerdagi `eps` aslida mutlaq xato (funksiyani noaniq hisoblashdan kelib chiqadigan xatolar hisobga olinmaydi).

`r - l > eps` mezoni o‘rniga to‘xtash mezoni sifatida iteratsiyalarning o‘zgarmas sonini tanlash mumkin. Iteratsiyalar soni kerakli aniqlikni ta’minlaydigan qilib tanlanishi kerak. Odatda ko‘pchilik dasturlash musobaqalarida xato chegarasi ${10}^{-6}$ bo‘ladi, shuning uchun 200 - 300 iteratsiya yetarli. Bundan tashqari, iteratsiyalar soni $l$ va $r$ qiymatlariga bog‘liq emas, shuning uchun iteratsiyalar soni kerakli nisbiy xatoga mos keladi.

## Mashq masalalari {#practice-problems}

- [Codeforces - New Bakery](https://codeforces.com/problemset/problem/1978/B)
- [Codechef - Race time](https://www.codechef.com/problems/AMCS03)
- [Hackerearth - Rescuer](https://www.hackerearth.com/problem/algorithm/rescuer-2d2495cb/)
- [Spoj - Building Construction](http://www.spoj.com/problems/KOPC12A/)
- [Codeforces - Weakness and Poorness](http://codeforces.com/problemset/problem/578/C)
* [LOJ - Closest Distance](http://lightoj.com/volume_showproblem.php?problem=1146)
* [GYM - Dome of Circus (D)](http://codeforces.com/gym/101309)
* [UVA - Galactic Taxes](https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=4898)
* [GYM - Chasing the Cheetahs (A)](http://codeforces.com/gym/100829)
* [UVA - 12197 - Trick or Treat](https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=3349)
* [SPOJ - Building Construction](http://www.spoj.com/problems/KOPC12A/)
* [Codeforces - Devu and his Brother](https://codeforces.com/problemset/problem/439/D)
* [Codechef - Is This JEE ](https://www.codechef.com/problems/ICM2003)
* [Codeforces - Restorer Distance](https://codeforces.com/contest/1355/problem/E)
* [TIMUS 1058 Chocolate](https://acm.timus.ru/problem.aspx?space=1&num=1058)
* [TIMUS 1436 Billboard](https://acm.timus.ru/problem.aspx?space=1&num=1436)
* [TIMUS 1451 Beerhouse Tale](https://acm.timus.ru/problem.aspx?space=1&num=1451)
* [TIMUS 1719 Kill the Shaitan-Boss](https://acm.timus.ru/problem.aspx?space=1&num=1719)
* [TIMUS 1913 Titan Ruins: Alignment of Forces](https://acm.timus.ru/problem.aspx?space=1&num=1913)
