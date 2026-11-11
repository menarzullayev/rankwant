# Kesishuvchi kesmalar juftini topish

Tekislikda $n$ ta kesma berilgan. Ulardan kamida ikkitasi bir-biri bilan kesishishini tekshirish talab qilinadi.
Javob "ha" bo‘lsa, kesishuvchi shu juftni chiqarish kerak; bir nechta javob orasidan istalgan bittasini tanlash yetarli.

Sodda yechim algoritmi barcha kesmalar juftini $O(n^2)$ vaqtda ko‘rib chiqib, har bir juft uchun ularning kesishish-kesishmasligini tekshirishdan iborat. Ushbu maqolada **supuruvchi chiziq algoritmi**ga asoslangan, ishlash vaqti $O(n \log n)$ bo‘lgan algoritm bayon qilinadi.

## Algoritm

Aqlan $x = -\infty$ vertikal chiziqni chizamiz va uni o‘ng tomonga siljita boshlaymiz.
Harakat davomida bu chiziq kesmalarga duch keladi va kesma chiziqni kesib o‘tadigan har bir vaqtda u chiziq bilan aynan bitta nuqtada kesishadi (vertikal kesmalar yo‘q deb hisoblaymiz).

  ![supuruvchi chiziq va kesmalarning kesishishi](/algorithms-media/geometry/sweep_line_1.png)

Shunday qilib, har bir kesma uchun qaysidir vaqtda uning nuqtasi supuruvchi chiziqda paydo bo‘ladi, so‘ng chiziq harakatlanishi bilan bu nuqta siljiydi va nihoyat, qaysidir paytda kesma chiziqdan yo‘qoladi.

Bizni vertikal bo‘yicha **kesmalarning nisbiy tartibi** qiziqtiradi.
Ya’ni, berilgan vaqtda supuruvchi chiziqni kesib o‘tuvchi kesmalar ro‘yxatini saqlaymiz; bunda kesmalar supuruvchi chiziqdagi $y$ koordinatasi bo‘yicha tartiblangan bo‘ladi.

  ![kesmalarning supuruvchi chiziq bo‘yicha nisbiy tartibi](/algorithms-media/geometry/sweep_line_2.png)

Bu tartib qiziq, chunki kesishuvchi kesmalar kamida bir paytda bir xil $y$ koordinataga ega bo‘ladi:

  ![kesishish nuqtasida y koordinatalar bir xil](/algorithms-media/geometry/sweep_line_3.png)

Asosiy tasdiqlarni shakllantiramiz:

  - Kesishuvchi juftni topish uchun supuruvchi chiziqning har bir qayd etilgan holatida **faqat qo‘shni kesmalarni** ko‘rib chiqish yetarli.
  - Supuruvchi chiziqni barcha mumkin bo‘lgan haqiqiy holatlarda $(-\infty \ldots +\infty)$ emas, balki **faqat yangi kesmalar paydo bo‘ladigan yoki eskilari yo‘qoladigan holatlardagina** ko‘rib chiqish yetarli. Boshqacha aytganda, o‘zimizni faqat kesmalar uchlarining abssissalariga teng holatlar bilan cheklash kifoya.
  - Yangi kesma paydo bo‘lganda uni oldingi supuruvchi chiziq uchun olingan ro‘yxatdagi kerakli joyga **qo‘shish** yetarli. Faqat **qo‘shilgan kesmaning ro‘yxatdagi yuqori va pastki bevosita qo‘shnilari bilan** kesishishini tekshirish kerak.
  - Kesma yo‘qolsa, uni joriy ro‘yxatdan **o‘chirish** yetarli. Shundan so‘ng **ro‘yxatdagi yuqori va pastki qo‘shnilarning kesishishini tekshirish** zarur.
  - Kesmalar ro‘yxatida tasvirlanganlardan boshqa o‘zgarishlar bo‘lmaydi. Boshqa kesishish tekshiruvlari talab qilinmaydi.

Bu tasdiqlarning to‘g‘riligini tushunish uchun quyidagi mulohazalar yetarli:

  - Kesishmaydigan ikki kesma o‘zining **nisbiy tartibini** hech qachon o‘zgartirmaydi.
    Haqiqatan, agar bir kesma avval ikkinchisidan yuqorida bo‘lib, keyin pastda bo‘lib qolgan bo‘lsa, bu ikki lahza orasida shu ikki kesmaning kesishishi bo‘lgan.
  - Kesishmaydigan ikki kesma bir xil $y$ koordinataga ham ega bo‘la olmaydi.
  - Bundan kelib chiqadiki, kesma paydo bo‘lgan paytda navbatdan unga joy topish mumkin va bu kesmani navbatda boshqa qayta joylashtirishga hojat qolmaydi: **uning navbatdagi boshqa kesmalarga nisbatan tartibi o‘zgarmaydi**.
  - Ikki kesishuvchi kesma kesishish nuqtasi paytida navbatda bir-biriga qo‘shni bo‘ladi.
  - Shuning uchun kesishuvchi kesmalar juftlarini topish uchun supuruvchi chiziq harakati davomida kamida bir marta bir-biriga qo‘shni bo‘lgan barcha va faqat shunday juftlarning kesishishini tekshirish yetarli.
    Qo‘shilgan kesmani faqat uning yuqori va pastki qo‘shnilari bilan, kesmani o‘chirishda esa uning yuqori va pastki qo‘shnilarini (ular o‘chirishdan keyin bir-biriga qo‘shni bo‘ladi) tekshirish yetarli ekanini payqash oson.
  - Shuni ta’kidlash kerakki, supuruvchi chiziqning qayd etilgan holatida avval shu x koordinatadan **boshlanadigan barcha kesmalarni qo‘shish**, va faqat **keyin** bu yerda tugaydigan **barcha kesmalarni o‘chirish** kerak.
    Shunday qilib, uchdagi kesishishlarni, ya’ni ikki kesma umumiy uchga ega bo‘lgan holatlarni o‘tkazib yubormaymiz.
  - E’tibor bering, **vertikal kesmalar** algoritmning to‘g‘riligiga aslida ta’sir qilmaydi.
    Bu kesmalar bir vaqtning o‘zida paydo bo‘lishi va yo‘qolishi bilan ajralib turadi. Biroq oldingi izohga ko‘ra, barcha kesmalar avval navbatga qo‘shilishini, va faqat keyin o‘chirilishini bilamiz. Shuning uchun vertikal kesma shu paytda ochiq bo‘lgan boshqa kesma bilan (shu jumladan vertikal kesma bilan) kesishsa, bu aniqlanadi.
    **Vertikal kesmalarni navbatning qaysi joyiga qo‘yish kerak?** Axir vertikal kesma bitta aniq $y$ koordinataga ega emas, u $y$ o‘qi bo‘ylab butun bir kesma bo‘ylab cho‘zilgan. Biroq bu kesmaning istalgan koordinatasini $y$ koordinata sifatida olish mumkinligini tushunish oson.

Shunday qilib, butun algoritm kesmalar juftining kesishishi bo‘yicha $2n$ tadan ko‘p bo‘lmagan tekshiruv bajaradi va kesmalar navbati bilan $O(n)$ ta amal bajaradi (har bir kesma paydo bo‘lishi va yo‘qolishi paytida $O(1)$ ta amal).

Natijada **algoritmning asimptotik ishlash vaqti** $O(n \log n)$ bo‘ladi.

## Implementatsiya

Tasvirlangan algoritmning to‘liq implementatsiyasini keltiramiz:

```cpp
const double EPS = 1E-9;

struct pt {
    double x, y;
};

struct seg {
    pt p, q;
    int id;

    double get_y(double x) const {
        if (abs(p.x - q.x) < EPS)
            return p.y;
        return p.y + (q.y - p.y) * (x - p.x) / (q.x - p.x);
    }
};

bool intersect1d(double l1, double r1, double l2, double r2) {
    if (l1 > r1)
        swap(l1, r1);
    if (l2 > r2)
        swap(l2, r2);
    return max(l1, l2) <= min(r1, r2) + EPS;
}

int vec(const pt& a, const pt& b, const pt& c) {
    double s = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
    return abs(s) < EPS ? 0 : s > 0 ? +1 : -1;
}

bool intersect(const seg& a, const seg& b)
{
    return intersect1d(a.p.x, a.q.x, b.p.x, b.q.x) &&
           intersect1d(a.p.y, a.q.y, b.p.y, b.q.y) &&
           vec(a.p, a.q, b.p) * vec(a.p, a.q, b.q) <= 0 &&
           vec(b.p, b.q, a.p) * vec(b.p, b.q, a.q) <= 0;
}

bool operator<(const seg& a, const seg& b)
{
    double x = max(min(a.p.x, a.q.x), min(b.p.x, b.q.x));
    return a.get_y(x) < b.get_y(x) - EPS;
}

struct event {
    double x;
    int tp, id;

    event() {}
    event(double x, int tp, int id) : x(x), tp(tp), id(id) {}

    bool operator<(const event& e) const {
        if (abs(x - e.x) > EPS)
            return x < e.x;
        return tp > e.tp;
    }
};

set<seg> s;
vector<set<seg>::iterator> where;

set<seg>::iterator prev(set<seg>::iterator it) {
    return it == s.begin() ? s.end() : --it;
}

set<seg>::iterator next(set<seg>::iterator it) {
    return ++it;
}

pair<int, int> solve(const vector<seg>& a) {
    int n = (int)a.size();
    vector<event> e;
    for (int i = 0; i < n; ++i) {
        e.push_back(event(min(a[i].p.x, a[i].q.x), +1, i));
        e.push_back(event(max(a[i].p.x, a[i].q.x), -1, i));
    }
    sort(e.begin(), e.end());

    s.clear();
    where.resize(a.size());
    for (size_t i = 0; i < e.size(); ++i) {
        int id = e[i].id;
        if (e[i].tp == +1) {
            set<seg>::iterator nxt = s.lower_bound(a[id]), prv = prev(nxt);
            if (nxt != s.end() && intersect(*nxt, a[id]))
                return make_pair(nxt->id, id);
            if (prv != s.end() && intersect(*prv, a[id]))
                return make_pair(prv->id, id);
            where[id] = s.insert(nxt, a[id]);
        } else {
            set<seg>::iterator nxt = next(where[id]), prv = prev(where[id]);
            if (nxt != s.end() && prv != s.end() && intersect(*nxt, *prv))
                return make_pair(prv->id, nxt->id);
            s.erase(where[id]);
        }
    }

    return make_pair(-1, -1);
}
```

Bu yerdagi asosiy funksiya `solve()` bo‘lib, u kesishuvchi kesmalar mavjud bo‘lsa, ularni, kesishmalar bo‘lmasa $(-1, -1)$ ni qaytaradi.

Ikki kesmaning kesishishini tekshirish `intersect ()` funksiyasi orqali amalga oshiriladi; u **uchburchakning yo‘naltirilgan yuziga asoslangan algoritm**dan foydalanadi.

Kesmalar navbati — `s` global o‘zgaruvchisi, ya’ni `set<seg>`. Navbatdagi har bir kesmaning o‘rnini ko‘rsatuvchi iteratorlar (kesmalarni navbatdan qulay o‘chirish uchun) `where` global massivida saqlanadi.

Shuningdek, oldingi va keyingi elementlarga iteratorlarni qaytaradigan (yoki ular mavjud bo‘lmasa, `end()` ni qaytaradigan) ikkita yordamchi funksiya `prev()` va `next()` kiritilgan.

`EPS` konstantasi ikki haqiqiy sonni solishtirishdagi xatolikni bildiradi (u asosan ikki kesmaning kesishishini tekshirishda ishlatiladi).

## Mashq masalalari
 * [TIMUS 1469 No Smoking!](https://acm.timus.ru/problem.aspx?space=1&num=1469)
