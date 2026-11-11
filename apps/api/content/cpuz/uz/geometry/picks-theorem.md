# Pick teoremasi {#picks-theorem}

O‘zini o‘zi kesmaydigan ko‘pburchak, agar uning barcha uchlari tekislikdagi biror butun koordinatali to‘rda butun koordinatalarga ega bo‘lsa, **panjaraviy** deyiladi. Pick teoremasi bunday ko‘pburchakning yuzini uning chegarasida yotgan nuqtalar soni va qat’iy ichida yotgan nuqtalar soni orqali hisoblash imkonini beradi.

## Formula {#formula}

Yuzi noldan farqli biror panjaraviy ko‘pburchak berilgan bo‘lsin.

Uning yuzini $S$ bilan, ko‘pburchak ichida qat’iy yotgan butun koordinatali nuqtalar sonini $I$ bilan, ko‘pburchak tomonlarida yotgan nuqtalar sonini esa $B$ bilan belgilaymiz.

U holda **Pick formulasi** quyidagini tasdiqlaydi:

$$
S=I+\frac{B}{2}-1
$$

Xususan, agar ko‘pburchak uchun $I$ va $B$ qiymatlari berilgan bo‘lsa, uchlarini bilmasdan turib ham yuzni $O(1)$ da hisoblash mumkin.

Bu formulani 1899-yilda avstriyalik matematik Georg Aleksandr Pick kashf etgan va isbotlagan.

## Isbot {#proof}

Isbot bir necha bosqichda, sodda ko‘pburchaklardan ixtiyoriy ko‘pburchaklarga qarab olib boriladi:

- Bitta kvadrat: $S=1, I=0, B=4$, bu formulani qanoatlantiradi.

- Tomonlari koordinata o‘qlariga parallel bo‘lgan ixtiyoriy aynimagan to‘g‘ri to‘rtburchak: $a$ va $b$ to‘rtburchak tomonlarining uzunliklari bo‘lsin. U holda $S=ab, I=(a-1)(b-1), B=2(a+b)$. O‘rniga qo‘yib, formula to‘g‘ri ekanini ko‘ramiz.

- Katetlari o‘qlarga parallel bo‘lgan to‘g‘ri burchakli uchburchak: buni isbotlash uchun har qanday bunday uchburchakni to‘g‘ri to‘rtburchakni diagonal bo‘yicha kesib hosil qilish mumkinligini payqang. Diagonalda yotgan butun nuqtalar sonini $c$ bilan belgilasak, Pick formulasi $c$ ga bog‘liq bo‘lmagan holda bu uchburchak uchun ham o‘rinli ekanini ko‘rsatish mumkin.

- Ixtiyoriy uchburchak: har qanday bunday uchburchakni katetlari o‘qlarga parallel bo‘lgan to‘g‘ri burchakli uchburchaklarni uning tomonlariga yopishtirish orqali to‘g‘ri to‘rtburchakka aylantirish mumkinligini payqang (buning uchun 3 tadan ortiq bunday uchburchak kerak bo‘lmaydi). Bundan istalgan uchburchak uchun to‘g‘ri formulani olamiz.

- Ixtiyoriy ko‘pburchak: buni isbotlash uchun uni triangulyatsiya qilamiz, ya’ni uchlari butun koordinatali uchburchaklarga bo‘lamiz. Keyin esa uchburchakka ko‘pburchak qo‘shilganda Pick teoremasi o‘z kuchini saqlashini isbotlash mumkin. Shunday qilib, Pick formulasini ixtiyoriy ko‘pburchak uchun isbotladik.

## Yuqori o‘lchamlarga umumlashtirish {#generalization-to-higher-dimensions}

Afsuski, bu sodda va go‘zal formulani yuqori o‘lchamlarga umumlashtirib bo‘lmaydi.

Buni 1957-yilda Jon Riv quyidagi uchlarga ega tetraedr (**Riv tetraedri**) taklif qilib ko‘rsatgan:

$$
A=(0,0,0),
B=(1,0,0),
C=(0,1,0),
D=(1,1,k),
$$

bu yerda $k$ istalgan natural son bo‘lishi mumkin. U holda har qanday $k$ uchun $ABCD$ tetraedr ichida butun nuqta yo‘q va chegarasida faqat $4$ ta nuqta, ya’ni $A, B, C, D$ bor. Shunday qilib, ichkarisidagi va chegarasidagi nuqtalar soni o‘zgarmasa ham, hajm va sirt yuzi turlicha bo‘lishi mumkin. Demak, Pick teoremasini umumlashtirib bo‘lmaydi.

Biroq yuqori o‘lchamlar uchun baribir **Ehrhart ko‘phadlari** yordamida umumlashtirish mavjud, lekin ular ancha murakkab va nafaqat ichkaridagi nuqtalarga, balki ko‘pyoqlining chegarasiga ham bog‘liq.

## Qo‘shimcha manbalar {#extra-resources}

Pick teoremasining bir nechta sodda misollari va oddiy isbotini [bu yerda](http://www.geometer.org/mathcircles/pick.pdf) topish mumkin.
