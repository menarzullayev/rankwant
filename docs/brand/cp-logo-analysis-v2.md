# CP logotiplar tahlili → RankWant belgi v2

**STATUS:** draft (2026-09-10)  
**Sabab:** v1 (`belgi-generated/`) yoqmadi — ko‘p belgi CP klishelari (ustun, shevron, pyedestal) va **Codeforces favicon** (3 ta rangli ustun) bilan chalkashadi.

## Raqobatchilar — vizual til

| Platforma                                 | Belgi tili                                              | Rang                 | Nima ishlaydi                | RankWant uchun                             |
| ----------------------------------------- | ------------------------------------------------------- | -------------------- | ---------------------------- | ------------------------------------------ |
| [Codeforces](https://codeforces.com/)     | 3 ta vertikal ustun (rating ranglari: sariq/ko‘k/qizil) | Ko‘k + rating        | Favicon = reyting metaforasi | **Ustun/chart belgilardan voz kechish**    |
| [AtCoder](https://atcoder.jp/)            | Gerb + unicorn + AC monogram                            | Qora/kulrang         | «Prestij» heraldika          | Oddiy app-icon uchun og‘ir; nusxa olmaslik |
| [LeetCode](https://leetcode.com/)         | `<` + C egri + chiziq (kod glyph)                       | To‘q sariq/oq        | Kod tilidan monogram         | Bracket klishesini takrorlamaslik          |
| [CodeChef](https://www.codechef.com/)     | Oshpaz shapkasi / ovqat metaforasi                      | Jigarrang/to‘q sariq | Esda qoladigan mascot        | Bizga mascot shart emas                    |
| [HackerRank](https://www.hackerrank.com/) | Yashil hexagon + H                                      | Yashil               | Oddiy, 16px da o‘qiydi       | Hex+harf yo‘li band                        |
| [KEP.uz](https://kep.uz/)                 | Burchakli diagonal fragmentlar / gradient «K» shakli    | Ko‘k gradient        | Abstrakt, mahalliy           | Gradient+ko‘p parchalar — farq qilish      |
| [RoboContest](https://robocontest.uz/)    | Robot shlem (mascot) + ROBOCONTEST                      | To‘q UI, cyan        | Personaj kuchli              | **Robot/mascot yo‘q** — RankWant boshqa    |
| [clist.by](https://clist.by/resources/)   | Aggregator; resurslar ro‘yxati                          | —                    | CP ekosistemasi xaritasi     | Ilhom: global CP, lekin o‘z ovozi          |

## RankWant brend cheklovlari

- Platforma: **RankWant** («reyting xohlayman») — motivatsiya, ochiq rating
- Coin: **Qvant** — alohida belgi bo‘lishi mumkin, asosiy mark emas
- Rang: `#5b8cff` / `#4470e6` / `#14171c`, oq fon
- Kerak: 16px favicon, app icon, wordmark yonida

## v2 strategiya (nima qilmaymiz / qilamiz)

**Qilmaymiz:** CF ustunlari, podium, oddiy shevron, atom orbita, qalqon, nishon, «Islamic» to‘ldirilgan naqsh, robot.

**Qilamiz:**

1. **Monogram** (RW / R) — CF/LC uslubidagi kuchli glyph, lekin o‘z shakli
2. **«Want» energiya** — uchqun, delta, yo‘nalish (ustunsiz)
3. **Bitta chiziq / bitta shakl** — 16px da omon qoladi
4. **Qvant seed** — coin uchun alohida (2–3 variant)
5. **Prestij** — lekin AtCoder gerbidan soddaroq

## v2 — 20 konsepsiya

| #   | Nom          | G‘oya                                           |
| --- | ------------ | ----------------------------------------------- |
| 01  | RW lock      | R va W bir-biriga qulflangan geometrik monogram |
| 02  | R-arrow      | R ning oyoq chizig‘i oldinga o‘q bo‘lib ketadi  |
| 03  | Want spark   | Bitta uchburchak uchqun + nuqta — istak         |
| 04  | Delta rise   | Δ shakli — reyting o‘zgarishi                   |
| 05  | Rank pin     | Xarita pin / joy belgisining sodda versiyasi    |
| 06  | Path stroke  | Bitta qalin chiziq: past → yuqori egri yo‘l     |
| 07  | Ribbon fold  | 1-o‘rin lenta, 2 bukilish, flat                 |
| 08  | Pulse want   | Bitta yurak urishi / signal to‘lqini            |
| 09  | Goal arc     | Yarim doira + ichida ko‘k nuqta (nishonsiz)     |
| 10  | Slash R      | Qalin R + diagonal kesish (`/`)                 |
| 11  | Twin peak W  | W ikki cho‘qqi sifatida (harf emas — siluet)    |
| 12  | Stamp RW     | Dumaloq muhr ichida RW                          |
| 13  | Ladder step  | 2 pog‘ona, bitta chiziq (3 ustun emas)          |
| 14  | Node W       | 5 tugunli W shaklidagi graf                     |
| 15  | Break loop   | Uzilgan halqa, yuqoriga ochilgan                |
| 16  | Qvant seed   | Q + bitta zarra (coin mark)                     |
| 17  | Orbit Q      | Bitta orbita, Q markazi (coin)                  |
| 18  | Bolt want    | Chaqmoq / energiya chizig‘i                     |
| 19  | Flag tip     | Finish bayroq silueti, sodda                    |
| 20  | Horizon rise | Gorizontal chiziq + bitta cho‘qqi               |

Natijalar: [`belgi-v2/`](./belgi-v2/)
