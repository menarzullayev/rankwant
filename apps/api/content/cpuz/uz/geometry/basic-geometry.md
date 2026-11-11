# Geometriya asoslari {#basic-geometry}

Ushbu maqolada butun analitik geometriyaning asosini tashkil qiladigan Evklid fazosidagi nuqtalar ustida bajariladigan asosiy amallarni ko‘rib chiqamiz.
Har bir $\mathbf r$ nuqta uchun $\mathbf 0$ dan $\mathbf r$ ga yo‘nalgan $\vec{\mathbf r}$ vektorni qaraymiz.
Keyinchalik $\mathbf r$ va $\vec{\mathbf r}$ ni farqlamaymiz va **nuqta** atamasini **vektor** atamasining sinonimi sifatida ishlatamiz.

## Chiziqli amallar {#linear-operations}

Ikki o‘lchamli ham, uch o‘lchamli ham nuqtalar chiziqli fazo tashkil qiladi; bu ular uchun nuqtalar yig‘indisi va nuqtani biror songa ko‘paytirish amallari aniqlanganini bildiradi. Ikki o‘lchamli holat uchun ularning asosiy implementatsiyalari quyidagicha:

```cpp
struct point2d {
    ftype x, y;
    point2d() {}
    point2d(ftype x, ftype y): x(x), y(y) {}
    point2d& operator+=(const point2d &t) {
        x += t.x;
        y += t.y;
        return *this;
    }
    point2d& operator-=(const point2d &t) {
        x -= t.x;
        y -= t.y;
        return *this;
    }
    point2d& operator*=(ftype t) {
        x *= t;
        y *= t;
        return *this;
    }
    point2d& operator/=(ftype t) {
        x /= t;
        y /= t;
        return *this;
    }
    point2d operator+(const point2d &t) const {
        return point2d(*this) += t;
    }
    point2d operator-(const point2d &t) const {
        return point2d(*this) -= t;
    }
    point2d operator*(ftype t) const {
        return point2d(*this) *= t;
    }
    point2d operator/(ftype t) const {
        return point2d(*this) /= t;
    }
};
point2d operator*(ftype a, point2d b) {
    return b * a;
}
```
Uch o‘lchamli nuqtalar:
```cpp
struct point3d {
    ftype x, y, z;
    point3d() {}
    point3d(ftype x, ftype y, ftype z): x(x), y(y), z(z) {}
    point3d& operator+=(const point3d &t) {
        x += t.x;
        y += t.y;
        z += t.z;
        return *this;
    }
    point3d& operator-=(const point3d &t) {
        x -= t.x;
        y -= t.y;
        z -= t.z;
        return *this;
    }
    point3d& operator*=(ftype t) {
        x *= t;
        y *= t;
        z *= t;
        return *this;
    }
    point3d& operator/=(ftype t) {
        x /= t;
        y /= t;
        z /= t;
        return *this;
    }
    point3d operator+(const point3d &t) const {
        return point3d(*this) += t;
    }
    point3d operator-(const point3d &t) const {
        return point3d(*this) -= t;
    }
    point3d operator*(ftype t) const {
        return point3d(*this) *= t;
    }
    point3d operator/(ftype t) const {
        return point3d(*this) /= t;
    }
};
point3d operator*(ftype a, point3d b) {
    return b * a;
}
```

Bu yerda `ftype` koordinatalar uchun ishlatiladigan biror tur bo‘lib, odatda `int`, `double` yoki `long long` bo‘ladi.

## Skalyar ko‘paytma {#dot-product}

### Ta’rif {#definition}
$\mathbf a$ va $\mathbf b$ vektorlarning skalyar ko‘paytmasi $\mathbf a \cdot \mathbf b$ ni ikki teng kuchli usulda ta’riflash mumkin.
Geometrik jihatdan u birinchi vektor uzunligining ikkinchi vektorning birinchi vektorga proyeksiyasi uzunligiga ko‘paytmasidir.
Quyidagi rasmdan ko‘rinib turibdiki, bu proyeksiya aynan $|\mathbf a| \cos \theta$ ga teng, bunda $\theta$ — $\mathbf a$ va $\mathbf b$ orasidagi burchak. Demak, $\mathbf a\cdot  \mathbf b = |\mathbf a| \cos \theta \cdot |\mathbf b|$.

  ![](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Dot_Product.svg/300px-Dot_Product.svg.png)

Skalyar ko‘paytma bir nechta diqqatga sazovor xossalarga ega:

1. $\mathbf a \cdot \mathbf b = \mathbf b \cdot \mathbf a$
2. $(\alpha \cdot \mathbf a)\cdot \mathbf b = \alpha \cdot (\mathbf a \cdot \mathbf b)$
3. $(\mathbf a + \mathbf b)\cdot \mathbf c = \mathbf a \cdot \mathbf c + \mathbf b \cdot \mathbf c$

Ya’ni u kommutativ funksiya bo‘lib, ikkala argumenti bo‘yicha chiziqlidir.
Birlik vektorlarni quyidagicha belgilaymiz:

$$\mathbf e_x = \begin{pmatrix} 1 \\ 0 \\ 0 \end{pmatrix}, \mathbf e_y = \begin{pmatrix} 0 \\ 1 \\ 0 \end{pmatrix}, \mathbf e_z = \begin{pmatrix} 0 \\ 0 \\ 1 \end{pmatrix}.$$

Bu belgilash bilan $\mathbf r = (x;y;z)$ vektorni $r = x \cdot \mathbf e_x + y \cdot \mathbf e_y + z \cdot \mathbf e_z$ ko‘rinishida yozish mumkin.
Birlik vektorlar uchun

$$\mathbf e_x\cdot \mathbf e_x = \mathbf e_y\cdot \mathbf e_y = \mathbf e_z\cdot \mathbf e_z = 1,\\
\mathbf e_x\cdot \mathbf e_y = \mathbf e_y\cdot \mathbf e_z = \mathbf e_z\cdot \mathbf e_x = 0$$

bo‘lgani uchun, $\mathbf a = (x_1;y_1;z_1)$ va $\mathbf b = (x_2;y_2;z_2)$ vektorlar uchun koordinatalarda quyidagi tenglik o‘rinli ekanini ko‘ramiz:

$$\mathbf a\cdot \mathbf b = (x_1 \cdot \mathbf e_x + y_1 \cdot\mathbf e_y + z_1 \cdot\mathbf e_z)\cdot( x_2 \cdot\mathbf e_x + y_2 \cdot\mathbf e_y + z_2 \cdot\mathbf e_z) = x_1 x_2 + y_1 y_2 + z_1 z_2$$

Bu skalyar ko‘paytmaning algebraik ta’rifidir.
Bundan uni hisoblaydigan funksiyalarni yozish mumkin.

```cpp
ftype dot(point2d a, point2d b) {
    return a.x * b.x + a.y * b.y;
}
ftype dot(point3d a, point3d b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}
```

Masalalarni yechishda skalyar ko‘paytmani hisoblash uchun algebraik ta’rifdan foydalanish kerak, lekin uni qo‘llash uchun geometrik ta’rif va xossalarni yodda tutish lozim.

### Xossalar {#properties}

Skalyar ko‘paytma orqali ko‘plab geometrik xossalarni aniqlash mumkin.
Masalan:

1. $\mathbf a$ ning normasi (uzunlik kvadrati): $|\mathbf a|^2 = \mathbf a\cdot \mathbf a$
2. $\mathbf a$ ning uzunligi: $|\mathbf a| = \sqrt{\mathbf a\cdot \mathbf a}$
3. $\mathbf a$ ning $\mathbf b$ ga proyeksiyasi: $\dfrac{\mathbf a\cdot\mathbf b}{|\mathbf b|}$
4. Vektorlar orasidagi burchak: $\arccos \left(\dfrac{\mathbf a\cdot \mathbf b}{|\mathbf a| \cdot |\mathbf b|}\right)$
5. Oldingi banddan ko‘rinadiki, vektorlar orasidagi burchak o‘tkir bo‘lsa skalyar ko‘paytma musbat, o‘tmas bo‘lsa manfiy, ular ortogonal bo‘lsa, ya’ni to‘g‘ri burchak hosil qilsa, nolga teng bo‘ladi.

E’tibor bering, bu funksiyalarning hech biri o‘lchamlar soniga bog‘liq emas, shuning uchun ular 2D va 3D holatlar uchun bir xil bo‘ladi:

```cpp
ftype norm(point2d a) {
    return dot(a, a);
}
double abs(point2d a) {
    return sqrt(norm(a));
}
double proj(point2d a, point2d b) {
    return dot(a, b) / abs(b);
}
double angle(point2d a, point2d b) {
    return acos(dot(a, b) / abs(a) / abs(b));
}
```

Keyingi muhim xossani ko‘rish uchun biror belgilangan $C$ o‘zgarmas uchun $\mathbf r\cdot \mathbf a = C$ bo‘ladigan $\mathbf r$ nuqtalar to‘plamini qarash kerak.
Bu nuqtalar to‘plami aynan $\mathbf a$ ga proyeksiyasi $C \cdot \dfrac{\mathbf a}{|\mathbf a| ^ 2}$ nuqta bo‘ladigan nuqtalar to‘plamidir va ular $\mathbf a$ ga ortogonal giper tekislikni hosil qiladi.
Quyidagi rasmda $\mathbf a$ vektor va u bilan bir xil skalyar ko‘paytmaga ega bo‘lgan bir nechta shunday vektor 2D da ko‘rsatilgan:

  ![a bilan bir xil skalyar ko‘paytmaga ega vektorlar](https://i.imgur.com/eyO7St4.png)

2D da bu vektorlar to‘g‘ri chiziq, 3D da esa tekislik hosil qiladi.
E’tibor bering, bu natija 2D da to‘g‘ri chiziqni $\mathbf r\cdot \mathbf n=C$ yoki $(\mathbf r - \mathbf r_0)\cdot \mathbf n=0$ ko‘rinishda aniqlash imkonini beradi; bunda $\mathbf n$ — chiziqqa ortogonal vektor, $\mathbf r_0$ — chiziqda allaqachon mavjud istalgan vektor va $C = \mathbf r_0\cdot \mathbf n$.
Xuddi shu tarzda 3D da tekislikni aniqlash mumkin.

## Vektor ko‘paytma {#cross-product}

### Ta’rif {#definition}

Quyidagi rasmdagidek parallelepipedga birlashtirilgan 3D fazodagi uchta $\mathbf a$, $\mathbf b$ va $\mathbf c$ vektor berilgan deylik:

  ![Uchta vektor](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Parallelepiped_volume.svg/250px-Parallelepiped_volume.svg.png)

Uning hajmini qanday hisoblaysiz?
Maktab kursidan bilamizki, asos yuzini balandlikka ko‘paytirish kerak; balandlik esa $\mathbf a$ ning asosga ortogonal yo‘nalishdagi proyeksiyasidir.
Demak, agar $\mathbf b \times \mathbf c$ ni $\mathbf b$ va $\mathbf c$ ning ikkalasiga ortogonal va uzunligi $\mathbf b$ hamda $\mathbf c$ hosil qilgan parallelogramm yuziga teng bo‘lgan vektor deb ta’riflasak, $|\mathbf a\cdot (\mathbf b\times\mathbf c)|$ parallelepiped hajmiga teng bo‘ladi.
Aniqlik uchun $\mathbf b\times \mathbf c$ har doim shunday yo‘naltirilgan deymizki, $\mathbf b\times \mathbf c$ nuqtasidan qaraganda $\mathbf b$ vektordan $\mathbf c$ vektorga burilish doim soat miliga teskari bo‘lsin (quyidagi rasmga qarang).

  ![vektor ko‘paytma](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Cross_product_vector.svg/250px-Cross_product_vector.svg.png)

Bu $\mathbf b$ va $\mathbf c$ vektorlarning vektor ko‘paytmasi $\mathbf b\times \mathbf c$ ni hamda $\mathbf a$, $\mathbf b$ va $\mathbf c$ vektorlarning aralash ko‘paytmasi $\mathbf a\cdot(\mathbf b\times \mathbf c)$ ni aniqlaydi.

Vektor va aralash ko‘paytmalarning diqqatga sazovor xossalari:

1.  $\mathbf a\times \mathbf b = -\mathbf b\times \mathbf a$
2.  $(\alpha \cdot \mathbf a)\times \mathbf b = \alpha \cdot (\mathbf a\times \mathbf b)$
3.  Istalgan $\mathbf b$ va $\mathbf c$ uchun shunday yagona $\mathbf r$ vektor mavjudki, istalgan $\mathbf a$ vektor uchun $\mathbf a\cdot (\mathbf b\times \mathbf c) = \mathbf a\cdot\mathbf r$ bo‘ladi.  Haqiqatan, agar shunday ikkita $\mathbf r_1$ va $\mathbf r_2$ vektor bo‘lsa, barcha $\mathbf a$ vektorlar uchun $\mathbf a\cdot (\mathbf r_1 - \mathbf r_2)=0$ bo‘ladi, bu esa faqat $\mathbf r_1 = \mathbf r_2$ bo‘lgandagina mumkin.
4.  $\mathbf a\cdot (\mathbf b\times \mathbf c) = \mathbf b\cdot (\mathbf c\times \mathbf a) = -\mathbf a\cdot( \mathbf c\times \mathbf b)$
5.  $(\mathbf a + \mathbf b)\times \mathbf c = \mathbf a\times \mathbf c + \mathbf b\times \mathbf c$.
    Haqiqatan, barcha $\mathbf r$ vektorlar uchun quyidagi tengliklar zanjiri o‘rinli:

    $$\mathbf r\cdot( (\mathbf a + \mathbf b)\times \mathbf c) = (\mathbf a + \mathbf b) \cdot (\mathbf c\times \mathbf r) =  \mathbf a \cdot(\mathbf c\times \mathbf r) + \mathbf b\cdot(\mathbf c\times \mathbf r) = \mathbf r\cdot (\mathbf a\times \mathbf c) + \mathbf r\cdot(\mathbf b\times \mathbf c) = \mathbf r\cdot(\mathbf a\times \mathbf c + \mathbf b\times \mathbf c)$$

    Bu 3-bandga ko‘ra $(\mathbf a + \mathbf b)\times \mathbf c = \mathbf a\times \mathbf c + \mathbf b\times \mathbf c$ ekanini isbotlaydi.

6.  $|\mathbf a\times \mathbf b|=|\mathbf a| \cdot |\mathbf b| \sin \theta$, bunda $\theta$ — $\mathbf a$ va $\mathbf b$ orasidagi burchak, chunki $|\mathbf a\times \mathbf b|$ $\mathbf a$ va $\mathbf b$ hosil qilgan parallelogramm yuziga teng.

Bularni va birlik vektorlar uchun quyidagi tenglik o‘rinli ekanini hisobga olsak

$$\mathbf e_x\times \mathbf e_x = \mathbf e_y\times \mathbf e_y = \mathbf e_z\times \mathbf e_z = \mathbf 0,\\
\mathbf e_x\times \mathbf e_y = \mathbf e_z,~\mathbf e_y\times \mathbf e_z = \mathbf e_x,~\mathbf e_z\times \mathbf e_x = \mathbf e_y$$

$\mathbf a = (x_1;y_1;z_1)$ va $\mathbf b = (x_2;y_2;z_2)$ ning vektor ko‘paytmasini koordinata shaklida hisoblashimiz mumkin:

$$\mathbf a\times \mathbf b = (x_1 \cdot \mathbf e_x + y_1 \cdot \mathbf e_y + z_1 \cdot \mathbf e_z)\times (x_2 \cdot \mathbf e_x + y_2 \cdot \mathbf e_y + z_2 \cdot \mathbf e_z) =$$

$$(y_1 z_2 - z_1 y_2)\mathbf e_x  + (z_1 x_2 - x_1 z_2)\mathbf e_y + (x_1 y_2 - y_1 x_2)\mathbf e_z$$

Buni yanada ixcham shaklda ham yozish mumkin:

$$\mathbf a\times \mathbf b = \begin{vmatrix}\mathbf e_x & \mathbf e_y & \mathbf e_z \\ x_1 & y_1 & z_1 \\ x_2 & y_2 & z_2 \end{vmatrix},~a\cdot(b\times c) = \begin{vmatrix} x_1 & y_1 & z_1 \\ x_2 & y_2 & z_2 \\ x_3 & y_3 & z_3 \end{vmatrix}$$

Bu yerda $| \cdot |$ matritsaning determinantini bildiradi.

Vektor ko‘paytmaning qandaydir ko‘rinishi (aynan psevdoskalyar ko‘paytma) 2D holatda ham amalga oshirilishi mumkin.
Agar $\mathbf a$ va $\mathbf b$ vektorlar hosil qilgan parallelogramm yuzini hisoblamoqchi bo‘lsak, $|\mathbf e_z\cdot(\mathbf a\times \mathbf b)| = |x_1 y_2 - y_1 x_2|$ ni hisoblardik.
Xuddi shu natijani olishning yana bir usuli — $|\mathbf a|$ (parallelogramm asosi) ni balandlikka ko‘paytirish; balandlik esa $\mathbf b$ vektorning $90^\circ$ ga burilgan $\mathbf a$ vektorga proyeksiyasi bo‘lib, burilgan vektor $\widehat{\mathbf a}=(-y_1;x_1)$ ga teng.
Ya’ni $|\widehat{\mathbf a}\cdot\mathbf b|=|x_1y_2 - y_1 x_2|$ ni hisoblash kerak.

Ishorani hisobga olsak, $\mathbf a$ dan $\mathbf b$ ga burilish (ya’ni $\mathbf e_z$ nuqtasidan qaraganda) soat miliga teskari bajarilsa yuza musbat, aks holda manfiy bo‘ladi.
Bu psevdoskalyar ko‘paytmani aniqlaydi.
E’tibor bering, u $|\mathbf a| \cdot |\mathbf b| \sin \theta$ ga ham teng, bunda $\theta$ — $\mathbf a$ dan $\mathbf b$ ga soat miliga teskari sanalgan burchak (burilish soat mili bo‘yicha bo‘lsa, manfiy).

Bularning hammasini amalga oshiramiz!

```cpp
point3d cross(point3d a, point3d b) {
    return point3d(a.y * b.z - a.z * b.y,
                   a.z * b.x - a.x * b.z,
                   a.x * b.y - a.y * b.x);
}
ftype triple(point3d a, point3d b, point3d c) {
    return dot(a, cross(b, c));
}
ftype cross(point2d a, point2d b) {
    return a.x * b.y - a.y * b.x;
}
```

### Xossalar {#properties}

Vektor ko‘paytmaga kelsak, u faqat va faqat $\mathbf a$ va $\mathbf b$ vektorlar kollinear bo‘lganda (ular umumiy to‘g‘ri chiziq hosil qiladi, ya’ni parallel) nol vektorga teng.
Aralash ko‘paytma uchun ham xuddi shunday: u faqat va faqat $\mathbf a$, $\mathbf b$ va $\mathbf c$ vektorlar komplanar bo‘lganda (ular umumiy tekislik hosil qiladi) nolga teng.

Bundan to‘g‘ri chiziq va tekisliklarni aniqlovchi universal tenglamalarni olish mumkin.
To‘g‘ri chiziqni uning yo‘naltiruvchi vektori $\mathbf d$ va boshlang‘ich nuqtasi $\mathbf r_0$ orqali yoki ikkita $\mathbf a$ va $\mathbf b$ nuqta orqali aniqlash mumkin.
U $(\mathbf r - \mathbf r_0)\times\mathbf d=0$ yoki $(\mathbf r - \mathbf a)\times (\mathbf b - \mathbf a) = 0$ ko‘rinishda aniqlanadi.
Tekislikni esa uchta $\mathbf a$, $\mathbf b$ va $\mathbf c$ nuqta orqali $(\mathbf r - \mathbf a)\cdot((\mathbf b - \mathbf a)\times (\mathbf c - \mathbf a))=0$ ko‘rinishda yoki boshlang‘ich nuqta $\mathbf r_0$ va shu tekislikda yotuvchi ikkita yo‘naltiruvchi vektor $\mathbf d_1$ va $\mathbf d_2$ orqali aniqlash mumkin: $(\mathbf r - \mathbf r_0)\cdot(\mathbf d_1\times \mathbf d_2)=0$.

2D da psevdoskalyar ko‘paytmadan ikki vektor orasidagi yo‘nalishni (orientatsiyani) tekshirish uchun ham foydalanish mumkin, chunki birinchi vektordan ikkinchisiga burilish soat miliga teskari bo‘lsa u musbat, aks holda manfiy bo‘ladi.
Va, albatta, undan ko‘pburchaklar yuzini hisoblash uchun foydalanish mumkin; bu boshqa maqolada tasvirlangan.
3D fazoda xuddi shu maqsadda aralash ko‘paytmadan foydalanish mumkin.

## Mashqlar {#exercises}

### Chiziqlarning kesishishi {#line-intersection}

2D da to‘g‘ri chiziqni aniqlashning ko‘plab usullari bor va ularni birlashtirishdan tortinmaslik kerak.
Masalan, ikkita to‘g‘ri chiziq berilgan va ularning kesishish nuqtalarini topmoqchimiz.
Birinchi chiziqning barcha nuqtalarini $\mathbf r = \mathbf a_1 + t \cdot \mathbf d_1$ ko‘rinishda parametrlash mumkin, bunda $\mathbf a_1$ — boshlang‘ich nuqta, $\mathbf d_1$ — yo‘nalish va $t$ — biror haqiqiy parametr.
Ikkinchi chiziqning barcha nuqtalari esa $(\mathbf r - \mathbf a_2)\times \mathbf d_2=0$ ni qanoatlantirishi kerak. Bundan $t$ parametrni osongina topamiz:

$$(\mathbf a_1 + t \cdot \mathbf d_1 - \mathbf a_2)\times \mathbf d_2=0 \quad\Rightarrow\quad t = \dfrac{(\mathbf a_2 - \mathbf a_1)\times\mathbf d_2}{\mathbf d_1\times \mathbf d_2}$$

Ikki to‘g‘ri chiziqni kesishtiradigan funksiyani amalga oshiramiz.

```cpp
point2d intersect(point2d a1, point2d d1, point2d a2, point2d d2) {
    return a1 + cross(a2 - a1, d2) / cross(d1, d2) * d1;
}
```

### Tekisliklarning kesishishi {#planes-intersection}

Biroq ba’zan geometrik mulohazalardan foydalanish qiyin bo‘lishi mumkin.
Masalan, boshlang‘ich nuqtalari $\mathbf a_i$ va yo‘nalishlari $\mathbf d_i$ bilan aniqlangan uchta tekislik berilgan va ularning kesishish nuqtasini topmoqchisiz.
Siz shunchaki quyidagi tenglamalar sistemasini yechish kerakligini payqashingiz mumkin:

$$\begin{cases}\mathbf r\cdot \mathbf n_1 = \mathbf a_1\cdot \mathbf n_1, \\ \mathbf r\cdot \mathbf n_2 = \mathbf a_2\cdot \mathbf n_2, \\ \mathbf r\cdot \mathbf n_3 = \mathbf a_3\cdot \mathbf n_3\end{cases}$$

Geometrik yondashuv haqida o‘ylash o‘rniga, bevosita olinadigan algebraik yondashuvni ishlab chiqish mumkin.
Masalan, nuqta sinfini allaqachon amalga oshirgan bo‘lsangiz, bu sistemani Kramer qoidasi bilan yechish oson bo‘ladi, chunki aralash ko‘paytma ustunlari shu vektorlardan iborat matritsaning determinantiga teng:

```cpp
point3d intersect(point3d a1, point3d n1, point3d a2, point3d n2, point3d a3, point3d n3) {
    point3d x(n1.x, n2.x, n3.x);
    point3d y(n1.y, n2.y, n3.y);
    point3d z(n1.z, n2.z, n3.z); 
    point3d d(dot(a1, n1), dot(a2, n2), dot(a3, n3));
    return point3d(triple(d, y, z),
                   triple(x, d, z),
                   triple(x, y, d)) / triple(n1, n2, n3);
}
```

Endi bularning hammasiga ko‘nikish uchun umumiy geometrik amallar uchun yondashuvlarni o‘zingiz topib ko‘rishingiz mumkin.
