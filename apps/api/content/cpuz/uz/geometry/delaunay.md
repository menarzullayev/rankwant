# Delaunay triangulyatsiyasi va Voronoi diagrammasi {#delaunay-triangulation-and-voronoi-diagram}

Tekislikda $\{p_i\}$ nuqtalar to‘plami berilgan bo‘lsin.
$\{p_i\}$ ning **Voronoi diagrammasi** $V(\{p_i\})$ — tekislikning $n$ ta $V_i$ sohaga bo‘linishi, bunda $V_i = \{p\in\mathbb{R}^2;\ \rho(p, p_i) = \min\ \rho(p, p_k)\}$.
Voronoi diagrammasining kataklari ko‘pburchaklardir (cheksiz bo‘lishi ham mumkin).
$\{p_i\}$ ning **Delaunay triangulyatsiyasi** $D(\{p_i\})$ — shunday triangulyatsiyaki, unda har bir $p_i$ nuqta har bir $T \in D(\{p_i\})$ uchburchakning tashqi chizilgan aylanasidan tashqarida yoki uning chegarasida yotadi.

Voronoi diagrammasi bog‘lanmagan va Delaunay triangulyatsiyasi mavjud bo‘lmaydigan yoqimsiz degenerativ holat bor. Bu barcha nuqtalar kollinear bo‘lgan holatdir.

## Xossalar {#properties}

Delaunay triangulyatsiyasi barcha mumkin bo‘lgan triangulyatsiyalar orasida eng kichik burchakni maksimal qiladi.

Nuqtalar to‘plamining minimal Evklid ostov daraxti uning Delaunay triangulyatsiyasi qirralarining qism to‘plamidir.

## Duallik {#duality}

Faraz qilaylik, $\{p_i\}$ kollinear emas va $\{p_i\}$ orasida hech qaysi to‘rtta nuqta bitta aylanada yotmaydi. U holda $V(\{p_i\})$ va $D(\{p_i\})$ dualdir, ya’ni ulardan birini topsak, ikkinchisini $O(n)$ da topish mumkin. Agar bunday bo‘lmasa-chi? Kollinear holatni oson qayta ishlash mumkin. Aks holda $V$ va $D'$ dualdir, bunda $D'$ — $D$ dan shunday qirralarni olib tashlash orqali hosil qilinadi, bu qirraning ikkala tomonidagi ikkita uchburchak bitta tashqi chizilgan aylanaga ega.

## Delaunay va Voronoi diagrammalarini qurish {#building-delaunay-and-voronoi}

Duallik tufayli $V$ va $D$ dan faqat bittasini hisoblaydigan tez algoritm yetarli. Biz $D(\{p_i\})$ ni $O(n\log n)$ da qurishni tavsiflaymiz. Triangulyatsiya Guibas va Stolfi tomonidan taklif qilingan divide-and-conquer (bo‘lib yechish) algoritmi yordamida quriladi.

## Quad-edge ma’lumotlar tuzilmasi {#quad-edge-data-structure}

Algoritm davomida $D$ quad-edge ma’lumotlar tuzilmasida saqlanadi. Bu tuzilma rasmda tasvirlangan:

  ![Quad-Edge](/algorithms-media/geometry/quad-edge.png)

Algoritmda qirralar ustida quyidagi funksiyalardan foydalanamiz:

  1. `make_edge(a, b)`
    Bu funksiya `a` nuqtadan `b` nuqtaga izolyatsiyalangan qirrani, uning teskari qirrasini va ikkala dual qirrani birga yaratadi.
  2. `splice(a, b)`
    Bu algoritmning asosiy funksiyasi. U `a->Onext` bilan `b->Onext` ni hamda `a->Onext->Rot->Onext` bilan `b->Onext->Rot->Onext` ni almashtiradi.
  3. `delete_edge(e)`
    Bu funksiya `e` ni triangulyatsiyadan o‘chiradi. `e` ni o‘chirish uchun `splice(e, e->Oprev)` va `splice(e->Rev, e->Rev->Oprev)` ni chaqirish kifoya.
  4. `connect(a, b)`
    Bu funksiya `a->Dest` dan `b->Org` ga shunday yangi `e` qirrani yaratadiki, `a`, `b`, `e` ning hammasi bir xil chap yuzga ega bo‘ladi. Buning uchun `e = make_edge(a->Dest, b->Org)`, `splice(e, a->Lnext)` va `splice(e->Rev, b)` ni chaqiramiz.

## Algoritm {#algorithm}

Algoritm triangulyatsiyani hisoblaydi va ikkita quad-edge qaytaradi: eng chap uchdan chiqadigan, soat miliga teskari yo‘nalishdagi qavariq qobiq qirrasi va eng o‘ng uchdan chiqadigan, soat mili yo‘nalishidagi qavariq qobiq qirrasi.

Barcha nuqtalarni x bo‘yicha, $x_1 = x_2$ bo‘lsa y bo‘yicha saralaymiz. Masalani biror $(l, r)$ kesma uchun yechamiz (boshida $(l, r) = (0, n - 1)$). Agar $r - l + 1 = 2$ bo‘lsa, $(p[l], p[r])$ qirrani qo‘shamiz va qaytamiz. Agar $r - l + 1 = 3$ bo‘lsa, avval $(p[l], p[l + 1])$ va $(p[l + 1], p[r])$ qirralarni qo‘shamiz. Ularni `splice(a->Rev, b)` yordamida ham bog‘lashimiz kerak. Endi uchburchakni yopishimiz kerak. Keyingi harakatimiz $p[l], p[l + 1], p[r]$ ning orientatsiyasiga bog‘liq. Agar ular kollinear bo‘lsa, uchburchak hosil qila olmaymiz, shuning uchun shunchaki `(a, b->Rev)` ni qaytaramiz. Aks holda `connect(b, a)` ni chaqirib, yangi `c` qirrani yaratamiz. Agar nuqtalar soat miliga teskari yo‘nalishda joylashgan bo‘lsa, `(a, b->Rev)` ni qaytaramiz. Aks holda `(c->Rev, c)` ni qaytaramiz.

Endi $r - l + 1 \ge 4$ bo‘lsin. Avval $L = (l, \frac{l + r}{2})$ va $R = (\frac{l + r}{2} + 1, r)$ ni rekursiv yechamiz. Endi bu triangulyatsiyalarni bitta triangulyatsiyaga birlashtirishimiz kerak. E’tibor bering, nuqtalarimiz saralangan, shuning uchun birlashtirish paytida L dan R ga qirralar (ular _ko‘ndalang_ qirralar deyiladi) qo‘shamiz va L dan L ga hamda R dan R ga ba’zi qirralarni olib tashlaymiz.
Ko‘ndalang qirralar qanday tuzilishga ega? Bu qirralarning barchasi y o‘qiga parallel va bo‘linish x qiymatida o‘tkazilgan chiziqni kesib o‘tishi kerak. Bu ko‘ndalang qirralarning chiziqli tartibini aniqlaydi, shuning uchun ketma-ket ko‘ndalang qirralar, eng pastki ko‘ndalang qirra va hokazo haqida gapirish mumkin. Algoritm ko‘ndalang qirralarni o‘sish tartibida qo‘shadi. E’tibor bering, ikkita qo‘shni ko‘ndalang qirra umumiy uchga ega bo‘ladi, ular aniqlaydigan uchburchakning uchinchi tomoni esa L dan L ga yoki R dan R ga boradi. Joriy ko‘ndalang qirrani `base` deb ataymiz. `base` ning keyingisi `base` ning chap uchidan o‘ng uchining R dagi qo‘shnilaridan biriga yoki aksincha boradi.
`base` va oldingi ko‘ndalang qirraning tashqi chizilgan aylanasini ko‘rib chiqaylik.
Faraz qilaylik, bu aylana `base` ni vatar qilib, lekin Oy yo‘nalishida yuqoriroq joylashgan boshqa aylanalarga aylantiriladi.
Bizning aylana bir muddat yuqoriga ko‘tariladi, lekin `base` L va R ning yuqori urinmasi bo‘lmasa, biz L yoki R ga tegishli nuqtaga duch kelamiz va u tashqi aylanasida hech qanday nuqta bo‘lmagan yangi uchburchakni hosil qiladi.
Bu uchburchakning yangi L-R qirrasi keyingi qo‘shiladigan ko‘ndalang qirra bo‘ladi.
Buni samarali bajarish uchun ikkita `lcand` va `rcand` qirrani hisoblaymiz: `lcand` bu jarayonda birinchi uchragan L nuqtaga, `rcand` esa birinchi uchragan R nuqtaga ishora qiladi.
So‘ng avval uchraydiganini tanlaymiz. Boshida `base` L va R ning pastki urinmasiga ishora qiladi.

## Implementatsiya {#implementation}

E’tibor bering, `in_circle` funksiyasining implementatsiyasi GCC ga xosdir.

```cpp
typedef long long ll;

bool ge(const ll& a, const ll& b) { return a >= b; }
bool le(const ll& a, const ll& b) { return a <= b; }
bool eq(const ll& a, const ll& b) { return a == b; }
bool gt(const ll& a, const ll& b) { return a > b; }
bool lt(const ll& a, const ll& b) { return a < b; }
int sgn(const ll& a) { return a >= 0 ? a ? 1 : 0 : -1; }

struct pt {
    ll x, y;
    pt() { }
    pt(ll _x, ll _y) : x(_x), y(_y) { }
    pt operator-(const pt& p) const {
        return pt(x - p.x, y - p.y);
    }
    ll cross(const pt& p) const {
        return x * p.y - y * p.x;
    }
    ll cross(const pt& a, const pt& b) const {
        return (a - *this).cross(b - *this);
    }
    ll dot(const pt& p) const {
        return x * p.x + y * p.y;
    }
    ll dot(const pt& a, const pt& b) const {
        return (a - *this).dot(b - *this);
    }
    ll sqrLength() const {
        return this->dot(*this);
    }
    bool operator==(const pt& p) const {
        return eq(x, p.x) && eq(y, p.y);
    }
};

const pt inf_pt = pt(1e18, 1e18);

struct QuadEdge {
    pt origin;
    QuadEdge* rot = nullptr;
    QuadEdge* onext = nullptr;
    bool used = false;
    QuadEdge* rev() const {
        return rot->rot;
    }
    QuadEdge* lnext() const {
        return rot->rev()->onext->rot;
    }
    QuadEdge* oprev() const {
        return rot->onext->rot;
    }
    pt dest() const {
        return rev()->origin;
    }
};

QuadEdge* make_edge(pt from, pt to) {
    QuadEdge* e1 = new QuadEdge;
    QuadEdge* e2 = new QuadEdge;
    QuadEdge* e3 = new QuadEdge;
    QuadEdge* e4 = new QuadEdge;
    e1->origin = from;
    e2->origin = to;
    e3->origin = e4->origin = inf_pt;
    e1->rot = e3;
    e2->rot = e4;
    e3->rot = e2;
    e4->rot = e1;
    e1->onext = e1;
    e2->onext = e2;
    e3->onext = e4;
    e4->onext = e3;
    return e1;
}

void splice(QuadEdge* a, QuadEdge* b) {
    swap(a->onext->rot->onext, b->onext->rot->onext);
    swap(a->onext, b->onext);
}

void delete_edge(QuadEdge* e) {
    splice(e, e->oprev());
    splice(e->rev(), e->rev()->oprev());
    delete e->rev()->rot;
    delete e->rev();
    delete e->rot;
    delete e;
}

QuadEdge* connect(QuadEdge* a, QuadEdge* b) {
    QuadEdge* e = make_edge(a->dest(), b->origin);
    splice(e, a->lnext());
    splice(e->rev(), b);
    return e;
}

bool left_of(pt p, QuadEdge* e) {
    return gt(p.cross(e->origin, e->dest()), 0);
}

bool right_of(pt p, QuadEdge* e) {
    return lt(p.cross(e->origin, e->dest()), 0);
}

template <class T>
T det3(T a1, T a2, T a3, T b1, T b2, T b3, T c1, T c2, T c3) {
    return a1 * (b2 * c3 - c2 * b3) - a2 * (b1 * c3 - c1 * b3) +
           a3 * (b1 * c2 - c1 * b2);
}

bool in_circle(pt a, pt b, pt c, pt d) {
// If there is __int128, calculate directly.
// Otherwise, calculate angles.
#if defined(__LP64__) || defined(_WIN64)
    __int128 det = -det3<__int128>(b.x, b.y, b.sqrLength(), c.x, c.y,
                                   c.sqrLength(), d.x, d.y, d.sqrLength());
    det += det3<__int128>(a.x, a.y, a.sqrLength(), c.x, c.y, c.sqrLength(), d.x,
                          d.y, d.sqrLength());
    det -= det3<__int128>(a.x, a.y, a.sqrLength(), b.x, b.y, b.sqrLength(), d.x,
                          d.y, d.sqrLength());
    det += det3<__int128>(a.x, a.y, a.sqrLength(), b.x, b.y, b.sqrLength(), c.x,
                          c.y, c.sqrLength());
    return det > 0;
#else
    auto ang = [](pt l, pt mid, pt r) {
        ll x = mid.dot(l, r);
        ll y = mid.cross(l, r);
        long double res = atan2((long double)x, (long double)y);
        return res;
    };
    long double kek = ang(a, b, c) + ang(c, d, a) - ang(b, c, d) - ang(d, a, b);
    if (kek > 1e-8)
        return true;
    else
        return false;
#endif
}

pair<QuadEdge*, QuadEdge*> build_tr(int l, int r, vector<pt>& p) {
    if (r - l + 1 == 2) {
        QuadEdge* res = make_edge(p[l], p[r]);
        return make_pair(res, res->rev());
    }
    if (r - l + 1 == 3) {
        QuadEdge *a = make_edge(p[l], p[l + 1]), *b = make_edge(p[l + 1], p[r]);
        splice(a->rev(), b);
        int sg = sgn(p[l].cross(p[l + 1], p[r]));
        if (sg == 0)
            return make_pair(a, b->rev());
        QuadEdge* c = connect(b, a);
        if (sg == 1)
            return make_pair(a, b->rev());
        else
            return make_pair(c->rev(), c);
    }
    int mid = (l + r) / 2;
    QuadEdge *ldo, *ldi, *rdo, *rdi;
    tie(ldo, ldi) = build_tr(l, mid, p);
    tie(rdi, rdo) = build_tr(mid + 1, r, p);
    while (true) {
        if (left_of(rdi->origin, ldi)) {
            ldi = ldi->lnext();
            continue;
        }
        if (right_of(ldi->origin, rdi)) {
            rdi = rdi->rev()->onext;
            continue;
        }
        break;
    }
    QuadEdge* basel = connect(rdi->rev(), ldi);
    auto valid = [&basel](QuadEdge* e) { return right_of(e->dest(), basel); };
    if (ldi->origin == ldo->origin)
        ldo = basel->rev();
    if (rdi->origin == rdo->origin)
        rdo = basel;
    while (true) {
        QuadEdge* lcand = basel->rev()->onext;
        if (valid(lcand)) {
            while (in_circle(basel->dest(), basel->origin, lcand->dest(),
                             lcand->onext->dest())) {
                QuadEdge* t = lcand->onext;
                delete_edge(lcand);
                lcand = t;
            }
        }
        QuadEdge* rcand = basel->oprev();
        if (valid(rcand)) {
            while (in_circle(basel->dest(), basel->origin, rcand->dest(),
                             rcand->oprev()->dest())) {
                QuadEdge* t = rcand->oprev();
                delete_edge(rcand);
                rcand = t;
            }
        }
        if (!valid(lcand) && !valid(rcand))
            break;
        if (!valid(lcand) ||
            (valid(rcand) && in_circle(lcand->dest(), lcand->origin,
                                       rcand->origin, rcand->dest())))
            basel = connect(rcand, basel->rev());
        else
            basel = connect(basel->rev(), lcand->rev());
    }
    return make_pair(ldo, rdo);
}

vector<tuple<pt, pt, pt>> delaunay(vector<pt> p) {
    sort(p.begin(), p.end(), [](const pt& a, const pt& b) {
        return lt(a.x, b.x) || (eq(a.x, b.x) && lt(a.y, b.y));
    });
    auto res = build_tr(0, (int)p.size() - 1, p);
    QuadEdge* e = res.first;
    vector<QuadEdge*> edges = {e};
    while (lt(e->onext->dest().cross(e->dest(), e->origin), 0))
        e = e->onext;
    auto add = [&p, &e, &edges]() {
        QuadEdge* curr = e;
        do {
            curr->used = true;
            p.push_back(curr->origin);
            edges.push_back(curr->rev());
            curr = curr->lnext();
        } while (curr != e);
    };
    add();
    p.clear();
    int kek = 0;
    while (kek < (int)edges.size()) {
        if (!(e = edges[kek++])->used)
            add();
    }
    vector<tuple<pt, pt, pt>> ans;
    for (int i = 0; i < (int)p.size(); i += 3) {
        ans.push_back(make_tuple(p[i], p[i + 1], p[i + 2]));
    }
    return ans;
}
```

## Masalalar {#problems}
 * [TIMUS 1504 Good Manners](http://acm.timus.ru/problem.aspx?space=1&num=1504)
 * [TIMUS 1520 Empire Strikes Back](http://acm.timus.ru/problem.aspx?space=1&num=1520)
 * [SGU 383 Caravans](https://codeforces.com/problemsets/acmsguru/problem/99999/383)
