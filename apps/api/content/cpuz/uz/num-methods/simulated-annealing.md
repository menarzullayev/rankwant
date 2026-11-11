# Simulyatsiyalangan toblash {#simulated-annealing}

**Simulyatsiyalangan toblash (Simulated Annealing, SA)** — funksiyaning global optimumini yaqinlashtiradigan tasodifiy algoritm. U tasodifiy algoritm deb ataladi, chunki qidiruvda ma’lum miqdorda tasodifiylikdan foydalanadi, shuning uchun bir xil kirish uchun ham uning chiqishi har xil bo‘lishi mumkin.

## Masala {#the-problem}

Bizga $s$ holatning energiyasini hisoblaydigan $E(s)$ funksiya berilgan. $E(s)$ minimal bo‘ladigan $s_{best}$ holatni topish talab qilinadi. **SA** holatlar diskret va $E(s)$ bir nechta lokal minimumga ega bo‘lgan masalalar uchun mos keladi. Misol sifatida [kommivoyajer masalasi (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem)ni olamiz.

### Kommivoyajer masalasi (TSP) {#travelling-salesman-problem-tsp}

Sizga 2 o‘lchamli fazodagi tugunlar to‘plami berilgan. Har bir tugun $x$ va $y$ koordinatalari bilan xarakterlanadi. Vazifangiz — tugunlarga shu tartibda tashrif buyurganda bosib o‘tiladigan masofani minimallashtiradigan tugunlar tartibini topish.

## Motivatsiya {#motivation}
Toblash — metallurgiya jarayoni bo‘lib, unda material qizdiriladi va sovishga qo‘yib yuboriladi, shunda ichidagi atomlar minimal ichki energiyali joylashuvga qayta joylashadi, bu esa o‘z navbatida materialning xossalari boshqacha bo‘lishiga olib keladi. Holat — atomlarning joylashuvi, ichki energiya esa minimallashtirilayotgan funksiyadir. Atomlarning dastlabki holatini ularning ichki energiyasi uchun lokal minimum deb tasavvur qilish mumkin. Materialni atomlarini qayta joylashtirishga undash uchun, global minimumga yetish maqsadida, uning ichki energiyasi minimal bo‘lmagan sohadan o‘tishga rag‘batlantirish kerak. Bu rag‘bat materialni yuqoriroq haroratgacha qizdirish orqali beriladi.

Simulyatsiyalangan toblash aynan shu jarayonni simulyatsiya qiladi. Biz tasodifiy holat (material) bilan boshlaymiz va yuqori temperatura o‘rnatamiz (uni qizdiramiz). Endi algoritm joriy holatdan yuqoriroq energiyali holatlarni qabul qilishga tayyor, chunki uni yuqori temperatura rag‘batlantiradi. Bu algoritmning lokal minimumlarda tiqilib qolishiga to‘sqinlik qiladi va global minimum tomon harakatlanishiga yordam beradi. Vaqt o‘tishi bilan algoritm soviydi, yuqoriroq energiyali holatlarni rad eta boshlaydi va o‘zi topgan eng yaqin minimumga o‘tadi.

### $E(s)$ energiya funksiyasi {#the-energy-function-es}

$E(s)$ — minimallashtirilishi (yoki maksimallashtirilishi) kerak bo‘lgan funksiya. U har bir holatni haqiqiy songa akslantiradi. TSP holida $E(s)$ holatdagi tugunlar tartibida bitta to‘liq aylanib chiqish masofasini qaytaradi.

### Holat {#state}

Holatlar fazosi — $E(s)$ energiya funksiyasining aniqlanish sohasi, holat esa holatlar fazosiga tegishli har qanday elementdir. TSP holida barcha tugunlarga tashrif buyurish uchun bosib o‘tish mumkin bo‘lgan barcha yo‘llar holatlar fazosini tashkil qiladi, bu yo‘llarning har bir alohida birini esa holat deb hisoblash mumkin.

### Qo‘shni holat {#neighbouring-state}

Bu holatlar fazosidagi oldingi holatga yaqin bo‘lgan holat. Odatda qo‘shni holatni dastlabki holatdan oddiy almashtirish yordamida olish mumkin. Kommivoyajer masalasida qo‘shni holat tasodifiy ravishda 2 ta tugun tanlab, ularning joriy holatdagi o‘rinlarini almashtirish orqali olinadi.

## Algoritm {#algorithm}

Biz tasodifiy $s$ holatdan boshlaymiz. Har qadamda joriy $s$ holatning $s_{next}$ qo‘shni holatini tanlaymiz. Agar $E(s_{next}) < E(s)$ bo‘lsa, $s = s_{next}$ deb yangilaymiz. Aks holda $s_{next}$ ga o‘tish yoki $s$ da qolishni hal qiluvchi $P(E(s),E(s_{next}),T)$ qabul qilish ehtimoli funksiyasidan foydalanamiz. Bu yerda $T$ — temperatura; u boshida yuqori qiymatga o‘rnatiladi va har qadamda asta-sekin kamayadi. Temperatura qancha yuqori bo‘lsa, $s_{next}$ ga o‘tish ehtimoli shuncha katta.
Shu bilan birga barcha iteratsiyalar bo‘yicha eng yaxshi $s_{best}$ holatni ham kuzatib boramiz. Jarayon yaqinlashguncha yoki vaqt tugaguncha davom etadi.

![](https://upload.wikimedia.org/wikipedia/commons/d/d5/Hill_Climbing_with_Simulated_Annealing.gif)

*Bir nechta lokal maksimumga ega funksiyaning maksimumini izlayotgan simulyatsiyalangan toblashning vizual ko‘rinishi.*


### Temperatura ($T$) va sovish ($u$) {#temperaturet-and-decayu}

Tizim temperaturasi algoritmning yuqoriroq energiyali holatni qabul qilishga tayyorligini miqdoriy ifodalaydi. Sovish (decay) — algoritmning «sovish tezligi»ni ifodalovchi o‘zgarmas. Sekin sovish (kattaroq $u$) yaxshiroq natija berishi ma’lum.

## Qabul qilish ehtimoli funksiyasi (PAF) {#probability-acceptance-functionpaf}

$P(E,E_{next},T) =
    \begin{cases}
       \text{True} &\quad\text{if }  \mathcal{U}_{[0,1]} \le \exp(-\frac{E_{next}-E}{T}) \\
       \text{False} &\quad\text{otherwise}\\
     \end{cases}$

Bu yerda $\mathcal{U}_{[0,1]}$ — $[0,1]$ oraliqdagi uzluksiz tekis taqsimlangan tasodifiy qiymat. Bu funksiya joriy holatni, keyingi holatni va temperaturani qabul qilib, qidiruvga $s_{next}$ ga o‘tish yoki $s$ da qolishni bildiruvchi mantiqiy qiymat qaytaradi. E’tibor bering, $E_{next} < E$ bo‘lganda bu funksiya doim True qaytaradi, aks holda u baribir $\exp(-\frac{E_{next}-E}{T})$ ehtimol bilan o‘tishni amalga oshirishi mumkin, bu [Gibbs o‘lchoviga](https://en.wikipedia.org/wiki/Gibbs_measure) mos keladi.

```cpp
bool P(double E,double E_next,double T,mt19937 rng){
    double prob =  exp(-(E_next-E)/T);
    if(prob > 1) return true;
    else{
        bernoulli_distribution d(prob); 
        return d(rng);
    }
}
```
## Kod shabloni {#code-template}

```cpp
class state {
    public:
    state() {
        // Generate the initial state
    }
    state next() {
        state s_next;
        // Modify s_next to a random neighboring state
        return s_next;
    }
    double E() {
        // Implement the energy function here
    };
};

pair<double, state> simAnneal() {
    state s = state();
    state best = s;
    double T = 10000; // Initial temperature
    double u = 0.995; // decay rate
    double E = s.E();
    double E_next;
    double E_best = E;
    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
    while (T > 1) {
        state next = s.next();
        E_next = next.E();
        if (P(E, E_next, T, rng)) {
            s = next;
            if (E_next < E_best) {
                best = s;
                E_best = E_next;
            }
            E = E_next;
        }
        T *= u;
    }
    return {E_best, best};
}

```
## Qanday foydalanish: {#how-to-use}
State sinfining funksiyalarini kerakli tarzda to‘ldiring. Agar minimum emas, global maksimumni topmoqchi bo‘lsangiz, $E()$ funksiya maksimallashtirilayotgan funksiyaning manfiy qiymatini qaytarishiga ishonch hosil qiling va oxirida $-E_{best}$ ni chop eting. Quyidagi parametrlarni ehtiyojingizga qarab o‘rnating.

### Parametrlar {#parameters}
- $T$ : Boshlang‘ich temperatura. Qidiruv uzoqroq ishlashini istasangiz, uni kattaroq qiymatga o‘rnating.
- $u$ : Sovish. Sovish tezligini belgilaydi. Sekinroq sovish ($u$ ning kattaroq qiymati) odatda yaxshiroq natija beradi, lekin uzoqroq ishlash evaziga. $u < 1$ ekaniga ishonch hosil qiling.

Sikl bajaradigan iteratsiyalar soni quyidagi ifoda bilan beriladi

$N =   \lceil -\log_{u}{T} \rceil$

$T$ va $u$ ni tanlash bo‘yicha maslahatlar: agar lokal minimumlar ko‘p va holatlar fazosi keng bo‘lsa, algoritm ko‘proq imkoniyatlarni o‘rganishi uchun sekin sovish tezligi uchun $u = 0.999$ qilib o‘rnating. Aksincha, holatlar fazosi tor bo‘lsa, $u = 0.99$ yetarli bo‘lishi kerak. Ishonchingiz komil bo‘lmasa, $u = 0.998$ yoki undan yuqori qiymat o‘rnatib, xavfsiz yo‘ldan boring. Algoritmning bitta iteratsiyasi vaqt murakkabligini hisoblang va undan TLE bo‘lmasligini ta’minlaydigan $N$ qiymatini taxminan aniqlash uchun foydalaning, so‘ng $T$ ni olish uchun quyidagi formuladan foydalaning.

$T = u^{-N}$

### TSP uchun namunaviy implementatsiya {#example-implementation-for-tsp}
```cpp

class state {
    public:
    vector<pair<int, int>> points;
	std::mt19937 mt{ static_cast<std::mt19937::result_type>(
		std::chrono::steady_clock::now().time_since_epoch().count()
		) };
    state() {
        points = {{0,0},{2,2},{0,2},{2,0},{0,1},{1,2},{2,1},{1,0}};
    }
    state next() {
        state s_next;
        s_next.points = points;
        uniform_int_distribution<> choose(0, points.size()-1);
        int a = choose(mt);
        int b = choose(mt);
        s_next.points[a].swap(s_next.points[b]);
        return s_next;
    }

    double euclidean(pair<int, int> a, pair<int, int> b) {
        return hypot(a.first - b.first, a.second - b.second);
    }
    
    double E() {
        double dist = 0;
        int n = points.size();
        for (int i = 0;i < n; i++)
            dist += euclidean(points[i], points[(i+1)%n]);
        return dist;
    };
};

int main() {
    pair<double, state> res;
    res = simAnneal();
    double E_best = res.first;
    state best = res.second;
    cout << "Length of shortest path found : " << E_best << "\n";
    cout << "Order of points in shortest path : \n";
    for(auto x: best.points) {
        cout << x.first << " " << x.second << "\n";
    }
}
```

## Algoritmga qo‘shimcha o‘zgartirishlar: {#further-modifications-to-the-algorithm}

- TLE bo‘lmasligi uchun while siklga vaqtga asoslangan chiqish shartini qo‘shing
- Yuqorida amalga oshirilgan sovish eksponensial sovishdir. Uni ehtiyojingizga mos sovish funksiyasi bilan almashtirishingiz mumkin.
- Yuqorida berilgan qabul qilish ehtimoli funksiyasi eksponent suratidagi $E_{next} - E$ ko‘paytuvchisi tufayli energiyasi pastroq holatlarni qabul qilishni afzal ko‘radi. Qabul qilish ehtimoli funksiyasini energiyalar farqiga bog‘liq bo‘lmagan qilish uchun bu ko‘paytuvchini shunchaki olib tashlashingiz mumkin.
- $E_{next} - E$ energiyalar farqining qabul qilish ehtimoli funksiyasiga ta’sirini quyida ko‘rsatilgandek eksponent asosini oshirish/kamaytirish orqali kuchaytirish/susaytirish mumkin:
```cpp
bool P(double E, double E_next, double T, mt19937 rng) {
    double e = 2; // set e to any real number greater than 1
    double prob =  pow(e,-(E_next-E)/T);
    if (prob > 1)
        return true;
    else {
        bernoulli_distribution d(prob); 
        return d(rng);
    }
}
```

## Masalalar {#problems}

- [USACO Jan 2017 - Subsequence Reversal](https://usaco.org/index.php?page=viewproblem2&cpid=698)
- [Deltix Summer 2021 - DIY Tree](https://codeforces.com/contest/1556/problem/H)
- [AtCoder Contest Scheduling](https://atcoder.jp/contests/intro-heuristics/tasks/intro_heuristics_a)
