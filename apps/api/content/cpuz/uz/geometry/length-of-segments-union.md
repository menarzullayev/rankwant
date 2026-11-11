# Kesmalar birlashmasining uzunligi {#length-of-the-union-of-segments}

To‘g‘ri chiziqda $n$ ta kesma berilgan, ularning har biri $(a_{i1}, a_{i2})$ koordinatalar jufti bilan beriladi. Ularning birlashmasi uzunligini topish kerak.

Quyidagi algoritmni 1977-yilda Klee taklif qilgan. U $O(n\log n)$ vaqtda ishlaydi va asimptotik jihatdan optimal ekani isbotlangan.

## Yechim {#solution}

Barcha kesmalarning uchlarini qiymatlari bo‘yicha saralab, $x$ massivida saqlaymiz. Bundan tashqari, har bir uch kesmaning chap uchi yoki o‘ng uchi ekanini ham eslab qolamiz. Endi massiv bo‘ylab yurib, hozir ochiq turgan kesmalar sonini $c$ hisoblagichda saqlaymiz. Joriy element chap uch bo‘lsa, hisoblagichni oshiramiz, aks holda kamaytiramiz. Javobni hisoblash uchun yangi koordinataga kelganimizda va hozir kamida bitta kesma ochiq bo‘lsa, oxirgi ikki $x$ qiymati orasidagi $x_i - x_{i-1}$ uzunlikni qo‘shamiz.

## Implementatsiya {#implementation}

```cpp
int length_union(const vector<pair<int, int>> &a) {
    int n = a.size();
    vector<pair<int, bool>> x(n*2);
    for (int i = 0; i < n; i++) {
        x[i*2] = {a[i].first, false};
        x[i*2+1] = {a[i].second, true};
    }

    sort(x.begin(), x.end());

    int result = 0;
    int c = 0;
    for (int i = 0; i < n * 2; i++) {
        if (i > 0 && x[i].first > x[i-1].first && c > 0)
            result += x[i].first - x[i-1].first;
        if (x[i].second)
            c--;
        else
            c++;
    }
    return result;
}
```
