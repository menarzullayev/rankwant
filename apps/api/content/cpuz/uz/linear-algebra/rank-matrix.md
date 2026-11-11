# Matritsa rangini topish

**Matritsa rangi** — matritsaning chiziqli mustaqil satrlari (yoki ustunlari) ning eng katta soni. Rang faqat kvadrat matritsalar uchun emas, istalgan matritsa uchun aniqlanadi.

Matritsa rangini yana matritsadagi noldan farqli har qanday minorning eng katta tartibi sifatida ham ta’riflash mumkin.

Matritsa to‘g‘ri to‘rtburchak va $N \times M$ o‘lchamli bo‘lsin.
E’tibor bering: agar matritsa kvadrat bo‘lsa va determinanti noldan farqli bo‘lsa, rang $N$ ($=M$) ga teng; aks holda u kichikroq bo‘ladi. Umuman olganda, matritsa rangi $\min (N, M)$ dan oshmaydi.

## Algoritm

Rangni [Gauss eliminatsiyasi](/algorithms/linear-algebra/linear-system-gauss) yordamida topish mumkin. Biz sistemani yechishda yoki determinantni topishda bajariladigan amallarning o‘zini bajaramiz. Lekin $i$-ustunda hali tanlanmagan satrlar orasida noldan farqli elementi bor satr bo‘lmasa, bu qadamni o‘tkazib yuboramiz.
Aks holda, agar $i$-qadamda $i$-ustunda noldan farqli elementi bor satr topilgan bo‘lsa, bu satrni tanlangan deb belgilaymiz, rangni bittaga oshiramiz (boshida rang $0$ ga teng) va bu satrni qolgan satrlardan ayirishning odatiy amallarini bajaramiz.

## Murakkablik

Bu algoritm $\mathcal{O}(n^3)$ vaqtda ishlaydi.

## Implementatsiya

```cpp
const double EPS = 1E-9;

int compute_rank(vector<vector<double>> A) {
    int n = A.size();
    int m = A[0].size();

    int rank = 0;
    vector<bool> row_selected(n, false);
    for (int i = 0; i < m; ++i) {
        int j;
        for (j = 0; j < n; ++j) {
            if (!row_selected[j] && abs(A[j][i]) > EPS)
                break;
        }

        if (j != n) {
            ++rank;
            row_selected[j] = true;
            for (int p = i + 1; p < m; ++p)
                A[j][p] /= A[j][i];
            for (int k = 0; k < n; ++k) {
                if (k != j && abs(A[k][i]) > EPS) {
                    for (int p = i + 1; p < m; ++p)
                        A[k][p] -= A[j][p] * A[k][i];
                }
            }
        }
    }
    return rank;
}
```

## Masalalar

 * [TIMUS1041 Nikifor](http://acm.timus.ru/problem.aspx?space=1&num=1041)
