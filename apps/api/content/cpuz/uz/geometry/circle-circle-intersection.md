# Ikki aylananing kesishmasi {#circle-circle-intersection}

Tekislikda ikkita aylana berilgan, ularning har biri markazining koordinatalari va radiusi bilan tavsiflanadi. Ularning kesishish nuqtalarini toping (mumkin bo‘lgan holatlar: bitta yoki ikkita nuqta, kesishmaslik yoki aylanalarning ustma-ust tushishi).

## Yechim {#solution}

Bu masalani [aylana va to‘g‘ri chiziq kesishmasi masalasi](/algorithms/geometry/circle-line-intersection)ga keltiramiz.

Umumiylikni yo‘qotmasdan birinchi aylananing markazi koordinatalar boshida deb faraz qilamiz (agar bunday bo‘lmasa, koordinatalar boshini birinchi aylananing markaziga ko‘chirib, chiqarish paytida kesishish nuqtalarining koordinatalarini mos ravishda to‘g‘rilashimiz mumkin). Ikki tenglamadan iborat sistemaga ega bo‘lamiz:

$$x^2+y^2=r_1^2$$

$$(x - x_2)^2 + (y - y_2)^2 = r_2^2$$

O‘zgaruvchilarning ikkinchi darajalaridan qutulish uchun ikkinchi tenglamadan birinchisini ayiramiz:

$$x^2+y^2=r_1^2$$

$$x \cdot (-2x_2) + y \cdot (-2y_2) + (x_2^2+y_2^2+r_1^2-r_2^2) = 0$$

Shunday qilib, dastlabki masalani birinchi aylana va to‘g‘ri chiziqning kesishish nuqtalarini topish masalasiga keltirdik:

$$Ax + By + C = 0$$

$$\begin{align}
A &= -2x_2 \\
B &= -2y_2 \\
C &= x_2^2+y_2^2+r_1^2-r_2^2
\end{align}$$

Bu masalani [tegishli maqolada](/algorithms/geometry/circle-line-intersection) bayon qilinganidek yechish mumkin.

Alohida ko‘rib chiqishimiz kerak bo‘lgan yagona maxsus holat — aylanalarning markazlari ustma-ust tushishi. Bu holda $x_2=y_2=0$ bo‘ladi va to‘g‘ri chiziq tenglamasi $C = r_1^2-r_2^2 = 0$ ko‘rinishini oladi. Agar aylanalarning radiuslari bir xil bo‘lsa, kesishish nuqtalari cheksiz ko‘p; agar farq qilsa, kesishish yo‘q.

## Mashq masalalari {#practice-problems}

- [RadarFinder](https://community.topcoder.com/stat?c=problem_statement&pm=7766)
- [Runaway to a shadow - Codeforces Round #357](http://codeforces.com/problemset/problem/681/E)
- [ASC 1 Problem F "Get out!"](http://codeforces.com/gym/100199/problem/F)
- [SPOJ: CIRCINT](http://www.spoj.com/problems/CIRCINT/)
- [UVA - 10301 - Rings and Glue](https://uva.onlinejudge.org/index.php?option=onlinejudge&page=show_problem&problem=1242)
- [Codeforces 933C A Colorful Prospect](https://codeforces.com/problemset/problem/933/C)
- [TIMUS 1429 Biscuits](https://acm.timus.ru/problem.aspx?space=1&num=1429)
