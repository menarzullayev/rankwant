# cp.uz algorithms import — analysis, 2026-11-11

Owner decision ③ of [content-and-archive](../../decisions/2026-11-11-content-and-archive.md):
import the cp.uz algorithms library (163 articles) under CC BY-SA 4.0, show the source and the
authors, and remove the one live algorithm article after it is confirmed. The order of work
([next-directions](../../decisions/2026-11-11-next-directions.md) ③) puts this after the
community features, with the bugs and UI problems met on the way fixed too.

Everything below was measured on 2026-11-11 from the local clone
`D:\Linux\Web_Projects\cp-uz` (`origin/main` = `91f90d7`, fetched the same day; the working
copy was three commits behind and was not changed) and from the live RankWant API.

## What cp.uz holds

**Repository.** `github.com/cp-uz/cp-uz`. Code is MIT; content is CC BY-SA 4.0
(`content/LICENSE-CC-BY-SA-4.0.txt`). The content is a portable snapshot with a deterministic
import contract (`content/exports/`), written for exactly this kind of import.

**Articles: 163**, Uzbek (Latin, with `‘` U+2018 in `o‘`/`g‘`).

- **Source.** Translations of [cp-algorithms](https://github.com/cp-algorithms/cp-algorithms) (CC BY-SA 4.0), pinned to upstream commit `85a9400`. They were migrated through `cp-uz/algo` at `f0b048b`.
- **Translator.** Recorded in the metadata as "OpenAI GPT-5.6 Pro / CP.UZ". Every article has `status: ai_full_translation_draft`.
- **Review: none.** 0 technical approvals and 0 language approvals. The cp.uz readme says so itself: "Public availability does not claim or replace either human review."
- **Levels.** Set by their editors: 58 beginner, 67 intermediate, 38 advanced.
- **13 categories.** graph 47, algebra 30, geometry 26, string 12, data structures 10, combinatorics 9, dynamic programming 7, numerical methods 5, others 5, linear algebra 4, schedules 3, sequences 3, game theory 2.
- **Size.** About 200 700 words, 466 code blocks, 401 links between articles (relative `*.md`), and 23 image references (47 image files: 45 PNG, 2 SVG).
- **Summaries.** Each article has a short Uzbek `idea`, `complexity` and `uses` in `metadata/articles.yml`.

**Practice links.** The cp.uz export lists 885 external exercise references. Under the
"Amaliy masalalar" headings we counted 435, by host:

| Host | Links |
|---|---|
| Codeforces | 112 |
| SPOJ | 103 |
| UVa | 79 |
| CodeChef | 27 |
| CSES | 15 |
| LeetCode | 12 |
| TopCoder | 10 |

**Glossary.** 174 terms, A–Z by the English term, with Uzbek name, aliases and a note
(`metadata/glossary.json`).

**Olympiad corpus — not part of decision ③**, but in the same repository:

- 103 problem statements: IOI 2026, EGOI 2026, APIO 2026, IZhO 2026 and IOI 2026 selection (round 4). These are statements only; there are no tests (0 test files).
- **Licences.** IOI 2026 and EGOI 2026 published their tasks under CC BY. The 12 selection statements were copied from KEP.uz, and cp.uz itself says no partnership or licence covers them.
- **People.** `content/seasons/` holds season and event JSON plus 197 participant profiles, which are personal data.

## What RankWant has today

- **`content.Article`.** It has `slug`, `kind` (`article` / `algorithm`), `title`, `summary`, `body` (Markdown + LaTeX), `locale`, `topics` (M2M to `problems.Topic`), `difficulty` (800–3500), `author`, `is_published` and `reading_minutes`.
- **What `Article` lacks:** source, licence, translator, review state, upstream revision, category, the short idea / complexity / uses, images and external links. There is no article translation model either; ADR-0058 covers problems only.
- **`ArticleProblemLink`.** It links an article to **our** problems only (practice / example / editorial).
- **Live articles: 4.** `kirish-cpp`, `dp-asoslari` and `graf-bfs-dfs` are kind `article`; **`ikkilik-qidiruv`** is kind `algorithm`. The last one is the "one live algorithm article" in decision ③, but deleting it waits for the owner's confirmation.
- **Live problems: 2 336 public.** 1 222 of them have a KEP.uz `source_url`; none points to Codeforces. So none of cp.uz's practice links resolves to one of our problems by URL.
- **Topics: 145**, with uz / ru / en names and a parent link.
- **Alphabet.** The new-alphabet converter (`packages/shared/src/alphabet.ts`) already accepts `‘`, `’`, `ʻ` and `'` as old apostrophes, so cp.uz text needs no rewrite before display.
- **Storage.** `problems.storage.put_media` stores media in S3, which is where the 47 images can go.

## Fixed constraints

- **ADR-0005** ("own content, cp.uz not a dependency") says any integration with cp.uz needs a new ADR. Importing copies the text, so nothing depends on cp.uz at run time. It is still a change of that ADR's stance and must be written down.
- **CC BY-SA 4.0** requires that we:
  - credit cp-algorithms contributors and CP.UZ, with links and the licence;
  - state that the text was changed;
  - license our adapted versions under CC BY-SA 4.0 too.

  ShareAlike applies to these articles, not to the rest of the site.
- **Quality.** The text is an unreviewed machine translation. Code and formulas were kept as in the original; the cp.uz metadata claims this ("formulas, code samples … retained"), and it can be checked mechanically against upstream.
- **No personal data imported without a basis:** the 197 participant profiles stay out.

## Decisions to discuss

Decided on 2026-11-11 in four rounds: [cpuz-import](../../decisions/2026-11-11-cpuz-import.md), [ADR-0062](../../07-adr/0062-cpuz-import.md).

1. **Licence and record.** A new ADR that amends ADR-0005, and the attribution block shown on each article.
2. **Quality gate before publishing.** Options: publish with a visible "AI translation, under review" mark; agent review first, as with Abramyan; or human review.
3. **Taxonomy.** Map the 13 categories to our 145 topics, or add a category field. The three levels: keep them as levels, or map them to the 800–3500 scale.
4. **Practice links.** Keep them as external links, add "similar problems here" picked by topic, or both.
5. **Images and internal links.** 47 files go to S3, and 401 `*.md` links are rewritten to our routes.
6. **Other languages.** The English cp-algorithms original (same licence) could serve as the `en` version. The other eight locales fall back to Uzbek.
7. **Updates.** A one-time snapshot, or a re-runnable import pinned to the cp.uz commit that never overwrites our own edits.
8. **Glossary.** Whether to import the 174 terms, and where they go: a page, search, tooltips.
9. **`ikkilik-qidiruv`.** Delete it and replace it with cp.uz's binary search article, once the owner confirms.
10. **Olympiad corpus.** Keep it as a separate decision (②), and leave the KEP statements and participant profiles out.
