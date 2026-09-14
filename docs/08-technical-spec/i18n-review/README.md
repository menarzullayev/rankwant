# Translation review sheets

Four languages ship in this app, but only some of them were translated by a
speaker of that language. The dictionaries for **Karakalpak (`kaa`)`,
**Kyrgyz (`ky`)`, **Tajik (`tg`)** and **Kazakh (`kk`)** were written by a
language model. They are plausible. Some are certainly wrong.

That is not a state CI can detect. A wrong word in a table header compiles,
type-checks and passes every check in this repository, and only the person
reading the screen notices. So the values are marked **unverified** rather
than trusted, and these sheets exist to get them verified.

## Files

| File | Language | Strings |
| --- | --- | --- |
| `kaa.md` | Karakalpak | see the file |
| `ky.md` | Kyrgyz | see the file |
| `tg.md` | Tajik | see the file |
| `kk.md` | Kazakh | see the file |

Each sheet has one row per string: the key, the **Uzbek source** the app was
written in, and the value a user of that language currently sees.

## How to review

Read column 3 against column 2. If the meaning is right, tick the last
column. If it is wrong, write the correct wording in it.

Two things are not mistakes and do not need changing:

- **Proper nouns and brand names** (`Qvant`, `ACM/ICPC`, `Aurora`,
  `Dashboard`) are identical in every language on purpose.
  `tools/check_i18n.py` lists them explicitly in `UNTRANSLATED_OK`, each
  with a reason.
- **Karakalpak and Uzbek share a large vocabulary.** `Kategoriya`, `Kod`,
  `Til`, `Xabar`, `Modul` and `Kim` are written the same way in both. The
  whitelist records that per key.

## Regenerating

The sheets are generated, not hand-written, because the dictionaries change
and a stale sheet is worse than none:

```sh
python tools/export_i18n_review.py                 # admin.* keys
python tools/export_i18n_review.py --prefix ""     # every key
python tools/export_i18n_review.py --prefix customizer.
```

After review, apply the corrections to
`apps/web/src/i18n/locales/<lang>.ts` and run `python tools/check_i18n.py`.
