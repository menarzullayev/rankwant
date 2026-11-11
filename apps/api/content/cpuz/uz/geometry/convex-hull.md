# Qavariq qobiqni qurish {#convex-hull-construction}

Ushbu maqolada berilgan nuqtalar to‘plamining qavariq qobig‘ini qurish masalasi ko‘rib chiqiladi.

Tekislikda $N$ ta nuqta berilgan bo‘lsin. Maqsad — qavariq qobiqni, ya’ni berilgan barcha nuqtalarni o‘z ichiga oladigan eng kichik
qavariq ko‘pburchakni hosil qilish.

Biz 1972-yilda Graham tomonidan e’lon qilingan **Graham scan** algoritmini hamda
1979-yilda Andrew tomonidan e’lon qilingan **Monotone chain** algoritmini ko‘rib chiqamiz. Ikkalasining murakkabligi
$\mathcal{O}(N \log N)$ bo‘lib, ular asimptotik jihatdan optimal (asimptotik jihatdan yaxshiroq algoritm
yo‘qligi isbotlangan), parallel yoki onlayn ishlov berish ishtirok etadigan ayrim masalalar bundan mustasno.

## Graham scan algoritmi {#grahams-scan-algorithm}
Algoritm avval eng pastdagi $P_0$ nuqtani topadi. Agar Y koordinatasi bir xil bo‘lgan bir nechta nuqta bo‘lsa,
X koordinatasi kichigi olinadi. Bu
bosqich $\mathcal{O}(N)$ vaqt oladi.

Keyin qolgan barcha nuqtalar qutbiy burchak bo‘yicha soat mili yo‘nalishida saralanadi.
Agar ikki yoki undan ortiq nuqtaning qutbiy burchagi bir xil bo‘lsa, tenglik $P_0$ gacha bo‘lgan masofa bo‘yicha, o‘sish tartibida buziladi.

Shundan so‘ng nuqtalarni birma-bir ko‘rib chiqamiz va joriy
nuqta hamda undan oldingi ikkita nuqta soat mili yo‘nalishidagi burilish hosil qilishiga ishonch hosil qilamiz, aks holda oldingi
nuqta tashlab yuboriladi, chunki u noqavariq shakl hosil qiladi. Burilish soat mili yo‘nalishida yoki unga teskari
ekanini [orientatsiyani](/algorithms/geometry/oriented-triangle-area) tekshirish orqali aniqlash mumkin.

Nuqtalarni saqlash uchun stekdan foydalanamiz va boshlang‘ich $P_0$ nuqtaga yetib kelganimizda
algoritm tugaydi va biz qavariq qobiqning barcha nuqtalarini
soat mili yo‘nalishida saqlovchi stekni qaytaramiz.

Agar Graham scan paytida kollinear nuqtalarni ham kiritish kerak bo‘lsa, saralashdan keyin yana bitta
qadam kerak bo‘ladi. $P_0$ dan eng katta qutbiy masofaga ega bo‘lgan (ular saralangan vektorning oxirida bo‘lishi kerak) va kollinear bo‘lgan nuqtalarni olish kerak.
Bu chiziqdagi nuqtalar teskari tartibga o‘giriladi, shunda barcha
kollinear nuqtalarni chiqarish mumkin bo‘ladi; aks holda algoritm shu
chiziqdagi eng yaqin nuqtani oladi va to‘xtaydi. Bu qadamni algoritmning kollinear bo‘lmagan
versiyasiga kiritmaslik kerak, aks holda eng kichik qavariq qobiqni olib bo‘lmaydi.

### Implementatsiya {#implementation}

```cpp
struct pt {
    double x, y;
    bool operator == (pt const& t) const {
        return x == t.x && y == t.y;
    }
};

int orientation(pt a, pt b, pt c) {
    double v = a.x*(b.y-c.y)+b.x*(c.y-a.y)+c.x*(a.y-b.y);
    if (v < 0) return -1; // clockwise
    if (v > 0) return +1; // counter-clockwise
    return 0;
}

bool cw(pt a, pt b, pt c, bool include_collinear) {
    int o = orientation(a, b, c);
    return o < 0 || (include_collinear && o == 0);
}
bool collinear(pt a, pt b, pt c) { return orientation(a, b, c) == 0; }

void convex_hull(vector<pt>& a, bool include_collinear = false) {
    pt p0 = *min_element(a.begin(), a.end(), [](pt a, pt b) {
        return make_pair(a.y, a.x) < make_pair(b.y, b.x);
    });
    sort(a.begin(), a.end(), [&p0](const pt& a, const pt& b) {
        int o = orientation(p0, a, b);
        if (o == 0)
            return (p0.x-a.x)*(p0.x-a.x) + (p0.y-a.y)*(p0.y-a.y)
                < (p0.x-b.x)*(p0.x-b.x) + (p0.y-b.y)*(p0.y-b.y);
        return o < 0;
    });
    if (include_collinear) {
        int i = (int)a.size()-1;
        while (i >= 0 && collinear(p0, a[i], a.back())) i--;
        reverse(a.begin()+i+1, a.end());
    }

    vector<pt> st;
    for (int i = 0; i < (int)a.size(); i++) {
        while (st.size() > 1 && !cw(st[st.size()-2], st.back(), a[i], include_collinear))
            st.pop_back();
        st.push_back(a[i]);
    }

    if (include_collinear == false && st.size() == 2 && st[0] == st[1])
        st.pop_back();

    a = st;
}
```

## Monotone chain algoritmi {#monotone-chain-algorithm}
Algoritm avval eng chapdagi va eng o‘ngdagi A va B nuqtalarni topadi. Bunday nuqtalar bir nechta bo‘lsa,
chapdagilar orasidan eng pasti (eng kichik Y koordinatali) A sifatida, o‘ngdagilar orasidan eng yuqorisi (eng katta Y koordinatali)
B sifatida olinadi. A va B ikkalasi ham qavariq qobiqqa tegishli ekani ravshan: ular eng uzoqda joylashgan va berilgan nuqtalardan
ikkitasi hosil qilgan hech bir to‘g‘ri chiziq ularni o‘z ichiga ola olmaydi.

Endi AB orqali to‘g‘ri chiziq o‘tkazamiz. U qolgan barcha nuqtalarni ikkita S1 va S2 to‘plamga ajratadi: S1 A va B ni
tutashtiruvchi chiziqdan yuqoridagi barcha nuqtalarni, S2 esa A va B ni tutashtiruvchi chiziqdan pastdagi barcha nuqtalarni o‘z ichiga oladi.
A va B ni tutashtiruvchi chiziqda yotgan nuqtalar istalgan to‘plamga tegishli bo‘lishi mumkin. A va B nuqtalar ikkala to‘plamga ham tegishli. Endi algoritm
yuqori S1 va pastki S2 to‘plamlarni quradi va javobni olish uchun ularni birlashtiradi.

Yuqori to‘plamni olish uchun barcha nuqtalarni x koordinata bo‘yicha saralaymiz. Har bir nuqta uchun quyidagilardan birini tekshiramiz: joriy nuqta oxirgi nuqta
(biz uni B deb belgilagan edik) yoki A va joriy nuqtani tutashtiruvchi chiziq bilan joriy nuqta va B ni tutashtiruvchi chiziq orasidagi orientatsiya soat mili yo‘nalishida. Bu holatlarda
joriy nuqta yuqori S1 to‘plamga tegishli bo‘ladi. Burilish soat mili yo‘nalishida yoki unga teskari ekanini [orientatsiyani](/algorithms/geometry/oriented-triangle-area) tekshirish orqali aniqlash mumkin.

Agar berilgan nuqta yuqori to‘plamga tegishli bo‘lsa, yuqori qavariq qobiqdagi oxirgidan oldingi va oxirgi nuqtalarni tutashtiruvchi chiziq
bilan yuqori qavariq qobiqdagi oxirgi nuqta va joriy nuqtani tutashtiruvchi chiziq hosil qilgan burchakni tekshiramiz. Agar burchak soat mili yo‘nalishida bo‘lmasa, yuqori qavariq qobiqqa
eng oxirgi qo‘shilgan nuqtani olib tashlaymiz, chunki joriy nuqta qavariq qobiqqa qo‘shilgach
oldingi nuqtani o‘z ichiga ola oladi.

Xuddi shu mantiq pastki S2 to‘plam uchun ham qo‘llaniladi. Agar joriy nuqta B bo‘lsa yoki A va joriy nuqtadan hamda joriy nuqta va B dan hosil bo‘lgan
chiziqlarning orientatsiyasi soat miliga teskari bo‘lsa, u S2 ga tegishli bo‘ladi.

Agar berilgan nuqta pastki to‘plamga tegishli bo‘lsa, yuqori to‘plamdagi nuqta kabi ish tutamiz, faqat soat mili yo‘nalishi o‘rniga soat miliga teskari
orientatsiyani tekshiramiz. Demak, pastki qavariq qobiqdagi oxirgidan oldingi va oxirgi nuqtalarni tutashtiruvchi chiziq bilan pastki qavariq qobiqdagi oxirgi nuqta va joriy nuqtani tutashtiruvchi
chiziq hosil qilgan burchak soat miliga teskari bo‘lmasa, pastki qavariq qobiqqa eng oxirgi qo‘shilgan nuqtani olib tashlaymiz, chunki joriy nuqta qobiqqa qo‘shilgach oldingi
nuqtani o‘z ichiga ola oladi.

Yakuniy qavariq qobiq yuqori va pastki qavariq qobiqlarning birlashmasidan olinadi va soat mili yo‘nalishidagi qobiqni tashkil qiladi; implementatsiya quyidagicha.

Agar kollinear nuqtalar kerak bo‘lsa, ularni soat mili yo‘nalishi/soat miliga teskari yo‘nalishni tekshiruvchi funksiyalarda tekshirish kifoya.
Biroq bu barcha kirish nuqtalari bitta to‘g‘ri chiziqda yotadigan degenerativ holatga yo‘l qo‘yadi va algoritm takrorlanuvchi nuqtalarni chiqaradi.
Buni hal qilish uchun yuqori qobiq barcha nuqtalarni o‘z ichiga olganini tekshiramiz va agar shunday bo‘lsa, nuqtalarni teskari tartibda qaytaramiz, chunki
bu holatda Graham implementatsiyasi ham shuni qaytaradi.

### Implementatsiya {#implementation}

```cpp
struct pt {
    double x, y;
};

int orientation(pt a, pt b, pt c) {
    double v = a.x*(b.y-c.y)+b.x*(c.y-a.y)+c.x*(a.y-b.y);
    if (v < 0) return -1; // clockwise
    if (v > 0) return +1; // counter-clockwise
    return 0;
}

bool cw(pt a, pt b, pt c, bool include_collinear) {
    int o = orientation(a, b, c);
    return o < 0 || (include_collinear && o == 0);
}
bool ccw(pt a, pt b, pt c, bool include_collinear) {
    int o = orientation(a, b, c);
    return o > 0 || (include_collinear && o == 0);
}

void convex_hull(vector<pt>& a, bool include_collinear = false) {
    if (a.size() == 1)
        return;

    sort(a.begin(), a.end(), [](pt a, pt b) {
        return make_pair(a.x, a.y) < make_pair(b.x, b.y);
    });
    pt p1 = a[0], p2 = a.back();
    vector<pt> up, down;
    up.push_back(p1);
    down.push_back(p1);
    for (int i = 1; i < (int)a.size(); i++) {
        if (i == a.size() - 1 || cw(p1, a[i], p2, include_collinear)) {
            while (up.size() >= 2 && !cw(up[up.size()-2], up[up.size()-1], a[i], include_collinear))
                up.pop_back();
            up.push_back(a[i]);
        }
        if (i == a.size() - 1 || ccw(p1, a[i], p2, include_collinear)) {
            while (down.size() >= 2 && !ccw(down[down.size()-2], down[down.size()-1], a[i], include_collinear))
                down.pop_back();
            down.push_back(a[i]);
        }
    }

    if (include_collinear && up.size() == a.size()) {
        reverse(a.begin(), a.end());
        return;
    }
    a.clear();
    for (int i = 0; i < (int)up.size(); i++)
        a.push_back(up[i]);
    for (int i = down.size() - 2; i > 0; i--)
        a.push_back(down[i]);
}
```

## Mashq masalalari {#practice-problems}

* [Kattis - Convex Hull](https://open.kattis.com/problems/convexhull)
* [Kattis - Keep the Parade Safe](https://open.kattis.com/problems/parade)
* [Codeforces - I. Birthday](https://codeforces.com/contest/2172/problem/I)
* [Latin American Regionals 2006 - Onion Layers](https://matcomgrader.com/problem/9413/onion-layers/)
* [Timus 1185: Wall](http://acm.timus.ru/problem.aspx?space=1&num=1185)
* [Usaco 2014 January Contest, Gold - Cow Curling](http://usaco.org/index.php?page=viewproblem2&cpid=382)
