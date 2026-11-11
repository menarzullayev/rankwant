# Manhattan masofasi {#manhattan-distance}

## Ta’rif {#definition}

Tekislikdagi $p$ va $q$ nuqtalar uchun ular orasidagi masofani $x$ va $y$ koordinatalari ayirmalari modullarining yig‘indisi sifatida aniqlash mumkin:

$$d(p,q) = |x_p - x_q| + |y_p - y_q|$$

Shunday aniqlangan masofa [Manhattan (taksikab) geometriyasi](https://en.wikipedia.org/wiki/Taxicab_geometry) deb ataladigan modelga mos keladi. Unda nuqtalar Manhattan kabi yaxshi rejalashtirilgan shahardagi chorrahalar sifatida qaraladi va faqat ko‘chalar bo‘ylab — gorizontal yoki vertikal — yurish mumkin, quyidagi rasmda ko‘rsatilgandek:

  ![Manhattan masofasi](https://upload.wikimedia.org/wikipedia/commons/0/08/Manhattan_distance.svg)

Bu rasmda bir qora nuqtadan ikkinchisiga boradigan eng qisqa yo‘llardan ba’zilari ko‘rsatilgan; ularning barchasining uzunligi $12$ ga teng.

Bu masofa bilan bog‘liq bir nechta qiziqarli usul va algoritmlar bor, ulardan ayrimlarini shu yerda ko‘rsatamiz.

## Manhattan masofasida eng uzoq nuqtalar jufti {#farthest-pair-of-points-in-manhattan-distance}

$n$ ta $P$ nuqta berilgan. Bir-biridan eng uzoq bo‘lgan $p,q$ nuqtalar juftini, ya’ni $|x_p - x_q| + |y_p - y_q|$ ni maksimal qiladigan juftni topmoqchimiz.

Avval bir o‘lchamli holatni, ya’ni $y=0$ ni ko‘raylik. Asosiy kuzatuv shuki, $|x_p - x_q|$ qiymati $x_p - x_q$ ga teng yoki $-x_p + x_q$ ga tengligini to‘liq ko‘rib chiqish (bruteforce) mumkin: modul ishorasini “adashtirsak”, faqat kichikroq qiymat olamiz va u javobga ta’sir qila olmaydi. Aniqroq aytganda:

$$|x_p - x_q| = \max(x_p - x_q, -x_p + x_q)$$

Shunday qilib, masalan, $x_p$ musbat ishorali bo‘ladigan $p$ ni tanlashga urinib ko‘rish mumkin, u holda $q$ manfiy ishorali bo‘lishi kerak. Bu yo‘l bilan quyidagini topamiz:

$$\max\limits_{p, q \in P}(x_p + (-x_q)) = \max\limits_{p \in P}(x_p) + \max\limits_{q \in P}( - x_q ).$$

E’tibor bering, bu g‘oyani 2 (yoki undan ko‘p!) o‘lchamga ham kengaytirish mumkin. $d$ o‘lchamda ishoralarning $2^d$ ta mumkin bo‘lgan qiymatini to‘liq ko‘rib chiqish kerak. Masalan, $2$ o‘lchamda $p$ ning ikkala ishorasi musbat bo‘lsin deb olsak, quyidagini topamiz:

$$\max\limits_{p, q \in P} [(x_p + (-x_q)) + (y_p + (-y_q))] = \max\limits_{p \in P}(x_p + y_p) + \max\limits_{q \in P}(-x_q - y_q).$$

$p$ va $q$ ni bir-biridan mustaqil qilganimiz uchun ifodani maksimal qiladigan $p$ va $q$ ni topish endi oson.

Quyidagi kod buni $d$ o‘lchamga umumlashtiradi va $O(n \cdot 2^d \cdot d)$ vaqtda ishlaydi.

```cpp
long long ans = 0;
for (int msk = 0; msk < (1 << d); msk++) {
    long long mx = LLONG_MIN, mn = LLONG_MAX;
    for (int i = 0; i < n; i++) {
        long long cur = 0;
        for (int j = 0; j < d; j++) {
            if (msk & (1 << j)) cur += p[i][j];
            else cur -= p[i][j];
        }
        mx = max(mx, cur);
        mn = min(mn, cur);
    }
    ans = max(ans, mx - mn);
}
```

## Nuqtalarni burish va Chebyshev masofasi {#rotating-the-points-and-chebyshev-distance}

Barcha $m, n \in \mathbb{R}$ uchun quyidagi tenglik yaxshi ma’lum:

$$|m| + |n| = \text{max}(|m + n|, |m - n|).$$

Buni isbotlash uchun $m$ va $n$ ning ishoralarini tahlil qilish kifoya. Bu mashq sifatida qoldiriladi.

Bu tenglikni Manhattan masofasi formulasiga qo‘llab, quyidagini olamiz:

$$d((x_1, y_1), (x_2, y_2)) = |x_1 - x_2| + |y_1 - y_2| = \text{max}(|(x_1 + y_1) - (x_2 + y_2)|, |(y_1 - x_1) - (y_2 - x_2)|).$$

Oldingi tenglikdagi oxirgi ifoda $(x_1 + y_1, y_1 - x_1)$ va $(x_2 + y_2, y_2 - x_2)$ nuqtalarning [Chebyshev masofasi](https://en.wikipedia.org/wiki/Chebyshev_distance)dir. Bu degani,

$$\alpha : (x, y) \to (x + y, y - x)$$

almashtirishni qo‘llaganimizdan keyin $p$ va $q$ nuqtalar orasidagi Manhattan masofasi $\alpha(p)$ va $\alpha(q)$ orasidagi Chebyshev masofasiga aylanadi.

Shuningdek, $\alpha$ markazi $(0, 0)$ bo‘lgan, soat mili yo‘nalishida $45^{\circ}$ ga burish burchagi va $\sqrt{2}$ marta kattalashtirish koeffitsiyentiga ega [spiral o‘xshashlik](https://en.wikipedia.org/wiki/Spiral_similarity) (tekislikni burib, so‘ng biror $O$ markazga nisbatan kattalashtirish) ekanini payqash mumkin.

Almashtirishni tasavvur qilishga yordam beradigan rasm:

  ![Chebyshev almashtirishi](/algorithms-media/geometry/chebyshev-transformation.png)

## Manhattan minimal ostov daraxti {#manhattan-minimum-spanning-tree}

Manhattan MST masalasi quyidagicha: tekislikda bir nechta nuqta berilgan, barcha nuqtalarni bog‘laydigan va og‘irliklarining umumiy yig‘indisi minimal bo‘lgan qirralarni topish kerak. Ikki nuqtani bog‘lovchi qirraning og‘irligi ularning Manhattan masofasiga teng. Soddalik uchun barcha nuqtalar turli joylarda joylashgan deb faraz qilamiz.
Bu yerda MST ni $O(n \log{n})$ da topish usulini ko‘rsatamiz: har bir nuqta uchun uning har bir oktantdagi eng yaqin qo‘shnisi topiladi (oktantlar quyidagi rasmda ko‘rsatilgan). Bu bizga $O(n)$ ta nomzod qirra beradi va quyida ko‘rsatamizki, ular MST ni o‘z ichiga olishi kafolatlanadi. Yakuniy qadam — biror standart MST algoritmini, masalan, [kesishmaydigan to‘plamlar birlashmasidan foydalanuvchi Kruskal algoritmini](https://cp-algorithms.com/graph/mst_kruskal_with_dsu.html) qo‘llash.

  ![8 ta oktant rasmi](/algorithms-media/geometry/manhattan-mst-octants.png)
  *S nuqtaga nisbatan 8 ta oktant*

Bu yerda ko‘rsatilgan algoritm birinchi marta [H. Zhou, N. Shenoy va W. Nichollos (2002)](https://ieeexplore.ieee.org/document/913303) maqolasida taqdim etilgan. Yana [J. Stolfi](https://www.academia.edu/15667173/On_computing_all_north_east_nearest_neighbors_in_the_L1_metric) tomonidan “bo‘lib tashla va hukmronlik qil” (divide and conquer) yondashuvidan foydalanadigan boshqa ma’lum algoritm ham bor; u ham juda qiziqarli bo‘lib, har bir oktantdagi eng yaqin qo‘shnini topish usulidagina farq qiladi. Ikkalasining murakkabligi bir xil, lekin bu yerda keltirilgani implementatsiya qilish uchun osonroq va doimiy ko‘paytuvchisi kichikroq.

Avval nima uchun har bir oktantdagi faqat eng yaqin qo‘shnini ko‘rib chiqish yetarli ekanini tushunib olaylik. G‘oya shuki, $s$ nuqta va bir oktantdagi har qanday ikkita boshqa $p$ va $q$ nuqta uchun $d(p, q) < \max(d(s, p), d(s, q))$ ekanini ko‘rsatamiz. Bu muhim, chunki agar $s$ nuqta $p$ va $q$ ning ikkalasiga ham ulangan MST mavjud bo‘lsa, bu qirralardan birini o‘chirib, $(p,q)$ qirrani qo‘shish mumkin va bu umumiy narxni kamaytiradi. Buni isbotlash uchun umumiylikni yo‘qotmasdan $p$ va $q$ nuqtalar $R_1$ oktantda deb faraz qilamiz; u quyidagicha aniqlanadi: $x_s \leq x$ va $x_s - y_s > x -  y$, so‘ng holatlarni alohida ko‘rib chiqamiz. Quyidagi rasm bunday bo‘lishining sababi haqida tasavvur beradi.

  ![yagona eng yaqin qo‘shni](/algorithms-media/geometry/manhattan-mst-uniqueness.png)
  *Sezgi bo‘yicha, oktant chegaralanganligi sababli $p$ va $q$ nuqtalarning ikkalasi ham $s$ ga bir-biriga qaraganda yaqinroq bo‘lishi mumkin emas*

Demak, asosiy savol — $n$ ta nuqtaning har biri uchun har bir oktantdagi eng yaqin qo‘shnini qanday topish.

## Har bir oktantdagi eng yaqin qo‘shni $O(n \log n)$ da {#nearest-neighbor-in-each-octant-in-on-log-n}

Soddalik uchun shimol-shimoli-sharqiy oktantga ($R_1$, yuqoridagi rasmga qarang) e’tibor qaratamiz. Boshqa barcha yo‘nalishlar kirish nuqtalarini burib, xuddi shu algoritm bilan topiladi.

Biz supuruvchi chiziq (sweep-line) yondashuvidan foydalanamiz. Nuqtalarni janubi-g‘arbdan shimoli-sharqqa qarab, ya’ni $x + y$ ning kamaymaydigan tartibida ko‘rib chiqamiz. Shuningdek, hali eng yaqin qo‘shnisi topilmagan nuqtalar to‘plamini saqlaymiz va uni “faol to‘plam” deb ataymiz. Algoritmni tasavvur qilishga yordam berish uchun quyidagi rasmlarni qo‘shdik.

  ![manhattan-mst-sweep](/algorithms-media/geometry/manhattan-mst-sweep-line-1.png)
  *Strelkali qora chiziq — supuruvchi chiziq yo‘nalishi. Bu chiziqdan pastdagi barcha nuqtalar faol to‘plamda, yuqoridagilari esa hali ishlov berilmagan. Yashil rangda ishlov berilayotgan nuqtaning oktantidagi nuqtalar ko‘rsatilgan. Qizil rangda qidirilayotgan oktantda bo‘lmagan nuqtalar.*

  ![manhattan-mst-sweep](/algorithms-media/geometry/manhattan-mst-sweep-line-2.png)
  *Bu rasmda $p$ nuqtaga ishlov berilgandan keyingi faol to‘plam ko‘rsatilgan. E’tibor bering, oldingi rasmdagi $2$ ta yashil nuqta uchun $p$ shimol-shimoli-sharqiy oktantda edi, ular o‘zlarining eng yaqin qo‘shnisini allaqachon topgani uchun endi faol to‘plamda emas.*

Yangi $p$ nuqta qo‘shilganda, o‘z oktantida $p$ ni saqlaydigan har bir $s$ nuqta uchun $p$ ni eng yaqin qo‘shni deb xavfsiz belgilash mumkin. Bu to‘g‘ri, chunki $p$ shimol-shimoli-sharqiy oktantda bo‘lgani uchun ularning orasidagi masofa $d(p,s) = |x_p - x_s| + |y_p - y_s| = (x_p + y_p) - (x_s + y_s)$. Saralash qadami tufayli keyingi barcha nuqtalarning $x + y$ qiymati kichikroq bo‘lmaydi, shuning uchun $p$ ning masofasi eng kichik bo‘lishi kafolatlanadi. Shunda bunday barcha nuqtalarni faol to‘plamdan olib tashlaymiz va nihoyat $p$ ni faol to‘plamga qo‘shamiz.

Keyingi savol: qaysi $s$ nuqtalar uchun $p$ shimol-shimoli-sharqiy oktantda yotishini samarali qanday topish mumkin? Ya’ni qaysi $s$ nuqtalar quyidagilarni qanoatlantiradi:

- $x_s \leq x_p$
- $x_p - y_p < x_s - y_s$

Faol to‘plamdagi hech bir nuqta boshqasining $R_1$ sohasida yotmagani uchun faol to‘plamdagi ikki $q_1$ va $q_2$ nuqta uchun $x_{q_1} \neq x_{q_2}$ bo‘ladi va ularning tartibi $x_{q_1} < x_{q_2} \implies x_{q_1} - y_{q_1} \leq x_{q_2} - y_{q_2}$ ni bildiradi.

Buni yuqoridagi rasmlarda $x - y$ tartibini shimoli-g‘arbdan janubi-sharqqa boradigan, ya’ni chizilganiga perpendikulyar bo‘lgan “supuruvchi chiziq” deb o‘ylab tasavvur qilishga urinib ko‘rishingiz mumkin.

Bu degani, agar faol to‘plamni $x$ bo‘yicha tartiblangan holda saqlasak, nomzod $s$ nuqtalar ketma-ket joylashgan bo‘ladi. Shunda $x_s \leq x_p$ bo‘lgan eng katta $x$ ni topib, ikkinchi shart $x_p - y_p < x_s - y_s$ buzilgunga qadar nuqtalarni $x$ ning kamayish tartibida ko‘rib chiqamiz (aslida $x_p - y_p = x_s - y_s$ bo‘lishiga ham ruxsat berish mumkin, bu koordinatalari teng bo‘lgan nuqtalar holatini hal qiladi). E’tibor bering, ishlov berishdan keyin nuqtalarni to‘plamdan darhol o‘chirganimiz uchun bu amortizatsiyalangan $O(n \log(n))$ murakkablikka ega bo‘ladi.
Endi shimoli-sharq yo‘nalishidagi eng yaqin nuqta bizda bor, nuqtalarni burib, jarayonni takrorlaymiz. Shu yo‘l bilan janubi-g‘arb yo‘nalishidagi eng yaqin nuqtani ham topishimizni ko‘rsatish mumkin, shuning uchun 8 marta emas, atigi 4 marta takrorlash yetarli.

Xulosa qilib, biz:

- Nuqtalarni $x + y$ bo‘yicha kamaymaydigan tartibda saralaymiz;
- Har bir nuqta uchun faol to‘plamni $x \leq x_p$ bo‘lgan eng katta $x$ li nuqtadan boshlab ko‘rib chiqamiz va $x_p - y_p \geq x_s - y_s$ bo‘lsa, siklni to‘xtatamiz. Har bir yaroqli $s$ nuqta uchun $(s,p, d(s,p))$ qirrani ro‘yxatimizga qo‘shamiz;
- $p$ nuqtani faol to‘plamga qo‘shamiz;
- Barcha oktantlar bo‘ylab o‘tib bo‘lgunimizcha nuqtalarni burib, takrorlaymiz.
- MST ni olish uchun qirralar ro‘yxatiga Kruskal algoritmini qo‘llaymiz.

Quyida [KACTL](https://github.com/kth-competitive-programming/kactl/blob/main/content/geometry/ManhattanMST.h) dagi variantga asoslangan implementatsiyani topishingiz mumkin.

```cpp
struct point {
    long long x, y;
};

// Returns a list of edges in the format (weight, u, v). 
// Passing this list to Kruskal algorithm will give the Manhattan MST.
vector<tuple<long long, int, int>> manhattan_mst_edges(vector<point> ps) {
    vector<int> ids(ps.size());
    iota(ids.begin(), ids.end(), 0);
    vector<tuple<long long, int, int>> edges;
    for (int rot = 0; rot < 4; rot++) { // for every rotation
        sort(ids.begin(), ids.end(), [&](int i, int j){
            return (ps[i].x + ps[i].y) < (ps[j].x + ps[j].y);
        });
        map<int, int, greater<int>> active; // (xs, id)
        for (auto i : ids) {
            for (auto it = active.lower_bound(ps[i].x); it != active.end();
            active.erase(it++)) {
                int j = it->second;
                if (ps[i].x - ps[i].y > ps[j].x - ps[j].y) break;
                assert(ps[i].x >= ps[j].x && ps[i].y >= ps[j].y);
                edges.push_back({(ps[i].x - ps[j].x) + (ps[i].y - ps[j].y), i, j});
            }
            active[ps[i].x] = i;
        }
        for (auto &p : ps) { // rotate
            if (rot & 1) p.x *= -1;
            else swap(p.x, p.y);
        }
    }
    return edges;
}
```

## Masalalar {#problems}

- [AtCoder Beginner Contest 178E - Dist Max](https://atcoder.jp/contests/abc178/tasks/abc178_e)
- [CodeForces 1093G - Multidimensional Queries](https://codeforces.com/contest/1093/problem/G)
- [CodeForces 944F - Game with Tokens](https://codeforces.com/contest/944/problem/F)
- [AtCoder Code Festival 2017D - Four Coloring](https://atcoder.jp/contests/code-festival-2017-quala/tasks/code_festival_2017_quala_d)
- [The 2023 ICPC Asia EC Regionals Online Contest (I) - J. Minimum Manhattan Distance](https://codeforces.com/gym/104639/problem/J)
- [Petrozavodsk Winter Training Camp 2016 Contest 4 - B. Airports](https://codeforces.com/group/eqgxxTNwgd/contest/100959/attachments)
