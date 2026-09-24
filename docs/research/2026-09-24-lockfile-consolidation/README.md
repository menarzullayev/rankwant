# Lockfile consolidation — `apps/web/package-lock.json` removed

**Date:** 2026-09-24
**Decision record:** `CLAUDE.md` (row dated 2026-09-24)
**Outcome:** one authoritative lockfile at the repository root.

## Why the file existed

`apps/web/package-lock.json` was committed **before** the repo became an npm
workspace. Measured on 2026-09-24:

```
$ git show main:package.json
fatal: path 'package.json' does not exist in 'main'
```

There was no root `package.json` in `main`, so the web app's lockfile was the
only one. Once `package.json` gained `"workspaces": ["packages/*", "apps/*"]`,
npm hoisted the whole tree to the root and wrote a new root
`package-lock.json` — leaving the per-package file behind as a fossil.

## Why the two diverged

The files were **not** in a parent/child relationship. Measured entry counts:

| Lockfile | `packages` entries | knows `@rankwant/shared` |
| --- | --- | --- |
| root `package-lock.json` | 603 | yes |
| `apps/web/package-lock.json` | 694 | **no** |

630 entries existed only in the web lockfile. A web lockfile that does not
know `@rankwant/shared` exists will silently drop that workspace dependency
if it is ever used for install.

## Why removal was safe

Code already pointed at the root lockfile; only prose referenced the old one:

- `tools/licence_inventory.py` → `NODE_LOCKS["web"] = "package-lock.json"`
- `.github/workflows/ci.yml:254` → `cache-dependency-path: package-lock.json`
  (with the RW-ARCH-013 rationale comment)
- `CLAUDE.md:88` — a historical 2026-09-21 measurement, **left untouched**

Post-removal verification:

```
$ python tools/licence_inventory.py --check
✓ Litsenziya inventari joyida: 733 paket manbalarga mos
```

## Provenance of the removed file

The deletion cannot be reproduced from the archive alone: `.handoff/` is
gitignored, so the byte copy lives only on the machine that performed the
removal. This record is the tracked proof.

```
sha256 129e8edf0f2ac7ee6de074710373afa932b61faf23e57b277041ef94a2072234
size   375781 bytes
source apps/web/package-lock.json
         (tracked in `main` as blob 4b411114)
copy   .handoff/lockfile-archive/apps-web-package-lock.json.20260924
```

Recovery, if the file is ever needed again:

```bash
git show main:apps/web/package-lock.json > /tmp/old-web-lock.json
sha256sum /tmp/old-web-lock.json   # must equal 129e8edf…
```

The git object is the durable source of truth; the `.handoff/` copy is
convenience only.

## What replaced it

A single root `package-lock.json` (603 entries, resolves `@rankwant/shared`
and every workspace package), committed alongside this record.
