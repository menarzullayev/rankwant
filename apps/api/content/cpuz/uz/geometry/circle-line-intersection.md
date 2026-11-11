# Aylana va to‘g‘ri chiziq kesishmasi

Aylana markazining koordinatalari va radiusi hamda to‘g‘ri chiziq tenglamasi berilgan; kesishish nuqtalarini topish talab qilinadi.

## Yechim

Ikki tenglamadan iborat sistemani yechish o‘rniga masalaga geometrik yondashamiz. Bu usul sonli turg‘unlik nuqtayi nazaridan aniqroq yechim beradi.

Umumiylikni yo‘qotmasdan aylana markazi koordinatalar boshida deb faraz qilamiz. Agar bunday bo‘lmasa, aylanani u yerga ko‘chiramiz va to‘g‘ri chiziq tenglamasidagi $C$ o‘zgarmasini to‘g‘rilaymiz. Demak, markazi $(0,0)$ nuqtada, radiusi $r$ bo‘lgan aylana va tenglamasi $Ax+By+C=0$ bo‘lgan to‘g‘ri chiziq berilgan.

Avval to‘g‘ri chiziqda koordinatalar boshiga eng yaqin $(x_0, y_0)$ nuqtani topamiz. Birinchidan, u

$$ d_0 = \frac{|C|}{\sqrt{A^2+B^2}} $$

masofada bo‘lishi kerak.

Ikkinchidan, $(A, B)$ vektor to‘g‘ri chiziqqa perpendikulyar bo‘lgani uchun nuqtaning koordinatalari bu vektorning koordinatalariga proporsional bo‘lishi kerak. Nuqtadan koordinatalar boshigacha bo‘lgan masofani bilganimiz uchun $(A, B)$ vektorni shu uzunlikka masshtablashtirish kifoya, shunda quyidagini olamiz:

$$\begin{align}
x_0 &= - \frac{AC}{A^2 + B^2} \\
y_0 &= - \frac{BC}{A^2 + B^2} 
\end{align}$$

Minus ishoralari ochiq-oydin emas, lekin $x_0$ va $y_0$ ni to‘g‘ri chiziq tenglamasiga qo‘yib, ularni osongina tekshirish mumkin.

Bu bosqichda kesishish nuqtalari sonini aniqlash, hatto nuqta bitta yoki nol bo‘lganda yechimni topish ham mumkin. Haqiqatan, agar $(x_0, y_0)$ nuqtadan koordinatalar boshigacha bo‘lgan masofa $d_0$ radius $r$ dan katta bo‘lsa, javob — **nol nuqta**. Agar $d_0=r$ bo‘lsa, javob — **bitta nuqta** $(x_0, y_0)$. Agar $d_0<r$ bo‘lsa, ikkita kesishish nuqtasi bor va endi ularning koordinatalarini topishimiz kerak.

Demak, $(x_0, y_0)$ nuqta aylana ichida. Ikkita kesishish nuqtasi, $(a_x, a_y)$ va $(b_x, b_y)$, $Ax+By+C=0$ to‘g‘ri chiziqqa tegishli bo‘lishi va $(x_0, y_0)$ dan bir xil $d$ masofada yotishi kerak; bu masofani topish oson:

$$ d = \sqrt{r^2 - \frac{C^2}{A^2 + B^2}} $$

E’tibor bering, $(-B, A)$ vektor to‘g‘ri chiziqqa kollinear, shuning uchun kerakli nuqtalarni $(x_0, y_0)$ nuqtaga $d$ uzunlikka masshtablangan $(-B,A)$ vektorni qo‘shib va ayirib topish mumkin.

Nihoyat, ikkita kesishish nuqtasining formulalari quyidagicha:

$$\begin{align}
m &= \sqrt{\frac{d^2}{A^2 + B^2}} \\
a_x &= x_0 + B \cdot m, a_y = y_0 - A \cdot m \\
b_x &= x_0 - B \cdot m, b_y = y_0 + A \cdot m
\end{align}$$

Dastlabki sistemani algebraik usullar bilan yechganimizda, ehtimol, javobni boshqacha ko‘rinishda va kattaroq xato bilan olgan bo‘lardik. Bu yerda tavsiflangan geometrik usul ko‘rgazmaliroq va aniqroq.

## Implementatsiya

Boshida aytilganidek, aylana markazi koordinatalar boshida deb faraz qilamiz, shuning uchun dasturning kirishi — aylananing radiusi $r$ va to‘g‘ri chiziq tenglamasining $A$, $B$, $C$ parametrlari.

```cpp
double r, a, b, c; // kirish sifatida beriladi
double x0 = -a*c/(a*a+b*b), y0 = -b*c/(a*a+b*b);
if (c*c > r*r*(a*a+b*b)+EPS)
    puts ("no points");
else if (abs (c*c - r*r*(a*a+b*b)) < EPS) {
    puts ("1 point");
    cout << x0 << ' ' << y0 << '\n';
}
else {
    double d = r*r - c*c/(a*a+b*b);
    double mult = sqrt (d / (a*a+b*b));
    double ax, ay, bx, by;
    ax = x0 + b * mult;
    bx = x0 - b * mult;
    ay = y0 - a * mult;
    by = y0 + a * mult;
    puts ("2 points");
    cout << ax << ' ' << ay << '\n' << bx << ' ' << by << '\n';
}
```

## Amaliy masalalar

- [CODECHEF: ANDOOR](https://www.codechef.com/problems/ANDOOR)
