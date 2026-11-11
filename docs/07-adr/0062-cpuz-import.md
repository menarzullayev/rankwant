# ADR 0062 — cp.uz content import (amends ADR-0005)

**STATUS:** accepted
**Date:** 2026-11-11
**Approved by:** Saidakbar (owner). Decision records:
- [content and archive](../decisions/2026-11-11-content-and-archive.md) ③;
- [cp.uz import, 4 rounds](../decisions/2026-11-11-cpuz-import.md).

**Analysis:** [2026-11-11-cpuz-import](../research/2026-11-11-cpuz-import/README.md).

**Scope:**
- `content` (articles, categories, translations, external links, glossary, review log);
- a new olympiad seasons area;
- `problems` (statement-only olympiad problems);
- web `/algorithms`.

## 1. Context

ADR-0005 made RankWant's content its own: cp.uz was a competitor and benchmark, not a
dependency. It also said any later integration with cp.uz needs a new ADR. The owner has now
decided to import cp.uz's algorithms library and its olympiad catalogue.

Importing copies text. Nothing in RankWant calls cp.uz at run time, so the "no dependency"
half of ADR-0005 stands. The "own content only" half changes for these articles.

## 2. Decision

1. **Import, not link.** Articles, metadata, images, glossary, seasons, events, olympiad
   statements and participant profiles are imported from the cp.uz content snapshot
   (`content/` of `github.com/cp-uz/cp-uz`). Each import is pinned to a cp.uz commit and can be
   run again; an article we edited is never overwritten.
2. **Licence.** The articles are CC BY-SA 4.0, adapted from cp-algorithms. Every imported
   article shows:
   - its upstream title and link;
   - the cp-algorithms contributors and CP.UZ;
   - "translated with AI; reviewed by AI";
   - that RankWant changed it;
   - a link to the licence.

   Our adapted versions of these articles are CC BY-SA 4.0 as well. This does not spread to the
   rest of the site.
3. **Quality gate.** Code blocks and formulas are compared mechanically with the pinned
   upstream. Then an agent reviews each article technically and linguistically, fixes what it
   can and logs every change. An article it cannot fix stays a draft. Everything is published
   together.
4. **English.** The cp-algorithms original (same licence, same pinned commit) becomes the
   `en` version of each article. The other eight locales fall back to Uzbek.
5. **Practice.** External exercise links are kept and stored under a normalised key (host and
   problem id). A problem imported later with the same source is attached automatically. Next
   to them comes a topic-and-difficulty pick from our own problems; editor picks come first.
6. **Olympiad material** is taken as cp.uz has it. Two parts carry risks, accepted by the owner:
   - The 12 selection statements copied from KEP.uz carry no licence. They are shown with their
     source link and a "no partnership" note, and are removed on request.
   - The 197 participant profiles (name and country, from official results; most are school
     pupils) are personal data. A removal request is honoured.

## 3. Consequences

- `content.Article` gains:
  - category, level;
  - source and upstream revision;
  - translator and review state;
  - edited-by-us flag;
  - a translation table;
  - external links;
  - a review log.

  `docs/05` is not touched: articles are not among its locked entities' fields.
- `/algorithms/<category>/<slug>` replaces `/algorithms/<slug>`.
- The live `ikkilik-qidiruv` article is deleted without a redirect (owner decision ⑨).
- A glossary page, with tooltips inside articles.

## 4. Rejected

- **Linking to cp.uz instead of importing.** The text would live on another site, ADR-0005's "no dependency" would break, and our search and practice links would not reach it.
- **Publishing the AI drafts unreviewed.** cp.uz itself records zero technical and zero language approvals.

## 5. Order

1. Model, importer, image upload, link rewriting, external links, the mechanical code and
   formula check, and the `ikkilik-qidiruv` deletion.
2. Agent review of the 163 articles, with fixes and a review log.
3. Web: the `/algorithms` catalogue by category and level, the article page with attribution
   and practice, and the AI marks.
4. English originals.
5. Glossary page and tooltips.
6. Olympiad: seasons and events, statements, participant profiles.
7. Publish everything together.

## 6. Notes from the build

- **Images** are part of the vendored snapshot and are served as the web's static files
  (`apps/web/public/algorithms-media/`), not uploaded to S3: 1.8 MB, versioned with the text.
- **Markup.** Our renderer draws no raw HTML on purpose, so the snapshot builder turns mkdocs
  admonitions, tabs, fence attributes and the `<img>`, `<figure>`, `<center>` and `<a>` tags
  into Markdown. Prose, code and formulas are left as they are.
- **Section links.** The originals link to sections across articles by mkdocs' heading ids.
  The builder gives every heading (Uzbek and English) the original's id, moves a
  `<div id>` anchor onto the heading it marks, and points a link to a paragraph anchor at
  its section. The Uzbek alphabet converter leaves `{#id}` as written.
- **Practice section.** The text's own practice section is not drawn on the page: the same
  links are listed under "on other sites", next to the problems on this site.
- **Personal data stays out of the repository.** The repository is public and its history
  is permanent. The participant profiles and the KEP statements are imported into the
  database from a cp-uz clone on the host, so a removal request can still be honoured
  (owner, 2026-11-11).
