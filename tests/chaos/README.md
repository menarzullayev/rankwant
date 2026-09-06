# tests/chaos — fault injection

test-strategy.md § 14. **Faqat staging'da.**

```bash
I_UNDERSTAND_THIS_IS_STAGING=yes tests/chaos/run.sh
```

Skript servislarni ataylab buzadi va tiklaydi. Har qadamda tekshiriladi:

1. **Judge worker `kill -9`** — attempt yo'qolmasligi, qayta navbatga tushishi
2. **Redis DOWN** — submit rad etiladi, lekin `Attempt` yozuvi saqlanadi
3. **Postgres DOWN** — toza `503`, tiklangach normal davom
4. **DB kechikishi** — sekinlashadi, lekin yiqilmaydi

Kutilgan xatti-harakat: [10-operations § Recovery](../../docs/10-operations/README.md).
