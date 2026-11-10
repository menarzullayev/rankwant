# Owner decisions

One file per decision of Saidakbar aka, the project owner, named
`YYYY-MM-DD-<slug>.md`. Each file holds the decision as a single table row
(`| Sana | Qaror | Kodda qayerda |`), in the language it was written in. The
one-line index lives in [`CLAUDE.md`](../../CLAUDE.md) § «Saidakbar aka
qarorlari», which every agent session loads.

An agent never overrides these decisions on its own, not even as an
"improvement". Changing one needs the owner's explicit approval, recorded in
the same PR as the code change: edit the file, or add a new file that says
which decision it replaces.

## Adding a decision

1. Create `docs/decisions/YYYY-MM-DD-<slug>.md` with the table header and one
   row; the row's date starts with the date in the file name.
2. Add one line to the index in `CLAUDE.md`, in date order and in the same
   shape as its neighbours: the date as a link to the file · the decision in
   a few words · `rule`. The last field is the `tools/check_decisions.py`
   rule function that guards the decision, or the file the decision lives in.

`tools/check_decisions.py` → `decisions_index_matches_files` fails when a
decision exists in one place only, when the index and the file disagree on
the date, when a file holds anything but exactly one row, when the index
names a rule that `check_decisions.py` does not have, when the index is out
of date order, or when a table row is written back into `CLAUDE.md`.

## Why the table moved (2026-11-10, audit Q-10)

The table had grown to 159 rows inside a 278 874-byte `CLAUDE.md`, which
every session loads in full, so the rules that matter were lost in it. On the
day of the move eleven PRs appended rows, and four of them hit merge conflicts
on that one table. A new decision is now a new file, so two PRs never edit
the same decision.
