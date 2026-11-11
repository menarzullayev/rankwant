# Eng kichik qamrab oluvchi aylana {#minimum-enclosing-circle}

Quyidagi masalani ko‘rib chiqamiz:

> **[Library Checker - Minimum Enclosing Circle](https://judge.yosupo.jp/problem/minimum_enclosing_circle)**
>
>
> Sizga $n \leq 10^5$ ta $p_i=(x_i, y_i)$ nuqta berilgan.
>
> Har bir $p_i$ uchun u $\{p_1,\dots,p_n\}$ to‘plamining eng kichik qamrab oluvchi aylanasi chizig‘ida yotish-yotmasligini aniqlang.

Bu yerda eng kichik qamrab oluvchi aylana (MEC, *minimum enclosing circle*) deganda barcha $n$ ta nuqtani aylana ichida yoki chegarasida saqlaydigan, radiusi mumkin bo‘lgan eng kichik aylanani tushunamiz. Bu masalaning sodda randomizatsiyalangan yechimi birinchi qarashda $O(n^3)$ vaqtda ishlaydigandek ko‘rinadi, aslida esa kutilgan $O(n)$ vaqtda ishlaydi.

Quyidagi mulohazalarni yaxshiroq tushunish uchun masala yechimi yagona ekanini darhol qayd etamiz:

> **MEC nega yagona?**
>
>
> Quyidagi qurilmani ko‘rib chiqamiz: $r$ — MEC radiusi bo‘lsin. $p_1,\dots,p_n$ nuqtalarning har biri atrofida radiusi $r$ bo‘lgan aylana chizamiz. Geometrik jihatdan, radiusi $r$ bo‘lgan va $p_1,\dots,p_n$ nuqtalarning barchasini qoplaydigan aylanalarning markazlari barcha $n$ ta aylananing kesishmasini tashkil qiladi.
>
> Endi, agar kesishma bitta nuqtadan iborat bo‘lsa, bu uning yagonaligini allaqachon isbotlaydi. Aks holda kesishma yuzi nolga teng bo‘lmagan shakl bo‘ladi, shuning uchun $r$ ni ozgina kamaytirsak ham kesishma bo‘sh bo‘lmay qoladi; bu esa $r$ qamrab oluvchi aylananing mumkin bo‘lgan eng kichik radiusi degan farazga zid.
>
> Shunga o‘xshash mulohaza bilan, agar aylana berilgan aniq $p_i$ nuqtadan yoki $p_i$ va $p_j$ ikki nuqtadan o‘tishi qo‘shimcha talab qilinsa ham, MEC ning yagonaligini ko‘rsatish mumkin (u yana yagona bo‘ladi, chunki uni radiusi yagona aniqlaydi).
>
> Shu bilan birga, ikkita MEC bor deb faraz qilib, ularning kesishmasi (u $p_1,\dots,p_n$ nuqtalarni allaqachon o‘z ichiga oladi) boshlang‘ich aylanalarnikidan kichikroq diametrga ega bo‘lishi kerakligini va shu sababli uni kichikroq aylana bilan qoplash mumkinligini ham ko‘rish mumkin.

## Welzl algoritmi {#welzls-algorithm}

Qisqalik uchun $\operatorname{mec}(p_1,\dots,p_n)$ orqali $\{p_1,\dots,p_n\}$ to‘plamining MEC sini, $P_i = \{p_1,\dots,p_i\}$ orqali esa birinchi $i$ ta nuqta to‘plamini belgilaymiz.

Welzl 1991-yilda [taklif qilgan](https://doi.org/10.1007/BFb0038202) bu algoritm quyidagicha ishlaydi:

1. Kirish nuqtalari ketma-ketligiga tasodifiy permutatsiya qo‘llaymiz.
2. MEC ning joriy nomzodi $C$ ni saqlaymiz; boshida $C = \operatorname{mec}(p_1, p_2)$.
3. $i=3..n$ bo‘yicha yurib, $p_i \in C$ ekanini tekshiramiz.
    1. Agar $p_i \in C$ bo‘lsa, bu $C$ ning $P_i$ uchun MEC ekanini bildiradi.
    2. Aks holda $C = \operatorname{mec}(p_i, p_1)$ deb olamiz va $j=2..i$ bo‘yicha yurib, $p_j \in C$ ekanini tekshiramiz.
        1. Agar $p_j \in C$ bo‘lsa, $C$ — $p_i$ nuqtadan o‘tuvchi aylanalar orasida $P_j$ ning MEC sidir.
        2. Aks holda $C=\operatorname{mec}(p_i, p_j)$ deb olamiz va $k=1..j$ bo‘yicha yurib, $p_k \in C$ ekanini tekshiramiz.
            1. Agar $p_k \in C$ bo‘lsa, $C$ — $p_i$ va $p_j$ nuqtalardan o‘tuvchi aylanalar orasida $P_k$ ning MEC sidir.
            2. Aks holda $C=\operatorname{mec}(p_i,p_j,p_k)$ — $p_i$ va $p_j$ nuqtalardan o‘tuvchi aylanalar orasida $P_k$ ning MEC sidir.

Ko‘rib turibmizki, bu yerdagi har bir ichma-ich daraja saqlanishi kerak bo‘lgan invariantga ega ($C$ — qo‘shimcha ravishda berilgan $0$, $1$ yoki $2$ nuqtadan ham o‘tadigan aylanalar orasida MEC bo‘lishi) va ichki sikl yopilganda uning invarianti ota siklning joriy iteratsiyasi invariantiga teng kuchli bo‘lib qoladi. Bu esa butun algoritmning *to‘g‘riligini* ta’minlaydi.

Hozircha ayrim texnik tafsilotlarni chetga surib, butun algoritmni C++ da quyidagicha implementatsiya qilish mumkin:

```cpp
struct point {...};

// Is represented by 2 or 3 points on its circumference
struct mec {...};

bool inside(mec const& C, point p) {
    return ...;
}

// Choose some good generator of randomness for the shuffle
mt19937_64 gen(...);
mec enclosing_circle(vector<point> &p) {
    int n = p.size();
    ranges::shuffle(p, gen);
    auto C = mec{p[0], p[1]};
    for(int i = 0; i < n; i++) {
        if(!inside(C, p[i])) {
            C = mec{p[i], p[0]};
            for(int j = 0; j < i; j++) {
                if(!inside(C, p[j])) {
                    C = mec{p[i], p[j]};
                    for(int k = 0; k < j; k++) {
                        if(!inside(C, p[k])) {
                            C = mec{p[i], p[j], p[k]};
                        }
                    }
                }
            }
        }
    }
    return C;
}
```

Kutish mumkinki, $p_i$ nuqta $2$ yoki $3$ nuqtaning MEC si ichida ekanini $O(1)$ vaqtda tekshirish mumkin (buni keyinroq muhokama qilamiz). Biroq shunda ham, yuqoridagi algoritm faqat ichma-ich sikllar tufayli eng yomon holatda $O(n^3)$ vaqt oladigandek ko‘rinadi. Xo‘sh, nega biz chiziqli kutilgan ishlash vaqtini da’vo qildik? Keling, aniqlaymiz!

### Murakkablik tahlili {#complexity-analysis}

Eng ichki sikl ($k$ bo‘yicha) uchun uning kutilgan ishlash vaqti, shubhasiz, $O(j)$ amal. $j$ bo‘yicha sikl-chi?

U keyingi siklni faqat $p_j$ nuqta $P_j$ ning $i$ nuqtadan ham o‘tuvchi MEC si chegarasida yotsa _va $p_j$ ni olib tashlash aylanani yanada kichraytirsa_ ishga tushiradi. $P_j$ dagi barcha nuqtalardan bunday xossaga ega bo‘lganlari ko‘pi bilan $2$ ta bo‘lishi mumkin: chunki agar chegarada $P_j$ ning $2$ tadan ortiq nuqtasi yotsa, ulardan istalgan birini olib tashlaganda ham chegarada kamida $3$ ta nuqta qoladi va ular aylanani yagona aniqlash uchun yetarli.

Boshqacha aytganda, boshlang‘ich tasodifiy aralashtirishdan keyin $p_j$ sifatida ko‘pi bilan ikkita “omadsiz” nuqtadan birini olish ehtimoli ko‘pi bilan $\frac{2}{j}$. Buni $j$ ning $1$ dan $i$ gacha barcha qiymatlari bo‘yicha yig‘sak, kutilgan ishlash vaqti

$$
\sum\limits_{j=1}^i \frac{2}{j} \cdot O(j) = O(i).
$$

Aynan shu tarzda tashqi sikl ham kutilgan $O(n)$ vaqtda ishlashini isbotlash mumkin.

### Nuqta $2$ yoki $3$ nuqtaning MEC sida ekanini tekshirish {#checking-that-a-point-is-in-the-mec-of-2-or-3-points}

Endi `point` va `mec` ning implementatsiya tafsilotlarini aniqlaymiz. Bu masalada nuqtalar uchun sinf sifatida [std::complex](https://codeforces.com/blog/entry/22175) dan foydalanish ayniqsa qulay bo‘lib chiqadi:

```cpp
using ftype = int64_t;
using point = complex<ftype>;
```

Eslatib o‘tamiz, kompleks son — $x+yi$ ko‘rinishdagi son, bunda $i^2=-1$ va $x, y \in \mathbb R$. C++ da bunday kompleks son ikki o‘lchovli $(x, y)$ nuqta bilan ifodalanadi. Kompleks sonlarda komponentlar bo‘yicha asosiy chiziqli amallar (qo‘shish, haqiqiy songa ko‘paytirish) allaqachon implementatsiya qilingan, ammo ularni ko‘paytirish va bo‘lishning ham ma’lum geometrik ma’nosi bor.

Juda chuqur kirmasdan, ushbu masala uchun eng muhim xossani qayd etamiz: ikki kompleks sonni ko‘paytirish ularning qutbiy burchaklarini ($Ox$ o‘qidan soat strelkasiga teskari yo‘nalishda hisoblanadi) qo‘shadi, qo‘shma kompleks sonni olish esa (ya’ni $z=x+yi$ ni $\overline{z} = x-yi$ ga almashtirish) qutbiy burchakni $-1$ ga ko‘paytiradi. Bu $z$ nuqta $2$ yoki $3$ aniq nuqtaning MEC si ichida yotish-yotmasligi uchun juda sodda mezonlar tuzishga imkon beradi.

#### $2$ nuqtaning MEC si {#mec-of-2-points}

$2$ ta $a$ va $b$ nuqta uchun ularning MEC si — markazi $\frac{a+b}{2}$ va radiusi $\frac{|a-b|}{2}$ bo‘lgan aylana, boshqacha aytganda $ab$ diametr bo‘lgan aylana. $z$ shu aylana ichida ekanini tekshirish uchun $za$ va $zb$ orasidagi burchak o‘tkir emasligini tekshirish kifoya.

![](https://upload.wikimedia.org/wikipedia/commons/8/8e/Diameter_angles.svg)

*Ichki burchaklar o‘tmas, tashqi burchaklar o‘tkir, aylana ustidagi burchaklar esa to‘g‘ri*

Teng kuchli ravishda, quyidagi

$$
I_0=(b-z)\overline{(a-z)}
$$

son musbat haqiqiy koordinataga ega emasligini tekshirish kerak (bu qutbiy burchagi $-90^\circ$ va $90^\circ$ orasida bo‘lgan nuqtalarga mos keladi).

#### $3$ nuqtaning MEC si {#mec-of-3-points}

$abc$ uchburchakka $z$ ni qo‘shsak, u to‘rtburchakka aylanadi. Quyidagi ifodani ko‘rib chiqamiz:

$$
\angle azb + \angle bca
$$

[Aylanaga ichki chizilgan to‘rtburchakda](https://en.wikipedia.org/wiki/Cyclic_quadrilateral) agar $c$ va $z$ $ab$ ning bir tomonida bo‘lsa, burchaklar teng bo‘ladi va ishorali (ya’ni soat strelkasiga teskari bo‘lsa musbat, soat strelkasi bo‘yicha bo‘lsa manfiy) qo‘shilganda $0^\circ$ ni beradi. Mos ravishda, agar $c$ va $z$ qarama-qarshi tomonlarda bo‘lsa, burchaklar yig‘indisi $180^\circ$ ga teng bo‘ladi.

![](https://upload.wikimedia.org/wikipedia/commons/3/30/Opposing_inscribed_angles.svg)

*Qo‘shni ichki chizilgan burchaklar teng, qarama-qarshi burchaklar esa 180 gradusgacha to‘ldiradi*

Kompleks sonlar tilida $\angle azb$ — $(b-z)\overline{(a-z)}$ ning qutbiy burchagi, $\angle bca$ esa $(a-c)\overline{(b-c)}$ ning qutbiy burchagi ekanini ko‘rish mumkin. Demak, $\angle azb + \angle bca$ — quyidagi sonning qutbiy burchagi degan xulosaga kelamiz:

$$
I_1 = (b-z) \overline{(a-z)} (a-c) \overline{(b-c)}
$$

Agar burchak $0^\circ$ yoki $180^\circ$ bo‘lsa, bu $I_1$ ning mavhum qismi $0$ ekanini bildiradi; aks holda $z$ nuqta $abc$ ni qamrab oluvchi aylana ichida yoki tashqarida ekanini $I_1$ mavhum qismining ishorasini tekshirib aniqlashimiz mumkin. Musbat mavhum qism musbat burchaklarga, manfiy mavhum qism manfiy burchaklarga mos keladi.

Ammo qaysi biri $z$ aylana ichida yoki tashqarida ekanini bildiradi? Biz allaqachon payqaganimizdek, $z$ aylana ichida bo‘lsa, odatda $\angle azb$ ning kattaligi ortadi, tashqarida bo‘lsa esa kamayadi. Shu sababli quyidagi 4 ta holat bor:

1. $\angle bca > 0^\circ$, $c$ va $z$ $ab$ ning bir tomonida. U holda $\angle azb < 0^\circ$ va aylana ichidagi nuqtalar uchun $\angle azb + \angle bca < 0^\circ$.
3. $\angle bca < 0^\circ$, $c$ va $z$ $ab$ ning bir tomonida. U holda $\angle azb > 0^\circ$ va aylana ichidagi nuqtalar uchun $\angle azb + \angle bca > 0^\circ$.
2. $\angle bca > 0^\circ$, $c$ va $z$ $ab$ ning qarama-qarshi tomonlarida. U holda $\angle azb > 0^\circ$ va aylana ichidagi nuqtalar uchun $\angle azb + \angle bca > 180^\circ$.
4. $\angle bca < 0^\circ$, $c$ va $z$ $ab$ ning qarama-qarshi tomonlarida. U holda $\angle azb < 0^\circ$ va aylana ichidagi nuqtalar uchun $\angle azb + \angle bca < 180^\circ$.

Boshqacha aytganda, agar $\angle bca$ musbat bo‘lsa, aylana ichidagi nuqtalar uchun $\angle azb + \angle bca < 0^\circ$, aks holda $\angle azb + \angle bca > 0^\circ$ bo‘ladi (burchaklar $-180^\circ$ va $180^\circ$ orasiga keltirilgan deb faraz qilamiz). Buni o‘z navbatida $I_2=(a-c)\overline{(b-c)}$ va $I_1 = I_0 I_2$ mavhum qismlarining ishoralari orqali tekshirish mumkin.

**Eslatma**: $I_1$ ni olish uchun to‘rtta kompleks sonni ko‘paytirganimiz sababli, oraliq koeffitsientlar $O(A^4)$ gacha katta bo‘lishi mumkin; bu yerda $A$ — kirishdagi eng katta koordinata moduli. Yaxshi tomoni shundaki, kirish butun sonlardan iborat bo‘lsa, yuqoridagi ikkala tekshiruvni ham to‘liq butun sonlarda bajarish mumkin.

#### Implementatsiya {#implementation}

Endi tekshiruvni amalda implementatsiya qilish uchun avval MEC ni qanday ifodalashni hal qilishimiz kerak. Bizning mezonlarimiz to‘g‘ridan-to‘g‘ri nuqtalar bilan ishlagani uchun, buning tabiiy va samarali yo‘li MEC ni uni aniqlaydigan nuqtalar jufti yoki uchligi ko‘rinishida bevosita ifodalashdir:

```cpp
using mec = variant<
    array<point, 2>,
    array<point, 3>
>;
```

Endi yuqoridagi mezonlarga muvofiq ikkala holatni samarali boshqarish uchun `std::visit` dan foydalanishimiz mumkin:

```cpp
/* I < 0 if z inside C,
   I > 0 if z outside C,
   I = 0 if z on the circumference of C */
ftype indicator(mec const& C, point z) {
    return visit([&](auto &&C) {
        point a = C[0], b = C[1];
        point I0 = (b - z) * conj(a - z);
        if constexpr (size(C) == 2) {
            return real(I0);
        } else {
            point c = C[2];
            point I2 = (a - c) * conj(b - c);
            point I1 = I0 * I2;
            return imag(I2) < 0 ? -imag(I1) : imag(I1);
        }
    }, C);
}

bool inside(mec const& C, point p) {
    return indicator(C, p) <= 0;
}

```

Endi masalani Library Checker ga yuborib, hamma narsa ishlashiga ishonch hosil qilishimiz mumkin: [#308668](https://judge.yosupo.jp/submission/308668).

## Amaliy masalalar {#practice-problems}

- [Library Checker - Minimum Enclosing Circle](https://judge.yosupo.jp/problem/minimum_enclosing_circle)
- [BOI 2002 - Aliens](https://www.spoj.com/problems/ALIENS)
