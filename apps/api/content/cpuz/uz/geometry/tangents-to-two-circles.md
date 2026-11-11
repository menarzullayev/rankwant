# Ikki aylanaga umumiy urinmalarni topish

Ikki aylana berilgan. Ularning barcha umumiy urinmalarini, ya’ni ikkala aylanaga bir vaqtda urinadigan barcha to‘g‘ri chiziqlarni topish kerak.

Quyida tavsiflanadigan algoritm aylanalardan biri (yoki ikkalasi) nuqtaga aylanib ketgan holatda ham ishlaydi. Demak, bu algoritmdan berilgan nuqta orqali o‘tuvchi aylanaga urinmalarni topish uchun ham foydalanish mumkin.

## Umumiy urinmalar soni

Ikki aylananing umumiy urinmalari soni **0, 1, 2, 3, 4** yoki **cheksiz** bo‘lishi mumkin.
Turli holatlar uchun rasmlarga qarang.

![](/algorithms-media/geometry/tangents-to-two-circles.png)

Bu yerda biz **o‘ta** holatlarni ko‘rib chiqmaymiz, ya’ni *aylanalar ustma-ust tushsa (bu holda ularning cheksiz ko‘p umumiy urinmasi bor), yoki bir aylana ikkinchisining ichida yotsa (bu holda ularning umumiy urinmasi yo‘q, aylanalar urinib tursa esa bitta umumiy urinma bor).*

Ko‘p hollarda ikki aylananing **to‘rtta** umumiy urinmasi bo‘ladi.

Agar aylanalar **bir-biriga urinsa**, ularning uchta umumiy urinmasi bo‘ladi, lekin buni o‘ta holat sifatida tushunish mumkin: go‘yo ikkita urinma ustma-ust tushgandek.

Bundan tashqari, quyida tavsiflanadigan algoritm aylanalardan birining yoki ikkalasining radiusi nolga teng bo‘lgan holda ham ishlaydi: bu holda mos ravishda ikkita yoki bitta umumiy urinma bo‘ladi.

Xulosa qilib aytganda, urinmalar cheksiz ko‘p bo‘ladigan holatdan tashqari (cheksiz urinmalar holatini alohida ko‘rib chiqish kerak va u bu yerda muhokama qilinmaydi) barcha holatlar uchun doim **to‘rtta urinma** qidiramiz. O‘ta holatlarda ayrim urinmalar ustma-ust tushadi, lekin baribir bu holatlar ham umumiy manzaraga mos keladi.

## Algoritm

Algoritmni soddalashtirish uchun umumiylikni yo‘qotmasdan birinchi aylana markazi $(0, 0)$ koordinatalarga ega deb faraz qilamiz. (Agar bunday bo‘lmasa, buni butun rasmni siljitish orqali erishish mumkin, yechim topilgandan keyin esa hosil bo‘lgan to‘g‘ri chiziqlarni orqaga siljitish kerak.)

Birinchi va ikkinchi aylanalarning radiuslarini $r_1$ va $r_2$ deb, ikkinchi aylana markazining koordinatalarini esa $(v_x,v_y)$ deb belgilaymiz; $v$ nuqta koordinatalar boshidan farqli. (Eslatma: ikkala aylana bir xil bo‘lgan holni ko‘rmayapmiz.)

Masalani yechish uchun unga sof **algebraik** yondashamiz. Koordinatalar boshidan $r_1$ masofada va $v$ nuqtadan $r_2$ masofada yotuvchi $ax + by + c = 0$ ko‘rinishdagi barcha to‘g‘ri chiziqlarni topishimiz kerak. Bundan tashqari, to‘g‘ri chiziqqa normallashtirish shartini qo‘yamiz: koeffitsiyentlar kvadratlarining yig‘indisi birga teng bo‘lishi kerak (bu zarur, aks holda bitta to‘g‘ri chiziqqa $ax + by + c = 0$ ko‘rinishdagi cheksiz ko‘p tasvir mos keladi). Jami izlanayotgan $a, b, c$ lar uchun quyidagi tenglamalar sistemasini olamiz:

$$\begin{align}
a^2 + b^2 &= 1 \\
\mid a \cdot 0 + b \cdot 0 + c \mid &= r_1 \\
\mid a \cdot v_x + b \cdot v_y + c \mid &= r_2
\end{align}$$

Modullardan qutulish uchun shuni qayd etamizki, bu sistemada modullarni ochishning faqat to‘rtta usuli bor. Modulni ochishni o‘ng tomondagi koeffitsiyent -1 ga ko‘paytirilishi mumkin deb tushunsak, bu usullarning barchasini umumiy holda ko‘rib chiqish mumkin. Boshqacha aytganda, quyidagi sistemaga o‘tamiz:

$$\begin{align}
a^2 + b^2 &= 1 \\
c &= \pm r_1 \\
a \cdot v_x + b \cdot v_y + c &= \pm r_2
\end{align}$$

$d_1 = \pm r_1$ va $d_2 = \pm r_2$ belgilashlarini kiritsak, sistema to‘rtta yechimga ega bo‘lishi kerak degan xulosaga kelamiz:

$$\begin{align}
a^2 + b^2 &= 1 \\
c &= d_1 \\
a \cdot v_x + b \cdot v_y + c &= d_2
\end{align}$$

Bu sistemani yechish kvadrat tenglamani yechishga keladi. Barcha murakkab hisob-kitoblarni tushirib qoldiramiz va tayyor javobni keltiramiz:

$$\begin{align}
a &= {( d_2 - d_1 ) v_x \pm v_y \sqrt{v_x^2 + v_y^2-(d_2-d_1)^2} \over {v_x^2 + v_y^2} } \\
b &= {( d_2 - d_1 ) v_y \pm v_x \sqrt{v_x^2 + v_y^2-(d_2-d_1)^2} \over {v_x^2 + v_y^2} } \\
c &= d_1
\end{align}$$

Jami to‘rtta o‘rniga sakkizta yechim oldik. Biroq ortiqcha yechimlar qayerdan paydo bo‘lishini tushunish oson: aslida oxirgi sistemada faqat bitta yechimni (masalan, birinchisini) olish yetarli. Haqiqatan ham, $\pm r_1$ va $\pm r_2$ ni olishning geometrik ma’nosi ravshan: biz aslida to‘g‘ri chiziq har bir aylananing qaysi tomonida yotishini saralayapmiz. Shuning uchun oxirgi sistemani yechishda hosil bo‘ladigan ikki usul ortiqcha: ikki yechimdan birini tanlash yetarli (faqat, albatta, to‘rttala holatda ham bir xil yechimlar oilasini tanlash kerak).

Hali ko‘rib chiqmagan oxirgi narsa — birinchi aylana dastlab koordinatalar boshida joylashmagan holda **to‘g‘ri chiziqlarni qanday siljitish**. Lekin bu yerda hammasi oddiy: to‘g‘ri chiziq tenglamasining chiziqliligidan kelib chiqadiki, $c$ koeffitsiyentdan $a \cdot x_0 + b \cdot y_0$ qiymatni ayirish kerak (bu yerda $x_0$ va $y_0$ — birinchi aylananing dastlabki markazi koordinatalari).

## Implementatsiya

Avval barcha kerakli ma’lumotlar tuzilmalarini va boshqa yordamchi ta’riflarni keltiramiz:

```cpp
struct pt {
    double x, y;

    pt operator- (pt p) {
        pt res = { x-p.x, y-p.y };
        return res;
    }
};

struct circle : pt {
    double r;
};

struct line {
    double a, b, c;
};

const double EPS = 1E-9;

double sqr (double a) {
    return a * a;
}
```

Keyin yechimning o‘zini quyidagicha yozish mumkin (bunda chaqirish uchun asosiy funksiya ikkinchisi, birinchisi esa yordamchi):

```cpp
void tangents (pt c, double r1, double r2, vector<line> & ans) {
    double r = r2 - r1;
    double z = sqr(c.x) + sqr(c.y);
    double d = z - sqr(r);
    if (d < -EPS)  return;
    d = sqrt (abs (d));
    line l;
    l.a = (c.x * r + c.y * d) / z;
    l.b = (c.y * r - c.x * d) / z;
    l.c = r1;
    ans.push_back (l);
}

vector<line> tangents (circle a, circle b) {
    vector<line> ans;
    for (int i=-1; i<=1; i+=2)
        for (int j=-1; j<=1; j+=2)
            tangents (b-a, a.r*i, b.r*j, ans);
    for (size_t i=0; i<ans.size(); ++i)
        ans[i].c -= ans[i].a * a.x + ans[i].b * a.y;
    return ans;
}
```

## Masalalar

[TIMUS 1163 Chapaev](https://acm.timus.ru/problem.aspx?space=1&num=1163)
