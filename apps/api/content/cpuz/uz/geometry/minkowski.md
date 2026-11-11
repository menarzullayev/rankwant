# Qavariq ko‘pburchaklarning Minkowski yig‘indisi {#minkowski-sum-of-convex-polygons}

## Ta’rif {#definition}

Tekislikdagi nuqtalarning ikkita $A$ va $B$ to‘plamini ko‘rib chiqaylik. Minkowski yig‘indisi $A + B$ quyidagicha aniqlanadi: $\{a + b| a \in A, b \in B\}$.
Bu yerda $A$ va $B$ to‘plamlar ichki qismlari bilan birga olingan $P$ va $Q$ qavariq ko‘pburchaklardan iborat bo‘lgan holni ko‘rib chiqamiz.
Maqola davomida ko‘pburchaklarni uchlarining tartiblangan ketma-ketligi bilan aynan bir deb qaraymiz, shunda $|P|$ yoki
$P_i$ kabi belgilar ma’noga ega bo‘ladi.
Ma’lum bo‘lishicha, $P$ va $Q$ qavariq ko‘pburchaklarning yig‘indisi ko‘pi bilan $|P| + |Q|$ ta uchga ega qavariq ko‘pburchak bo‘ladi.

## Algoritm {#algorithm}

Bu yerda ko‘pburchaklar siklik tartibda raqamlangan deb hisoblaymiz, ya’ni $P_{|P|} = P_0,\ Q_{|Q|} = Q_0$ va hokazo.

Yig‘indining o‘lchami dastlabki ko‘pburchaklar o‘lchamlariga nisbatan chiziqli bo‘lgani uchun chiziqli vaqtli algoritm topishni maqsad qilishimiz kerak.
Faraz qilaylik, ikkala ko‘pburchak ham soat miliga teskari tartibda berilgan. Qirralarning $\{\overrightarrow{P_iP_{i+1}}\}$
va $\{\overrightarrow{Q_jQ_{j+1}}\}$ ketma-ketliklarini qutbiy burchak bo‘yicha tartiblangan holda ko‘rib chiqamiz. $P + Q$ ning qirralari ketma-ketligini shu
ikki ketma-ketlikni qutbiy burchak tartibini saqlagan holda birlashtirib va ketma-ket kelgan bir xil yo‘nalishli vektorlarni ularning yig‘indisi bilan almashtirib olish mumkin, deb da’vo qilamiz. Bu g‘oyadan to‘g‘ridan-to‘g‘ri foydalanish
chiziqli vaqtli algoritmga olib keladi, biroq $P + Q$ ning uchlarini qirralar ketma-ketligidan tiklash vektorlarni qayta-qayta qo‘shishni talab qiladi,
bu esa haqiqiy sonli koordinatalar bilan ishlaganda keraksiz aniqlik muammolarini keltirib chiqarishi mumkin, shuning uchun bu g‘oyaning biroz
o‘zgartirilgan variantini tasvirlaymiz.

Avval uchlarni shunday qayta tartiblash kerakki, har bir ko‘pburchakning birinchi uchi eng kichik y-koordinataga ega bo‘lsin (bunday uchlar bir nechta bo‘lsa, eng kichik x-koordinatali uchni tanlang). Shundan keyin ikkala ko‘pburchakning tomonlari
qutbiy burchak bo‘yicha tartiblangan bo‘ladi, shuning uchun ularni qo‘lda saralash shart emas.
Endi ikkita ko‘rsatkich yaratamiz: $i$ ($P$ ning uchiga ishora qiladi) va $j$ ($Q$ ning uchiga ishora qiladi), ikkalasi boshida 0 ga teng.
$i < |P|$ yoki $j < |Q|$ bo‘lguncha quyidagi qadamlarni takrorlaymiz.

1. $P_i + Q_j$ ni $P + Q$ ga qo‘shamiz.

2. $\overrightarrow{P_iP_{i + 1}}$ va $\overrightarrow{Q_jQ_{j+1}}$ ning qutbiy burchaklarini solishtiramiz.

3. Burchagi kichikroq bo‘lgan ko‘rsatkichni bittaga oshiramiz (burchaklar teng bo‘lsa, ikkalasini oshiramiz).

## Vizualizatsiya {#visualization}

Quyida nima sodir bo‘layotganini tushunishga yordam beradigan yaxshi vizualizatsiya keltirilgan.

![Visual](/algorithms-media/geometry/minkowski.gif)

## Ikki ko‘pburchak orasidagi masofa {#distance-between-two-polygons}

Minkowski yig‘indisining eng keng tarqalgan qo‘llanishlaridan biri — ikkita qavariq ko‘pburchak orasidagi masofani hisoblash (yoki shunchaki ularning kesishishini tekshirish).
$P$ va $Q$ qavariq ko‘pburchaklar orasidagi masofa $\min\limits_{a \in P, b \in Q} ||a - b||$ sifatida aniqlanadi. Shuni ta’kidlash mumkinki,
masofa har doim ikki uch yoki bir uch va bir qirra orasida erishiladi, shuning uchun masofani $O(|P||Q|)$ vaqtda osongina topish mumkin. Biroq
Minkowski yig‘indisidan mohirlik bilan foydalanib, murakkablikni $O(|P| + |Q|)$ gacha kamaytirish mumkin.

$Q$ ni $(0, 0)$ nuqtaga nisbatan akslantirib, $-Q$ ko‘pburchakni hosil qilsak, masala $P + (-Q)$ dagi nuqta bilan $(0, 0)$ orasidagi eng kichik masofani topishga
keladi. Bu masofani chiziqli vaqtda quyidagi g‘oya yordamida topish mumkin.
Agar $(0, 0)$ ko‘pburchak ichida yoki chegarasida bo‘lsa, masofa $0$ ga teng, aks holda masofa $(0, 0)$ bilan ko‘pburchakning biror uchi yoki qirrasi orasida erishiladi.
Minkowski yig‘indisini
chiziqli vaqtda hisoblash mumkin bo‘lgani uchun ikkita qavariq ko‘pburchak orasidagi masofani topishning chiziqli vaqtli algoritmini olamiz.

## Implementatsiya {#implementation}

Quyida butun koordinatali nuqtalarga ega ko‘pburchaklar uchun Minkowski yig‘indisining implementatsiyasi keltirilgan. E’tibor bering, bu holda barcha hisob-kitoblarni butun sonlarda bajarish mumkin, chunki
qutbiy burchaklarni hisoblab, to‘g‘ridan-to‘g‘ri solishtirish o‘rniga ikki vektor vektor ko‘paytmasining ishorasiga qarash mumkin.

```cpp
struct pt{
    long long x, y;
    pt operator + (const pt & p) const {
        return pt{x + p.x, y + p.y};
    }
    pt operator - (const pt & p) const {
        return pt{x - p.x, y - p.y};
    }
    long long cross(const pt & p) const {
        return x * p.y - y * p.x;
    }
};

void reorder_polygon(vector<pt> & P){
    size_t pos = 0;
    for(size_t i = 1; i < P.size(); i++){
        if(P[i].y < P[pos].y || (P[i].y == P[pos].y && P[i].x < P[pos].x))
            pos = i;
    }
    rotate(P.begin(), P.begin() + pos, P.end());
}

vector<pt> minkowski(vector<pt> P, vector<pt> Q){
    // birinchi uch eng quyi bo‘lishi kerak
    reorder_polygon(P);
    reorder_polygon(Q);
    // siklik indekslashni ta’minlashimiz kerak
    P.push_back(P[0]);
    P.push_back(P[1]);
    Q.push_back(Q[0]);
    Q.push_back(Q[1]);
    // asosiy qism
    vector<pt> result;
    size_t i = 0, j = 0;
    while(i < P.size() - 2 || j < Q.size() - 2){
        result.push_back(P[i] + Q[j]);
        auto cross = (P[i + 1] - P[i]).cross(Q[j + 1] - Q[j]);
        if(cross >= 0 && i < P.size() - 2)
            ++i;
        if(cross <= 0 && j < Q.size() - 2)
            ++j;
    }
    return result;
}

```

## Masalalar {#problems}

* [Codeforces 87E Mogohu-Rea Idol](https://codeforces.com/problemset/problem/87/E)
* [Codeforces 1195F Geometers Anonymous Club](https://codeforces.com/contest/1195/problem/F)
* [TIMUS 1894 Non-Flying Weather](https://acm.timus.ru/problem.aspx?space=1&num=1894)
