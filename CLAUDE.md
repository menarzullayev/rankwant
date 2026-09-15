# RankWant — agent uchun kirish nuqtasi

Loyiha hujjatlangan: `docs/` da 10 bo'lim, `docs/07-adr/` da 19 ta ADR.
**Bu fayl ularni takrorlamaydi** — bu yerda faqat kod yozayotganda darhol
kerak bo'ladigan buyruqlar va ilgari vaqt yegan tuzoqlar.

## Qayerga qarash kerak

| Savol | Hujjat |
| ----- | ------ |
| Entity, maydon, o'chirish qoidalari | `docs/05-domain-model/` (locked) |
| Nega shunday qilingan | `docs/07-adr/` — har qaror alohida ADR |
| Deploy, incident, backup, monitoring | `docs/10-operations/` |
| Verdikt kodlari, sahifalash, xato formati | `docs/08-technical-spec/` |
| Judge shartnomasi va bake-off | `services/bakeoff/protocol.md` |

Pul mantiqi bo'yicha bitta qoida hammasidan muhim (ADR-0002):
**balans hech qachon to'g'ridan-to'g'ri yozilmaydi, faqat ledger orqali.**
`qvant_audit` buni butun baza bo'yicha tekshiradi.

## Darvozalar

Pre-push hook shularni o'zi ishga tushiradi, lekin ish davomida qo'lda
chaqirish tezroq:

```bash
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run mypy . && env CELERY_EAGER=1 uv run pytest -q -n 4
```

```bash
cd apps/web && npm run lint && npm run typecheck && npm run build
```

```bash
python3 tools/check_i18n.py && python3 tools/check_contrast.py && python3 tools/check_docs.py && python3 tools/check_contract.py
```

Endpoint qo'shilsa yoki serializer o'zgarsa, sxemani yangilash **shart** —
aks holda CI yiqiladi:

```bash
cd apps/api && uv run python manage.py spectacular --file openapi/schema.yml
```

`pytest -n 4` — `auto` EMAS: runner shu mashinada, jonli preview bilan
yonma-yon ishlaydi.

`CELERY_EAGER=1` ham **shart**. Busiz task navbatga yoziladi va test
javobni kutib qotadi; `settings.py` uni `CELERY_TASK_ALWAYS_EAGER` ga
o'giradi, ya'ni task chaqirilgan joyda bajariladi. Haqiqiy darvozalar
ikkalasi ham shuni beradi (`.githooks/pre-push`, `.github/workflows/ci.yml`)
va hook uni «SHART» deb belgilagan — o'lchangan farq: 14m54s → 1m57s.

## Preview

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml up -d --build --wait
```

**`-p rankwant` tushib qolmasin.** `docker-compose.yml` da `name:` kaliti
yo'q, ya'ni loyiha nomi joriy KATALOG nomidan olinadi. Worktree ichidan
bayroqsiz chaqirilsa, compose jimgina alohida stack va **alohida baza**
ko'taradi — xato bermaydi, shunchaki boshqa ma'lumot ko'rsatadi. Faqat
`docker-compose.ci.yml` o'z nomini (`rankwant-ci`) o'zi belgilaydi.

Mashina dual-boot (Linux + Windows), har tizimda preview'ning o'z bazasi bor.
Tizim almashtirishdan **oldin** `tools/handoff.sh out` (Linux) yoki
`tools\handoff.ps1 out` (Windows), yuklangandan keyin `in` — aks holda ikki
baza jimgina ajralib ketadi. Protokol: [10-operations](docs/10-operations/README.md)
§ «Ikki tizimli preview».
Linux'da `in` ni yuklanishda `rankwant-handoff.service` o'zi chaqiradi va
`tools/handoff.sh switch` bitta buyruqda `out` + Windows'ga qayta yuklashni
bajaradi. Windows'da bunday `switch` yo'q: `out`, keyin qayta yuklash —
EFI tartibi Ubuntu'ni birinchi qo'yadi. U yerda avtomatik `in` uchun logon
vazifasi bir marta ro'yxatga olinadi (hujjatda).

**Servis nomini ro'yxatlab qisqartirmang.** Django kodi API'da ham,
`worker` da ham, `beat` da ham ishlaydi; faqat `api` ni qayta qursangiz
worker eski kodda qoladi. O'lchangan oqibat: judge yangi verdikt
yubordi, eski worker uni tanimay `IE` ga aylantirdi va sabab faqat
worker logida ko'rindi.

Portlar: web `127.0.0.1:8300`, API `127.0.0.1:8301`. `ALLOWED_HOSTS`
tufayli curl'ga host sarlavhasi kerak, aks holda bo'sh 400 keladi:

```bash
curl -H 'Host: rankwant.uz' http://127.0.0.1:8301/api/v1/health/
```

## Bake-off (judge izolyatsiyasi)

Ishga tushirishdan oldin `worker` va `beat` **to'xtatilishi shart** —
`drain_results` natijalarni harness'dan oldin olib ketadi va hisobot
«XAVFSIZLIKDAN O'TMADI» deb yozadi, aslida sandbox soz:

```bash
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml stop worker beat
IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rankwant-redis-1)
apps/api/.venv/bin/python services/bakeoff/harness/runner.py --worker judge-go --redis redis://$IP:6379/0
docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml start worker beat
```

Redis host portiga chiqarilmagan — shuning uchun konteyner IP'si olinadi.
`rankwant-redis-1` nomi ham aynan `-p rankwant` bo'lgandagina topiladi:
konteyner nomini compose loyiha nomidan yasaydi. Bayroq tushsa
`docker inspect` bo'sh qaytaradi va `IP` o'zgaruvchisi jimgina bo'sh
qoladi.

## Ish uslubi

Issue ishlatilmaydi — **PR asosida** (0 issue, 8 PR). Vazifa qo'shish
kerak bo'lsa branch va PR ochiladi, tracker'ga ticket yozilmaydi.
