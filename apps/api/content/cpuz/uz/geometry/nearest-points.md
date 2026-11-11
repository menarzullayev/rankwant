# Eng yaqin nuqtalar juftini topish

## Masala sharti

Tekislikda $n$ ta nuqta berilgan. Har bir $p_i$ nuqta o‘zining $(x_i,y_i)$ koordinatalari bilan aniqlanadi. Ular orasidan shunday ikkita nuqtani topish talab etiladiki, ular orasidagi masofa minimal bo‘lsin:

$$ \min_{\scriptstyle i, j=0 \ldots n-1,\atop \scriptstyle i \neq j } \rho (p_i, p_j). $$

Odatdagi Evklid masofalarini olamiz:

$$ \rho (p_i,p_j) = \sqrt{(x_i-x_j)^2 + (y_i-y_j)^2} .$$

Oddiy algoritm — barcha juftliklarni ko‘rib chiqib, har biri uchun masofani hisoblash — $O(n^2)$ da ishlaydi.

$O(n \log n)$ vaqtda ishlaydigan algoritm quyida tasvirlangan. Bu algoritmni 1975-yilda Shamos va Hoey taklif qilgan. (Manba: Kleinberg va Tardosning _Algorithm Design_ kitobi 5-bobining izohlari, shuningdek [bu yerga](https://ieeexplore.ieee.org/abstract/document/4567872) qarang.) Preparata va Shamos, shuningdek, bu algoritm qaror daraxti modelida optimal ekanini ko‘rsatgan.

## Algoritm

Algoritmni **bo‘lib yechish** algoritmlarining umumiy sxemasi bo‘yicha quramiz: algoritm rekursiv funksiya sifatida tuziladi, unga nuqtalar to‘plami uzatiladi; bu rekursiv funksiya to‘plamni teng ikkiga bo‘ladi, har bir yarmi uchun o‘zini rekursiv chaqiradi, so‘ng javoblarni birlashtirish uchun ba’zi amallarni bajaradi. Birlashtirish amali optimal yechimning bir nuqtasi bir yarmga, ikkinchi nuqtasi esa ikkinchi yarmga tushgan holatlarni aniqlashdan iborat (bu holda har bir yarmdan qilingan rekursiv chaqiruvlar bu juftni alohida aniqlay olmaydi). Bo‘lib yechish algoritmlarida doim bo‘lgani kabi, asosiy qiyinchilik birlashtirish bosqichini samarali implementatsiya qilishda yotadi. Agar rekursiv funksiyaga $n$ ta nuqtadan iborat to‘plam uzatilsa, birlashtirish bosqichi $O(n)$ dan ortiq ishlamasligi kerak; shunda butun algoritmning asimptotikasi $T(n)$ quyidagi tenglamadan topiladi:

$$T(n) = 2T(n/2) + O(n).$$

Ma’lumki, bu tenglamaning yechimi $T(n) = O(n \log n).$

Shunday qilib, algoritmni qurishga o‘tamiz. Kelgusida birlashtirish bosqichini samarali implementatsiya qilish uchun nuqtalar to‘plamini ularning $x$-koordinatalariga ko‘ra ikki qism to‘plamga ajratamiz: aslida, nuqtalar to‘plamini taxminan bir xil o‘lchamli ikkita qism to‘plamga ajratuvchi biror vertikal chiziq o‘tkazamiz. Bunday ajratishni quyidagicha qilish qulay: nuqtalarni standart usulda, ya’ni sonlar juftligi sifatida saralaymiz, ya’ni:

$$p_i < p_j \Longleftrightarrow (x_i < x_j) \lor \Big(\left(x_i = x_j\right) \wedge \left(y_i < y_j \right) \Big) $$

So‘ng saralangandan keyingi o‘rta nuqta $p_m (m = \lfloor n/2 \rfloor)$ ni olamiz; undan oldingi barcha nuqtalar va $p_m$ ning o‘zi birinchi yarmga, undan keyingi barcha nuqtalar esa ikkinchi yarmga tegishli bo‘ladi:

$$A_1 = \{p_i \ | \ i = 0 \ldots m \}$$

$$A_2 = \{p_i \ | \ i = m + 1 \ldots n-1 \}.$$

Endi $A_1$ va $A_2$ to‘plamlarning har biri uchun rekursiv chaqirib, ularning har biri bo‘yicha $h_1$ va $h_2$ javoblarni topamiz. Va ularning eng yaxshisini olamiz: $h = \min(h_1, h_2)$.

Endi **birlashtirish bosqichi**ni bajarishimiz kerak, ya’ni orasidagi masofa $h$ dan kichik bo‘lgan va bir nuqtasi $A_1$ da, ikkinchisi $A_2$ da yotgan nuqtalar juftlarini topishga harakat qilamiz.
Faqat vertikal chiziqdan masofasi $h$ dan kichik bo‘lgan nuqtalarni ko‘rib chiqish yetarli ekani ravshan, ya’ni bu bosqichda ko‘riladigan $B$ nuqtalar to‘plami quyidagiga teng:

$$B = \{ p_i\ | \ | x_i - x_m\ | < h \}.$$

$B$ to‘plamdagi har bir nuqta uchun undan $h$ dan yaqinroq nuqtalarni topishga harakat qilamiz. Masalan, faqat $y$-koordinatasi undan $h$ dan ko‘p farq qilmaydigan nuqtalarni ko‘rib chiqish yetarli. Bundan tashqari, $y$-koordinatasi joriy nuqtaning $y$-koordinatasidan katta bo‘lgan nuqtalarni ko‘rib chiqishning ma’nosi yo‘q. Shunday qilib, har bir $p_i$ nuqta uchun ko‘riladigan nuqtalar to‘plami $C(p_i)$ ni quyidagicha aniqlaymiz:

$$C(p_i) = \{ p_j\ |\ p_j \in B,\ \ y_i - h < y_j \le y_i \}.$$

Agar $B$ to‘plam nuqtalarini $y$-koordinata bo‘yicha saralasak, $C(p_i)$ ni topish juda oson bo‘ladi: bular $p_i$ nuqtadan oldingi qatorda kelgan bir nechta nuqta.

Shunday qilib, yangi belgilashlarda **birlashtirish bosqichi** quyidagicha ko‘rinadi: $B$ to‘plamni quramiz, undagi nuqtalarni $y$-koordinata bo‘yicha saralaymiz, so‘ng har bir $p_i \in B$ nuqta uchun barcha $p_j \in C(p_i)$ nuqtalarni ko‘rib chiqamiz va har bir $(p_i,p_j)$ juftlik uchun masofani hisoblab, joriy eng yaxshi masofa bilan taqqoslaymiz.

Bir qarashda bu hamon optimal bo‘lmagan algoritm: $C(p_i)$ to‘plamlar o‘lchami $n$ tartibida bo‘lib, talab qilingan asimptotika ishlamaydigandek tuyuladi. Biroq, ajablanarlisi, har bir $C(p_i)$ to‘plamning o‘lchami $O(1)$ miqdor ekanini, ya’ni nuqtalarning o‘ziga bog‘liq bo‘lmagan holda biror kichik doimiydan oshmasligini isbotlash mumkin. Bu faktning isboti keyingi bo‘limda keltirilgan.

Nihoyat, yuqoridagi algoritm tarkibidagi saralashlarga e’tibor beramiz: birinchisi — $(x, y)$ juftliklar bo‘yicha saralash, ikkinchisi — $B$ to‘plam elementlarini $y$ bo‘yicha saralash. Aslida, rekursiv funksiya ichidagi bu ikkala saralashni ham yo‘qotish mumkin (aks holda **birlashtirish bosqichi** uchun $O(n)$ bahoga erisha olmas edik, algoritmning umumiy asimptotikasi esa $O(n \log^2 n)$ bo‘lar edi). Birinchi saralashdan qutulish oson — bu saralashni rekursiyani boshlashdan oldin bajarish yetarli: axir elementlarning o‘zi rekursiya ichida o‘zgarmaydi, shuning uchun qayta saralash shart emas. Ikkinchi saralash bilan biroz qiyinroq; uni oldindan bajarish ishlamaydi. Ammo bo‘lib yechish tamoyilida ishlaydigan birlashtirib saralashni eslab, bu saralashni shunchaki o‘z rekursiyamizga kiritishimiz mumkin. Rekursiya biror nuqtalar to‘plamini (eslaganimizdek, $(x, y)$ juftliklar bo‘yicha tartiblangan) olib, xuddi shu to‘plamni, lekin $y$-koordinata bo‘yicha saralangan holda qaytarsin. Buning uchun rekursiv chaqiruvlar qaytargan ikki natijani ($O(n)$ da) birlashtirish kifoya. Bu $y$-koordinata bo‘yicha saralangan to‘plamni beradi.

## Asimptotikani baholash

Yuqoridagi algoritm haqiqatan $O(n \log n)$ da bajarilishini ko‘rsatish uchun quyidagi faktni isbotlashimiz kerak: $|C(p_i)| = O(1)$.

Demak, biror $p_i$ nuqtani ko‘rib chiqaylik; eslatib o‘tamiz, $C(p_i)$ to‘plam — $y$-koordinatasi $[y_i-h; y_i]$ kesmada yotgan nuqtalar to‘plami, bundan tashqari, $x$ koordinata bo‘yicha $p_i$ nuqtaning o‘zi ham, $C(p_i)$ to‘plamning barcha nuqtalari ham kengligi $2h$ bo‘lgan polosada yotadi. Boshqacha aytganda, biz ko‘rayotgan $p_i$ va $C(p_i)$ nuqtalari o‘lchami $2h \times h$ bo‘lgan to‘g‘ri to‘rtburchakda yotadi.

Vazifamiz — bu $2h \times h$ to‘g‘ri to‘rtburchakda yotishi mumkin bo‘lgan nuqtalarning maksimal sonini baholash; shu bilan $C(p_i)$ to‘plamning maksimal o‘lchamini baholaymiz. Shu bilan birga, baholashda takrorlanuvchi nuqtalar bo‘lishi mumkinligini unutmasligimiz kerak.

Eslang, $h$ ikkita rekursiv chaqiruv — $A_1$ va $A_2$ to‘plamlar — natijalaridan olingan, bunda $A_1$ ajratuvchi chiziqning chap tomonidagi va qisman uning ustidagi nuqtalarni, $A_2$ esa ajratuvchi chiziqdagi qolgan nuqtalarni va undan o‘ngdagi nuqtalarni o‘z ichiga oladi. $A_1$ dan ham, $A_2$ dan ham olingan istalgan nuqtalar juftligi uchun masofa $h$ dan kichik bo‘la olmaydi — aks holda bu rekursiv funksiyaning noto‘g‘ri ishlashini bildirardi.

$2h \times h$ to‘g‘ri to‘rtburchakdagi nuqtalarning maksimal sonini baholash uchun uni ikkita $h \times h$ kvadratga bo‘lamiz; birinchi kvadrat $C(p_i) \cap A_1$ ning barcha nuqtalarini, ikkinchisi esa qolganlarini, ya’ni $C(p_i) \cap A_2$ ni o‘z ichiga oladi. Yuqoridagi mulohazalardan bu kvadratlarning har birida istalgan ikki nuqta orasidagi masofa kamida $h$ ekani kelib chiqadi.

Har bir kvadratda ko‘pi bilan to‘rtta nuqta borligini ko‘rsatamiz. Masalan, buni quyidagicha qilish mumkin: kvadratni tomonlari $h/2$ bo‘lgan $4$ ta kichik kvadratga bo‘lamiz. U holda bu kichik kvadratlarning har birida bittadan ortiq nuqta bo‘lishi mumkin emas (chunki diagonali ham $h / \sqrt{2}$ ga teng, bu $h$ dan kichik). Demak, butun kvadratda $4$ tadan ortiq nuqta bo‘lishi mumkin emas.

Shunday qilib, $2h \times h$ to‘g‘ri to‘rtburchakda $4 \cdot 2 = 8$ tadan ortiq nuqta bo‘lishi mumkin emasligini, demak, $C(p_i)$ to‘plamning o‘lchami $7$ dan oshmasligini isbotladik, shuni talab qilgan edik.

## Implementatsiya

Nuqtani (uning koordinatalari va raqamini) saqlash uchun ma’lumotlar tuzilmasini hamda ikki turdagi saralash uchun zarur taqqoslash operatorlarini kiritamiz:

```cpp
struct pt {
    int x, y, id;
};

struct cmp_x {
    bool operator()(const pt & a, const pt & b) const {
        return a.x < b.x || (a.x == b.x && a.y < b.y);
    }
};
 
struct cmp_y {
    bool operator()(const pt & a, const pt & b) const {
        return a.y < b.y;
    }
};
 
int n;
vector<pt> a;
```

Rekursiyani qulay implementatsiya qilish uchun yordamchi `upd_ans()` funksiyasini kiritamiz: u ikki nuqta orasidagi masofani hisoblab, uning joriy javobdan yaxshiroq ekanini tekshiradi:

```cpp
double mindist;
pair<int, int> best_pair;
 
void upd_ans(const pt & a, const pt & b) {
    double dist = sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y));
    if (dist < mindist) {
        mindist = dist;
        best_pair = {a.id, b.id};
    }
}
```

Nihoyat, rekursiyaning o‘zi implementatsiyasi. Uni chaqirishdan oldin $a[]$ massiv allaqachon $x$-koordinata bo‘yicha saralangan deb faraz qilinadi. Rekursiyaga faqat ikkita $l, r$ ko‘rsatkichni uzatamiz; ular $a[l \ldots r)$ uchun javob qidirish kerakligini bildiradi. Agar $r$ va $l$ orasidagi masofa juda kichik bo‘lsa, rekursiyani to‘xtatib, eng yaqin juftni topish uchun oddiy algoritmni bajarish va so‘ng qism massivni $y$-koordinata bo‘yicha saralash kerak.

Rekursiv chaqiruvlardan olingan ikkita nuqtalar to‘plamini bittaga ($y$-koordinata bo‘yicha tartiblangan) birlashtirish uchun standart STL `merge()` funksiyasidan foydalanamiz va yordamchi $t[]$ buferini (barcha rekursiv chaqiruvlar uchun bitta) yaratamiz. (`inplace_merge()` dan foydalanish maqsadga muvofiq emas, chunki u odatda chiziqli vaqtda ishlamaydi.)

Nihoyat, $B$ to‘plam ham xuddi shu $t$ massivida saqlanadi.

```cpp
vector<pt> t;

void rec(int l, int r) {
    if (r - l <= 3) {
        for (int i = l; i < r; ++i) {
            for (int j = i + 1; j < r; ++j) {
                upd_ans(a[i], a[j]);
            }
        }
        sort(a.begin() + l, a.begin() + r, cmp_y());
        return;
    }

    int m = (l + r) >> 1;
    int midx = a[m].x;
    rec(l, m);
    rec(m, r);

    merge(a.begin() + l, a.begin() + m, a.begin() + m, a.begin() + r, t.begin(), cmp_y());
    copy(t.begin(), t.begin() + r - l, a.begin() + l);

    int tsz = 0;
    for (int i = l; i < r; ++i) {
        if (abs(a[i].x - midx) < mindist) {
            for (int j = tsz - 1; j >= 0 && a[i].y - t[j].y < mindist; --j)
                upd_ans(a[i], t[j]);
            t[tsz++] = a[i];
        }
    }
}
```

Aytgancha, agar barcha koordinatalar butun bo‘lsa, rekursiya vaqtida kasr qiymatlarga o‘tmasdan, $mindist$ da minimal masofaning kvadratini saqlash mumkin.

Asosiy dasturda rekursiya quyidagicha chaqirilishi kerak:

```cpp
t.resize(n);
sort(a.begin(), a.end(), cmp_x());
mindist = 1E20;
rec(0, n);
```

## Chiziqli vaqtli tasodifiy algoritmlar

### Kutilgan chiziqli vaqtli tasodifiy algoritm

Dastlab 1976-yilda Rabin taklif qilgan muqobil usul ishlash vaqtini evristik yaxshilashning juda sodda g‘oyasidan kelib chiqadi: tekislikni $d \times d$ kvadratlardan iborat to‘rga bo‘lib, faqat bir xil blokdagi yoki qo‘shni bloklardagi nuqtalar orasidagi masofalarni tekshirish yetarli (agar barcha kvadratlar bir-biridan uzilgan bo‘lmasa; buni esa loyihalash orqali oldini olamiz), chunki har qanday boshqa juft orasidagi masofa bir kvadratdagi ikki nuqta orasidagi masofadan kattaroq.

![Kvadratlar strategiyasiga misol](/algorithms-media/geometry/nearest_points_blocks_example.png)

Faqat kamida bitta nuqtasi bor kvadratlarni ko‘rib chiqamiz. Qolgan $k$ ta kvadratning har biridagi nuqtalar sonini $n_1, n_2, \dots, n_k$ bilan belgilaymiz. Kamida ikkita nuqta bir xil yoki qo‘shni kvadratlarda joylashgan va takrorlanuvchi nuqtalar yo‘q deb faraz qilsak, vaqt murakkabligi $\Theta\!\left(\sum\limits_{i=1}^k n_i^2\right)$ bo‘ladi. Takrorlanuvchi nuqtalarni xesh jadvali yordamida kutilgan chiziqli vaqtda qidirish mumkin va ular topilgan taqdirda javob shu juftlik bo‘ladi.

> **Isbot**
>
> $n_i$ ta nuqtali $i$-kvadrat uchun uning ichidagi juftliklar soni $\Theta(n_i^2)$. Agar $i$-kvadrat $j$-kvadratga qo‘shni bo‘lsa, biz yana $n_i n_j \le \max(n_i, n_j)^2 \le n_i^2 + n_j^2$ ta masofa taqqoslashini bajaramiz. E’tibor bering, har bir kvadratning ko‘pi bilan $8$ ta qo‘shnisi bor, shuning uchun barcha taqqoslashlar yig‘indisini $\Theta(\sum_{i=1}^{k} n_i^2)$ bilan chegaralashimiz mumkin. $\quad \blacksquare$

Endi $\Theta\!\left(\sum\limits_{i=1}^k n_i^2\right)$ ni minimallashtiradigan qilib $d$ ni qanday tanlashni hal qilishimiz kerak.

#### $d$ ni tanlash

Bizga $d$ minimal masofa $d$ ning yaqinlashuvi bo‘lishi kerak. Richard Lipton $n$ ta masofani tasodifiy tanlab olishni va $d$ ning yaqinlashuvi sifatida shu masofalarning eng kichigini tanlashni taklif qildi. Endi algoritmning kutilgan ishlash vaqti chiziqli ekanini isbotlaymiz.

> **Isbot**
>
> Nuqtalarning kvadratlardagi joylashuvini $d$ ning biror aniq tanlovida, aytaylik $x$ da, tasavvur qiling. $d$ ni masofalarni tanlab olishimiz natijasida hosil bo‘lgan tasodifiy miqdor deb qarang. $d=x$ ni tanlaganimizda ma’lum bir joylashuv uchun xarajat bahosi sifatida $C(x) := \sum_{i=1}^{k(x)} n_i(x)^2$ ni aniqlaymiz. Endi $\lambda(x)$ ni $C(x) = \lambda(x) \, n$ bo‘ladigan qilib aniqlaymiz. Bunday $x$ tanlovi $n$ ta mustaqil masofani tanlab olishdan «omon qolish» ehtimoli qanday? Tanlab olinganlar orasidan bitta juftning masofasi ham $x$ dan kichik bo‘lsa, bu joylashuv kichikroq $d$ bilan almashtiriladi. Kvadrat ichida juftlarning taxminan $1/16$ qismi kichikroq masofa beradi (har bir kvadratda to‘rtta kichik kvadratni tasavvur qiling; Dirixle prinsipiga ko‘ra, kamida bitta kichik kvadratda $n_i/4$ nuqta bor), shuning uchun yakuniy $d$ ni kichraytiradigan taxminan $\sum_{i=1}^{k} {n_i/4 \choose 2} \approx \sum_{i=1}^{k} \frac{1}{16} {n_i \choose 2}$ juftlik bor. Bu taxminan $\frac{1}{32} \sum_{i=1}^{k} n_i^2 = \frac{1}{32} \lambda(x) n$ ga teng. Boshqa tomondan, tanlab olinishi mumkin bo‘lgan taxminan $\frac{1}{2} n^2$ juftlik bor. Demak, masofasi $x$ dan kichik bo‘lgan juftni tanlab olish ehtimoli kamida (taxminan)
>
> $$\frac{\lambda(x) \, n / 32}{n^2 / 2} = \frac{\lambda(x)/16}{n}$$
>
> bo‘ladi, shuning uchun $n$ ta urinish davomida bunday juftlardan kamida bittasi tanlanishi (va shu bilan kichikroq $d$ topilishi) ehtimoli
>
> $$1 - \left(1 - \frac{\lambda(x)/16}{n}\right)^n \ge 1 - e^{-\lambda(x)/16}$$
>
> bo‘ladi (biz har qanday haqiqiy $x$ soni uchun $(1 + x)^n \le e^{xn}$ ekanidan foydalandik, [Bernulli tengsizliklari](https://en.wikipedia.org/wiki/Bernoulli%27s_inequality#Related_inequalities)ga qarang). E’tibor bering, bu ehtimol $\lambda(x)$ ortishi bilan eksponensial ravishda $1$ ga intiladi. Bu $d$ yomon tanlangan bo‘lsa, $\lambda$ kichik bo‘lishini anglatadi.
>
>
> Biz $\Pr(d \le x) \ge 1 - e^{-\lambda(x)/16}$ yoki unga teng ravishda $\Pr(d \ge x) \le e^{-\lambda(x)/16}$ ekanini ko‘rsatdik. Uning matematik kutilmasini baholay olish uchun $\Pr(\lambda(d) \ge \text{biror qiymat})$ ni bilishimiz kerak. $\lambda(d) \ge \lambda(x) \iff d \ge x$ ekanini payqaymiz. Buning sababi, kvadratlarni kichraytirish har bir kvadratdagi nuqtalar sonini faqat kamaytiradi (nuqtalarni boshqa kvadratlarga bo‘lib yuboradi) va bu kvadratlar yig‘indisini kamaytirishda davom etadi. Shuning uchun,
>
> $$\Pr(\lambda(d) \ge \lambda(x)) = \Pr(d \ge x) \le e^{-\lambda(x)/16} \implies \Pr(\lambda(d) \ge t) \le e^{-t/16} \implies \mathbb{E}[\lambda(d)] \le \int_{0}^{+\infty} e^{-t/16} \, \mathrm{d}t = 16$$
>
> (biz $E[X] = \int_0^{+\infty} \Pr(X \ge x) \, \mathrm{d}x$ ekanidan foydalandik, [Stackexchange isboti](https://math.stackexchange.com/a/1690829)ga qarang).
>
> Nihoyat, $\mathbb{E}[C(d)] = \mathbb{E}[\lambda(d) \, n] \le 16n$, va kutilgan ishlash vaqti $O(n)$, doimiy ko‘paytuvchisi esa maqbul. $\quad \blacksquare$

#### Algoritmning implementatsiyasi

Bu algoritmning afzalligi — implementatsiya qilish oddiy, lekin amalda baribir yaxshi samaradorlikka ega. Avval $n$ ta masofani tasodifiy tanlab olamiz va $d$ ni shu masofalarning minimumi deb olamiz. So‘ng nuqtalarni 2 o‘lchamli koordinatalardan nuqtalar vektoriga o‘tkazuvchi xesh jadvali yordamida «bloklar»ga joylashtiramiz. Nihoyat, faqat bir xil blokdagi juftlar va qo‘shni blokdagi juftlar orasidagi masofalarni hisoblaymiz. Xesh jadvali amallarining kutilgan vaqt xarajati $O(1)$, shuning uchun algoritmimiz kutilgan $O(n)$ vaqt xarajatini, faqat kattaroq doimiy bilan, saqlab qoladi.

Library Checker’ga yuborilgan [bu yechimga](https://judge.yosupo.jp/submission/309605) qarang.

```cpp
#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using ld = long double;

struct pt {
	ll x, y;
	pt() {}
	pt(ll x_, ll y_) : x(x_), y(y_) {}
	void read() {
		cin >> x >> y;
	}
};

bool operator==(const pt& a, const pt& b) {
    return a.x == b.x and a.y == b.y;
}

struct CustomHashPoint {
	size_t operator()(const pt& p) const {
		static const uint64_t C = chrono::steady_clock::now().time_since_epoch().count();
		return C ^ ((p.x << 32) ^ p.y);
	}
};

ll dist2(pt a, pt b) {
	ll dx = a.x - b.x;
	ll dy = a.y - b.y;
	return dx*dx + dy*dy;
}

pair<int,int> closest_pair_of_points(vector<pt> P) {
    int n = int(P.size());
    assert(n >= 2);

    // if there is a duplicated point, we have the solution
    unordered_map<pt,int,CustomHashPoint> previous;
    for (int i = 0; i < int(P.size()); ++i) {
        auto it = previous.find(P[i]);
        if (it != previous.end()) {
            return {it->second, i};
        }
        previous[P[i]] = i;
    }

	unordered_map<pt,vector<int>,CustomHashPoint> grid;
	grid.reserve(n);

	mt19937 rd(chrono::system_clock::now().time_since_epoch().count());
	uniform_int_distribution<int> dis(0, n-1);

	ll d2 = dist2(P[0], P[1]);
	pair<int,int> closest = {0, 1};

	auto candidate_closest = [&](int i, int j) -> void {
		ll ab2 = dist2(P[i], P[j]);
		if (ab2 < d2) {
			d2 = ab2;
			closest = {i, j};
		}
	};

	for (int i = 0; i < n; ++i) {
		int j = dis(rd);
		int k = dis(rd);
		while (j == k) k = dis(rd);
		candidate_closest(j, k);
	}

	ll d = ll( sqrt(ld(d2)) + 1 );

	for (int i = 0; i < n; ++i) {
		grid[{P[i].x/d, P[i].y/d}].push_back(i);
	}

	// same block
	for (const auto& it : grid) {
		int k = int(it.second.size());
		for (int i = 0; i < k; ++i) {
			for (int j = i+1; j < k; ++j) {
				candidate_closest(it.second[i], it.second[j]);
			}
		}
	}
 
	// adjacent blocks
	for (const auto& it : grid) {
		auto coord = it.first;
		for (int dx = 0; dx <= 1; ++dx) {
			for (int dy = -1; dy <= 1; ++dy) {
				if (dx == 0 and dy == 0) continue;
				pt neighbour = pt(
					coord.x  + dx, 
					coord.y + dy
                );
				for (int i : it.second) {
					if (not grid.count(neighbour)) continue;
					for (int j : grid.at(neighbour)) {
						candidate_closest(i, j);
					}
				}
			}
		}
	}

	return closest;
}
```

### Kutilgan chiziqli vaqtli muqobil tasodifiy algoritm

Endi boshqa, amaliyroq bo‘lmagan, lekin kutilgan chiziqli vaqtda ishlashini ko‘rsatish juda oson bo‘lgan tasodifiy algoritmni keltiramiz.

- $n$ ta nuqtani tasodifiy almashtiramiz
- $\delta := \operatorname{dist}(p_1, p_2)$ ni olamiz
- Tekislikni tomoni $\delta/2$ bo‘lgan kvadratlarga bo‘lamiz
- $i = 1,2,\dots,n$ uchun:
    - $p_i$ ga mos kvadratni olamiz
    - Tekislikni bo‘lgan kvadratlar to‘rida bizning kvadratimizdan ikki qadam ichida joylashgan $25$ ta kvadrat bo‘ylab yuramiz
    - Agar shu kvadratlardagi biror $p_j$ uchun $\operatorname{dist}(p_j, p_i) < \delta$ bo‘lsa, u holda
        - Bo‘linish va kvadratlarni $\delta := \operatorname{dist}(p_j, p_i)$ bilan qayta hisoblaymiz
        - $p_1, \dots, p_i$ nuqtalarni mos kvadratlarda saqlaymiz
    - aks holda $p_i$ ni mos kvadratda saqlaymiz
- $\delta$ ni chiqaramiz

To‘g‘rilik shundan kelib chiqadiki, istalgan paytda bizda masofasi $\delta$ bo‘lgan biror juft allaqachon bor, shuning uchun faqat masofasi $\delta$ dan kichik bo‘lgan yangi juftlarni topishga harakat qilamiz. Har bir kvadratning tomoni $\delta/2$ bo‘lgani uchun nomzod juft ko‘pi bilan $2$ kvadrat masofada bo‘lishi mumkin, shuning uchun berilgan nuqta uchun atrofdagi $25$ ta kvadratdagi nomzodlarni tekshiramiz. Undan uzoqroqdagi kvadratning har qanday nuqtasi doim $\delta$ dan kattaroq masofa beradi.

Bu algoritm hamma narsani bir necha marta qayta hisoblagani uchun sekin ko‘rinishi mumkin, ammo umumiy kutilgan xarajat chiziqli ekanini ko‘rsatish mumkin.

> **Isbot**
>
> $X_i$ tasodifiy miqdor bo‘lsin: $p_i$ nuqta $\delta$ ning o‘zgarishiga va ma’lumotlar tuzilmalarining qayta hisoblanishiga sabab bo‘lsa $1$, aks holda $0$ ga teng. Xarajat $O(n + \sum_{i=1}^{n} i X_i)$ ekanini ko‘rsatish oson, chunki $i$-qadamda faqat dastlabki $i$ ta nuqtani ko‘rib chiqamiz. Biroq $\Pr(X_i = 1) \le \frac{2}{i}$ ekani ma’lum bo‘ladi. Buning sababi, $i$-qadamda $\delta$ — $\{p_1,\dots,p_i\}$ dagi eng yaqin juftning masofasi, $\Pr(X_i = 1)$ esa $p_i$ ning eng yaqin juftga tegishli bo‘lish ehtimoli; bu mumkin bo‘lgan $i(i-1)$ ta juftdan faqat $2(i-1)$ tasida sodir bo‘ladi (barcha masofalar turlicha deb faraz qilsak), shuning uchun ehtimol ko‘pi bilan $\frac{2(i-1)}{i(i-1)} = \frac{2}{i}$, chunki nuqtalarni avval bir tekis aralashtirgan edik.
>
> Demak, kutilgan xarajat
>
> $$O\!\left(n + \sum_{i=1}^{n} i \Pr(X_i = 1)\right) \le O\!\left(n + \sum_{i=1}^{n} i \frac{2}{i}\right) = O(3n) = O(n) \quad \quad \blacksquare$$

## Umumlashtirish: minimal perimetrli uchburchakni topish

Yuqorida tasvirlangan algoritm bu masalaga qiziqarli tarzda umumlashtiriladi: berilgan nuqtalar to‘plamidan uchta turli nuqtani shunday tanlash kerakki, ular orasidagi juft masofalar yig‘indisi eng kichik bo‘lsin.

Aslida, bu masalani yechish uchun algoritm o‘zgarishsiz qoladi: maydonni vertikal chiziq bilan ikki yarmga bo‘lamiz, har ikki yarm uchun yechimni rekursiv chaqiramiz, topilgan perimetrlardan minimal $minper$ ni tanlaymiz, qalinligi $minper / 2$ bo‘lgan polosa quramiz va javobni yaxshilashi mumkin bo‘lgan barcha uchburchaklarni ko‘rib chiqamiz. (E’tibor bering, perimetri $\le minper$ bo‘lgan uchburchakning eng uzun tomoni $\le minper / 2$ bo‘ladi.)

## Mashq masalalari

* [UVA 10245 "The Closest Pair Problem" [qiyinlik: oson]](https://uva.onlinejudge.org/index.php?option=onlinejudge&page=show_problem&problem=1186)
* [SPOJ #8725 CLOPPAIR "Closest Point Pair" [qiyinlik: oson]](https://www.spoj.com/problems/CLOPPAIR/)
* [CODEFORCES Team Olympiad Saratov - 2011 "Minimum amount" [qiyinlik: o‘rta]](http://codeforces.com/contest/120/problem/J)
* [Google CodeJam 2009 Final "Min Perimeter" [qiyinlik: o‘rta]](https://github.com/google/coding-competitions-archive/blob/main/codejam/2009/world_finals/min_perimeter/statement.pdf)
* [SPOJ #7029 CLOSEST "Closest Triple" [qiyinlik: o‘rta]](https://www.spoj.com/problems/CLOSEST/)
* [TIMUS 1514 National Park [qiyinlik: o‘rta]](https://acm.timus.ru/problem.aspx?space=1&num=1514)
