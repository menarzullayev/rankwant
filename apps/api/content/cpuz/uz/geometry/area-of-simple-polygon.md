# Sodda ko‘pburchak yuzini $O(N)$ vaqtda topish {#finding-area-of-simple-polygon-in-on}

Sodda ko‘pburchak (ya’ni o‘zini kesmaydigan, qavariq bo‘lishi shart bo‘lmagan ko‘pburchak) berilgan bo‘lsin. Uning uchlari bo‘yicha yuzini hisoblash talab qilinadi.

## 1-usul {#method-1}

Buni barcha qirralar bo‘ylab yurib, har bir qirra va x o‘qi bilan chegaralangan trapesiya yuzlarini qo‘shish orqali oson bajarish mumkin. Ortiqcha yuz kamayishi uchun yuz ishora bilan olinishi kerak. Demak, formula quyidagicha:

$$A = \sum_{(p,q)\in \text{edges}} \frac{(p_x - q_x) \cdot (p_y + q_y)}{2}$$

Kod:

```cpp
double area(const vector<point>& fig) {
    double res = 0;
    for (unsigned i = 0; i < fig.size(); i++) {
        point p = i ? fig[i - 1] : fig.back();
        point q = fig[i];
        res += (p.x - q.x) * (p.y + q.y);
    }
    return fabs(res) / 2;
}
```

## 2-usul {#method-2}

Ixtiyoriy $O$ nuqtani tanlab, barcha qirralar bo‘ylab yuramiz va har bir qirra hamda $O$ nuqta hosil qilgan uchburchakning yo‘nalgan yuzini qo‘shamiz. Bu yerda ham yuz ishorasi tufayli ortiqcha yuz kamayadi.

Bu usul yaxshiroq, chunki uni murakkabroq holatlarga (masalan, ayrim tomonlar to‘g‘ri chiziq o‘rniga yoy bo‘lganda) umumlashtirish mumkin.
