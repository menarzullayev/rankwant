# Ikki kesma kesishmasini topish

Sizga ikkita AB va CD kesma berilgan, ular uchlari juftlari bilan ifodalangan. Agar kesmaning uchlari bir xil bo‘lsa, u bitta nuqtadan iborat bo‘lishi mumkin.
Bu kesmalarning kesishmasini topish kerak. Kesishma bo‘sh (kesmalar kesishmasa), bitta nuqta yoki kesma (berilgan kesmalar ustma-ust tushsa) bo‘lishi mumkin.

## Yechim

Kesmalarning kesishish nuqtasini [to‘g‘ri chiziqlar kesishmasini](/algorithms/geometry/lines-intersection) topishdagi kabi topish mumkin:
kesmalarning uchlaridan to‘g‘ri chiziq tenglamalarini tiklaymiz va ularning parallel yoki parallel emasligini tekshiramiz.

Agar to‘g‘ri chiziqlar parallel bo‘lmasa, ularning kesishish nuqtasini topib, u ikkala kesmaga ham tegishli ekanini tekshirish kerak
(buning uchun kesishish nuqtasi har bir kesmaning X va Y o‘qlaridagi proyeksiyasiga tegishli ekanini tekshirish yetarli).
Bu holatda javob yo “kesishma yo‘q” bo‘ladi, yo to‘g‘ri chiziqlar kesishishining yagona nuqtasi bo‘ladi.

Parallel to‘g‘ri chiziqlar holati biroz murakkabroq (bir yoki bir nechta kesma bitta nuqta bo‘lgan holat ham shu yerga kiradi).
Bu holda ikkala kesma ham bitta to‘g‘ri chiziqqa tegishli ekanini tekshirish kerak.
Agar tegishli bo‘lmasa, javob “kesishma yo‘q”.
Agar tegishli bo‘lsa, javob bitta to‘g‘ri chiziqda yotgan kesmalarning kesishmasi bo‘ladi. Uni olish uchun
ikkala kesmaning uchlarini ma’lum bir koordinata o‘sish tartibida saralab, chap uchlarning eng o‘ngdagisini va o‘ng uchlarning eng chapdagisini olamiz.

Agar ikkala kesma ham bitta nuqta bo‘lsa, bu nuqtalar bir xil bo‘lishi shart va bu tekshiruvni alohida bajarish mantiqiy.

Algoritm boshida chegaraviy to‘g‘ri to‘rtburchak (bounding box) tekshiruvini qo‘shamiz: u kesmalar bitta to‘g‘ri chiziqda yotgan holat uchun zarur,
va (yengil tekshiruv bo‘lgani uchun) algoritmga tasodifiy testlarda o‘rtacha tezroq ishlash imkonini beradi.

## Implementatsiya

Quyida to‘g‘ri chiziqlar va kesmalarni qayta ishlashning barcha yordamchi funksiyalarini o‘z ichiga olgan implementatsiya keltirilgan.

Asosiy `intersect` funksiyasi kesmalarning kesishmasi bo‘sh bo‘lmasa true qaytaradi
va kesishma kesmasining uchlarini `left` va `right` argumentlariga yozadi.
Agar javob bitta nuqta bo‘lsa, `left` va `right` ga yozilgan qiymatlar bir xil bo‘ladi.

```cpp
const double EPS = 1E-9;

struct pt {
    double x, y;

    bool operator<(const pt& p) const
    {
        return x < p.x - EPS || (abs(x - p.x) < EPS && y < p.y - EPS);
    }
};

struct line {
    double a, b, c;

    line() {}
    line(pt p, pt q)
    {
        a = p.y - q.y;
        b = q.x - p.x;
        c = -a * p.x - b * p.y;
        norm();
    }

    void norm()
    {
        double z = sqrt(a * a + b * b);
        if (abs(z) > EPS)
            a /= z, b /= z, c /= z;
    }

    double dist(pt p) const { return a * p.x + b * p.y + c; }
};

double det(double a, double b, double c, double d)
{
    return a * d - b * c;
}

inline bool betw(double l, double r, double x)
{
    return min(l, r) <= x + EPS && x <= max(l, r) + EPS;
}

inline bool intersect_1d(double a, double b, double c, double d)
{
    if (a > b)
        swap(a, b);
    if (c > d)
        swap(c, d);
    return max(a, c) <= min(b, d) + EPS;
}

bool intersect(pt a, pt b, pt c, pt d, pt& left, pt& right)
{
    if (!intersect_1d(a.x, b.x, c.x, d.x) || !intersect_1d(a.y, b.y, c.y, d.y))
        return false;
    line m(a, b);
    line n(c, d);
    double zn = det(m.a, m.b, n.a, n.b);
    if (abs(zn) < EPS) {
        if (abs(m.dist(c)) > EPS || abs(n.dist(a)) > EPS)
            return false;
        if (b < a)
            swap(a, b);
        if (d < c)
            swap(c, d);
        left = max(a, c);
        right = min(b, d);
        return true;
    } else {
        left.x = right.x = -det(m.c, m.b, n.c, n.b) / zn;
        left.y = right.y = -det(m.a, m.c, n.a, n.c) / zn;
        return betw(a.x, b.x, left.x) && betw(a.y, b.y, left.y) &&
               betw(c.x, d.x, left.x) && betw(c.y, d.y, left.y);
    }
}
```
