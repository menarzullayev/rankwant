# Nuqta qavariq ko‘pburchakka tegishli ekanini $O(\log N)$ da tekshirish

Quyidagi masalani ko‘rib chiqamiz: butun koordinatali uchlarga ega qavariq ko‘pburchak va ko‘plab so‘rovlar berilgan.
Har bir so‘rov — bitta nuqta; uning ko‘pburchak ichida yoki chegarasida yotishi yoki yotmasligini aniqlash kerak.
Ko‘pburchak soat miliga teskari yo‘nalishda tartiblangan deb faraz qilamiz. Har bir so‘rovga $O(\log n)$ da onlayn javob beramiz.

## Algoritm
Eng kichik x-koordinatali nuqtani tanlaymiz. Bunday nuqtalar bir nechta bo‘lsa, eng kichik y-koordinatalisini olamiz. Uni $p_0$ deb belgilaymiz.
Endi ko‘pburchakning qolgan barcha $p_1,\dots,p_n$ nuqtalari tanlangan nuqtadan olingan qutb burchagi bo‘yicha tartiblangan (chunki ko‘pburchak soat miliga teskari yo‘nalishda tartiblangan).

Agar nuqta ko‘pburchakka tegishli bo‘lsa, u biror $p_0, p_i, p_{i + 1}$ uchburchakka tegishli bo‘ladi (agar nuqta uchburchaklar chegarasida yotsa, bunday uchburchak bittadan ko‘p bo‘lishi mumkin).
$p$ shu uchburchakka tegishli bo‘ladigan va $i$ barcha shunday uchburchaklar orasida eng katta bo‘lgan $p_0, p_i, p_{i + 1}$ uchburchakni ko‘rib chiqamiz.

Bitta maxsus holat bor: $p$ nuqta $(p_0, p_n)$ kesmada yotadi. Bu holatni alohida tekshiramiz.
Aks holda $i$ dan oshmaydigan indeksli barcha $p_j$ nuqtalar $p_0$ ga nisbatan $p$ dan soat miliga teskari tomonda joylashadi, qolgan nuqtalar esa soat miliga teskari tomonda emas.
Demak, $p_0$ ga nisbatan $p$ dan soat miliga teskari tomonda bo‘lmagan va $i$ eng katta bo‘lgan $p_i$ nuqtani binar qidiruv bilan topish mumkin.
Keyin esa nuqta haqiqatan ham aniqlangan uchburchak ichida ekanini tekshiramiz.

$(a - c) \times (b - c)$ ning ishorasi $a$ nuqta $c$ nuqtaga nisbatan $b$ nuqtadan soat mili bo‘yicha yoki soat miliga teskari tomonda joylashganini bildiradi.
Agar $(a - c) \times (b - c) > 0$ bo‘lsa, $a$ nuqta $c$ dan $b$ ga yo‘nalgan vektorning o‘ng tomonida bo‘ladi, ya’ni $c$ ga nisbatan $b$ dan soat mili bo‘yicha joylashadi.
Agar $(a - c) \times (b - c) < 0$ bo‘lsa, nuqta chap tomonda, ya’ni soat miliga teskari tomonda bo‘ladi.
Va nuqta aynan $b$ va $c$ nuqtalar orasidagi to‘g‘ri chiziqda yotadi.

Algoritmga qaytamiz:
$p$ so‘rov nuqtasini ko‘rib chiqamiz.
Avvalo nuqta $p_1$ va $p_n$ orasida yotishini tekshirishimiz kerak.
Aks holda uning ko‘pburchakka tegishli bo‘la olmasligini allaqachon bilamiz.
Buni $(p_1 - p_0)\times(p - p_0)$ vektor ko‘paytmasi nolga teng ekanini yoki $(p_1 - p_0)\times(p_n - p_0)$ bilan bir xil ishorali ekanini, shuningdek $(p_n - p_0)\times(p - p_0)$ nolga teng ekanini yoki $(p_n - p_0)\times(p_1 - p_0)$ bilan bir xil ishorali ekanini tekshirish orqali bajarish mumkin.
Keyin $p$ nuqta $(p_0, p_1)$ chiziqning qismi bo‘lgan maxsus holatni ko‘rib chiqamiz.
Shundan so‘ng $p_1,\dots p_n$ orasidan $p_0$ ga nisbatan $p$ dan soat miliga teskari tomonda bo‘lmagan oxirgi nuqtani binar qidiruv bilan topamiz.
Bitta $p_i$ nuqta uchun bu shartni $(p_i - p_0)\times(p - p_0) \le 0$ ekanini tekshirish orqali bilish mumkin. Bunday $p_i$ nuqtani topgach, $p$ nuqta $p_0, p_i, p_{i + 1}$ uchburchak ichida yotadimi yoki yo‘qmi, tekshirishimiz kerak.
Nuqtaning uchburchakka tegishli ekanini tekshirish uchun shunchaki $|(p_i - p_0)\times(p_{i + 1} - p_0)| = |(p_0 - p)\times(p_i - p)| + |(p_i - p)\times(p_{i + 1} - p)| + |(p_{i + 1} - p)\times(p_0 - p)|$ tengligini tekshirish kifoya.
Bu $p_0, p_i, p_{i+1}$ uchburchakning yuzi $p_0, p_i, p$ uchburchak, $p_0, p, p_{i+1}$ uchburchak va $p_i, p_{i+1}, p$ uchburchak yuzlari yig‘indisiga aniq teng ekanini tekshiradi.
Agar $p$ tashqarida bo‘lsa, bu uchta uchburchak yuzlarining yig‘indisi uchburchak yuzidan katta bo‘ladi.
Agar ichkarida bo‘lsa, ular teng bo‘ladi.

## Implementatsiya

`prepare` funksiyasi leksikografik jihatdan eng kichik nuqta (eng kichik x qiymatli, x teng bo‘lsa eng kichik y qiymatli) $p_0$ bo‘lishini ta’minlaydi va $p_i - p_0$ vektorlarni hisoblaydi.
Keyin `pointInConvexPolygon` funksiyasi so‘rov natijasini hisoblaydi.
Bundan tashqari, biz $p_0$ nuqtani eslab qolamiz va masofalarni to‘g‘ri hisoblash uchun barcha so‘ralgan nuqtalarni u bilan siljitamiz, chunki vektorlarning boshlang‘ich nuqtasi yo‘q.
So‘rov nuqtalarini siljitish orqali barcha vektorlar koordinata boshi $(0, 0)$ dan boshlanadi deb hisoblash mumkin, bu esa masofa va uzunliklarni hisoblashni soddalashtiradi.

```cpp
struct pt {
    long long x, y;
    pt() {}
    pt(long long _x, long long _y) : x(_x), y(_y) {}
    pt operator+(const pt &p) const { return pt(x + p.x, y + p.y); }
    pt operator-(const pt &p) const { return pt(x - p.x, y - p.y); }
    long long cross(const pt &p) const { return x * p.y - y * p.x; }
    long long dot(const pt &p) const { return x * p.x + y * p.y; }
    long long cross(const pt &a, const pt &b) const { return (a - *this).cross(b - *this); }
    long long dot(const pt &a, const pt &b) const { return (a - *this).dot(b - *this); }
    long long sqrLen() const { return this->dot(*this); }
};

bool lexComp(const pt &l, const pt &r) {
    return l.x < r.x || (l.x == r.x && l.y < r.y);
}

int sgn(long long val) { return val > 0 ? 1 : (val == 0 ? 0 : -1); }

vector<pt> seq;
pt translation;
int n;

bool pointInTriangle(pt a, pt b, pt c, pt point) {
    long long s1 = abs(a.cross(b, c));
    long long s2 = abs(point.cross(a, b)) + abs(point.cross(b, c)) + abs(point.cross(c, a));
    return s1 == s2;
}

void prepare(vector<pt> &points) {
    n = points.size();
    int pos = 0;
    for (int i = 1; i < n; i++) {
        if (lexComp(points[i], points[pos]))
            pos = i;
    }
    rotate(points.begin(), points.begin() + pos, points.end());

    n--;
    seq.resize(n);
    for (int i = 0; i < n; i++)
        seq[i] = points[i + 1] - points[0];
    translation = points[0];
}

bool pointInConvexPolygon(pt point) {
    point = point - translation;
    if (seq[0].cross(point) != 0 &&
            sgn(seq[0].cross(point)) != sgn(seq[0].cross(seq[n - 1])))
        return false;
    if (seq[n - 1].cross(point) != 0 &&
            sgn(seq[n - 1].cross(point)) != sgn(seq[n - 1].cross(seq[0])))
        return false;

    if (seq[0].cross(point) == 0)
        return seq[0].sqrLen() >= point.sqrLen();

    int l = 0, r = n - 1;
    while (r - l > 1) {
        int mid = (l + r) / 2;
        int pos = mid;
        if (seq[pos].cross(point) >= 0)
            l = mid;
        else
            r = mid;
    }
    int pos = l;
    return pointInTriangle(seq[pos], seq[pos + 1], pt(0, 0), point);
}
```

## Masalalar
* [SGU253 Theodore Roosevelt](https://codeforces.com/problemsets/acmsguru/problem/99999/253)
* [Codeforces 55E Very simple problem](https://codeforces.com/contest/55/problem/E)
* [Codeforces 166B Polygons](https://codeforces.com/problemset/problem/166/B)
