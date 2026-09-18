# Hissa qo'shish

## Hujjat birinchi

Bu loyihada **hujjat koddan oldin** keladi. `docs/` dagi bosqichlar 🔒 `locked` bo'lsa — ularni
o'zgartirish uchun **yangi ADR** kerak (`docs/07-adr/`). Bu byurokratiya emas: qulflangan
qaror bir necha hujjatga tarqalgan bo'ladi, ADR esa nima uchun o'zgarganini saqlaydi.

Qaerdan boshlash: [INDEX.md](INDEX.md) → [docs/README.md](docs/README.md)

## Branch va commit

- Branch: `feat/…`, `fix/…`, `chore/…`, `docs/…`
- Commit: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- `main` ga to'g'ridan-to'g'ri push **yopiq** — faqat PR orqali. Buni `.githooks/pre-push`
  (`tools/push_guard.py`) ushlab turadi: GitHub bu repoda branch protection bermaydi
  (bepul private tarif, 403). PR GitHub'da, CI yashil bo'lgach birlashtiriladi.
  Favqulodda holat uchun `RANKWANT_ALLOW_MAIN_PUSH=1` — faqat odam qarori bilan.
- Commit muallifi haqiqiy bo'lishi shart: `@example.com`, `.test`, `localhost` kabi soxta
  manzilli commit'lar push qilinmaydi. Eski tarix `.mailmap` orqali to'g'rilangan.

## Parallel agentlar

Bu mashinada bir nechta agent (Claude, Cursor, WorkBuddy) bitta repo va bitta jonli stack
bilan ishlaydi. Qoidalar 2026-09-17 kechqurunidan keyin yozildi: o'sha kuni ish asosiy
checkout'da branch'siz olib borildi va jonli `api` `tools/deploy.sh` siz qayta yaratildi —
natijada 21 ta fayl bitta savatda qoldi va production'da qaysi commit ishlayotganini kod
aytmay qo'ydi (`org.rankwant.git-sha` yorlig'i `unknown`).

- **Har ish o'z worktree'sida va branch'ida, agentning O'Z papkasida:**
  `git worktree add -b feat/<mavzu> C:/Users/nsn/project/wt/<agent>/<mavzu> origin/main`,
  bu yerda `<agent>` — `claude`, `cursor` yoki `workbuddy`. Worktree `cp/` ichida
  ochilmaydi. Bitta PR — bitta mavzu.
- **Agent faqat o'z papkasida yaratadi va o'chiradi.** Sabab (2026-09-18): «barcha
  worktree'larni o'chir» topshirig'i boshqa agentning ishini ham o'chirdi va uning push
  qilinmagan commit'i uchinchi qo'lda PR bo'lib chiqdi. Bu safar zarar bo'lmadi, lekin
  kimning ishi ekani hech qayerda ko'rinmasdi: git muallifi hamma agentda bir xil, egalikni
  faqat yo'l ko'rsatadi.
- **Sessiya tugashidan oldin commit'lar push qilinadi** — tugallanmagan bo'lsa ham, `wip/`
  branch'ida. Faqat diskda turgan commit papka bilan birga yo'qolishi mumkin.
- **Asosiy checkout (`cp/rankwant`) `main` da va toza qoladi.** Rejali Windows vazifalari
  skriptlarni aynan shu papkadan o'qiydi (`RankWant Monthly Backup` → `tools/backup.sh`,
  `RankWant Tunnel Monitor` → `tools/monitor.ps1`), shuning uchun u yerda yarim tahrirlangan
  fayl yoki begona branch turmasligi kerak.
- **Deploy faqat `tools/deploy.sh` orqali.** U darvoza (`tools/check_deploy_gate.py`) va
  qulfni o'zi bajaradi, obrazga commit yorlig'ini yozadi. Qo'lda `docker compose up` bilan
  production yangilanmaydi: darvoza ham, qulf ham chetlab o'tiladi.
- **Compose va `.env` o'zgarishi kod bilan birga PR'ga tushadi.** Commit qilinmagan
  `docker-compose*.yml` bo'lsa darvoza deploy'ni to'xtatadi — jonli stack o'sha fayl bilan
  ko'tarilgan bo'lishi va deploy uni jimgina yo'qotishi mumkin.
- **PR'lar parallel bo'lishi mumkin**, lekin og'ir smoke asosan `main`da.
  Ikkinchi runner (`rankwant-ci-runner-2`) bir xil `rankwant` label'ida;
  u register qilinmaguncha navbat yana ketma-ket. Hosted runner yo'q.
- **Boshqa agentning ish daraxtiga tegilmaydi:** uning commit qilinmagan fayllarini
  o'zgartirmang, `git pull`/`checkout` qilmang, faqat o'qing.
- `tools/check_negative.py` ishlayotgan worktree'da fayllarni mutatsiya qiladi — o'sha
  vaqtda o'sha worktree'da commit qilinmaydi.

## Til

Qaror (2026-09-17): repo **aralash tilda qoladi**, migratsiya rejalashtirilmagan —
qoida faqat noaniqlikni yo'qotadi.

- **Kod izohi va docstring — inglizcha**, fayl qaysi tilda yozilganidan qat'i nazar.
  Mavjud o'zbekcha izohlar tarjima qilinmaydi; bir faylda ikki til bo'lishi kutilgan
  holat, «tozalash» uchun qayta yozilmaydi.
- **Hujjat** (`README`, `docs/`, `CONTRIBUTING`) — yangi fayl inglizcha; mavjud fayl
  o'z tilida davom etadi.
- `docs/research/` — sanali yozuvlar, yozilganicha qoladi.
- **Commit va PR** — inglizcha, conventional commits.
- **Foydalanuvchiga ko'rinadigan matn** — faqat i18n lug'atlarida
  (`apps/web/src/i18n/`), kodda qattiq yozilmaydi.
- Tekshiruv skriptlarining chiqish xabarlari o'zbekcha (foydalanuvchi bilan muloqot).

## Definition of Done

Har PR uchun: [09-development-plan § Definition of Done](docs/09-development-plan/README.md).
PR shabloni shu ro'yxatni avtomatik chiqaradi.

## Test

To'liq strategiya: [docs/10-operations/test-strategy.md](docs/10-operations/test-strategy.md)

Qamrovi **majburiy** bo'lgan to'rt soha — bularsiz PR birlashtirilmaydi:

1. Judge pipeline (submit → verdict)
2. 4 reyting formulasi
3. Qvant ledger
4. Auth va PAT scope

## Xavfsizlik

Foydalanuvchi kodi **faqat** judge hostda ishlaydi. Judge ga tegadigan har qanday o'zgarish
`tests/security/` ni yangilashni talab qiladi.

Zaiflik topsangiz — **ommaviy issue ochmang**, GitHub Security Advisory orqali xabar bering.

## Local ishga tushirish

```bash
docker compose up -d          # postgres + redis + minio
python3 tools/check_docs.py   # hujjat yaxlitligi
```
