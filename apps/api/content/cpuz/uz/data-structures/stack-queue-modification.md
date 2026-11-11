# Minimum stek va minimum navbat {#minimum-stack-minimum-queue}

Ushbu maqolada uchta masalani ko‘rib chiqamiz: avval stekni undagi eng kichik elementni $O(1)$ vaqtda topish mumkin bo‘ladigan qilib o‘zgartiramiz; keyin navbat uchun ham xuddi shunday imkoniyat yaratamiz; nihoyat, shu ma’lumotlar tuzilmalaridan foydalanib massivdagi berilgan uzunlikka ega barcha ostmassivlarning minimumini $O(n)$ vaqtda topamiz.

## Stekni o‘zgartirish {#stack-modification}

Stek ma’lumotlar tuzilmasini undagi eng kichik elementni $O(1)$ vaqtda topish mumkin bo‘ladigan qilib o‘zgartirmoqchimiz. Bunda stekka element qo‘shish va undan element olib tashlash amallarining asimptotik murakkabligi o‘zgarmasligi kerak.

Eslatib o‘tamiz: stekda elementlar faqat bitta uchidan qo‘shiladi va olib tashlanadi.

Buning uchun stekda faqat elementlarning o‘zini emas, balki juftliklarni saqlaymiz: elementning o‘zi va shu elementdan boshlab stekning pastigacha bo‘lgan qismdagi minimum.

```cpp
stack<pair<int, int>> st;
```

Butun stekdagi minimumni topish uchun faqat `stack.top().second` qiymatiga qarash kifoya ekani ravshan.

Yangi elementni stekka qo‘shish yoki undan element olib tashlash ham o‘zgarmas vaqtda bajarilishi aniq.

Implementatsiya:

* Element qo‘shish:

```cpp
int new_min = st.empty() ? new_elem : min(new_elem, st.top().second);
st.push({new_elem, new_min});
```

* Elementni olib tashlash:

```cpp
int removed_element = st.top().first;
st.pop();
```

* Minimumni topish:

```cpp
int minimum = st.top().second;
```

## Navbatni o‘zgartirish (1-usul) {#queue-modification-method-1}

Endi navbat bilan ham xuddi shu amallarni bajarishni istaymiz, ya’ni elementlarni oxiriga qo‘shamiz va boshidan olib tashlaymiz.

Bu yerda navbatni o‘zgartirishning sodda usulini ko‘rib chiqamiz. Biroq uning katta kamchiligi bor: o‘zgartirilgan navbat aslida barcha elementlarni saqlamaydi.

Asosiy g‘oya — navbatda faqat minimumni aniqlash uchun kerak bo‘ladigan elementlarni saqlash. Aniqrog‘i, navbatdagi qiymatlarni kamaymaydigan tartibda tutamiz, ya’ni eng kichik qiymat navbat boshida turadi. Albatta, tartibni shunchaki ixtiyoriy usulda saqlamaymiz: haqiqiy joriy minimum har doim navbatda qolishi kerak.

Shunda eng kichik element doimo navbat boshida bo‘ladi. Yangi elementni navbatga qo‘shishdan oldin “kesish” amalini bajarish kifoya: navbatning oxiridan yangi elementdan katta bo‘lgan barcha elementlarni olib tashlaymiz, so‘ng yangi elementni oxiriga qo‘shamiz.

Bu bilan navbatning tartibini buzmaymiz va yangi element keyingi biror qadamda minimum bo‘lib qolsa, uni yo‘qotmaymiz. Olib tashlangan elementlarning hech biri endi hech qachon minimum bo‘la olmaydi, shuning uchun ularni o‘chirish mumkin.

Navbat boshidan bir elementni chiqarishni istaganimizda, u aslida u yerda bo‘lmasligi ham mumkin: oldinroq undan kichikroq element qo‘shilganda u o‘chirib yuborilgan bo‘lishi ehtimol. Shu sababli navbatdan element o‘chirishda o‘chirilishi kerak bo‘lgan elementning qiymatini bilishimiz zarur. Agar navbat boshidagi qiymat shu qiymatga teng bo‘lsa, uni xavfsiz olib tashlaymiz; aks holda hech narsa qilmaymiz.

Yuqoridagi amallarning implementatsiyasi:

```cpp
deque<int> q;
```

* Minimumni topish:

```cpp
int minimum = q.front();
```

* Element qo‘shish:

```cpp
while (!q.empty() && q.back() > new_element)
    q.pop_back();
q.push_back(new_element);
```

* Elementni olib tashlash:

```cpp
if (!q.empty() && q.front() == remove_element)
    q.pop_front();
```

Bu amallarning barchasi o‘rtacha $O(1)$ vaqt olishi ravshan, chunki har bir element faqat bir marta qo‘shilishi va faqat bir marta olib tashlanishi mumkin.

## Navbatni o‘zgartirish (2-usul) {#queue-modification-method-2}

Bu — 1-usulning o‘zgartirilgan ko‘rinishi. Qaysi elementni olib tashlashimizni bilmasdan ham navbat boshidan element o‘chira olishni istaymiz.

Buning uchun navbatdagi har bir element bilan birga uning indeksini saqlaymiz. Shuningdek, jami nechta element qo‘shilganini va nechta element olib tashlanganini eslab boramiz.

```cpp
deque<pair<int, int>> q;
int cnt_added = 0;
int cnt_removed = 0;
```

* Minimumni topish:

```cpp
int minimum = q.front().first;
```

* Element qo‘shish:

```cpp
while (!q.empty() && q.back().first > new_element)
    q.pop_back();
q.push_back({new_element, cnt_added});
cnt_added++;
```

* Elementni olib tashlash:

```cpp
if (!q.empty() && q.front().second == cnt_removed) 
    q.pop_front();
cnt_removed++;
```

## Navbatni o‘zgartirish (3-usul) {#queue-modification-method-3}

Bu yerda minimumni $O(1)$ vaqtda topish uchun navbatni o‘zgartirishning yana bir usulini ko‘rib chiqamiz. Bu usulni implementatsiya qilish biroz murakkabroq, ammo bu safar barcha elementlar haqiqatan ham saqlanadi. Bundan tashqari, olib tashlanayotgan elementning qiymatini bilmasdan navbat boshidan element o‘chira olamiz.

G‘oya masalani avval yechilgan stek masalasiga keltirishdan iborat. Demak, faqat ikkita stek yordamida navbatni qanday modellashtirishni o‘rganishimiz kerak.

`s1` va `s2` nomli ikkita stek yaratamiz. Albatta, bu steklar minimumni $O(1)$ vaqtda topishga imkon beradigan o‘zgartirilgan shaklda bo‘ladi. Yangi elementlarni `s1` stekiga qo‘shamiz, elementlarni esa `s2` stekidan olib tashlaymiz. Agar biror payt `s2` bo‘sh bo‘lsa, `s1` dagi barcha elementlarni `s2` ga ko‘chiramiz; bu amalda ularning tartibini teskarisiga aylantiradi.

Navbat minimumini topish uchun ikki stek minimumining kichigini olish kifoya. Shunday qilib, barcha amallar o‘rtacha $O(1)$ vaqtda bajariladi: har bir element `s1` ga bir marta qo‘shiladi, `s2` ga bir marta ko‘chiriladi va `s2` dan bir marta chiqariladi.

Implementatsiya:

```cpp
stack<pair<int, int>> s1, s2;
```

* Minimumni topish:

```cpp
if (s1.empty() || s2.empty()) 
    minimum = s1.empty() ? s2.top().second : s1.top().second;
else
    minimum = min(s1.top().second, s2.top().second);
```

* Element qo‘shish:

```cpp
int minimum = s1.empty() ? new_element : min(new_element, s1.top().second);
s1.push({new_element, minimum});
```

* Elementni olib tashlash:

```cpp
if (s2.empty()) {
    while (!s1.empty()) {
        int element = s1.top().first;
        s1.pop();
        int minimum = s2.empty() ? element : min(element, s2.top().second);
        s2.push({element, minimum});
    }
}
int remove_element = s2.top().first;
s2.pop();
```

## Berilgan uzunlikdagi barcha ostmassivlar minimumini topish {#finding-the-minimum-for-all-subarrays-of-fixed-length}

Uzunligi $N$ bo‘lgan $A$ massiv va $M \le N$ soni berilgan bo‘lsin. Massivdagi uzunligi $M$ bo‘lgan har bir ostmassivning minimumini, ya’ni quyidagi qiymatlarni topishimiz kerak:

$$\min_{0 \le i \le M-1} A[i], \min_{1 \le i \le M} A[i], \min_{2 \le i \le M+1} A[i],~\dots~, \min_{N-M \le i \le N-1} A[i]$$

Masalani chiziqli, ya’ni $O(n)$ vaqtda yechish talab qilinadi.

Yuqoridagi uchta o‘zgartirilgan navbatdan istalgan biri bilan masalani yechish mumkin. Yechim sodda: massivning dastlabki $M$ ta elementini navbatga qo‘shamiz, minimumni topib chiqaramiz; keyin navbatdagi elementni qo‘shib, massivning eng oldingi elementini olib tashlaymiz va yangi minimumni chiqaramiz; shu jarayonni davom ettiramiz.

Navbat bilan barcha amallar o‘rtacha o‘zgarmas vaqtda bajarilgani uchun butun algoritmning murakkabligi $O(n)$ bo‘ladi.

## Amaliy masalalar {#practice-problems}

* [Queries with Fixed Length](https://www.hackerrank.com/challenges/queries-with-fixed-length/problem)
* [Sliding Window Minimum](https://cses.fi/problemset/task/3221)
* [Binary Land](https://www.codechef.com/MAY20A/problems/BINLAND)
