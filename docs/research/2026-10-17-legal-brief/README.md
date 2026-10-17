# Brief for legal counsel

**Date:** 2026-10-17 · **Prepared for:** the platform owner, to hand to counsel
**Gate:** `docs/09-development-plan/README.md` — "Huquqiy: litsenziya tahlili yurist tomonidan tasdiqlangan".

> This is a fact sheet and a list of questions, **not** a legal opinion. Every
> statement under "Owner's answers" is the owner's own, given on 2026-10-17;
> the agent that wrote this did not verify them against external records.
> The gate checkbox stays unchecked until counsel has signed off.

## 1. Scope the owner wants counsel to cover

1. Dependency licences (the literal gate item).
2. Problem content imported from other platforms.
3. Terms of service, privacy policy and personal data.
4. Company registration and the path to revenue.

## 2. Owner's answers (facts as stated)

| # | Topic | Answer |
|---|---|---|
| 1 | Operator | **No legal entity yet** — the project is run by the owner as a natural person. |
| 2 | Revenue | Not charging now. Subscriptions/payments are planned; advertising and sponsorship are planned for later. |
| 3 | Imported accounts | About 974 thousand accounts, imported through **public APIs, public data only** (handle, rating, rank). |
| 4 | Problem content | Currently imported **only from kep.uz**, without tests, generators or checkers. Planned: import from kep.uz, robocontest.uz, codeforces.uz, leetcode.uz and clist.by, with tests/checkers written by the team. Original problems are planned for later. |
| 5 | Terms / Privacy | Written by the owner / AI. **No lawyer has seen them.** |
| 6 | Personal data | Wide profile: address, job, education, phone (see § 4). |
| 7 | Hosting | Database is local (one Windows host). Third-party services are external (see § 4). |
| 8 | User content | Code stays the user's; the platform may publish it, process it and delete it at any time ("full rights" to do so). |
| 9 | Brand | Owner states the name "RankWant" was checked and no conflict was found. Nothing is registered as a trademark (not stated; counsel to confirm). |

## 3. Questions for counsel

### A. Problem content (highest exposure)
1. Is importing problem statements from kep.uz, robocontest.uz, codeforces.uz, leetcode.uz and clist.by lawful, with or without the original tests? Does it matter whether the statement is translated, rewritten, or only the idea is kept?
2. Do any of those sites' terms of service forbid copying or scraping their problems? (Counsel should read the current terms of each; the agent did not.)
3. What attribution, licence statement or takedown process do we need? Should imported problems be removed before launch and replaced by original ones?
4. Does the answer change once the platform earns revenue?

### B. Dependency licences
Inventory: `docs/research/2026-09-21-licence-inventory/README.md` (877 packages, 10 base images; snapshot 2026-09-21, to be regenerated).

5. **26 packages have no determined licence** (21 are Go modules of `services/judge-go`, which ships; 4 Node, 1 Python). Counsel or we must resolve them; the agent will fill the Go ones from `go.mod`/module sources before handoff.
6. **4 packages need a reading**: `python-dateutil` ("Dual License"), `caniuse-lite` (`CC-BY-4.0`, a content licence on a code dependency), and two more listed in the inventory.
7. **Weak copyleft:** `@img/sharp-libvips-*` is LGPL-3.0 (Next.js image optimiser, runtime). Are we compliant when serving it as a hosted service? No strong copyleft was found (0).
8. Base images (nsjail, language toolchains) are not in the package count: do they need review?
9. Hosted-service use (no distribution) versus any future distribution of the software.

### C. Terms, privacy, personal data
10. The Terms and Privacy pages were not written by a lawyer. Please review or replace them (ADR-0016 requires them to be reachable from every page).
11. Personal data held: email, username, password hash, address, job, education, phone; about 974k imported accounts with public data. What is the lawful basis, and do the imported accounts need notice or consent?
12. Which Uzbek law governs personal data here, and does it require storing data in Uzbekistan? The database is local; email delivery, OAuth (Google/GitHub/Telegram) and the CDN (Cloudflare) process data outside it. What agreements and disclosures are needed?
13. Are minors among the users (school students are a likely audience)? What consent is needed?
14. Account deletion exists (14-day grace, then anonymisation). Does it satisfy erasure duties? Imported accounts cannot be deleted by policy — is that acceptable?
15. User content: is a licence of "user keeps ownership; platform may publish, process and remove" sufficient, or does it need explicit wording in the Terms? Public solutions raise a plagiarism question for contests.

### D. Company and revenue
16. Which form should operate the platform (individual entrepreneur or LLC) and when should registration happen relative to accepting payments or ads?
17. Liability of a natural person operating a public platform today.
18. What is needed before charging users, selling the in-platform currency (Qvant), or selling advertising?
19. Trademark: should "RankWant" and the logo be registered, and where?

## 4. Reference facts about the system

- Data stack: one PostgreSQL on a single host; Redis; MinIO object storage; Cloudflare tunnel and CDN in front. Backups are local only (decision 2026-09-17).
- External processors: Cloudflare, an email chain (Mailjet / Brevo / Resend / MailerSend), sign-in via Google, GitHub and Telegram, Turnstile.
- Registration is open; abuse controls exist (login throttle, Turnstile).
- Search engines are allowed to index the site; AI crawlers are blocked; `/users/` profiles are `noindex`.
- Translations to 10 languages are machine-made and not reviewed by native speakers (`threat-model.md` A-8).
- Related: `docs/10-operations/threat-model.md`, ADR-0016 (sign-up and login), ADR-0023 (indexing).

## 5. Live Terms and Privacy text, and where it disagrees with the system

The live text is in `apps/web/src/content/legal.ts` (Uzbek, Russian, English;
other languages fall back to Uzbek). Both documents carry the date
`2026-09-10`. Counsel should read that file; it is the exact text users see at
`/terms` and `/privacy`.

Measured on 2026-10-17, the **Privacy policy lists** username, email, password
hash, optional display name / bio / avatar link / language / Telegram id,
activity (submissions and their code, verdicts, ratings, contest results, Qvant
transactions), and the IP address and browser name on a password reset. It says
school students are a target audience and that age is neither asked nor stored.

The **system holds more than that**. `User` has 67 fields since 2026-09-18
(ADR-0024), among them phone (`phone`), a delivery address for prizes
(`postal_*`), device fingerprint, plan, and the education and work blocks in
settings. None of phone, postal address, device fingerprint, education or work
appears in the policy text. The policy also does not mention the ~974 thousand
imported accounts or that deletion is refused for them. This is a gap between
the published policy and the data actually kept; it is the first thing to fix
whatever counsel decides about the rest.

Not checked by the agent: whether each of those fields is actually filled in
production, and the law that applies to them.

## 6. Licence inventory status (2026-10-17)

After reading the 21 Go modules' LICENSE files (Apache-2.0, MIT, BSD), UNKNOWN
fell from 26 to 4: the four left are this repository's own workspace packages,
which are not third-party dependencies.
Needs-a-reading stays at 4; weak copyleft at 50 (LGPL/MPL); strong copyleft 0.
