# Panjaraviy bo‘lmagan ko‘pburchak ichidagi panjara nuqtalari

Panjaraviy ko‘pburchaklar uchun ko‘pburchak ichidagi panjara nuqtalarini sanash uchun Pick formulasi mavjud.
Uchlari ixtiyoriy bo‘lgan ko‘pburchaklar-chi?

Ko‘pburchakning har bir qirrasini alohida ko‘rib chiqamiz, so‘ng har bir qirra ostidagi panjara nuqtalar sonini qo‘shib chiqamiz; bunda ishorani qirraning yo‘nalishiga qarab tanlaymiz (ko‘pburchak yuzini trapesiyalar yordamida hisoblashdagi kabi).

Avvalo shuni ta’kidlaymizki, agar joriy qirraning uchlari $A=(x_1;y_1)$ va $B=(x_2;y_2)$ nuqtalarda bo‘lsa, uni chiziqli funksiya ko‘rinishida yozish mumkin:

$$y=y_1+(y_2-y_1) \cdot \dfrac{x-x_1}{x_2-x_1}=\left(\dfrac{y_2-y_1}{x_2-x_1}\right)\cdot x + \left(\dfrac{y_1x_2-x_1y_2}{x_2-x_1}\right)$$

$$y = k \cdot x + b,~k = \dfrac{y_2-y_1}{x_2-x_1},~b = \dfrac{y_1x_2-x_1y_2}{x_2-x_1}$$

Endi $x=x'+\lceil x_1 \rceil$ almashtirishni bajaramiz, shunda $b' = b + k \cdot \lceil x_1 \rceil$ bo‘ladi.
Bu bizga $x_1'=0$ va $x_2'=x_2 - \lceil x_1 \rceil$ bilan ishlash imkonini beradi.
$n = \lfloor x_2' \rfloor$ deb belgilaymiz.

Algoritmning yaxlitligi uchun $x = n$ dagi va $y = 0$ dagi nuqtalarni yig‘indiga qo‘shmaymiz.
Ularni keyinroq qo‘lda qo‘shish mumkin.
Shunday qilib, biz $\sum\limits_{x'=0}^{n - 1} \lfloor k' \cdot x' + b'\rfloor$ yig‘indini hisoblashimiz kerak. Shuningdek, $k' \geq 0$ va $b'\geq 0$ deb faraz qilamiz.
Aks holda $x'=-t$ almashtirishni bajarib, $b'$ ga $\lceil|b'|\rceil$ ni qo‘shish kerak.

$\sum\limits_{x=0}^{n - 1} \lfloor k \cdot x + b\rfloor$ yig‘indini qanday hisoblash mumkinligini ko‘rib chiqamiz.
Ikki holat mavjud:

  - $k \geq 1$ yoki $b \geq 1$.

    U holda avval $y=\lfloor k \rfloor \cdot x + \lfloor b \rfloor$ chiziq ostidagi nuqtalarni yig‘ib chiqishdan boshlaymiz. Ularning soni quyidagiga teng:

    $$
    \sum\limits_{x=0}^{n - 1} \lfloor k \rfloor \cdot x + \lfloor b \rfloor=\dfrac{(\lfloor k \rfloor(n-1)+2\lfloor b \rfloor) n}{2}.
    $$

    Endi bizni faqat $\lfloor k \rfloor \cdot x + \lfloor b \rfloor < y \leq k\cdot x + b$ shartni qanoatlantiruvchi $(x;y)$ nuqtalar qiziqtiradi.
    Bu miqdor $0 < y \leq (k - \lfloor k \rfloor) \cdot x + (b - \lfloor b \rfloor)$ shartni qanoatlantiruvchi nuqtalar soniga teng.
    Demak, masalani $k'= k - \lfloor k \rfloor$, $b' = b - \lfloor b \rfloor$ ga keltirdik, va endi $k'$ ham, $b'$ ham $1$ dan kichik.
    Mana rasm: biz ko‘k nuqtalarni yig‘ib chiqdik va $k$ hamda $b$ uchun kichikroq qiymatlarga o‘tish maqsadida qora chiziqli funksiyadan ko‘k chiziqli funksiyani ayirdik:

  ![Subtracting floored linear function](/algorithms-media/geometry/lattice.png)

  - $k < 1$ va $b < 1$.

    Agar $\lfloor k \cdot n + b\rfloor$ nolga teng bo‘lsa, ishonch bilan $0$ qaytarishimiz mumkin.
    Aks holda $x < 0$ va $0 < y \leq k \cdot x + b$ shartni qanoatlantiruvchi panjara nuqtalari yo‘q deyish mumkin.
    Bu shuni anglatadiki, $O'=(n;\lfloor k\cdot n + b\rfloor)$ bo‘lgan, $x'$ o‘qi pastga, $y'$ o‘qi esa chapga yo‘nalgan yangi koordinatalar sistemasini qaralsa ham javob o‘zgarmaydi.
    Bu sistemada bizni quyidagi to‘plamdagi panjara nuqtalari qiziqtiradi:

    $$
    \left\{(x;y)~\bigg|~0 \leq x < \lfloor k \cdot n + b\rfloor,~ 0 < y \leq \dfrac{x+(k\cdot n+b)-\lfloor k\cdot n + b \rfloor}{k}\right\}
    $$

    bu esa bizni yana $k>1$ holiga qaytaradi.
    Quyidagi rasmda yangi $O'$ boshlang‘ich nuqta va $X'$ hamda $Y'$ o‘qlarni ko‘rishingiz mumkin:

  ![New reference and axes](/algorithms-media/geometry/mirror.png)

    Ko‘rib turganingizdek, yangi koordinatalar sistemasida chiziqli funksiyaning koeffitsiyenti $\tfrac 1 k$ bo‘ladi va uning nol nuqtasi $\lfloor k\cdot n + b \rfloor-(k\cdot n+b)$ nuqtada joylashadi; bu yuqoridagi formulani to‘g‘ri qiladi.

## Murakkablik tahlili

Biz ko‘pi bilan $\dfrac{(k(n-1)+2b)n}{2}$ ta nuqtani sanashimiz kerak.
Ularning ichidan birinchi qadamdayoq $\dfrac{\lfloor k \rfloor (n-1)+2\lfloor b \rfloor}{2}$ tasini sanaymiz.
$b$ ni juda kichik deb hisoblash mumkin, chunki uni avvalo $1$ dan kichik qilib boshlash mumkin.
Bu holda barcha nuqtalarning taxminan $\dfrac{\lfloor k \rfloor}{k} \geq \dfrac 1 2$ qismini sanaymiz, deyish mumkin.
Shunday qilib, $O(\log n)$ qadamda tugatamiz.

## Implementatsiya

Quyida $0 \leq x < n$ va $0 < y \leq \lfloor k x+b\rfloor$ shartlarni qanoatlantiruvchi butun $(x;y)$ nuqtalar sonini hisoblaydigan sodda funksiya keltirilgan:

```cpp
int count_lattices(Fraction k, Fraction b, long long n) {
    auto fk = k.floor();
    auto fb = b.floor();
    auto cnt = 0LL;
    if (k >= 1 || b >= 1) {
        cnt += (fk * (n - 1) + 2 * fb) * n / 2;
        k -= fk;
        b -= fb;
    }
    auto t = k * n + b;
    auto ft = t.floor();
    if (ft >= 1) {
        cnt += count_lattices(1 / k, (t - t.floor()) / k, t.floor());
    }
    return cnt;
}
```

Bu yerda `Fraction` ratsional sonlar bilan ishlaydigan biror sinfdir.
Amalda, agar barcha maxraj va suratlar absolyut qiymati bo‘yicha ko‘pi bilan $C$ bo‘lsa, suratlar va maxrajlarni eng katta umumiy bo‘luvchiga bo‘lib borilganda, rekursiv chaqiruvlarda ular ko‘pi bilan $C^2$ bo‘lishi ko‘rinadi.
Shu farazga asosan, `double` ishlatib, $\varepsilon^2$ aniqlikni talab qilish mumkin, bunda $\varepsilon$ — $k$ va $b$ berilgan aniqlik.
Bu shuni anglatadiki, `floor` da sonlar butun sondan ko‘pi bilan $\varepsilon^2$ ga farq qilsa, ularni butun deb hisoblash kerak.
