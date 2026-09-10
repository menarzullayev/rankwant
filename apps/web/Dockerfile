FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_* brauzer bundle'iga BUILD vaqtida yoziladi. Uni faqat
# runtime `environment` da berish brauzerga umuman ta'sir qilmaydi —
# standings jonli yangilanishi qotib qolgan manzilga urinardi.
ARG NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
RUN npm run build

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production
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
