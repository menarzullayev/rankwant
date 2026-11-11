# Determinantni Gauss usuli bilan hisoblash

$N\times N$ o‘lchamli $A$ matritsa berilgan. Uning determinantini hisoblash kerak.

## Algoritm

Yechim [chiziqli tenglamalar sistemasini yechishdagi Gauss usuli](/algorithms/linear-algebra/linear-system-gauss) g‘oyalariga asoslanadi.

Biz chiziqli tenglamalar sistemasini yechishdagi qadamlarning xuddi o‘zini bajaramiz, faqat joriy satrni $a_{ij}$ ga bo‘lishni chiqarib tashlaymiz. Bu amallar matritsa determinantining absolyut qiymatini o‘zgartirmaydi. Ammo matritsaning ikki satri o‘rni almashtirilsa, determinant ishorasi o‘zgarishi mumkin.

Matritsaga Gauss usulini qo‘llagach, diagonal matritsa hosil bo‘ladi, uning determinanti shunchaki diagonaldagi elementlarning ko‘paytmasiga teng. Ishora yuqorida aytilganidek, almashtirilgan satrlar sonidan aniqlanadi (agar son toq bo‘lsa, determinant ishorasini teskarisiga o‘zgartirish kerak). Shunday qilib, Gauss algoritmi yordamida matritsa determinantini $O(N^3)$ murakkablikda hisoblash mumkin.

Shuni ta’kidlash kerakki, agar biror paytda joriy ustunda noldan farqli katak topilmasa, algoritm to‘xtashi va 0 qaytarishi kerak.

## Implementatsiya

```cpp
const double EPS = 1E-9;
int n;
vector<vector<double>> a(n, vector<double>(n));

double det = 1;
for (int i = 0; i < n; ++i) {
    int k = i;
    for (int j = i + 1; j < n; ++j)
        if (abs(a[j][i]) > abs(a[k][i]))
            k = j;

    if (abs(a[k][i]) < EPS) {
        det = 0;
        break;
    }

    swap(a[i], a[k]);
    if (i != k)
        det = -det;

    det *= a[i][i];
    for (int j = i + 1; j < n; ++j)
        a[i][j] /= a[i][i];

    for (int j = 0; j < n; ++j)
        if (j != i && abs(a[j][i]) > EPS)
            for (int k = i + 1; k < n; ++k)
                a[j][k] -= a[i][k] * a[j][i];
}

cout << det;
```

## Mashq masalalari

- [Codeforces 167E — Wizards and Bets](http://codeforces.com/contest/167/problem/E)
