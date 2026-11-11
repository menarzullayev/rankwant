# Uchburchakning yo‘nalgan yuzi {#oriented-area-of-a-triangle}

Uchta $p_1$, $p_2$ va $p_3$ nuqta berilgan. Ular hosil qilgan uchburchakning yo‘nalgan (ishorali) yuzini hisoblang. Yuzning ishorasi quyidagicha aniqlanadi: tasavvur qiling, siz tekislikda $p_1$ nuqtada turibsiz va yuzingiz $p_2$ tomonga qaragan. Siz $p_2$ ga borasiz va agar $p_3$ sizning o‘ng tomoningizda qolsa (u holda uch vektor “soat mili bo‘yicha” buriladi deymiz), yuzning ishorasi manfiy, aks holda musbat bo‘ladi. Agar uchta nuqta bir to‘g‘ri chiziqda yotsa, yuz nolga teng.

Shu ishorali yuz yordamida biz oddiy (ishorasiz) yuzni ham (ishorali yuzning moduli sifatida) olishimiz, nuqtalar berilgan tartibda soat mili bo‘yicha yoki unga teskari joylashganini ham aniqlashimiz mumkin (bu, masalan, qavariq qobiq algoritmlarida foydali).

## Hisoblash {#calculation}
$2\times 2$ matritsa determinanti matritsaning ustun (yoki satr) vektorlariga qurilgan parallelogrammning ishorali yuziga teng ekanidan foydalanamiz.
Bu ikki o‘lchamli vektor ko‘paytma ta’rifining o‘xshashidir ([Asosiy geometriya](/algorithms/geometry/basic-geometry) maqolasiga qarang).
Bu yuzni ikkiga bo‘lib, bizni qiziqtirgan uchburchak yuzini olamiz.
Ustun vektorlari sifatida $\vec{p_1p_2}$ va $\vec{p_2p_3}$ ni olamiz va $2\times 2$ determinantni hisoblaymiz:

$$2S=\left|\begin{matrix}x_2-x_1 & x_3-x_2\\y_2-y_1 & y_3-y_2\end{matrix}\right|=(x_2-x_1)(y_3-y_2)-(x_3-x_2)(y_2-y_1)$$

## Implementatsiya {#implementation}

```cpp
int signed_area_parallelogram(point2d p1, point2d p2, point2d p3) {
    return cross(p2 - p1, p3 - p2);
}

double triangle_area(point2d p1, point2d p2, point2d p3) {
    return abs(signed_area_parallelogram(p1, p2, p3)) / 2.0;
}

bool clockwise(point2d p1, point2d p2, point2d p3) {
    return signed_area_parallelogram(p1, p2, p3) < 0;
}

bool counter_clockwise(point2d p1, point2d p2, point2d p3) {
    return signed_area_parallelogram(p1, p2, p3) > 0;
}
```

## Mashq masalalari {#practice-problems}
* [Codechef - Chef and Polygons](https://www.codechef.com/problems/CHEFPOLY)
