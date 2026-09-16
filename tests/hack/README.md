# tests/hack — hack oqimi, haqiqiy judge bilan

[ADR-0020](../../docs/07-adr/0020-hacking.md) ning uch bosqichi (generator →
etalon yechim → himoyachi) birlik testlarida **soxta** judge bilan sinaladi:
bosqichlar tartibi tekshiriladi, lekin nsjail, kompilyatsiya, validatorning
chiqish kodi va S3 dagi test ma'lumoti umuman ishlatilmaydi. Bu skript
shularning hammasini bitta o'tishda o'tkazadi.

**Faqat izolyatsiyalangan stackda.** Jonli stack tegilmasligi uchun alohida
loyiha nomi va host portlarisiz (`docker-compose.ci.yml` portlarni olib
tashlaydi):

```bash
docker compose -p rwhack -f docker-compose.yml -f docker-compose.ci.yml \
  up -d --build postgres redis minio migrate api worker beat judge
docker compose -p rwhack exec -T api python manage.py shell < tests/hack/flow.py
docker compose -p rwhack down -v
```

Tekshiriladi:

1. **Himoyachining yechimi `AC`** — kompilyatsiya, sandbox va S3 dagi test
2. **Yaroqsiz kiritma `INVALID_INPUT`** — validator rad etadi, jarima YO'Q
3. **Rad etish sababi** — validatorning o'z xabari ko'rinadi
4. **Haqiqiy hack `SUCCESSFUL`** — himoyachining urinishi `HACKED`, test
   to'plamga qo'shiladi, yechilgan masala yozuvi bekor qilinadi va mukofot
   ledgerga tushadi

Nega kerak: shu skript aynan 3-bandni topdi. nsjail o'z ogohlantirishini
bolaning `stderr`iga yozadi, ya'ni foydalanuvchi validatorning xabari
o'rniga `[W][…] logParams():347 Process will be UID/EUID=0 …` ni ko'rardi —
soxta judge bilan bu sinf butunlay ko'rinmas edi
([sandbox.go](../../services/judge-go/sandbox.go), `--really_quiet`).

To'liq strategiya: [docs/10-operations/test-strategy.md](../../docs/10-operations/test-strategy.md)
