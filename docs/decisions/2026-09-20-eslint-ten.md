| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **ESLint 10** (HITL: avval #154, keyin 10 + plugin tuzatish). `eslint-config-next@16.3.5` compiled babel parser ESLint 10 `ScopeManager.addGlobals` bermaydi (o'lchandi: `vitest.config.mts`). Parser = `typescript-eslint`. Next import/jsx-a11y/react pluginlari hali peer ^9 — npm override, lint yashil | `apps/web/eslint.config.mjs`; `apps/web/package.json`; `tools/check_decisions.py` → `eslint_ten_uses_ts_parser`; salbiy testlar 2 ta |
