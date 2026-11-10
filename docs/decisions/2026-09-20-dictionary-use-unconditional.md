| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **Lug'at `use()` shartsiz** (HITL: lh-react-467). `if (window && !hasMessages) use(loadDictionary)` hidratsiyada hook qo'shardi — React #467, Best practices 96 (AFTER-08, Slow 4G + inline HTML). `use(dictionaryReady)` + barqaror `READY` | `LocaleProvider.tsx`; `tools/check_decisions.py` → `locale_use_is_unconditional`; salbiy test 1 ta |
