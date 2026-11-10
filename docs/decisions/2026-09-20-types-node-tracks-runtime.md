| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **`@types/node` major = Node major** (HITL: 4 variant → Node 22 da qolish, #143 yopiladi). Dependabot `26.6.1` ni Node 22 ustiga qo'ymoqchi edi — `skipLibCheck` yolg'on yashil. Node 22 2027-04 gacha Maintenance LTS; 26 Current. Dependabot `@types/node` semver-major'ni ignore qiladi (22.x patch/minor keladi) | `.github/dependabot.yml`; `apps/web/package.json`; `apps/web/Dockerfile`; `.github/workflows/ci.yml`; `tools/check_decisions.py` → `types_node_tracks_runtime`; salbiy testlar 2 ta |
