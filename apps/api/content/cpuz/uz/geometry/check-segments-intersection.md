# Ikki kesma kesishishini tekshirish

Sizga $(a, b)$ va $(c, d)$ kesmalar berilgan.
Ularning kesishishini tekshirish kerak.
Albatta, ularning kesishish nuqtasini topib, u bo‘sh emasligini tekshirish mumkin, lekin butun koordinatali kesmalar uchun buni butun sonlarda bajarib bo‘lmaydi.
Bu yerda tasvirlangan yondashuv butun sonlarda ishlay oladi.

## Algoritm

Avvalo, kesmalar bitta to‘g‘ri chiziqning qismlari bo‘lgan holni ko‘rib chiqamiz.
Bu holda ularning $Ox$ va $Oy$ o‘qlaridagi proyeksiyalari kesishishini tekshirish yetarli.
Boshqa holda $a$ va $b$ nuqtalar $(c, d)$ to‘g‘ri chiziqning bir tomonida yotmasligi, $c$ va $d$ nuqtalar esa $(a, b)$ to‘g‘ri chiziqning bir tomonida yotmasligi kerak.
Buni bir necha vektor ko‘paytma yordamida tekshirish mumkin.

## Implementatsiya

Berilgan algoritm butun koordinatali nuqtalar uchun amalga oshirilgan. Albatta, uni `double` bilan ishlaydigan qilib osongina o‘zgartirish mumkin.

```cpp
struct pt {
    long long x, y;
    pt() {}
    pt(long long _x, long long _y) : x(_x), y(_y) {}
    pt operator-(const pt& p) const { return pt(x - p.x, y - p.y); }
    long long cross(const pt& p) const { return x * p.y - y * p.x; }
    long long cross(const pt& a, const pt& b) const { return (a - *this).cross(b - *this); }
};

int sgn(const long long& x) { return x >= 0 ? x ? 1 : 0 : -1; }

bool inter1(long long a, long long b, long long c, long long d) {
    if (a > b)
        swap(a, b);
    if (c > d)
        swap(c, d);
    return max(a, c) <= min(b, d);
}

bool check_inter(const pt& a, const pt& b, const pt& c, const pt& d) {
    if (c.cross(a, d) == 0 && c.cross(b, d) == 0)
        return inter1(a.x, b.x, c.x, d.x) && inter1(a.y, b.y, c.y, d.y);
    return sgn(a.cross(b, c)) != sgn(a.cross(b, d)) &&
           sgn(c.cross(d, a)) != sgn(c.cross(d, b));
}
```

## Amaliy masalalar

* [CSES - Line Segment Intersection](https://cses.fi/problemset/task/2190)
