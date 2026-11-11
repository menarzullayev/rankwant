# ADR 0063 — Partner contests, official qualifiers and mirrors (amends the locked contest model)

**STATUS:** accepted
**Date:** 2026-11-12
**Approved by:** Saidakbar (owner). Decision record:
[community and contests](../decisions/2026-11-11-community-and-contests.md) ②.

**Scope:** `contests` (model, staff and organizer API, public API), `olympiads` (event detail),
web contest pages and the staff panel.

## 1. Context

The owner chose four contest additions on 2026-11-10 (decision ②): standings by region, the
statements as a PDF, **partner contests** («tashkilot nomi, logosi va sovrinlar bloki») and
**official olympiad qualifiers and mirrors** («rasmiy olimpiadalar saralash bosqichini
platformada o'tkazish va mirror qilish»). The first two need no model change and shipped in
#558. The last two add fields to `Contest`, which `docs/05-domain-model` locks, so they are
recorded here.

`Contest.mirror_of` (self FK) is already in the locked model. The staff panel and
`contests.services.create_mirror` set it, and `create_mirror` already made a mirror unrated, but
no page showed it and nothing stopped the staff panel from rating one. Most official olympiads that RankWant would mirror
are not RankWant contests: they are events of the olympiad archive (ADR-0062, `olympiads`).

## 2. Decision

1. **Organizations.** A new model `contests.Organization`: slug, name, kind (school,
   university, learning centre, company, community, government), logo, website, about. A
   contest may name one as its **partner** (`Contest.partner`). One organization runs many
   contests, so it is a row, not text on each contest.
2. **Prizes.** `Contest.prizes` is Markdown, shown as its own block on the contest page. The
   organizer of a draft may write it (ADR-0025); prizes are theirs to promise.
3. **Official qualifier.** `Contest.official_title` and `Contest.official_url`: what the contest
   officially is (for example «Respublika olimpiadasi, saralash bosqichi») and the document that
   says so. A filled title shows an «official» badge with the link.
4. **Mirrors.** A contest mirrors either another RankWant contest (`mirror_of`, now shown) or an
   olympiad archive event (`mirror_of_event`, new). The contest page names the original; the
   original's page, and the archive event page, list their mirrors.
5. **Who sets what.** Partner, official title and link, and both mirror links are **staff
   only**. An organizer could otherwise claim a university's name or an official status for
   their own contest. The organizer API exposes them read-only.
6. **A mirror is never rated.** Its problems were already set elsewhere, so a participant may
   know them. The database refuses a rated mirror (`CheckConstraint`), and the staff API says
   why. On 2026-11-12 production had 3 contests and no mirror, so the constraint refuses no
   existing row.
7. **Logos are addresses, not uploads.** A logo is a site path or an `https://` URL, as for team
   photos; `javascript:`, `http://`, `//host` and `data:` are refused. `official_url` and
   `website` must be `https://`.

## 3. Consequences

- The contest list and page show partner, official and mirror marks; the olympiad event page
  links to its mirror contests.
- An organization is managed in the staff panel; deleting one leaves its contests without a
  partner (`SET_NULL`), the contests themselves stay.
- Official status is a claim the staff make by hand, with a link the reader can check. Nothing
  verifies it against the ministry or the agency; the partnership work is outside the code.
- `docs/05-domain-model` stays locked; this ADR is the amendment.
