# Qism niqoblarni sanab chiqish {#submask-enumeration}

## Berilgan niqobning barcha qism niqoblarini sanab chiqish {#enumerating-all-submasks-of-a-given-mask}

$m$ bit niqobi berilgan bo‘lsin. Uning barcha qism niqoblari, ya’ni faqat $m$ niqobida mavjud bitlar o‘rnatilgan $s$ niqoblari bo‘ylab samarali yurish kerak.

Bit amallari bilan bog‘liq hiylalarga asoslangan ushbu algoritm implementatsiyasini ko‘rib chiqamiz:

```cpp
int s = m;
while (s > 0) {
 ... you can use s ...
 s = (s-1) & m;
}
```

yoki yanada ixcham `for` operatoridan foydalanib:

```cpp
for (int s=m; s; s=(s-1)&m)
 ... you can use s ...
```

Kodning ikkala variantida ham nolga teng qism niqob qayta ishlanmaydi. Uni sikldan tashqarida qayta ishlashimiz yoki, masalan, unchalik chiroyli bo‘lmagan quyidagi tuzilishdan foydalanishimiz mumkin:

```cpp
for (int s=m; ; s=(s-1)&m) {
 ... you can use s ...
 if (s==0)  break;
}
```

Yuqoridagi kod nima sababdan $m$ ning barcha qism niqoblariga takrorlanmasdan va kamayish tartibida tashrif buyurishini ko‘rib chiqamiz.

Joriy $s$ bit niqobi berilgan va keyingi bit niqobga o‘tmoqchimiz, deb faraz qilaylik. $s$ niqobidan birni ayirganda, eng o‘ngdagi o‘rnatilgan bit olib tashlanadi va uning o‘ngidagi barcha bitlar 1 ga aylanadi. Keyin $m$ niqobida mavjud bo‘lmagani uchun qism niqobga kira olmaydigan barcha «ortiqcha» bir bitlarni olib tashlaymiz. Buni `(s-1) & m` bitli amali yordamida bajaramiz.
Natijada $s-1$ niqobini u olishi mumkin bo‘lgan eng katta qiymatgacha «kesamiz»; bu kamayish tartibida $s$ dan keyingi qism niqobdir.

Shunday qilib, bu algoritm har bir iteratsiyada atigi ikkita amal bajarib, berilgan niqobning barcha qism niqoblarini kamayish tartibida hosil qiladi.

$s = 0$ bo‘lgan hol alohida e’tibor talab qiladi. $s-1$ bajarilgach, barcha bitlari o‘rnatilgan niqob (-1 ning bitli ifodasi) hosil bo‘ladi, `(s-1) & m` dan keyin esa $s$ yana $m$ ga teng bo‘ladi. Shu sababli $s = 0$ niqobiga ehtiyot bo‘ling: agar sikl nolda tugamasa, algoritm cheksiz siklga kirib qolishi mumkin.

## Barcha niqoblar va ularning qism niqoblari bo‘ylab yurish. Murakkablik $O(3^n)$ {#iterating-through-all-masks-with-their-submasks-complexity-o3n}

Ko‘plab masalalarda, ayniqsa bit niqobi bo‘yicha dinamik dasturlash ishlatiladigan masalalarda, barcha bit niqoblar bo‘ylab va har bir niqob uchun uning barcha qism niqoblari bo‘ylab yurish talab qilinadi:

```cpp
for (int m=0; m<(1<<n); ++m)
 	for (int s=m; s; s=(s-1)&m)
 ... s and m ...
```

Ichki sikl jami $O(3^n)$ ta iteratsiya bajarishini isbotlaymiz.

**Birinchi isbot**: $i$-bitni ko‘rib chiqamiz. U uchun aynan uchta imkoniyat bor:

1. u $m$ niqobiga kiritilmagan (demak, $s$ qism niqobiga ham kiritilmagan),
2. u $m$ ga kiritilgan, ammo $s$ ga kiritilmagan, yoki
3. u ham $m$, ham $s$ ga kiritilgan.

Jami $n$ ta bit bo‘lgani uchun, $3^n$ ta turli kombinatsiya mavjud bo‘ladi.

**Ikkinchi isbot**: $m$ niqobida $k$ ta yoqilgan bit bo‘lsa, uning $2^k$ ta qism niqobi bo‘lishiga e’tibor bering. $k$ ta yoqilgan bitli niqoblar soni jami $\binom{n}{k}$ ta bo‘lgani uchun ([binomial koeffitsiyentlar](/algorithms/combinatorics/binomial-coefficients)ga qarang), barcha niqoblar bo‘yicha kombinatsiyalarning umumiy soni:

$$
\sum_{k=0}^n \binom{n}{k} \cdot 2^k
$$

Bu sonni hisoblash uchun yuqoridagi yig‘indi binom teoremasi bo‘yicha $(1+2)^n$ yoyilmasiga teng ekaniga e’tibor bering. Demak, isbotlash talab qilinganidek, $3^n$ ta kombinatsiya bor.

## Mashq masalalari {#practice-problems}

* [Atcoder - Close Group](https://atcoder.jp/contests/abc187/tasks/abc187_f)
* [Codeforces - Nuclear Fusion](http://codeforces.com/problemset/problem/71/E)
* [Codeforces - Sandy and Nuts](http://codeforces.com/problemset/problem/599/E)
* [Uva 1439 - Exclusive Access 2](https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=4185)
* [UVa 11825 - Hackers' Crackdown](https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=2925)
