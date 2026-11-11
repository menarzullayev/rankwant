# Kesma uchun to‘g‘ri chiziq tenglamasini topish

Masala: kesma uchlarining koordinatalari berilgan; shu kesma orqali o‘tuvchi to‘g‘ri chiziqni qurish kerak.

Kesma aynimagan (degenerat emas), ya’ni uzunligi noldan katta deb faraz qilamiz (aks holda, albatta, u orqali cheksiz ko‘p turli to‘g‘ri chiziqlar o‘tadi).

### Ikki o‘lchamli holat

Berilgan kesma $PQ$ bo‘lsin, ya’ni uning uchlarining $P_x , P_y , Q_x , Q_y$ koordinatalari ma’lum.

Shu kesma orqali o‘tuvchi **tekislikdagi to‘g‘ri chiziq tenglamasini** qurish kerak, ya’ni to‘g‘ri chiziq tenglamasidagi $A , B , C$ koeffitsiyentlarni topish lozim:

$$A x + B y + C = 0.$$

E’tibor bering: izlanayotgan $(A, B, C)$ uchliklar uchun berilgan kesmani tasvirlaydigan **cheksiz ko‘p** yechim mavjud:
uchala koeffitsiyentni ixtiyoriy nolga teng bo‘lmagan songa ko‘paytirib, xuddi shu to‘g‘ri chiziqni olish mumkin.
Shuning uchun vazifamiz shu uchliklardan birini topishdir.

Quyidagi koeffitsiyentlar to‘plami mos kelishini tekshirish oson (bu ifodalarni va $P$ hamda $Q$ nuqtalarning koordinatalarini to‘g‘ri chiziq tenglamasiga qo‘yib ko‘rish kifoya):

$$\begin{align}
A &= P_y - Q_y, \\
B &= Q_x - P_x, \\
C &= - A P_x - B P_y.
\end{align}$$

### Butun sonli holat

To‘g‘ri chiziqni qurishning bu usulining muhim afzalligi shundaki, uchlarning koordinatalari butun bo‘lsa, hosil bo‘ladigan koeffitsiyentlar ham **butun** bo‘ladi. Ayrim hollarda bu geometrik amallarni haqiqiy sonlarga umuman murojaat qilmasdan bajarishga imkon beradi.

Biroq kichik kamchilik ham bor: bir xil to‘g‘ri chiziq uchun turli koeffitsiyentlar uchliklarini olish mumkin.
Buning oldini olish va shu bilan birga butun koeffitsiyentlardan chiqib ketmaslik uchun ko‘pincha **normallashtirish** deb ataladigan quyidagi usulni qo‘llash mumkin. $| A | , | B | , | C |$ sonlarining [eng katta umumiy bo‘luvchisi](/algorithms/algebra/euclid-algorithm) topiladi, uchala koeffitsiyent unga bo‘linadi, so‘ng ishora normallashtiriladi: agar $A <0$ yoki $A = 0, B <0$ bo‘lsa, uchala koeffitsiyent $-1$ ga ko‘paytiriladi.
Natijada bir xil to‘g‘ri chiziqlar uchun bir xil koeffitsiyentlar uchliklari hosil bo‘ladi, bu esa to‘g‘ri chiziqlarning tengligini tekshirishni osonlashtiradi.

### Haqiqiy sonli holat

Haqiqiy sonlar bilan ishlaganda doimo xatoliklarni hisobga olish kerak.

$A$ va $B$ koeffitsiyentlar boshlang‘ich koordinatalar tartibida, $C$ koeffitsiyent esa ularning kvadrati tartibida bo‘ladi. Bu allaqachon ancha katta sonlar bo‘lishi mumkin va, masalan, [to‘g‘ri chiziqlarni kesishtirganda](/algorithms/geometry/lines-intersection) ular yanada kattalashadi; bu uchlarning koordinatalari $10^3$ tartibida bo‘lganda ham katta yaxlitlash xatoliklariga olib kelishi mumkin.

Shu sababli haqiqiy sonlar bilan ishlaganda **normallashtirish** deb ataladigan amalni bajarish tavsiya etiladi; u sodda: koeffitsiyentlarni $A ^ 2 + B ^ 2 = 1$ bo‘ladigan qilib tanlash kerak. Buning uchun $Z$ sonini hisoblaymiz:

$$Z = \sqrt{A ^ 2 + B ^ 2},$$

va uchala $A , B , C$ koeffitsiyentni unga bo‘lamiz.

Shunday qilib, $A$ va $B$ koeffitsiyentlar tartibi kirish koordinatalari tartibiga bog‘liq bo‘lmaydi, $C$ koeffitsiyent esa kirish koordinatalari bilan bir xil tartibda bo‘ladi. Amalda bu hisob-kitoblar aniqligini sezilarli darajada oshiradi.

Nihoyat, to‘g‘ri chiziqlarni **taqqoslash** haqida: aslida bunday normallashtirishdan keyin bir xil to‘g‘ri chiziq uchun koeffitsiyentlarning faqat ikkita uchligi — $-1$ ga ko‘paytirish aniqligida — hosil bo‘lishi mumkin.
Shunga ko‘ra, ishorani hisobga olib qo‘shimcha normallashtirishni bajarsak (agar $A < -\varepsilon$ yoki $| A | < \varepsilon$, $B <- \varepsilon$ bo‘lsa, $-1$ ga ko‘paytiramiz), hosil bo‘lgan koeffitsiyentlar yagona bo‘ladi.

### Uch o‘lchamli va ko‘p o‘lchamli holat

Uch o‘lchamli holatdayoq to‘g‘ri chiziqni tasvirlaydigan **oddiy tenglama yo‘q** (uni ikki tekislikning kesishmasi, ya’ni ikkita tenglamalar sistemasi sifatida berish mumkin, ammo bu noqulay usul).

Shuning uchun uch o‘lchamli va ko‘p o‘lchamli holatlarda to‘g‘ri chiziqni berishning **parametrik usulidan** foydalanish kerak, ya’ni uni $p$ nuqta va $v$ vektor orqali ifodalash:

$$p + v t, ~~~ t \in \mathbb{R}.$$

Ya’ni to‘g‘ri chiziq — $p$ nuqtaga $v$ vektorni ixtiyoriy koeffitsiyent bilan qo‘shib hosil qilish mumkin bo‘lgan barcha nuqtalardir.

To‘g‘ri chiziqni kesma uchlarining koordinatalari bo‘yicha parametrik ko‘rinishda **qurish** oddiy: $p$ nuqta sifatida kesmaning bir uchini, $v$ vektor sifatida esa birinchi uchdan ikkinchisiga yo‘nalgan vektorni olamiz.
