# D55 — Live verify after bake

**Sana:** 2026-09-21  
**Qaror:** B — bake’dan keyin live verify  
**Tanlangan variant:** `live-verify`  
**CTO tavsiyasi:** B (qabul qilindi)

## Qaror

D48–D54 ni yangi arxitektura forkisiz, `https://rankwant.uz` da o‘lchash.
Mehmon sessiyasi; admin hisobining ko‘rinishiga tegilmaydi.

## O‘lchov (2026-09-21 ~04:50–04:56 +05)

| Manba | Qiymat |
|---|---|
| `origin/main` / deploy worktree | `2fd1e3d` (D54, #221) |
| Jonli `rankwant-web-1` `org.rankwant.git-sha` | `f4f9099` (D49, #216) |
| Jonli `org.rankwant.built-at` | `2026-09-20T23:28:13Z` |
| `deploy_scope.py --from-live --to HEAD` | `web` |
| Main `CI` `2fd1e3d` | yashil (`35545821187`, Web 1m40s) |
| `check_deploy.sh` | `rankwant-web-1` **ESKIRGAN** |

**Interfeys (mehmon, customizer ochiq, Interface accordion):**

- Kit oilalari hali **chip katalogi** (Automatic / Badge only / Lucide / Paper / Field…). Combobox / `SelectField` = **0**.
- Layout: Navigation Sidebar/Top bar chip (D53-ga mos, lekin D49 obrazida ham chip edi).
- Templates ochiqligida Import: native **Choose File / No file chosen** + **Load from file** (D54 jonli emas).

D51–D54 **mahsulot regressiyasi emas** — ishlayotgan obraz D49.

## Nega bake bo‘lmadi

Watcher driftni to‘g‘ri ko‘radi (`jonli f4f9099 ≠ main 2fd1e3d`), lekin
`check_deploy_gate.py` **exit 1**:

```text
commit qilinmagan compose — C:/Users/nsn/project/wt/workbuddy/adminer-declared: ?? docker-compose.tools.yml
```

`ADMINER-001` (workbuddy-1) `docker-compose.tools.yml` ni lock qilgan.
Darvoza **har** worktree’dagi `docker-compose*.yml` ni skanaydi.
CI yashil bo‘lsa ham `tools/deploy.sh` / Auto Deploy web ni qurmaydi.

`deploy.sh` scope=`web` da `up -d --no-deps web` — adminer konteyneriga
tegmas edi. Darvoza SCOPE’ni hisobga olmaydi.

## Trade-off

O‘lchov to‘liq post-bake UI tekshiruviga yetmadi. D51 SelectField,
D49 Klassik apply, D54 a11y — bake’dan keyin qayta o‘lchanadi.

## Ta’sir

Hujjat + o‘lchov. `apps/web` o‘zgarmadi.
