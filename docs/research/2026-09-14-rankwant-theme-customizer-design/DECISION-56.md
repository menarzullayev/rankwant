# D56 — Compose-dirty gate doirasi

**Sana:** 2026-09-21  
**Qaror:** B — darvoza faqat live + deploy daraxtini skanaydi  
**Tanlangan variant:** `narrow-gate`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

`check_deploy_gate.py` `docker-compose*.yml` ni **jonli checkout**
(`RANKWANT_LIVE_DIR`, standart `cp/rankwant`) va **deploy worktree**
(`RANKWANT_DEPLOY_DIR`, standart `wt/deploy`) da qidiradi. Har AOP
daraxti emas.

2026-09-17 himoyasi saqlanadi: iflos compose **jonli** daraxtida bo‘lsa
bake to‘xtaydi. Izolatsiya qilingan `adminer-declared` dagi untracked
`docker-compose.tools.yml` endi yashil main web’ni muzlatmaydi.

`--checkouts` fixture o‘zgarishsiz — salbiy testlar shu orqali
yozyapti.

## Trade-off

Agent o‘z daraxtidan allaqachon `compose --profile tools up` qilgan
sidecar keyingi **to‘liq** bake’da tushib qolishi mumkin. `deploy.sh`
scope=`web` da `up -d --no-deps web` — adminer’ga tegmaydi.

## Ta’sir

`tools/check_deploy_gate.py`, `docs/10-operations/deploy-runbook.md`,
`CONTRIBUTING.md`. `tools/check_negative.py` / `CLAUDE.md` ga tegilmadi
(boshqa agent lock).
