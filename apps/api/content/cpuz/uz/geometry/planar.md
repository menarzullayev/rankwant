# Tekis graf yuzlarini topish {#finding-faces-of-a-planar-graph}

$n$ ta tugun va $m$ ta qirraga ega $G$ graf berilgan bo‘lsin. Uni tekislikda ikki qirra faqat umumiy tugunda (agar u mavjud bo‘lsa) kesishadigan qilib chizish mumkin. Bunday graflar **tekis** (planar) deyiladi. Endi bizga tekis graf uning to‘g‘ri chiziqli joylashtirilishi bilan birga berilgan deylik. Bu har bir $v$ tugun uchun unga mos $(x, y)$ nuqta berilganini va barcha qirralar shu nuqtalar orasidagi kesmalar ko‘rinishida kesishmasdan chizilganini bildiradi (bunday joylashtirish doim mavjud). Bu kesmalar tekislikni yuz deb ataladigan bir nechta sohaga bo‘ladi. Yuzlardan aynan bittasi chegaralanmagan. Bu yuz **tashqi** yuz deyiladi, qolganlari esa **ichki** yuzlardir.

Ushbu maqolada tekis grafning ham ichki, ham tashqi yuzlarini topish bilan shug‘ullanamiz. Graf bog‘langan deb faraz qilamiz.

## Tekis graflar haqida ba’zi faktlar {#some-facts-about-planar-graphs}

Bu bo‘limda tekis graflar haqidagi bir nechta faktni isbotsiz keltiramiz. Isbotlar bilan qiziqqan o‘quvchilar [R. Diestelning «Graph Theory»](https://www.math.uni-hamburg.de/home/diestel/books/graph.theory/preview/Ch4.pdf) kitobiga (shuningdek, shu kitobga asoslangan [planarlik bo‘yicha video darslarga](https://www.youtube.com/@DiestelGraphTheory)) yoki boshqa biror kitobga murojaat qilishi mumkin.

### Eyler teoremasi {#eulers-theorem}

Eyler teoremasiga ko‘ra, $n$ ta tugun, $m$ ta qirra va $f$ ta yuzga ega bog‘langan tekis grafning har qanday to‘g‘ri joylashtirilishi uchun quyidagi tenglik bajariladi:

$$n - m + f = 2$$

Umumiyroq holda, $k$ ta bog‘langan komponentli har qanday tekis graf uchun:

$$n - m + f = 1 + k$$

### Tekis grafdagi qirralar soni {#number-of-edges-of-a-planar-graph}

Agar $n \ge 3$ bo‘lsa, $n$ ta tugunli tekis grafdagi qirralarning maksimal soni $3n - 6$ ga teng. Bu songa har bir yuzi uchburchak bilan chegaralangan istalgan bog‘langan tekis grafda erishiladi. Murakkablik nuqtayi nazaridan bu fakt har qanday tekis graf uchun $m = O(n)$ ekanini bildiradi.

### Tekis grafdagi yuzlar soni {#number-of-faces-of-a-planar-graph}

Yuqoridagi faktning bevosita natijasi sifatida, agar $n \ge 3$ bo‘lsa, $n$ ta tugunli tekis grafdagi yuzlarning maksimal soni $2n - 4$ ga teng.

### Tekis grafdagi minimal tugun darajasi {#minimum-vertex-degree-in-a-planar-graph}

Har bir tekis grafda darajasi 5 yoki undan kichik bo‘lgan tugun mavjud.

## Algoritm {#the-algorithm}

Avval har bir tugun uchun unga qo‘shni qirralarni qutb burchagi bo‘yicha saralaymiz.
Endi grafni quyidagicha aylanib chiqamiz. Faraz qilaylik, biz $u$ tugunga $(v, u)$ qirra orqali kirdik va $(u, w)$ qirra $u$ ning saralangan qo‘shnilik ro‘yxatida $(v, u)$ dan keyingi qirra bo‘lsin. Unda keyingi tugun $w$ bo‘ladi. Ma’lum bo‘lishicha, agar bu aylanishni biror $(v, u)$ qirradan boshlasak, $(v, u)$ ga qo‘shni yuzlardan aynan birini aylanib chiqamiz; qaysi yuz ekani birinchi qadamimiz $u$ dan $v$ ga yoki $v$ dan $u$ ga qarab qilinishiga bog‘liq.

Endi algoritm ancha ravshan. Grafning barcha qirralari bo‘ylab yurib, oldingi aylanishlarning birortasida ko‘rilmagan har bir qirra uchun aylanishni boshlashimiz kerak. Shu yo‘l bilan har bir yuz aynan bir marta topiladi, har bir qirra esa ikki marta (har bir yo‘nalishda bir martadan) o‘tiladi.

### Keyingi qirrani topish {#finding-the-next-edge}

Aylanish vaqtida soat miliga teskari tartibdagi keyingi qirrani topishimiz kerak. Keyingi qirrani topishning eng ravshan usuli — burchak bo‘yicha ikkilik qidiruv. Biroq har bir tugun uchun qo‘shni qirralarning soat miliga teskari tartibi ma’lum bo‘lgani uchun, keyingi qirralarni oldindan hisoblab, xesh jadvalida saqlashimiz mumkin. Agar qirralar burchak bo‘yicha allaqachon saralangan bo‘lsa, bu holda barcha yuzlarni topish murakkabligi chiziqli bo‘ladi.

### Tashqi yuzni topish {#finding-the-outer-face}

Algoritm har bir ichki yuzni soat mili bo‘ylab, tashqi yuzni esa soat miliga teskari tartibda aylanib chiqishini ko‘rish qiyin emas, shuning uchun tashqi yuzni har bir yuzning aylanish tartibini tekshirib topish mumkin.

### Murakkablik {#complexity}

Algoritmning murakkabligi saralash sababli $O(m \log m)$ ekani ancha ravshan, $m = O(n)$ bo‘lgani uchun esa u aslida $O(n \log n)$ dir. Yuqorida aytilganidek, saralashsiz murakkablik $O(n)$ bo‘ladi.

## Graf bog‘lanmagan bo‘lsa-chi? {#what-if-the-graph-isnt-connected}

Dastlabki qarashda bog‘lanmagan grafning yuzlarini topish unchalik qiyin emasdek tuyulishi mumkin, chunki har bir bog‘langan komponent uchun xuddi shu algoritmni ishga tushirish mumkin. Biroq komponentlar bir-birining ichida joylashgan bo‘lishi va **teshiklar** hosil qilishi mumkin (quyidagi rasmga qarang). Bu holda biror komponentning ichki yuzi boshqa komponentlarning tashqi yuziga aylanadi va murakkab, bog‘lanmagan chegaraga ega bo‘ladi. Bunday holatlar bilan ishlash ancha qiyin; mumkin bo‘lgan yondashuvlardan biri — ichma-ich joylashgan komponentlarni [nuqtaning joylashuvini aniqlash](/algorithms/geometry/point-location) algoritmlari yordamida aniqlash.

  ![Teshikli tekis graf](/algorithms-media/geometry/planar_hole.png)

## Implementatsiya {#implementation}

Quyidagi implementatsiya har bir yuz uchun tugunlar vektorini qaytaradi, tashqi yuz birinchi turadi.
Ichki yuzlar soat miliga teskari tartibda, tashqi yuz esa soat mili bo‘ylab tartibda qaytariladi.

Soddalik uchun keyingi qirrani burchak bo‘yicha ikkilik qidiruv orqali topamiz.

```cpp
struct Point {
    int64_t x, y;

    Point(int64_t x_, int64_t y_): x(x_), y(y_) {}

    Point operator - (const Point & p) const {
        return Point(x - p.x, y - p.y);
    }

    int64_t cross (const Point & p) const {
        return x * p.y - y * p.x;
    }

    int64_t cross (const Point & p, const Point & q) const {
        return (p - *this).cross(q - *this);
    }

    int half () const {
        return int(y < 0 || (y == 0 && x < 0));
    }
};

std::vector<std::vector<size_t>> find_faces(std::vector<Point> vertices, std::vector<std::vector<size_t>> adj) {
    size_t n = vertices.size();
    std::vector<std::vector<char>> used(n);
    for (size_t i = 0; i < n; i++) {
        used[i].resize(adj[i].size());
        used[i].assign(adj[i].size(), 0);
        auto compare = [&](size_t l, size_t r) {
            Point pl = vertices[l] - vertices[i];
            Point pr = vertices[r] - vertices[i];
            if (pl.half() != pr.half())
                return pl.half() < pr.half();
            return pl.cross(pr) > 0;
        };
        std::sort(adj[i].begin(), adj[i].end(), compare);
    }
    std::vector<std::vector<size_t>> faces;
    for (size_t i = 0; i < n; i++) {
        for (size_t edge_id = 0; edge_id < adj[i].size(); edge_id++) {
            if (used[i][edge_id]) {
                continue;
            }
            std::vector<size_t> face;
            size_t v = i;
            size_t e = edge_id;
            while (!used[v][e]) {
                used[v][e] = true;
                face.push_back(v);
                size_t u = adj[v][e];
                size_t e1 = std::lower_bound(adj[u].begin(), adj[u].end(), v, [&](size_t l, size_t r) {
                    Point pl = vertices[l] - vertices[u];
                    Point pr = vertices[r] - vertices[u];
                    if (pl.half() != pr.half())
                        return pl.half() < pr.half();
                    return pl.cross(pr) > 0;
                }) - adj[u].begin() + 1;
                if (e1 == adj[u].size()) {
                    e1 = 0;
                }
                v = u;
                e = e1;
            }
            std::reverse(face.begin(), face.end());
            Point p1 = vertices[face[0]];
            __int128 sum = 0;
            for (int j = 0; j < face.size(); ++j) {
                Point p2 = vertices[face[j]];
                Point p3 = vertices[face[(j + 1) % face.size()]];
                sum += (p2 - p1).cross(p3 - p2);
            }
            if (sum <= 0) {
                faces.insert(faces.begin(), face);
            } else {
                faces.emplace_back(face);
            }
        }
    }
    return faces;
}
```

## Kesmalardan tekis graf qurish {#building-planar-graph-from-line-segments}

Ba’zan graf sizga aniq berilmaydi, balki tekislikdagi kesmalar to‘plami sifatida beriladi va haqiqiy graf shu kesmalarning kesishishidan hosil bo‘ladi (quyidagi rasmga qarang). Bu holda grafni o‘zingiz qurishingiz kerak. Buning eng oson yo‘li quyidagicha. Biror kesmani tanlaymiz va uni qolgan barcha kesmalar bilan kesishtiramiz. So‘ng barcha kesishish nuqtalarini kesmaning ikki uchi bilan birga leksikografik tartibda saralab, grafga tugun sifatida qo‘shamiz. Shuningdek, leksikografik tartibda har ikki qo‘shni tugunni qirra bilan bog‘laymiz. Bu amalni barcha kesmalar uchun bajargach, graf hosil bo‘ladi. Albatta, ikkita bir xil kesishish nuqtasi doim bitta tugunga mos kelishini ta’minlashimiz kerak. Buning eng oson yo‘li — nuqtalarni koordinatalari bo‘yicha map da saqlash va koordinatalari kichik songa (masalan, $10^{-9}$ dan kam) farq qiladigan nuqtalarni teng deb hisoblash. Bu algoritm $O(n^2 \log n)$ vaqtda ishlaydi.

  ![Bilvosita berilgan graf](/algorithms-media/geometry/planar_implicit.png)

## Implementatsiya {#implementation}

```cpp
using dbl = long double;

const dbl eps = 1e-9;

struct Point {
    dbl x, y;

    Point(){}
    Point(dbl x_, dbl y_): x(x_), y(y_) {}

    Point operator * (dbl d) const {
        return Point(x * d, y * d);
    }

    Point operator + (const Point & p) const {
        return Point(x + p.x, y + p.y);
    }

    Point operator - (const Point & p) const {
        return Point(x - p.x, y - p.y);
    }

    dbl cross (const Point & p) const {
        return x * p.y - y * p.x;
    }

    dbl cross (const Point & p, const Point & q) const {
        return (p - *this).cross(q - *this);
    }

    dbl dot (const Point & p) const {
        return x * p.x + y * p.y;
    }

    dbl dot (const Point & p, const Point & q) const {
        return (p - *this).dot(q - *this);
    }

    bool operator < (const Point & p) const {
        if (fabs(x - p.x) < eps) {
            if (fabs(y - p.y) < eps) {
                return false;
            } else {
                return y < p.y;
            }
        } else {
            return x < p.x;
        }
    }

    bool operator == (const Point & p) const {
        return fabs(x - p.x) < eps && fabs(y - p.y) < eps;
    }

    bool operator >= (const Point & p) const {
        return !(*this < p);
    }
};

struct Line{
	Point p[2];

	Line(Point l, Point r){p[0] = l; p[1] = r;}
	Point& operator [](const int & i){return p[i];}
	const Point& operator[](const int & i)const{return p[i];}
	Line(const Line & l){
		p[0] = l.p[0]; p[1] = l.p[1];
	}
	Point getOrth()const{
		return Point(p[1].y - p[0].y, p[0].x - p[1].x);
	}
	bool hasPointLine(const Point & t)const{
		return std::fabs(p[0].cross(p[1], t)) < eps;
	}
	bool hasPointSeg(const Point & t)const{
		return hasPointLine(t) && t.dot(p[0], p[1]) < eps;
	}
};

std::vector<Point> interLineLine(Line l1, Line l2){
	if(std::fabs(l1.getOrth().cross(l2.getOrth())) < eps){
		if(l1.hasPointLine(l2[0]))return {l1[0], l1[1]};
		else return {};
	}
	Point u = l2[1] - l2[0];
	Point v = l1[1] - l1[0];
	dbl s = u.cross(l2[0] - l1[0])/u.cross(v);
	return {Point(l1[0] + v * s)};
}

std::vector<Point> interSegSeg(Line l1, Line l2){
	if (l1[0] == l1[1]) {
		if (l2[0] == l2[1]) {
			if (l1[0] == l2[0])
                return {l1[0]};
			else 
                return {};
		} else {
			if (l2.hasPointSeg(l1[0]))
                return {l1[0]};
			else
                return {};
		}
	}
	if (l2[0] == l2[1]) {
		if (l1.hasPointSeg(l2[0]))
            return {l2[0]};
		else 
            return {};
	}
	auto li = interLineLine(l1, l2);
	if (li.empty())
        return li;
	if (li.size() == 2) {
		if (l1[0] >= l1[1])
            std::swap(l1[0], l1[1]);
		if (l2[0] >= l2[1])
            std::swap(l2[0], l2[1]);
        std::vector<Point> res(2);
		if (l1[0] < l2[0])
            res[0] = l2[0];
        else
            res[0] = l1[0];
		if (l1[1] < l2[1])
            res[1] = l1[1];
        else
            res[1] = l2[1];
		if (res[0] == res[1])
            res.pop_back();
		if (res.size() == 2u && res[1] < res[0])
            return {};
		else 
            return res;
	}
	Point cand = li[0];
	if (l1.hasPointSeg(cand) && l2.hasPointSeg(cand))
        return {cand};
	else 
        return {};
}

std::pair<std::vector<Point>, std::vector<std::vector<size_t>>> build_graph(std::vector<Line> segments) {
    std::vector<Point> p;
    std::vector<std::vector<size_t>> adj;
    std::map<std::pair<int64_t, int64_t>, size_t> point_id;
    auto get_point_id = [&](Point pt) {
        auto repr = std::make_pair(
            int64_t(std::round(pt.x * 1000000000) + 1e-6),
            int64_t(std::round(pt.y * 1000000000) + 1e-6)
        );
        if (!point_id.count(repr)) {
            adj.emplace_back();
            size_t id = point_id.size();
            point_id[repr] = id;
            p.push_back(pt);
            return id;
        } else {
            return point_id[repr];
        }
    };
    for (size_t i = 0; i < segments.size(); i++) {
        std::vector<size_t> curr = {
            get_point_id(segments[i][0]),
            get_point_id(segments[i][1])
        };
        for (size_t j = 0; j < segments.size(); j++) {
            if (i == j)
                continue;
            auto inter = interSegSeg(segments[i], segments[j]);
            for (auto pt: inter) {
                curr.push_back(get_point_id(pt));
            }
        }
        std::sort(curr.begin(), curr.end(), [&](size_t l, size_t r) { return p[l] < p[r]; });
        curr.erase(std::unique(curr.begin(), curr.end()), curr.end());
        for (size_t j = 0; j + 1 < curr.size(); j++) {
            adj[curr[j]].push_back(curr[j + 1]);
            adj[curr[j + 1]].push_back(curr[j]);
        }
    }
    for (size_t i = 0; i < adj.size(); i++) {
        std::sort(adj[i].begin(), adj[i].end());
        // bir necha marta qo‘shilgan qirralarni olib tashlaymiz
        adj[i].erase(std::unique(adj[i].begin(), adj[i].end()), adj[i].end());
    }
    return {p, adj};
}
```

## Masalalar {#problems}

 * [TIMUS 1664 Pipeline Transportation](https://acm.timus.ru/problem.aspx?space=1&num=1664)
 * [TIMUS 1681 Brother Bear's Garden](https://acm.timus.ru/problem.aspx?space=1&num=1681)
