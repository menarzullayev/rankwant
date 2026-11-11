# To‘g‘ri chiziqlarning kesishish nuqtasi

Ikkita to‘g‘ri chiziq $a_1 x + b_1 y + c_1 = 0$ va $a_2 x + b_2 y + c_2 = 0$ tenglamalari bilan berilgan.
Chiziqlarning kesishish nuqtasini topish yoki ularning parallel ekanini aniqlash kerak.

## Yechim

Agar ikkita to‘g‘ri chiziq parallel bo‘lmasa, ular kesishadi.
Kesishish nuqtasini topish uchun quyidagi chiziqli tenglamalar sistemasini yechish kerak:

$$\begin{cases} a_1 x + b_1 y + c_1 = 0 \\
a_2 x + b_2 y + c_2 = 0
\end{cases}$$

Kramer qoidasidan foydalanib, sistemaning yechimini, ya’ni chiziqlarning izlanayotgan kesishish nuqtasini darhol yozish mumkin:

$$x = - \frac{\begin{vmatrix}c_1 & b_1 \cr c_2 & b_2\end{vmatrix}}{\begin{vmatrix}a_1 & b_1 \cr a_2 & b_2\end{vmatrix} } = - \frac{c_1 b_2 - c_2 b_1}{a_1 b_2 - a_2 b_1},$$

$$y = - \frac{\begin{vmatrix}a_1 & c_1 \cr a_2 & c_2\end{vmatrix}}{\begin{vmatrix}a_1 & b_1 \cr a_2 & b_2\end{vmatrix}} = - \frac{a_1 c_2 - a_2 c_1}{a_1 b_2 - a_2 b_1}.$$

Agar maxraj $0$ ga teng bo‘lsa, ya’ni

$$\begin{vmatrix}a_1 & b_1 \cr a_2 & b_2\end{vmatrix} = a_1 b_2 - a_2 b_1 = 0 $$

u holda sistema yo yechimga ega emas (chiziqlar parallel va ustma-ust tushmaydi), yo cheksiz ko‘p yechimga ega (chiziqlar ustma-ust tushadi).
Bu ikki holatni farqlash kerak bo‘lsa, $c$ koeffitsiyentlari $a$ va $b$ koeffitsiyentlari bilan bir xil nisbatda proporsional ekanini tekshirish lozim.
Buning uchun quyidagi determinantlarni hisoblash yetarli; ikkalasi ham $0$ ga teng bo‘lsa, chiziqlar ustma-ust tushadi:

$$\begin{vmatrix}a_1 & c_1 \cr a_2 & c_2\end{vmatrix}, \begin{vmatrix}b_1 & c_1 \cr b_2 & c_2\end{vmatrix} $$

Shuni ta’kidlaymizki, kesishish nuqtasini hisoblashning boshqa usuli [Geometriya asoslari](/algorithms/geometry/basic-geometry) maqolasida bayon etilgan.

## Dastur kodi

```cpp
struct pt {
    double x, y;
};

struct line {
    double a, b, c;
};

const double EPS = 1e-9;

double det(double a, double b, double c, double d) {
    return a*d - b*c;
}

bool intersect(line m, line n, pt & res) {
    double zn = det(m.a, m.b, n.a, n.b);
    if (abs(zn) < EPS)
        return false;
    res.x = -det(m.c, m.b, n.c, n.b) / zn;
    res.y = -det(m.a, m.c, n.a, n.c) / zn;
    return true;
}

bool parallel(line m, line n) {
    return abs(det(m.a, m.b, n.a, n.b)) < EPS;
}

bool equivalent(line m, line n) {
    return abs(det(m.a, m.b, n.a, n.b)) < EPS
        && abs(det(m.a, m.c, n.a, n.c)) < EPS
        && abs(det(m.b, m.c, n.b, n.c)) < EPS;
}
```
