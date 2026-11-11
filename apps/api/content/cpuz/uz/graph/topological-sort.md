# Topologik saralash

Sizga $n$ ta tugun va $m$ ta qirrali yo‘naltirilgan graf berilgan.
Har bir qirra kichikroq indeksli tugundan kattaroq indeksli tugunga yo‘naladigan qilib tugunlarning **tartibini** topishingiz kerak.

Boshqacha aytganda, grafning barcha qirralari belgilaydigan tartibga mos tugunlar permutatsiyasini (**topologik tartib**ni) topmoqchisiz.

Quyida bir graf va uning topologik tartibi ko‘rsatilgan:

  ![yo‘naltirilgan graf misoli](/algorithms-media/graph/topological_1.png)
  ![bir topologik tartib](/algorithms-media/graph/topological_2.png)

Topologik tartib **yagona bo‘lmasligi** mumkin (masalan, agar $a$, $b$, $c$ tugunlar uchun $a$ dan $b$ ga va $a$ dan $c$ ga yo‘llar mavjud, ammo $b$ dan $c$ ga ham, $c$ dan $b$ ga ham yo‘l mavjud bo‘lmasa).
Misoldagi graf ham bir nechta topologik tartibga ega; ikkinchi topologik tartib quyidagicha:

  ![ikkinchi topologik tartib](/algorithms-media/graph/topological_3.png)

Topologik tartib umuman **mavjud bo‘lmasligi** ham mumkin.
U faqat yo‘naltirilgan grafda sikl bo‘lmasa mavjud.
Aks holda qarama-qarshilik yuzaga keladi: agar $a$ va $b$ tugunlarni o‘z ichiga olgan sikl mavjud bo‘lsa, $a$ ning indeksi $b$ nikidan kichik bo‘lishi kerak ($a$ dan $b$ ga yetish mumkin), ayni paytda katta ham bo‘lishi kerak ($b$ dan $a$ ga yetish mumkin).
Ushbu maqolada tasvirlangan algoritm har bir yo‘naltirilgan siklsiz grafda kamida bitta topologik tartib mavjudligini konstruktiv ravishda ham ko‘rsatadi.

Topologik saralash uchraydigan odatiy masalalardan biri quyidagicha. Qiymatlari noma’lum $n$ ta o‘zgaruvchi bor. Ayrim o‘zgaruvchilar uchun ulardan biri boshqasidan kichikligini bilamiz. Bu cheklovlar qarama-qarshi emasligini tekshirish va agar qarama-qarshi bo‘lmasa, o‘zgaruvchilarni o‘sish tartibida chiqarish kerak (bir nechta javob bo‘lsa, istalganini chiqaring). Bu aynan $n$ tugunli grafning topologik tartibini topish masalasi ekanini payqash oson.

## Algoritm

Bu masalani yechish uchun [chuqurlik bo‘yicha qidiruv](/algorithms/graph/depth-first-search)dan foydalanamiz.

Graf siklsiz deb faraz qilamiz. Chuqurlik bo‘yicha qidiruv nima qiladi?

Biror $v$ tugundan boshlaganda DFS $v$ dan chiquvchi barcha qirralar bo‘ylab yurishga urinadi.
Uchlariga avval tashrif buyurilgan qirralarda to‘xtaydi, qolgan qirralar bo‘ylab o‘tib, ularning uchlarida rekursiv davom etadi.

Shunday qilib, $\text{dfs}(v)$ funksiya chaqiruvi tugagan paytga kelib, $v$ dan erishish mumkin bo‘lgan barcha tugunlarga qidiruv bevosita (bitta qirra orqali) yoki bilvosita tashrif buyurgan bo‘ladi.

$\text{dfs}(v)$ ni tugatganimizda $v$ tugunni ro‘yxatga qo‘shamiz. Barcha erishiladigan tugunlarga allaqachon tashrif buyurilgani sababli, $v$ ni qo‘shayotganimizda ular ro‘yxatda oldinroq joylashgan bo‘ladi.
Buni grafdagi har bir tugun uchun bitta yoki bir nechta chuqurlik bo‘yicha qidiruv orqali bajaramiz.
Grafdagi har bir $v \rightarrow u$ yo‘naltirilgan qirra uchun $u$ ro‘yxatda $v$ dan oldin keladi, chunki $u$ ga $v$ dan erishish mumkin.
Demak, ro‘yxatdagi tugunlarga shunchaki $n-1, n-2, \dots, 1, 0$ yorliqlarini bersak, grafning topologik tartibini topgan bo‘lamiz.
Boshqacha aytganda, ro‘yxat teskari topologik tartibni ifodalaydi.

Bu tushuntirishlarni DFS algoritmining chiqish vaqtlari orqali ham ifodalash mumkin.
$v$ tugunning chiqish vaqti — $\text{dfs}(v)$ chaqiruvi tugagan vaqt (vaqtlarni $0$ dan $n-1$ gacha raqamlash mumkin).
Istalgan $v$ tugunning chiqish vaqti undan erishish mumkin bo‘lgan istalgan tugunning chiqish vaqtidan doim katta ekanini tushunish oson (chunki ularga $\text{dfs}(v)$ chaqirilishidan oldin yoki uning davomida tashrif buyurilgan). Demak, kerakli topologik tartib tugunlarni chiqish vaqtlari kamayish tartibida joylashtirish orqali olinadi.

## Implementatsiya

Quyidagi implementatsiya graf siklsiz, ya’ni kerakli topologik tartib mavjud deb faraz qiladi. Zarur bo‘lsa, [chuqurlik bo‘yicha qidiruv](/algorithms/graph/depth-first-search) maqolasida tasvirlanganidek, graf siklsiz ekanini oson tekshirish mumkin.

```cpp
int n; // number of vertices
vector<vector<int>> adj; // adjacency list of graph
vector<bool> visited;
vector<int> ans;

void dfs(int v) {
    visited[v] = true;
    for (int u : adj[v]) {
        if (!visited[u]) {
            dfs(u);
        }
    }
    ans.push_back(v);
}

void topological_sort() {
    visited.assign(n, false);
    ans.clear();
    for (int i = 0; i < n; ++i) {
        if (!visited[i]) {
            dfs(i);
        }
    }
    reverse(ans.begin(), ans.end());
}
```

Yechimning asosiy funksiyasi `topological_sort` bo‘lib, u DFS o‘zgaruvchilarini boshlang‘ich holatga keltiradi, DFS ni ishga tushiradi va javobni `ans` vektorida oladi. Graf siklsiz bo‘lmaganida ham `topological_sort` natijasi ma’lum ma’noda mazmunli bo‘lishini qayd etish kerak: agar $u$ tugunga $v$ dan erishish mumkin bo‘lsa-yu, aksincha erishish mumkin bo‘lmasa, natijaviy massivda $v$ doim oldin keladi.
Berilgan implementatsiyaning bu xossasi siklli yo‘naltirilgan grafda kuchli bog‘langan komponentlar va ularning topologik tartibini ajratish uchun [Kosaraju algoritmi](/algorithms/graph/strongly-connected-components)da ishlatiladi.

## Mashq masalalari

- [SPOJ TOPOSORT - Topological Sorting [qiyinlik: oson]](http://www.spoj.com/problems/TOPOSORT/)
- [UVA 10305 - Ordering Tasks [qiyinlik: oson]](https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=1246)
- [UVA 124 - Following Orders [qiyinlik: oson]](https://onlinejudge.org/index.php?option=onlinejudge&page=show_problem&problem=60)
- [UVA 200 - Rare Order [qiyinlik: oson]](https://onlinejudge.org/index.php?option=onlinejudge&page=show_problem&problem=136)
- [Codeforces 510C - Fox and Names [qiyinlik: oson]](http://codeforces.com/problemset/problem/510/C)
- [SPOJ RPLA - Answer the boss!](https://www.spoj.com/problems/RPLA/)
- [CSES - Course Schedule](https://cses.fi/problemset/task/1679)
- [CSES - Longest Flight Route](https://cses.fi/problemset/task/1680)
- [CSES - Game Routes](https://cses.fi/problemset/task/1681)
