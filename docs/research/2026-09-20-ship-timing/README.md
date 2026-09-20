# Commit → live: wall-clock tahlili

**Sana:** 2026-09-20  
**Holat:** tadqiqot yozuvi (tirik siyosat emas)  
**Manba:** shu mashina (Git Bash `elapsed_ms`, `gh run view` job vaqtlari,
`.handoff/auto-deploy.log`, ikkita `deploy.sh --yes`)

> Amaldagi qoidalar runbook va CLAUDE.md da. Shu yozuv **o'lchangan
> vaqt** va qisqartirish takliflari. Deploy TIMER: [deploy-timing](../2026-09-20-deploy-timing/README.md).

Bog'liq: [FINDINGS.md](FINDINGS.md)

---

## 1. Bir jumla

Lokal git (commit + push + PR + merge) **~14 s**. Vaqt shu yerdan
**keyin** ketadi: CI 18–140 s (PR va main da ikki marta), avto-deploy
kutish **0–5 min**, `deploy.sh` **2.6–16 min**. Eng qimmat qism —
image qurish (ayniqsa judge) va 5 daqiqalik watcher.

## 2. O'lchangan zanjir

| Bosqich | O'lchov | Odatiy | Qayerdan |
|---|---|---|---|
| Commit | `git commit` wall | 1.3 s | #187, hook yo'q |
| Push | `git push` + pre-push | 4.0–4.1 s | #187, «Darvozalar o'tdi» |
| PR ochish | `gh pr create` | 3.9 s | #187 |
| Merge | `gh pr merge --squash` | 4.8 s | #187 |
| CI — faqat docs | run created→updated | 18–24 s | #185, #186 |
| CI — tools (`check_negative`) | xuddi shu | 59–76 s | #187 PR/main |
| CI — web o'zgarishi | xuddi shu | 103–140 s | #180, #182 |
| Security (main) | parallel | ~37 s | #187 push |
| Avto-deploy kutish | poll 5 min | 0–300 s, o'lchangan ~5 min | 16:00 CI yashil → 16:05 deploy |
| Deploy issiq | `deploy.sh --yes` | 156 s (2.6 min) | terminal 937901 |
| Deploy judge miss | xuddi shu | 954 s (15.9 min) | terminal 937900 |
| Avto-deploy yurish | log | 170 s | 16:05:11 → 16:08:01 |

PR ochiq turish (create→merge), bugun 12 ta: **50–364 s**, median **~185 s
(3.1 min)**. #187 364 s — birinchi CI qizil + tuzatish.

## 3. Happy-path (birinchi CI yashil)

Taxminiy yig'indi, avto-deploy kutishsiz:

| Yo'l | Lokal | PR CI | Merge | Main CI | Deploy | Jami (kutishsiz) |
|---|---|---|---|---|---|---|
| Docs | 14 s | 20 s | 5 s | 22 s | 0 (kerak emas) | **~1 min** |
| Tools | 14 s | 59 s | 5 s | 76 s | 0 (obrazga tushmaydi) | **~2.6 min** |
| Web | 14 s | 110 s | 5 s | 110 s | 156 s | **~6.6 min** |
| Judge Dockerfile | 14 s | ~80 s | 5 s | ~80 s | 954 s | **~19 min** |

Avto-deploy hozir **har main commit** ni obraz qurishga undashi mumkin
(konteyner SHA ≠ HEAD). Docs/tools PR dan keyin ham ~2.6 min issiq
qurilish — foydalanuvchi hech narsa ko'rmaydi.

## 4. Qayerda vaqt yo'qoladi

Tartib: ta'sir × chastota.

1. **`deploy.sh` image bake** — issiq 87 s, judge miss 866 s. PR/merge
   emas, live.
2. **5 daqiqa watcher** — CI yashil bo'lgach ham keyingi tick. O'lchangan:
   #183 main CI 16:00:21, deploy 16:05:11.
3. **CI ikki marta** — PR SHA va squash SHA. Tools: 59+76 s; web: 110+110 s.
4. **Web job `npm ci` (14–20 s) + salbiy testlar (21–32 s)** — `tools/**`
   o'zgarsa ham, Next build o'tkazilsa ham.
5. **Qizil CI + qayta push** — #187 da +69 s mashina + odam vaqti.
6. **`verify` sleep 10** — har deploy da kamida 10 s.

Lokal commit/push/PR/merge — 14 s, kesish shart emas.
