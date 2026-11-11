# Convex Hull Trick va Li Chao daraxti {#convex-hull-trick-and-li-chao-tree}

Quyidagi masalani ko‘rib chiqamiz. $n$ ta shahar bor va siz avtomobilda $1$-shahardan $n$-shaharga borishingiz kerak. Buning uchun benzin sotib olishingiz lozim. $k$-shaharda bir litr benzin $cost_k$ turishi ma’lum. Dastlab yonilg‘i baki bo‘sh, avtomobil esa har kilometrga bir litr benzin sarflaydi. Shaharlar bitta to‘g‘ri chiziqda, o‘sish tartibida joylashgan; $k$-shaharning koordinatasi $x_k$. Bundan tashqari, $k$-shaharga kirish uchun $toll_k$ to‘lashingiz kerak. Vazifangiz — safarni eng kam mumkin bo‘lgan xarajat bilan amalga oshirish. Yechimni dinamik dasturlash orqali hisoblash mumkinligi ravshan:

$$
dp_i = toll_i+\min\limits_{j<i}(cost_j \cdot (x_i - x_j)+dp_j)
$$

Sodda yondashuv $O(n^2)$ murakkablik beradi; uni $O(n \log n)$ yoki $O(n \log [C \varepsilon^{-1}])$ gacha yaxshilash mumkin, bunda $C$ — mumkin bo‘lgan eng katta $|x_i|$, $\varepsilon$ esa $x_i$ qanday aniqlikda qaralishini bildiradi (butun sonlar uchun, odatda shunday bo‘ladi, $\varepsilon = 1$). Buning uchun masalani to‘plamga $k \cdot x + b$ ko‘rinishidagi chiziqli funksiyalarni qo‘shish va funksiyalarning biror $x$ nuqtadagi eng kichik qiymatini topishga keltirish mumkinligini payqash kerak. Bu yerda ikkita asosiy yondashuvdan foydalanish mumkin.

## Convex hull trick {#convex-hull-trick}

Bu yondashuvning g‘oyasi chiziqli funksiyalarning pastki qavariq qobig‘ini yuritishdan iborat.
Aslida ularni chiziqli funksiyalar sifatida emas, tekislikdagi $(k;b)$ nuqtalar sifatida qarash biroz qulayroq: u holda berilgan $(x;1)$ nuqta bilan skalyar ko‘paytmasi eng kichik bo‘lgan nuqtani topishimiz kerak bo‘ladi, ya’ni shu nuqta uchun $kx+b$ minimal bo‘ladi — bu dastlabki masalaning o‘zi.
Bunday minimum albatta ushbu nuqtalarning pastki qavariq qobig‘ida bo‘ladi, buni quyidagi rasmdan ko‘rish mumkin:

  ![lower convex hull](/algorithms-media/geometry/convex_hull_trick.png)

Qobiqdagi nuqtalarni va qobiq qirralarining normal vektorlarini saqlash kerak.
$(x;1)$ so‘rovi kelganda, ular orasidagi burchaklar nuqtai nazaridan unga eng yaqin normal vektorni topish kerak bo‘ladi; shunda optimal chiziqli funksiya uning uchlaridan biriga mos keladi.
Buni ko‘rish uchun shuni qayd etish kerakki, $(x;1)$ bilan skalyar ko‘paytmasi o‘zgarmas bo‘lgan nuqtalar $(x;1)$ ga ortogonal to‘g‘ri chiziqda yotadi; shuning uchun optimal chiziqli funksiya — qavariq qobiqqa o‘tkazilgan, $(x;1)$ ning normaliga kollinear bo‘lgan urinma qobiqqa tegadigan nuqtadagi funksiya bo‘ladi.
Bu nuqta shunday nuqtaki, uning chap va o‘ng tomonida yotgan qirralarning normallari $(x;1)$ ga nisbatan turli tomonlarga yo‘nalgan bo‘ladi.

Bu yondashuv chiziqli funksiyalarni qo‘shish so‘rovlari $k$ bo‘yicha monoton bo‘lganda yoki oflayn ishlaganimizda, ya’ni avval barcha chiziqli funksiyalarni qo‘shib, so‘ng so‘rovlarga javob berganimizda foydali.
Demak, shaharlar/benzin masalasini bu usul bilan yecha olmaymiz.
Buning uchun onlayn so‘rovlarni qayta ishlash kerak bo‘lardi.
Onlayn so‘rovlar bilan ishlashga kelganda esa ish qiyinlashadi va to‘g‘ri qavariq qobiqni amalga oshirish uchun biror to‘plam (set) ma’lumotlar tuzilmasidan foydalanishga to‘g‘ri keladi.
Biroq onlayn yondashuv murakkabligi tufayli va ikkinchi yondashuv (Li Chao daraxti) masalani ancha sodda yechishga imkon berganligi sababli bu maqolada ko‘rib chiqilmaydi.
Shuni ham aytib o‘tish kerakki, bu yondashuvni onlayn rejimda kvadrat ildiz dekompozitsiyasi yordamida murakkabliklarsiz ishlatish mumkin.
Ya’ni har $\sqrt n$ ta yangi chiziqdan keyin qavariq qobiqni noldan qayta qurish kerak.

Bu yondashuvni amalga oshirish uchun biror geometrik yordamchi funksiyalardan boshlash kerak; bu yerda C++ ning kompleks sonlar turidan foydalanishni tavsiya qilamiz.

```cpp
typedef int ftype;
typedef complex<ftype> point;
#define x real
#define y imag
 
ftype dot(point a, point b) {
    return (conj(a) * b).x();
}
 
ftype cross(point a, point b) {
    return (conj(a) * b).y();
}
```

Bu yerda chiziqli funksiyalar qo‘shilganda ularning $k$ qiymati faqat ortib boradi va biz eng kichik qiymatlarni topmoqchimiz deb faraz qilamiz.
Nuqtalarni $hull$ vektorida, normal vektorlarni esa $vecs$ vektorida saqlaymiz.
Yangi nuqta qo‘shganda qavariq qobiqdagi oxirgi qirra bilan qobiqdagi oxirgi nuqtadan yangi nuqtaga yo‘nalgan vektor orasida hosil bo‘ladigan burchakka qarash kerak.
Bu burchak soat strelkasiga teskari yo‘nalishda bo‘lishi kerak, ya’ni qobiqdagi oxirgi normal vektor (qobiq ichiga yo‘nalgan) bilan oxirgi nuqtadan yangi nuqtaga yo‘nalgan vektorning skalyar ko‘paytmasi manfiy bo‘lmasligi lozim.
Bu shart bajarilmaguncha, qavariq qobiqdagi oxirgi nuqtani mos qirra bilan birga o‘chirib borishimiz kerak.

```cpp
vector<point> hull, vecs;
 
void add_line(ftype k, ftype b) {
    point nw = {k, b};
    while(!vecs.empty() && dot(vecs.back(), nw - hull.back()) < 0) {
        hull.pop_back();
        vecs.pop_back();
    }
    if(!hull.empty()) {
        vecs.push_back(1i * (nw - hull.back()));
    }
    hull.push_back(nw);
}
 
```
Endi biror nuqtadagi minimum qiymatni olish uchun $(x;1)$ dan soat strelkasiga teskari yo‘nalgan qavariq qobiqdagi birinchi normal vektorni topamiz. Shunday qirraning chap uchi javob bo‘ladi. $a$ vektor $b$ vektordan soat strelkasiga teskari yo‘nalmaganligini tekshirish uchun ularning vektor ko‘paytmasi $[a,b]$ musbat ekanini tekshirish kerak.
```cpp
int get(ftype x) {
    point query = {x, 1};
    auto it = lower_bound(vecs.begin(), vecs.end(), query, [](point a, point b) {
        return cross(a, b) > 0;
    });
    return dot(query, hull[it - vecs.begin()]);
}
```

## Li Chao daraxti {#li-chao-tree}

Faraz qilaylik, har ikkitasi ko‘pi bilan bir marta kesishadigan funksiyalar to‘plami berilgan. Segment daraxtining har bir tugunida biror funksiyani shunday saqlaymizki, ildizdan bargga tushganda yo‘lda uchragan funksiyalardan biri shu bargda minimum qiymatni berishi kafolatlansin. Uni qanday qurishni ko‘rib chiqamiz.

Faraz qilaylik, biz $[l,r)$ yarim kesmaga mos tugundamiz, unda $f_{old}$ funksiya saqlanmoqda va biz $f_{new}$ funksiyani qo‘shyapmiz. Unda kesishish nuqtasi yo $[l;m)$ da, yo $[m;r)$ da bo‘ladi, bunda $m=\left\lfloor\tfrac{l+r}{2}\right\rfloor$. Buni funksiyalarning $l$ va $m$ nuqtalardagi qiymatlarini solishtirib samarali aniqlash mumkin. Agar ustun funksiya almashsa, kesishish $[l;m)$ da, aks holda $[m;r)$ da bo‘ladi. Endi kesishish bo‘lmagan kesma yarmi uchun pastroq funksiyani tanlab, uni joriy tugunga yozamiz. Bu doim $m$ nuqtada pastroq bo‘lgan funksiya bo‘lishini ko‘rish mumkin. Shundan so‘ng yuqoriroq bo‘lgan funksiya bilan kesmaning ikkinchi yarmiga rekursiv ravishda o‘tamiz. Ko‘rinib turibdiki, bu kesmaning birinchi yarmida to‘g‘rilikni saqlaydi, ikkinchisida esa to‘g‘rilik rekursiv chaqiruv davomida ta’minlanadi. Shunday qilib, funksiyalarni qo‘shish va nuqtadagi minimal qiymatni tekshirishni $O(\log [C\varepsilon^{-1}])$ vaqtda bajarish mumkin.

Tugunga yangi funksiya qo‘shilganda nima bo‘layotganining tasviri:

  ![Li Chao Tree vertex](/algorithms-media/geometry/li_chao_vertex.png)

Endi amalga oshirishga o‘tamiz. Chiziqli funksiyalarni saqlash uchun yana kompleks sonlardan foydalanamiz.

```cpp
typedef long long ftype;
typedef complex<ftype> point;
#define x real
#define y imag
 
ftype dot(point a, point b) {
    return (conj(a) * b).x();
}
 
ftype f(point a,  ftype x) {
    return dot(a, {x, 1});
}
```
Funksiyalarni $line$ massivida saqlaymiz va segment daraxtining ikkilik indekslashidan foydalanamiz. Agar uni katta sonlar yoki haqiqiy sonlar uchun ishlatmoqchi bo‘lsangiz, dinamik segment daraxtidan foydalanish kerak.
Segment daraxti standart qiymatlar bilan, masalan, $0x + \infty$ chiziqlari bilan initsializatsiya qilinishi kerak.

```cpp
const int maxn = 2e5;
 
point line[4 * maxn];
 
void add_line(point nw, int v = 1, int l = 0, int r = maxn) {
    int m = (l + r) / 2;
    bool lef = f(nw, l) < f(line[v], l);
    bool mid = f(nw, m) < f(line[v], m);
    if(mid) {
        swap(line[v], nw);
    }
    if(r - l == 1) {
        return;
    } else if(lef != mid) {
        add_line(nw, 2 * v, l, m);
    } else {
        add_line(nw, 2 * v + 1, m, r);
    }
}
```
Endi biror $x$ nuqtadagi minimumni olish uchun shu nuqtaga olib boradigan yo‘l bo‘ylab eng kichik qiymatni oddiygina tanlaymiz.
```cpp
ftype get(int x, int v = 1, int l = 0, int r = maxn) {
    int m = (l + r) / 2;
    if(r - l == 1) {
        return f(line[v], x);
    } else if(x < m) {
        return min(f(line[v], x), get(x, 2 * v, l, m));
    } else {
        return min(f(line[v], x), get(x, 2 * v + 1, m, r));
    }
}
```

## Mashq masalalari {#problems}

* [Codebreaker - TROUBLES](https://codeforces.com/gym/103536/problem/B) (bir nechta kuzatuvdan keyin Convex Hull Trick ning oddiy qo‘llanishi)
* [CS Academy - Squared Ends](https://csacademy.com/contest/archive/task/squared-ends)
* [Codeforces - Escape Through Leaf](http://codeforces.com/contest/932/problem/F)
* [CodeChef - Polynomials](https://www.codechef.com/NOV17/problems/POLY)
* [Codeforces - Kalila and Dimna in the Logging Industry](https://codeforces.com/problemset/problem/319/C)
* [Codeforces - Product Sum](https://codeforces.com/problemset/problem/631/E)
* [Codeforces - Bear and Bowling 4](https://codeforces.com/problemset/problem/660/F)
* [APIO 2010 - Commando](https://dmoj.ca/problem/apio10p1)
