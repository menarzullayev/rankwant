# Yarim tekisliklar kesishmasi {#half-plane-intersection}

Ushbu maqolada yarim tekisliklar to‘plamining kesishmasini hisoblash masalasini ko‘rib chiqamiz. Bunday kesishmani qavariq soha/ko‘pburchak sifatida qulay ifodalash mumkin: uning ichidagi har bir nuqta barcha yarim tekisliklar ichida ham yotadi, va aynan shu ko‘pburchakni topish yoki qurish kerak. Masala haqida dastlabki tasavvur beramiz, Sort-and-Incremental algoritmi deb ataladigan $O(N \log N)$ yondashuvni tavsiflaymiz va bu usulning ayrim namunaviy qo‘llanishlarini keltiramiz.

O‘quvchidan asosiy geometrik primitivlar va amallarni (nuqtalar, vektorlar, to‘g‘ri chiziqlar kesishishi) bilish qat’iy tavsiya etiladi. Bundan tashqari, [Qavariq qobiq](/algorithms/geometry/convex-hull) yoki [Convex Hull Trick](/algorithms/geometry/convex-hull-trick) haqidagi bilimlar maqoladagi tushunchalarni yaxshiroq anglashga yordam beradi, ammo bular hech qanday ma’noda majburiy shart emas.

## Dastlabki izohlar va ta’riflar {#initial-clarifications-and-definitions}

Butun maqola davomida (boshqacha aytilmasa) quyidagi farazlarni qabul qilamiz:

1. $N$ — berilgan to‘plamdagi yarim tekisliklar soni.
2. To‘g‘ri chiziqlar va yarim tekisliklarni bitta nuqta va bitta vektor bilan ifodalaymiz (berilgan chiziqda yotuvchi istalgan nuqta va chiziqning yo‘nalish vektori). Yarim tekisliklar uchun har bir yarim tekislik o‘z yo‘nalish vektorining chap tomonidagi sohani ruxsat etadi deb hisoblaymiz. Bundan tashqari, yarim tekislikning burchagini uning yo‘nalish vektorining qutbiy burchagi deb ta’riflaymiz. Misol uchun quyidagi rasmga qarang.
3. Natijaviy kesishma doim yoki chegaralangan, yoki bo‘sh deb faraz qilamiz. Chegaralanmagan holatni qayta ishlash kerak bo‘lsa, yetarlicha katta chegaralovchi to‘rtburchakni belgilaydigan 4 ta yarim tekislik qo‘shish kifoya.
4. Soddalik uchun berilgan to‘plamda parallel yarim tekisliklar yo‘q deb faraz qilamiz. Maqola oxirida bunday holatlarni qanday hal qilish haqida to‘xtalamiz.

![](/algorithms-media/geometry/halfplanes_rep.png)

$y \geq 2x - 2$ yarim tekisligini $P = (1, 0)$ nuqta va $PQ = Q - P = (1, 2)$ yo‘nalish vektori bilan ifodalash mumkin.

## Qo‘pol kuch usuli — $O(N^3)$ {#brute-force-approach-on3}

Eng sodda va ravshan yechimlardan biri — barcha yarim tekisliklar juftlari chiziqlarining kesishish nuqtasini hisoblash va har bir nuqta uchun u boshqa barcha yarim tekisliklar ichida yotishini tekshirishdir. Kesishish nuqtalari $O(N^2)$ ta bo‘lgani va ularning har biri uchun $O(N)$ ta yarim tekislikni tekshirish kerakligi sababli, umumiy vaqt murakkabligi $O(N^3)$. Kesishma sohasining o‘zini, masalan, barcha yarim tekisliklarga kiritilgan kesishish nuqtalari to‘plamiga Qavariq qobiq algoritmini qo‘llab tiklash mumkin.

Bu usul nima uchun ishlashini tushunish ancha oson: natijaviy qavariq ko‘pburchakning uchlari yarim tekislik chiziqlarining kesishish nuqtalaridir va ularning har biri, shubhasiz, barcha yarim tekisliklarga tegishli. Bu usulning asosiy afzalligi — kesishma bo‘shmi yoki yo‘qligini tekshirish kerak bo‘lganda uni tushunish, eslab qolish va shu zahotiyoq yozish oson. Biroq u dahshatli darajada sekin va ko‘pchilik masalalar uchun yaroqsiz, shuning uchun tezroq narsa kerak.

## Inkremental usul — $O(N^2)$ {#incremental-approach-on2}

Yana bir oddiy yondashuv — yarim tekisliklar kesishmasini bittadan qo‘shib, bosqichma-bosqich qurish. Bu usul mohiyatan qavariq ko‘pburchakni to‘g‘ri chiziq bilan $N$ marta kesish va har bir bosqichda ortiqcha yarim tekisliklarni olib tashlashga teng. Buning uchun qavariq ko‘pburchakni kesmalar ro‘yxati sifatida ifodalash va uni yarim tekislik bilan kesish uchun kesmalarning yarim tekislik chizig‘i bilan kesishish nuqtalarini topish kifoya (chiziq ko‘pburchakni haqiqatan kesib o‘tsa, faqat ikkita kesishish nuqtasi bo‘ladi), so‘ng oradagi barcha kesmalarni yarim tekislikka mos yangi kesma bilan almashtiramiz. Bunday amal chiziqli vaqtda bajarilishi mumkin bo‘lgani uchun katta chegaralovchi to‘rtburchakdan boshlab, uni har bir yarim tekislik bilan kesib borish mumkin va umumiy vaqt murakkabligi $O(N^2)$ bo‘ladi.

Bu usul to‘g‘ri yo‘nalishdagi katta qadam, ammo har bir bosqichda $O(N)$ ta yarim tekislik bo‘ylab yurish isrofgarchilikdek tuyuladi. Quyida ayrim mohirona kuzatishlar yordamida bu inkremental yondashuvdagi g‘oyalarni qayta ishlatib, $O(N \log N)$ algoritm yaratish mumkinligini ko‘ramiz.

## Sort-and-Incremental algoritmi — $O(N \log N)$ {#sort-and-incremental-algorithm-on-log-n}

Bu algoritmning to‘g‘ri hujjatlashtirilgan birinchi manbasi sifatida topa olganimiz — Zeyuan Zhu ning 2006-yilgi Xitoy jamoaviy tanlov musobaqasi uchun yozilgan [New Algorithm for Half-plane Intersection and its Practical Value](http://people.csail.mit.edu/zeyuan/publications.htm) nomli dissertatsiyasi. Quyida tavsiflanadigan yondashuv shu algoritmga asoslangan, ammo kesishmaning pastki va yuqori yarmlari uchun ikkita alohida kesishmani hisoblash o‘rniga, uni deque (ikki tomonlama navbat) yordamida bir o‘tishda butunlay quramiz.

Algoritmning o‘zi, nomidan bilinib turganidek, yarim tekisliklar kesishmasidan hosil bo‘lgan soha qavariq ekanligidan foydalanadi va shu sababli u yarim tekisliklarning burchaklari bo‘yicha tartiblangan ayrim kesmalaridan iborat bo‘ladi. Bu muhim kuzatishga olib keladi: agar yarim tekisliklarni burchak bo‘yicha tartiblangan holda (ular kesishmaning yakuniy natijaviy shaklida paydo bo‘ladigan tartibda) inkremental ravishda kesishtirib, ikki tomonlama navbatda saqlasak, yarim tekisliklarni faqat deque boshidan va oxiridan o‘chirishga to‘g‘ri keladi.

Bu faktni yaxshiroq tasavvur qilish uchun, yuqorida tasvirlangan inkremental usulni burchak bo‘yicha saralangan yarim tekisliklar to‘plamiga qo‘llayapmiz deylik (bu holda ular $-\pi$ dan $\pi$ gacha saralangan deb faraz qilamiz) va biror ixtiyoriy $k$-qadamni boshlamoqchi bo‘lamiz. Bu birinchi $k-1$ ta yarim tekislikning kesishmasi allaqachon qurilganini bildiradi. Endi yarim tekisliklar burchak bo‘yicha saralangani uchun $k$-yarim tekislik qanday bo‘lishidan qat’i nazar, u $(k-1)$-yarim tekislik bilan qavariq burilish hosil qilishiga ishonch hosil qilishimiz mumkin. Shu sababli bir nechta narsa yuz berishi mumkin:

1. Kesishma oxiridagi ayrim (ehtimol hech qaysi) yarim tekisliklar *ortiqcha* bo‘lib qolishi mumkin. Bu holda ushbu endi foydasiz yarim tekisliklarni deque oxiridan olib tashlashimiz kerak.
2. Boshidagi ayrim (ehtimol hech qaysi) yarim tekisliklar *ortiqcha* bo‘lib qolishi mumkin. 1-holatga o‘xshab, ularni deque boshidan olib tashlaymiz.
3. (1- va/yoki 2-holatlarni qayta ishlagandan keyin) kesishma bo‘sh bo‘lib qolishi mumkin. Bu holda kesishma bo‘shligini e’lon qilib, algoritmni tugatamiz.

*Agar yarim tekislik kesishmaga hech narsa qo‘shmasa, uni “ortiqcha” deymiz. Bunday yarim tekislikni olib tashlash mumkin va natijaviy kesishma umuman o‘zgarmaydi.*

Quyida rasm bilan kichik misol keltirilgan:

$H = \{ A, B, C, D, E \}$ kesishmada hozir mavjud bo‘lgan yarim tekisliklar to‘plami bo‘lsin. Bundan tashqari, $P = \{ p, q, r, s \}$ — $H$ dagi qo‘shni yarim tekisliklarning kesishish nuqtalari to‘plami bo‘lsin. Endi quyidagi rasmda ko‘rsatilganidek, uni $F$ yarim tekislik bilan kesishtirmoqchimiz:

![](/algorithms-media/geometry/halfplanes_hp1.png)

E’tibor bering, $F$ yarim tekislik $A$ va $E$ ni kesishmada ortiqcha qiladi. Shuning uchun $A$ va $E$ ni mos ravishda kesishmaning boshidan va oxiridan olib tashlaymiz, oxiriga esa $F$ ni qo‘shamiz. Natijada $P = \{ q, r, t, u \}$ bilan yangi $H = \{ B, C, D, F\}$ kesishmani olamiz.

![](/algorithms-media/geometry/halfplanes_hp2.png)

Shularni hisobga olsak, algoritmni amalda implementatsiya qilish uchun deyarli hamma narsa bor, ammo hali ayrim maxsus holatlar haqida gapirishimiz kerak. Maqola boshida kesishma chegaralanmagan bo‘lishi mumkin bo‘lgan holatlarni hal qilish uchun chegaralovchi to‘rtburchak qo‘shishni aytgan edik, shuning uchun haqiqatan ham qayta ishlashimiz kerak bo‘lgan yagona murakkab holat — parallel yarim tekisliklar. Ikkita kichik holat bo‘lishi mumkin: ikki yarim tekislik bir xil yo‘nalishda yoki qarama-qarshi yo‘nalishda parallel bo‘lishi mumkin. Bu holat alohida ko‘rib chiqilishi sababi shundaki, yarim tekislik ortiqchami yoki yo‘qmi tekshirish uchun yarim tekislik chiziqlarining kesishish nuqtalarini hisoblashimiz kerak, ikkita parallel chiziqning esa kesishish nuqtasi yo‘q, shuning uchun ular bilan ishlashning maxsus usuli kerak.

Qarama-qarshi yo‘nalishli parallel yarim tekisliklar holati uchun: chegaralanmagan holatni hal qilish uchun chegaralovchi to‘rtburchak qo‘shayotganimiz sababli, bu saralashdan keyin qarama-qarshi yo‘nalishli ikkita qo‘shni parallel yarim tekislik bo‘lgan holatni ham hal qiladi, chunki bu ikkisi orasida chegaralovchi to‘rtburchakning kamida bitta yarim tekisligi bo‘lishi shart (ular burchak bo‘yicha saralanganini eslang).

 * Biroq deque oxiridan ayrim yarim tekisliklarni o‘chirgandan keyin qarama-qarshi yo‘nalishli ikkita parallel yarim tekislik yonma-yon qolib ketishi mumkin. Bu holat aynan shu ikkala yarim tekislik bo‘sh kesishma hosil qilgandagina yuz beradi, chunki bu oxirgi yarim tekislik deque dagi hamma narsani o‘chirib yuborishga sabab bo‘ladi. Bu muammoning oldini olish uchun parallel yarim tekisliklarni qo‘lda tekshirishimiz kerak va agar ular qarama-qarshi yo‘nalishli bo‘lsa, algoritmni zudlik bilan to‘xtatib, bo‘sh kesishmani qaytaramiz.

Shunday qilib, haqiqatan ham qayta ishlashimiz kerak bo‘lgan yagona holat — bir xil burchakli bir nechta yarim tekislik mavjudligi, va bu holatni hal qilish ancha oson ekan: faqat eng chapdagi yarim tekislikni saqlab, qolganlarini o‘chirish kerak, chunki ular baribir butunlay ortiqcha bo‘ladi.

Xulosa qilsak, to‘liq algoritm taxminan quyidagicha ko‘rinadi:

1. Avval yarim tekisliklar to‘plamini burchak bo‘yicha saralaymiz; bu $O(N \log N)$ vaqt oladi.
2. Yarim tekisliklar to‘plami bo‘ylab yuramiz va har biri uchun inkremental amalni bajaramiz, kerak bo‘lganda ikki tomonlama navbatning boshidan va oxiridan o‘chiramiz. Har bir yarim tekislik faqat bir marta qo‘shilishi yoki o‘chirilishi mumkin bo‘lgani uchun bu jami chiziqli vaqt oladi.
3. Oxirida kesishmadan hosil bo‘lgan qavariq ko‘pburchakni amal tugagach deque dagi qo‘shni yarim tekisliklarning kesishish nuqtalarini hisoblash orqali oddiygina olish mumkin. Bu ham chiziqli vaqt oladi. Bunday nuqtalarni 2-qadam davomida saqlab, bu qadamni butunlay o‘tkazib yuborish ham mumkin, ammo ularni shu zahotiyoq hisoblash (implementatsiya nuqtayi nazaridan) biroz osonroq deb hisoblaymiz.

Jami $O(N \log N)$ vaqt murakkabligiga erishdik. Saralash aniq to‘siq bo‘lgani uchun, yarim tekisliklar burchaklari bo‘yicha oldindan saralab berilgan maxsus holatda (bunday holatga qavariq ko‘pburchakni aniqlaydigan yarim tekisliklarni olish misol bo‘ladi) algoritmni chiziqli vaqtda ishlaydigan qilish mumkin.

### To‘g‘ridan-to‘g‘ri implementatsiya {#direct-implementation}

Quyida algoritmning namunaviy, to‘g‘ridan-to‘g‘ri implementatsiyasi keltirilgan; ko‘pchilik qismlar izohlar bilan tushuntirilgan:

Oddiy nuqta/vektor va yarim tekislik strukturalari:

```cpp
// eps va inf ni kerak bo‘lsa qayta aniqlang. Aniqlik xatolariga e’tibor bering.
const long double eps = 1e-9, inf = 1e9; 

// Oddiy nuqta/vektor strukturasi.
struct Point { 

    long double x, y;
    explicit Point(long double x = 0, long double y = 0) : x(x), y(y) {}

    // Qo‘shish, ayirish, o‘zgarmasga ko‘paytirish, skalyar ko‘paytma, vektor ko‘paytma.

    friend Point operator + (const Point& p, const Point& q) {
        return Point(p.x + q.x, p.y + q.y); 
    }

    friend Point operator - (const Point& p, const Point& q) { 
        return Point(p.x - q.x, p.y - q.y); 
    }

    friend Point operator * (const Point& p, const long double& k) { 
        return Point(p.x * k, p.y * k); 
    } 
    
    friend long double dot(const Point& p, const Point& q) {
    	return p.x * q.x + p.y * q.y;
    }

    friend long double cross(const Point& p, const Point& q) { 
        return p.x * q.y - p.y * q.x; 
    }
};

// Oddiy yarim tekislik strukturasi.
struct Halfplane { 

    // 'p' — chiziq o‘tadigan nuqta, 'pq' — chiziqning yo‘nalish vektori.
    Point p, pq; 
    long double angle;

    Halfplane() {}
    Halfplane(const Point& a, const Point& b) : p(a), pq(b - a) {
        angle = atan2l(pq.y, pq.x);    
    }

    // 'r' nuqta bu yarim tekislikdan tashqarida ekanini tekshiradi. 
    // Har bir yarim tekislik o‘z chizig‘ining CHAP tomonidagi sohani ruxsat etadi.
    bool out(const Point& r) { 
        return cross(pq, r - p) < -eps; 
    }

    // Saralash uchun komparator. 
    bool operator < (const Halfplane& e) const { 
        return angle < e.angle;
    } 

    // Ikki yarim tekislik chiziqlarining kesishish nuqtasi. Ular hech qachon parallel emas deb faraz qilinadi.
    friend Point inter(const Halfplane& s, const Halfplane& t) {
        long double alpha = cross((t.p - s.p), t.pq) / cross(s.pq, t.pq);
        return s.p + (s.pq * alpha);
    }
};
```

Algoritm:

```cpp
// Algoritmning o‘zi
vector<Point> hp_intersect(vector<Halfplane>& H) { 

    Point box[4] = {  // Soat miliga teskari tartibdagi chegaralovchi to‘rtburchak
        Point(inf, inf), 
        Point(-inf, inf), 
        Point(-inf, -inf), 
        Point(inf, -inf) 
    };

    for(int i = 0; i<4; i++) { // Chegaralovchi to‘rtburchakning yarim tekisliklarini qo‘shamiz.
        Halfplane aux(box[i], box[(i+1) % 4]);
        H.push_back(aux);
    }

    // Burchak bo‘yicha saralab, algoritmni boshlaymiz
    sort(H.begin(), H.end());
    deque<Halfplane> dq;
    int len = 0;
    for(int i = 0; i < int(H.size()); i++) {

        // Oxirgi yarim tekislik ortiqcha bo‘lsa, deque oxiridan o‘chiramiz
        while (len > 1 && H[i].out(inter(dq[len-1], dq[len-2]))) {
            dq.pop_back();
            --len;
        }

        // Birinchi yarim tekislik ortiqcha bo‘lsa, deque boshidan o‘chiramiz
        while (len > 1 && H[i].out(inter(dq[0], dq[1]))) {
            dq.pop_front();
            --len;
        }
        
        // Maxsus holatni tekshirish: parallel yarim tekisliklar
        if (len > 0 && fabsl(cross(H[i].pq, dq[len-1].pq)) < eps) {
        	// Bir-biri bilan solishtirilib qolgan qarama-qarshi yo‘nalishli parallel yarim tekisliklar.
        	if (dot(H[i].pq, dq[len-1].pq) < 0.0)
        		return vector<Point>();
        	
        	// Bir xil yo‘nalishli yarim tekislik: faqat eng chapdagisini saqlaymiz.
        	if (H[i].out(dq[len-1].p)) {
        		dq.pop_back();
        		--len;
        	}
        	else continue;
        }
        
        // Yangi yarim tekislikni qo‘shamiz
        dq.push_back(H[i]);
        ++len;
    }

    // Yakuniy tozalash: boshdagi yarim tekisliklarni oxiridagilar bilan va aksincha tekshiramiz
    while (len > 2 && dq[0].out(inter(dq[len-1], dq[len-2]))) {
        dq.pop_back();
        --len;
    }

    while (len > 2 && dq[len-1].out(inter(dq[0], dq[1]))) {
        dq.pop_front();
        --len;
    }

    // Kerak bo‘lsa, kesishma bo‘sh ekanini bildiramiz
    if (len < 3) return vector<Point>();

    // Qolgan yarim tekisliklardan qavariq ko‘pburchakni tiklaymiz.
    vector<Point> ret(len);
    for(int i = 0; i+1 < len; i++) {
        ret[i] = inter(dq[i], dq[i+1]);
    }
    ret.back() = inter(dq[len-1], dq[0]);
    return ret;
}
```

### Implementatsiya muhokamasi {#implementation-discussion}

Shuni alohida ta’kidlash kerakki, agar bir nechta yarim tekislik aynan bitta nuqtada kesishsa, bu algoritm yakuniy ko‘pburchakda takrorlangan qo‘shni nuqtalarni qaytarishi mumkin. Biroq bu kesishma bo‘shmi yoki yo‘qmi degan masalani to‘g‘ri baholashga hech qanday ta’sir qilmaydi va ko‘pburchak yuziga ham umuman ta’sir etmaydi. Keyin bajarmoqchi bo‘lgan vazifalaringizga qarab bu takrorlarni olib tashlashni xohlashingiz mumkin. Buni std::unique yordamida juda osonlik bilan qilish mumkin. Yuzi nolga teng kesishmalar (masalan, bitta nuqta, chiziq yoki kesmadan iborat kesishmalar) to‘g‘ri hisoblanishi uchun algoritm bajarilishi davomida takrorlangan nuqtalarni saqlab qolishni xohlaymiz. O‘quvchiga kesishma bitta nuqta yoki chiziqqa aylanadigan ayrim kichik qo‘lda tuzilgan holatlarni sinab ko‘rishni tavsiya qilaman.

Yana bir gapirish kerak bo‘lgan narsa — yarim tekisliklar chiziqli cheklov ko‘rinishida berilsa (masalan, $ax + by + c \leq 0$) nima qilish kerak. Bu holda ikki variant bor. Algoritmni bunday ifodalash bilan ishlash uchun tegishli o‘zgartirishlar bilan implementatsiya qilishingiz mumkin (aslida o‘zingizning yarim tekislik strukturangizni yaratish; agar convex hull trick bilan tanish bo‘lsangiz, bu ancha oson bo‘ladi), yoki har bir chiziqning istalgan 2 ta nuqtasini olib, chiziqlarni biz maqolada ishlatgan ko‘rinishga o‘tkazishingiz mumkin. Umuman olganda, qo‘shimcha aniqlik muammolarining oldini olish uchun masalada berilgan ko‘rinish bilan ishlash tavsiya etiladi.

## Masalalar, vazifalar va qo‘llanishlar {#problems-tasks-and-applications}

Yarim tekisliklar kesishmasi yordamida yechiladigan ko‘plab masalalarni uning yordamisiz ham, lekin (odatda) murakkabroq yoki kamroq uchraydigan yondashuvlar bilan yechish mumkin. Odatda yarim tekisliklar kesishmasi ko‘pburchaklar (asosan qavariq), tekislikdagi ko‘rinuvchanlik va ikki o‘lchovli chiziqli dasturlash bilan bog‘liq masalalarda uchraydi. Quyida shu usul bilan yechiladigan ayrim namunaviy vazifalar keltirilgan:

### Qavariq ko‘pburchaklar kesishmasi {#convex-polygon-intersection}

Yarim tekisliklar kesishmasining klassik qo‘llanishlaridan biri: $N$ ta ko‘pburchak berilgan, ularning barchasi ichida bo‘lgan sohani hisoblash kerak.

Yarim tekisliklar to‘plamining kesishmasi qavariq ko‘pburchak bo‘lgani uchun, qavariq ko‘pburchakni ham yarim tekisliklar to‘plami sifatida ifodalash mumkin (ko‘pburchakning har bir tomoni yarim tekislikning kesmasidir). Har bir ko‘pburchak uchun shu yarim tekisliklarni hosil qilib, butun to‘plamning kesishmasini hisoblang. Umumiy vaqt murakkabligi $O(S \log S)$, bu yerda $S$ — barcha ko‘pburchaklar tomonlarining umumiy soni. Masalani nazariy jihatdan $N$ ta yarim tekisliklar to‘plamini uyum yordamida birlashtirib, so‘ng saralash qadamisiz algoritmni ishga tushirib, $O(S \log N)$ da ham yechish mumkin, ammo bunday yechimning doimiy ko‘paytuvchisi oddiy saralashdan ancha yomon va faqat juda kichik $N$ uchun ozgina tezlik beradi.

### Tekislikda ko‘rinuvchanlik {#visibility-in-the-plane}

“Tekislikdagi biror nuqta(lar)dan ba’zi kesmalar ko‘rinadimi yoki yo‘qmi aniqlang” kabi talab qilinadigan masalalarni odatda yarim tekisliklar kesishmasi masalasi sifatida ifodalash mumkin. Misol uchun, quyidagi vazifani olaylik: biror sodda (albatta qavariq bo‘lmagan) ko‘pburchak berilgan; ko‘pburchak ichida shunday nuqta borligini aniqlang, bu nuqtadan ko‘pburchakning butun chegarasini ko‘rish mumkin bo‘lsin. Bu [ko‘pburchak yadrosini](https://en.wikipedia.org/wiki/Star-shaped_polygon) topish deb ham ataladi va ko‘pburchakning har bir tomonini yarim tekislik sifatida olib, so‘ng uning kesishmasini hisoblash orqali oddiy yarim tekisliklar kesishmasi bilan yechish mumkin.

Quyida Artem Vasilyev o‘zining [Braziliya ICPC yozgi maktabi ma’ruzalaridan](https://youtu.be/WKyZSitpm6M?t=6463) birida keltirgan, shu bilan bog‘liq, qiziqarliroq masala:
tekislikda $p_1, p_2\ \dots \ p_n$ nuqtalardan iborat $p$ to‘plam berilgan; $p$ ning barcha nuqtalarini ularning indekslari o‘sish tartibida chapdan o‘ngga ko‘ra oladigan joyda tura olishingiz mumkin bo‘lgan biror $q$ nuqta bor-yo‘qligini aniqlang.

Bunday masalani quyidagini payqash orqali yechish mumkin: biror $p_i$ nuqtani $p_j$ ning chap tomonida ko‘ra olish $p_i$ dan $p_j$ gacha kesmaning o‘ng tomonini ko‘ra olish bilan bir xil (yoki unga teng kuchli ravishda, $p_j$ dan $p_i$ gacha kesmaning chap tomonini ko‘ra olish). Shuni hisobga olib, har bir $p_i p_{i+1}$ kesma uchun (yoki tanlagan yo‘nalishingizga qarab $p_{i+1} p_i$) yarim tekislik yaratib, butun to‘plam kesishmasi bo‘shmi yoki yo‘qligini tekshirish kifoya.

### Ikkilik qidiruv bilan yarim tekisliklar kesishmasi {#half-plane-intersection-with-binary-search}

Yana bir keng tarqalgan qo‘llanish — yarim tekisliklar kesishmasini ikkilik qidiruv jarayonining predikatini tekshirish vositasi sifatida ishlatish. Quyida shunday masalaga misol keltirilgan; u ham yuqorida eslatilgan ma’ruzada Artem Vasilyev tomonidan keltirilgan: **qavariq** $P$ ko‘pburchak berilgan; uning ichiga chizish mumkin bo‘lgan eng katta aylanani toping.

Qandaydir yopiq ko‘rinishdagi yechim, noqulay formulalar yoki tushunarsiz algoritmik yechimlarni izlash o‘rniga, javob bo‘yicha ikkilik qidiruv qilib ko‘raylik. E’tibor bering, biror qat’iy $r$ uchun radiusi $r$ bo‘lgan aylana $P$ ichiga faqat $P$ ichida $P$ chegarasining barcha nuqtalariga masofasi $r$ dan katta yoki unga teng bo‘lgan biror nuqta mavjud bo‘lgandagina chizilishi mumkin. Bu shartni ko‘pburchakni ichkariga $r$ masofaga “qisqartirish” va ko‘pburchak aynimagan holda qolishini (yoki o‘zi nuqta/kesma ekanini) tekshirish orqali tasdiqlash mumkin. Bunday amalni ko‘pburchak tomonlarining yarim tekisliklarini soat miliga teskari tartibda olib, ularning har birini ruxsat etilgan soha yo‘nalishida (ya’ni yarim tekislikning yo‘nalish vektoriga ortogonal) $r$ masofaga surib, kesishma bo‘sh emasligini tekshirish orqali simulyatsiya qilish mumkin.

Shubhasiz, agar $r$ radiusli aylana chizish mumkin bo‘lsa, $r$ dan kichik radiusli istalgan boshqa aylanani ham chizish mumkin. Shuning uchun $r$ radius bo‘yicha ikkilik qidiruv o‘tkazib, har bir qadamni yarim tekisliklar kesishmasi yordamida tekshirishimiz mumkin. Shuningdek, qavariq ko‘pburchak yarim tekisliklari allaqachon burchak bo‘yicha saralangan, shuning uchun algoritmda saralash qadamini o‘tkazib yuborish mumkin. Shunday qilib, jami $O(NK)$ vaqt murakkabligini olamiz, bu yerda $N$ — ko‘pburchak uchlari soni, $K$ — ikkilik qidiruv iteratsiyalari soni (haqiqiy qiymat mumkin bo‘lgan javoblar oralig‘i va kerakli aniqlikka bog‘liq bo‘ladi).

### Ikki o‘lchovli chiziqli dasturlash {#two-dimensional-linear-programming}

Yarim tekisliklar kesishmasining yana bir qo‘llanishi — ikki o‘zgaruvchili chiziqli dasturlash. Ikki o‘zgaruvchi uchun barcha chiziqli cheklovlarni $Ax + By + C \leq 0$ ko‘rinishida ifodalash mumkin (tengsizlik belgisi har xil bo‘lishi mumkin). Shubhasiz, bular shunchaki yarim tekisliklar, shuning uchun chiziqli cheklovlar to‘plami uchun yaroqli yechim mavjudligini yarim tekisliklar kesishmasi yordamida tekshirish mumkin. Bundan tashqari, berilgan chiziqli cheklovlar to‘plami uchun yaroqli yechimlar sohasini (ya’ni yarim tekisliklar kesishmasini) hisoblash va so‘ng cheklovlar ostida biror chiziqli $f(x, y)$ funksiyani maksimallashtirish/minimallashtirishga oid ko‘plab so‘rovlarga ikkilik qidiruv yordamida (convex hull trickka juda o‘xshash) har bir so‘rov uchun $O(\log N)$ da javob berish mumkin.

Shuni ham aytib o‘tish kerakki, chiziqli cheklovlar to‘plami yaroqli yechimga ega yoki ega emasligini tekshiradigan hamda berilgan cheklovlar ostida biror chiziqli funksiyani maksimallashtiradigan/minimallashtiradigan ancha sodda randomizatsiyalangan algoritm ham mavjud. Bu randomizatsiyalangan algoritmni ham Artem Vasilyev yuqorida eslatilgan ma’ruzada yaxshi tushuntirgan. O‘quvchi qiziqsa, u haqida qo‘shimcha manbalar: [CG - Lecture 4, parts 4 and 5](https://youtu.be/5dfc355t2y4) va [Petr Mitrichev blogi (quyidagi mashq masalalari ro‘yxatidagi eng qiyin masalaning yechimini o‘z ichiga oladi)](https://petr-mitrichev.blogspot.com/2016/07/a-half-plane-week.html).

## Mashq masalalari {#practice-problems}

### Klassik masalalar, bevosita qo‘llash {#classic-problems-direct-application}

* [Codechef - Animesh decides to settle down](https://www.codechef.com/problems/CHN02)
* [POJ - How I mathematician Wonder What You Are!](http://poj.org/problem?id=3130)
* [POJ - Rotating Scoreboard](http://poj.org/problem?id=3335)
* [POJ - Video Surveillance](http://poj.org/problem?id=1474)
* [POJ - Art Gallery](http://poj.org/problem?id=1279)
* [POJ - Uyuw's Concert](http://poj.org/problem?id=2451)

### Qiyinroq masalalar {#harder-problems}

* [POJ - Most Distant Point from the Sea - Medium](http://poj.org/problem?id=3525)
* [Baekjoon - Jeju's Island - Same as above but seemingly stronger test cases](https://www.acmicpc.net/problem/3903)
* [POJ - Feng Shui - Medium](http://poj.org/problem?id=3384)
* [POJ - Triathlon - Medium/hard](http://poj.org/problem?id=1755)
* [DMOJ - Arrow - Medium/hard](https://dmoj.ca/problem/ccoprep3p3)
* [POJ - Jungle Outpost - Hard](http://poj.org/problem?id=3968)
* [Codeforces - Jungle Outpost (alternative link, problem J) - Hard](https://codeforces.com/gym/101309/attachments?mobile=false)
* [Yandex - Asymmetry Value (need virtual contest to see, problem F) - Very Hard](https://contest.yandex.com/contest/2540/enter/)

### Qo‘shimcha masalalar {#additional-problems}

* 40th Petrozavodsk Programming Camp, Winter 2021 - Day 1: Jagiellonian U Contest, Grand Prix of Krakow - Problem B: (Almost) Fair Cake-Cutting. Maqola yozilgan paytda bu masala yopiq edi va faqat Programming Camp ishtirokchilari uchun ochiq edi.

## Havolalar, bibliografiya va boshqa manbalar {#references-bibliography-and-other-sources}

### Asosiy manbalar {#main-sources}

* [New Algorithm for Half-plane Intersection and its Practical Value.](http://people.csail.mit.edu/zeyuan/publications.htm) Algoritmning asl maqolasi.
* [Artem Vasilyev's Brazilian ICPC Summer School 2020 lecture.](https://youtu.be/WKyZSitpm6M?t=6463) Yarim tekisliklar kesishmasi haqidagi ajoyib ma’ruza. Boshqa geometriya mavzularini ham qamrab oladi.

### Yaxshi bloglar (xitoy tilida) {#good-blogs-chinese}

* [Fundamentals of Computational Geometry - Intersection of Half-planes.](https://zhuanlan.zhihu.com/p/83499723)
* [Detailed introduction to the half-plane intersection algorithm.](https://blog.csdn.net/qq_40861916/article/details/83541403)
* [Summary of Half-plane intersection problems.](https://blog.csdn.net/qq_40482358/article/details/87921815)
* [Sorting incremental method of half-plane intersection.](https://blog.csdn.net/u012061345/article/details/23872929)

### Randomizatsiyalangan algoritm {#randomized-algorithm}

* [Linear Programming and Half-Plane intersection - Parts 4 and 5.](https://youtu.be/5dfc355t2y4)
* [Petr Mitrichev's Blog: A half-plane week.](https://petr-mitrichev.blogspot.com/2016/07/a-half-plane-week.html)
