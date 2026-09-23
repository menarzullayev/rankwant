# DECISION-DUALBOOT-01 — Rankwant Windows canonical path

**Sana:** 2026-09-23  
**Domain:** Architecture / boundary (dual-boot Shared NTFS)  
**Status:** Accepted → implemented

## Kontekst

- Ubuntu kanonik: `D:\Linux\Web_Projects\rankwant` (`/media/nsn/Shared/Linux/Web_Projects/rankwant`), `origin/main` @ `4f1321c`.
- Windows nusxa: `C:\Users\nsn\project\cp\rankwant` — `main` 2 commit orqada (`b8ee191`), stash bor, 8 ta git worktree C `.git` ga bog‘langan.
- Push qilinmagan commit yo‘q; D dagi “dirty” faqat NTFS `filemode` (755→644).
- Deploy/scriptlar ko‘p joyda `C:/Users/nsn/project/cp/rankwant` yo‘lini ishlatadi.

## Qaror

**Variant A:** D Shared — yagona canonical working tree; Windows legacy yo‘l **directory junction** orqali D ga ulanadi.

## Tanlangan variant

`C:\Users\nsn\project\cp\rankwant` → junction → `D:\Linux\Web_Projects\rankwant`

## Sabab

- GitHub bilan sinxron nusxa D da; C eski nusxa split-brain xavfini beradi.
- Junction mavjud Windows yo‘llarini (backup, deploy, parallel-agents) buzmasdan Shared NTFS bilan birlashtiradi.
- Ubuntu va Windows bir xil fayl tizimini ko‘radi.

## Trade-off

- Eski C `.git` (worktree + stash) **arxivga** ko‘chiriladi; worktree’lar vaqtincha arxiv `.git` ga `gitdir` patch orqali bog‘lanadi (keyingi qaror: worktree’larni D main ga qayta ulash).
- NTFS executable bit yo‘qolishi — Linuxda `core.filemode=false` yoki checkout; commit qilinmaydi.

## Ta’sirlangan komponentlar

- `C:\Users\nsn\project\cp\rankwant` (junction)
- `D:\Linux\Web_Projects\rankwant` (canonical)
- `D:\Windows\archive\rankwant-c-main-20260923` (retired C clone)
- `C:\Users\nsn\project\wt\*` worktree (gitdir yangilanadi)

## Validation (2026-09-23 implement)

| Check | Baseline | After |
|---|---|---|
| `C:\Users\nsn\project\cp\rankwant` HEAD | `b8ee191` (2 behind) | **`4f1321c`** (= `origin/main` oldin) |
| Junction | yo‘q (real C clone) | **Junction → `D:\Linux\Web_Projects\rankwant`** |
| Dirty (content) | 12× filemode (D) | **`core.filemode=false`** → faqat decision doc |
| Local commit | 0 | **`93fcfcd`** (decision doc; push → PR hook) |
| Eski C `.git` | `C:\...\rankwant` | **`D:\Windows\archive\rankwant-c-main-20260923`** + stash saqlangan |
| Worktree `wt/deploy` gitdir | C `.git/worktrees` | **arxiv `.git/worktrees`** (vaqtincha) |

**Eslatma:** `cloudflared` `.handoff` logi uchun vaqtincha to‘xtatildi; tunnel qayta ishga tushirish kerak bo‘lishi mumkin.
