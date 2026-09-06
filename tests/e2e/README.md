# tests/e2e — Playwright

test-strategy.md § 4. Ishlayotgan stack talab qiladi.

```bash
npm install && npm run install-browsers

# Stack ko'tarilgan bo'lishi kerak
E2E_BASE_URL=http://localhost:3000 \
E2E_API_BASE=http://localhost:8000/api/v1 \
npm test
```

## Nima qamrab olingan

| Spec | Oqim |
| ---- | ---- |
| `browse.spec.ts` | Ochiq sahifalar, SSR mazmuni, reyting formulalari ochiqligi |
| `submit-flow.spec.ts` | Ro'yxat → login → submit; PAT scope; IDOR |
| `contest.spec.ts` | Contest sahifasi va standings |

## Nega PR da ishlamaydi

Judge konteyneri `--privileged` talab qiladi va uni har PR da ko'tarish
qimmat. Bu testlar **staging deploy'dan keyin** ishlaydi
([10-operations § CI/CD](../../docs/10-operations/README.md)).
