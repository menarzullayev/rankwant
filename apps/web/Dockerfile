# ⚠️ BUILD KONTEKSTI — REPO ILDIZI, `apps/web` EMAS.
#
# 2026-09-24 gacha bu fayl `apps/web` kontekstida ishlardi va muvaffaqiyatli
# build bo'lardi, chunki o'shanda `apps/web/package-lock.json` bor edi.
# Monorepo qayta tuzilgandan keyin esa:
#
#   * yagona `package-lock.json` ILDIZDA (npm workspaces);
#   * `apps/web/package.json` da `@rankwant/shared: "*"` bog'liqligi bor;
#   * `tsconfig.json` `@rankwant/shared` ni `../../packages/shared/src/...`
#     ga bog'laydi — ya'ni build MANBANI ko'radi, symlink emas.
#
# Eski kontekstda build shunday yiqilardi (o'lchandi, run 35951769214):
#
#     [web deps 3/4] COPY package.json package-lock.json ./
#     ERROR: failed to calculate checksum ... "/package-lock.json": not found
#
# `docker-compose.yml` mos ravishda shunday chaqiradi:
#
#     build:
#       context: .
#       dockerfile: apps/web/Dockerfile
#
# Shuning uchun quyidagi COPY yo'llari ildizga NISBATAN yozilgan.

FROM node:22-slim AS deps
WORKDIR /app
# Workspace ildizining manifesti va yagona lockfile. Ikkalasi birga kerak:
# `npm ci` lockfile'ni ildizdan o'qiydi va workspace'larni undan topadi.
COPY package.json package-lock.json ./
# `packages/*` va `apps/*` manifestlari. `npm ci` ularni ko'rmasa
# "workspace not found" beradi — lockfile ularsiz yaroqsiz.
COPY packages/shared/package.json ./packages/shared/
COPY apps/web/package.json ./apps/web/
# ⚠️ `--workspace apps/web` ATAYLAB YO'Q. U bilan npm faqat shu
# workspace'ning bog'liqliklarini ildiz `node_modules` ga hoist qiladi va
# `next` ni `apps/web/node_modules/` da qoldiradi — natijada build
# shunday yiqiladi (o'lchandi, 2026-09-24):
#
#     > next build
#     sh: 1: next: not found
#
# To'liq `npm ci` butun daraxtni bir xil holatda yig'adi, ya'ni build
# bosqichi kompyuterda ishlayotgan tuzilmani aynan takrorlaydi.
# `--mount=type=cache`: npm'ning o'z HTTP keshi `node_modules` dan
# ALOHIDA saqlanadi. `package-lock.json` o'zgarganda ham faqat YANGI
# paketlar yuklanadi (api Dockerfile'dagi pip kesh bilan bir xil qoida).
# `target=/root/.npm` — root foydalanuvchining standart npm keshi.
# O'lchandi: import qadami ~23 s, keshsiz har o'zgarishda takrorlanardi.
RUN --mount=type=cache,target=/root/.npm \
    npm ci

FROM node:22-slim AS build
WORKDIR /app
# ⚠️⚠️ TARTIB MUHIM: MANBA AVVAL, `node_modules` KEYIN.
#
# `COPY <dir> <dir>` Docker'da manba daraxtini nishon ustiga YOZADI. Agar
# `node_modules` avval ko'chirilsa, keyingi `COPY apps/web ./apps/web`
# uning ustidan yozadi va paketlar yo'qoladi. `.dockerignore`
# `**/node_modules/` ni chiqarib tashlagani uchun manba ko'chirmasi
# ularni QAYTA qo'shmaydi — natijada `next` va uning bog'liqliklari
# (masalan `picocolors`) yo'qolib, build shunday yiqiladi (o'lchandi,
# 2026-09-24, Turbopack 48 xato):
#
#     ./node_modules/katex/dist/katex.min.css
#     Error: Cannot find module 'picocolors'
#
# Manba: `packages/shared` MANBASI ham kerak, chunki `tsconfig.json`
# `@rankwant/shared` ni to'g'ridan-to'g'ri `packages/shared/src/...` ga
# bog'laydi. Ildizda `tsconfig*.json` YO'Q (`apps/web/tsconfig.json`
# quyidagi `COPY apps/web` bilan keladi), shuning uchun bu yerda faqat
# ikki manba ko'chiriladi.
COPY packages ./packages
COPY apps/web ./apps/web
# `node_modules` IKKI joyda bo'ladi va IKKALASI ham kerak:
#   * ildizdagi — hoist qilingan umumiy paketlar, `picocolors` kabi
#     `next` ichki kutubxonalari va `node_modules/@rankwant/*` bog'lamalari;
#   * `apps/web/node_modules` — hoist QILINMAGAN paketlar. `next` aynan
#     shular orasida (`node_modules/next` mavjud emas), ya'ni usiz
#     `npm run build` shunday yiqiladi (o'lchandi, 2026-09-24):
#
#         > next build
#         sh: 1: next: not found
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
# ⚠️ QO'SHIMCHA "tuzatish" QADAMI YO'Q — va bu ATAYLAB.
#
# Bu joyda avval `ln -s`/`cp -r` bilan `picocolors`/`nanoid`/`source-map-js`
# ni `apps/web/node_modules` ga ko'chirish urinishi bor edi. U CHALG'ITDI:
# `require.resolve` hammasini topardi (tekshiruv o'tardi), build esa
# baribir yiqilardi. Haqiqiy sabab boshqa joyda edi — `next.config.ts`
# dagi `turbopack.root` ko'rsatilmagani. Root kengaygach (repo ildizi)
# ikkala muammo ham bir yo'la yopildi:
#
#   * `@rankwant/shared/*` (`paths` `../../packages/shared/src/*` ga
#     ishora qiladi — root ichida qoldi);
#   * `next` ichki `postcss` ining hoist qilingan bog'liqliklari
#     (`picocolors`, `nanoid`, `source-map-js` — ildiz `node_modules` da
#     va root endi ularni qamraydi).
#
# O'lchandi (2026-09-24): `turbopack.root` bilan MINIMAL Dockerfile
# (faqat shu ikki COPY, hech qanday symlink/nusxa) build qilindi —
# RC=0, `✓ Compiled successfully`, bundle'da faqat to'g'ri API manzili.
# Ya'ni qo'shimcha qadam keraksiz va keyinchalik npm tuzilmasi
# o'zgarsa — yolg'on signal beradi. Shuning uchun olib tashlandi.
#
# Bitta tekshiruv qoladi: `packages/shared` manbasi build paytida
# joyida bo'lishi shart. Yo'q bo'lsa xato `Can't resolve
# '@rankwant/shared/validation'` ko'rinishida chiqadi va sababini
# topish qiyin — shuning uchun oldindan aytamiz.
RUN test -f /app/packages/shared/src/index.ts \
 && test -f /app/packages/shared/src/validation/index.ts \
 || (echo "packages/shared manbasi build kontekstida yo'q — \
`COPY packages ./packages` ni tekshiring (.dockerignore)" >&2 && exit 1)
WORKDIR /app/apps/web
# runtime `environment` da berish brauzerga umuman ta'sir qilmaydi —
# standings jonli yangilanishi qotib qolgan manzilga urinardi.
# ⚠️ Default ATAYLAB YO'Q: avval `http://localhost:8000/api/v1` edi va
# build-arg berilmaganda JIMGINA buzuq bundle yasardi — brauzer shu
# qotib qolgan manzilga murojaat qiladi (2026-09-13 avariyasining
# uchinchi qavati). Endi bo'sh bo'lsa build YIQILADI: buzuq artifact
# o'rniga aniq xato. Compose har doim qiymat beradi
# (`docker-compose.yml`, `docker-compose.public.yml`), ya'ni hech bir
# workflow buzilmaydi — bu faqat to'g'ridan-to'g'ri `docker build` uchun.
ARG NEXT_PUBLIC_API_BASE
RUN test -n "$NEXT_PUBLIC_API_BASE" \
  || (echo "NEXT_PUBLIC_API_BASE kerak (masalan: https://rankwant.uz/api/v1)" >&2 \
      && exit 1)
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
# Next.js'ning o'z keshi `.next/cache` da (webpack/SWC). U ham qatlam
# keshiga qo'shiladi: kod o'zgarganda qayta kompilyatsiya tezroq ketadi.
RUN --mount=type=cache,target=/app/apps/web/.next/cache \
    npm run build

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production
# Build qaysi manbadan chiqqanini belgilaydi. `.git` build kontekstiga
# kirmaydi (.dockerignore), shuning uchun commit tashqaridan beriladi.
# Nega kerak: `tools/check_deploy.sh` ishlab turgan konteyner manbadan
# eskimi yoki yo'qmi shu yorliq orqali aniqlaydi. Usiz Next.js'ning
# siqilgan `.next` chiqishini solishtirishning ishonchli yo'li yo'q edi
# va 2026-09-13 dagi «eski image» hodisasi sezilmay qoldi.
ARG GIT_SHA=unknown
ARG BUILT_AT=unknown
LABEL org.rankwant.git-sha=$GIT_SHA
LABEL org.rankwant.built-at=$BUILT_AT
# Runtime faqat `apps/web` ni ishlatadi: `next start` shu katalogdan
# ishga tushadi. Monorepo daraxtini ko'chirish SHART EMAS — ildiz
# `node_modules` yetarli, chunki Next o'z bog'liqliklarini hoist
# qilingan daraxtdan oladi.
COPY --from=build /app/apps/web/.next ./apps/web/.next
COPY --from=build /app/apps/web/package.json ./apps/web/
# `next` hoist QILINMAGAN — u `apps/web/node_modules` da qoladi. Ildiz
# daraxti yolg'iz o'zi yetmaydi: `npx next start` uni topa olmaydi.
# Ikkalasi ham kerak (deps bosqichidagi izohga qarang).
COPY --from=build /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=build /app/node_modules ./node_modules
# `public/` — favicon, logotip, xat sarlavhasidagi rasm. Next uni build
# ichiga QO'SHMAYDI, runtime da o'qiydi: usiz `/favicon.ico` va
# `/brand/*` 404 beradi. O'lchandi — xatdagi logotip aynan shu sababli
# siniq kelgan.
COPY --from=build /app/apps/web/public ./apps/web/public
# `next.config.ts` runtime'da qayta o'qiladi (`next start` uni yuklaydi).
COPY --from=build /app/apps/web/next.config.ts ./apps/web/
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["npx", "next", "start"]
