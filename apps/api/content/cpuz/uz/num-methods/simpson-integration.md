# Simpson formulasi bilan integrallash {#integration-by-simpsons-formula}

Quyidagi aniq integralning qiymatini hisoblashimiz kerak:

$$
\int_a ^ b f (x) dx
$$

Bu yerda tavsiflangan yechim **Thomas Simpson**ning dissertatsiyalaridan birida 1743-yilda e’lon qilingan.

## Simpson formulasi {#simpsons-formula}

$n$ biror natural son bo‘lsin. Integrallash kesmasi $[a, b]$ ni $2n$ ta teng qismga bo‘lamiz:

$$
x_i = a + i h, ~~ i = 0 \ldots 2n,
$$

$$
h = \frac {b-a} {2n}.
$$

Endi integralni $[x_ {2i-2}, x_ {2i}]$, $i = 1 \ldots n$ kesmalarning har birida alohida hisoblaymiz, so‘ng barcha qiymatlarni qo‘shamiz.

Aytaylik, navbatdagi $[x_ {2i-2}, x_ {2i}],  i = 1 \ldots n$ kesmani ko‘rib chiqamiz. Unda $f(x)$ funksiyani $(x_ {2i-2}, x_ {2i-1}, x_ {2i})$ nuqtalar orqali o‘tadigan $P(x)$ parabola bilan almashtiramiz. Bunday parabola doim mavjud va yagona; uni analitik usulda topish mumkin.
Masalan, uni Lagrange ko‘phad interpolyatsiyasi yordamida qurish mumkin.
Endi faqat shu ko‘phadni integrallash qoladi.
Buni umumiy $f$ funksiya uchun bajarsangiz, juda sodda ifodaga ega bo‘lasiz:

$$
\int_{x_ {2i-2}} ^ {x_ {2i}} f (x) ~dx \approx \int_{x_ {2i-2}} ^ {x_ {2i}} P (x) ~dx = \left(f(x_{2i-2}) + 4f(x_{2i-1})+(f(x_{2i})\right)\frac {h} {3}
$$

Bu qiymatlarni barcha kesmalar bo‘yicha qo‘shib, yakuniy **Simpson formulasi**ni olamiz:

$$
\int_a ^ b f (x) dx \approx \left(f (x_0) + 4 f (x_1) + 2 f (x_2) + 4f(x_3) + 2 f(x_4) + \ldots + 4 f(x_{2N-1}) + f(x_{2N}) \right)\frac {h} {3}
$$

## Xatolik {#error}

Integralni Simpson formulasi bilan yaqinlashtirishdagi xatolik quyidagiga teng:

$$
-\tfrac{1}{90} \left(\tfrac{b-a}{2}\right)^5 f^{(4)}(\xi)
$$

bu yerda $\xi$ — $a$ va $b$ orasidagi biror son.

Xatolik asimptotik jihatdan $(b-a)^5$ ga proporsional. Biroq yuqoridagi mulohazalar $(b-a)^4$ ga proporsional xatolikni ko‘rsatadi. Simpson qoidasi qo‘shimcha bir tartibga yutadi, chunki integral ostidagi funksiya hisoblanadigan nuqtalar $[a, b]$ kesmada simmetrik taqsimlangan.

## Implementatsiya {#implementation}

Bu yerda $f(x)$ — foydalanuvchi tomonidan aniqlangan biror funksiya.

```cpp
const int N = 1000 * 1000; // number of steps (already multiplied by 2)

double simpson_integration(double a, double b){
    double h = (b - a) / N;
    double s = f(a) + f(b); // a = x_0 and b = x_2n
    for (int i = 1; i <= N - 1; ++i) { // Refer to final Simpson's formula
        double x = a + h * i;
        s += f(x) * ((i & 1) ? 4 : 2);
    }
    s *= h / 3;
    return s;
}
```

## Mashq masalalari {#practice-problems}

* [Latin American Regionals 2012 - Environment Protection](https://matcomgrader.com/problem/9335/environment-protection/)
