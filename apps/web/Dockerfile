FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# `--mount=type=cache`: npm'ning o'z HTTP keshi `node_modules` dan
# ALOHIDA saqlanadi. `package-lock.json` o'zgarganda ham faqat YANGI
# paketlar yuklanadi (api Dockerfile'dagi pip kesh bilan bir xil qoida).
# `target=/root/.npm` — root foydalanuvchining standart npm keshi.
# O'lchandi: import qadami ~23 s, keshsiz har o'zgarishda takrorlanardi.
RUN --mount=type=cache,target=/root/.npm \
    npm ci

FROM node:22-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_* brauzer bundle'iga BUILD vaqtida yoziladi. Uni faqat
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
RUN --mount=type=cache,target=/app/.next/cache \
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
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./
# `public/` — favicon, logotip, xat sarlavhasidagi rasm. Next uni build
# ichiga QO'SHMAYDI, runtime da o'qiydi: usiz `/favicon.ico` va
# `/brand/*` 404 beradi. O'lchandi — xatdagi logotip aynan shu sababli
# siniq kelgan.
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["npx", "next", "start"]
