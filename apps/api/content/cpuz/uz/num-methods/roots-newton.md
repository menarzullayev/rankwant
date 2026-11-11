# Ildiz topish uchun Newton usuli

Bu iteratsion usulni Isaac Newton taxminan 1664-yilda ixtiro qilgan. Biroq usul ba’zan Raphson usuli deb ham ataladi: Raphson xuddi shu algoritmni Newtondan bir necha yil keyin ixtiro qilgan, ammo uning maqolasi ancha oldin nashr etilgan.

Masala quyidagicha. Quyidagi tenglama berilgan:

$$f(x) = 0$$

Tenglamani yechish kerak. Aniqrog‘i, uning ildizlaridan birini topish kerak (ildiz mavjud deb faraz qilinadi). $f(x)$ funksiya $[a, b]$ oraliqda uzluksiz va differensiallanuvchi deb faraz qilinadi.

## Algoritm

Algoritmning kirish parametrlari faqat $f(x)$ funksiyadan emas, balki boshlang‘ich yaqinlashuvdan, ya’ni algoritm boshlanadigan biror $x_0$ dan ham iborat.

![plot_f(x)](/algorithms-media/num-methods/roots_newton.png)

Faraz qilaylik, $x_i$ ni allaqachon hisoblab bo‘ldik; $x_{i+1}$ ni quyidagicha hisoblaymiz. $f(x)$ funksiya grafigiga $x = x_i$ nuqtada urinma o‘tkazamiz va bu urinmaning $x$ o‘qi bilan kesishish nuqtasini topamiz. $x_{i+1}$ topilgan nuqtaning $x$-koordinatasiga teng deb olinadi va butun jarayon boshidan takrorlanadi.

Quyidagi formulani hosil qilish qiyin emas:

$$ x_{i+1} = x_i - \frac{f(x_i)}{f^\prime(x_i)} $$

Avval $f(x)$ ning hosilasi — $f'(x)$ qiyalikni hisoblaymiz, so‘ng urinma tenglamasini aniqlaymiz:

$$ y - f(x_i) = f'(x_i)(x - x_i) $$

Urinma $x$ o‘qi bilan $y = 0$ va $x = x_{i+1}$ koordinatada kesishadi:

$$ - f(x_i) = f'(x_i)(x_{i+1} - x_i) $$

Endi tenglamani yechib, $x_{i+1}$ qiymatini olamiz.

Agar $f(x)$ funksiya “yaxshi” (silliq) bo‘lsa va $x_i$ ildizga yetarlicha yaqin bo‘lsa, $x_{i+1}$ izlanayotgan ildizga yanada yaqin bo‘lishi ko‘z oldimizga ayon.

Yaqinlashish tezligi kvadratik: shartli aytganda, bu taqribiy $x_i$ qiymatdagi to‘g‘ri raqamlar soni har bir iteratsiyada ikki baravar ortishini bildiradi.

## Kvadrat ildizni hisoblashda qo‘llash

Newton usulini kvadrat ildizni hisoblash misolida ko‘ramiz.

$f(x) = x^2 - n$ deb olib, ifodani soddalashtirsak, quyidagini hosil qilamiz:

$$ x_{i+1} = \frac{x_i + \frac{n}{x_i}}{2} $$

Masalaning birinchi odatiy varianti: ratsional $n$ soni berilgan va uning ildizini biror `eps` aniqlikda hisoblash kerak:

```cpp
double sqrt_newton(double n) {
	const double eps = 1E-15;
	double x = 1;
	for (;;) {
		double nx = (x + n / x) / 2;
		if (abs(x - nx) < eps)
			break;
		x = nx;
	}
	return x;
}
```

Masalaning yana bir keng tarqalgan varianti: butun ildizni hisoblash kerak (berilgan $n$ uchun $x^2 \le n$ shartni qanoatlantiradigan eng katta $x$ ni topish). Bu yerda algoritmning to‘xtash shartini biroz o‘zgartirish kerak, chunki $x$ javob atrofida “sakray” boshlashi mumkin. Shu sababli quyidagi shartni qo‘shamiz: agar oldingi qadamda $x$ qiymati kamaygan bo‘lsa, joriy qadamda esa ortishga harakat qilsa, algoritm to‘xtatilishi kerak.

```cpp
int isqrt_newton(int n) {
	int x = 1;
	bool decreased = false;
	for (;;) {
		int nx = (x + n / x) >> 1;
		if (x == nx || nx > x && decreased)
			break;
		decreased = nx < x;
		x = nx;
	}
	return x;
}
```

Nihoyat, uchinchi variant — bignum arifmetikasi holati. $n$ soni yetarlicha katta bo‘lishi mumkinligi sababli, boshlang‘ich yaqinlashuvga e’tibor berish ma’qul. Ravshanki, u ildizga qancha yaqin bo‘lsa, natijaga shuncha tez erishiladi. Boshlang‘ich yaqinlashuv sifatida $2^{\textrm{bits}/2}$ sonini olish yetarlicha sodda va samarali; bu yerda $\textrm{bits}$ — $n$ sonidagi bitlar soni. Quyida shu variantni ko‘rsatadigan Java kodi keltirilgan:

```java
public static BigInteger isqrtNewton(BigInteger n) {
	BigInteger a = BigInteger.ONE.shiftLeft(n.bitLength() / 2);
	boolean p_dec = false;
	for (;;) {
		BigInteger b = n.divide(a).add(a).shiftRight(1);
		if (a.compareTo(b) == 0 || a.compareTo(b) < 0 && p_dec)
			break;
		p_dec = a.compareTo(b) > 0;
		a = b;
	}
	return a;
}
```

Masalan, bu kod $n = 10^{1000}$ uchun $60$ millisekundda bajariladi, boshlang‘ich yaqinlashuvni yaxshilab tanlashni olib tashlasak (shunchaki $1$ dan boshlasak), taxminan $120$ millisekund ketadi.

## Amaliy masalalar

- [UVa 10428 - The Roots](https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&category=16&page=show_problem&problem=1369)
