"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { FM_INP, FM_LAB } from "@/components/form/chrome";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type Locale, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import {
  fromSiteInput,
  letterAt,
  parseUsernames,
  studioContests,
  toSiteInput,
  type ContestParticipant,
  type ContestScoring,
  type MineContest,
  type MineContestProblem,
} from "../api/contests";
import { slugify, type MineProblem } from "../api/problems";
import { CONTEST_TABS, DEFAULT_CONTEST_TAB, type ContestTab } from "../contest-tabs";

const TAB_LABEL: Record<ContestTab, MessageKey> = {
  settings: "studio.contest.tab.settings",
  problems: "studio.contest.tab.problems",
  participants: "studio.contest.tab.participants",
};

const SCORING: readonly { value: ContestScoring; key: MessageKey }[] = [
  { value: "acm", key: "admin.label.text.acmIcpc" },
  { value: "ioi", key: "admin.label.text.ioi" },
];

/** Field errors the server names, mapped to the page's own words. */
const FIELD_ERRORS: readonly { field: string; key: MessageKey }[] = [
  { field: "slug", key: "studio.error.slug" },
  { field: "end_at", key: "studio.error.endBeforeStart" },
  { field: "testers", key: "studio.error.testers" },
  { field: "problems", key: "studio.error.problems" },
];

function failure(locale: Locale, error: unknown): string {
  if (!(error instanceof ApiError)) return String(error);
  const known = FIELD_ERRORS.find((row) => error.details && row.field in error.details);
  return known ? t(locale, known.key) : errorText(locale, error.code);
}

type Settings = {
  slug: string;
  title: string;
  description: string;
  start: string;
  end: string;
  freeze: string;
  scoring: ContestScoring;
  testers: string;
};

/** A new contest starts a week ahead at 14:00 site time and lasts two
 *  hours — a draft needs some window, and this one is obviously a guess. */
function defaults(): Settings {
  const day = toSiteInput(new Date(Date.now() + 7 * 86_400_000).toISOString()).slice(0, 10);
  return {
    slug: "",
    title: "",
    description: "",
    start: `${day}T14:00`,
    end: `${day}T16:00`,
    freeze: "0",
    scoring: "acm",
    testers: "",
  };
}

function settingsOf(contest: MineContest | null): Settings {
  if (!contest) return defaults();
  return {
    slug: contest.slug,
    title: contest.title,
    description: contest.description,
    start: toSiteInput(contest.start_at),
    end: toSiteInput(contest.end_at),
    freeze: String(contest.freeze_minutes),
    scoring: contest.scoring_type,
    testers: contest.testers.join(", "),
  };
}

function ErrorLine({ text }: { text: string }) {
  if (!text) return null;
  return (
    <p role="alert" className="text-theme-sm rw-bad-ink">
      {text}
    </p>
  );
}

function SettingsForm({
  contest,
  onSaved,
}: {
  contest: MineContest | null;
  onSaved: (contest: MineContest) => void;
}) {
  const locale = useLocale();
  const router = useRouter();
  const confirm = useConfirm();
  const [saved, setSaved] = useState<Settings>(() => settingsOf(contest));
  const [form, setForm] = useState<Settings>(saved);
  const [slugTouched, setSlugTouched] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const creating = contest === null;
  const dirty = JSON.stringify(form) !== JSON.stringify(saved);

  function set<K extends keyof Settings>(key: K, value: Settings[K]) {
    setDone(false);
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      if (creating && key === "title" && !slugTouched) next.slug = slugify(String(value));
      return next;
    });
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = {
        title: form.title,
        description: form.description,
        start_at: fromSiteInput(form.start),
        end_at: fromSiteInput(form.end),
        freeze_minutes: Number(form.freeze) || 0,
        scoring_type: form.scoring,
        testers: parseUsernames(form.testers),
      };
      if (creating) {
        const made = await studioContests.create({ ...body, slug: form.slug });
        router.replace(`/studio/contests/${encodeURIComponent(made.slug)}` as Route);
        return;
      }
      const updated = await studioContests.update(contest.slug, body);
      const next = settingsOf(updated);
      setSaved(next);
      setForm(next);
      setDone(true);
      onSaved(updated);
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  async function remove(origin: HTMLElement) {
    if (!contest) return;
    const ok = await confirm(fill(t(locale, "studio.contest.deleteConfirm"), { title: contest.title }), {
      danger: true,
      confirmLabel: t(locale, "studio.contest.delete"),
      origin,
    });
    if (!ok) return;
    try {
      await studioContests.remove(contest.slug);
      router.replace("/studio/contests" as Route);
      router.refresh();
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-6 xl:grid-cols-2">
        <div className="space-y-4">
          <Field
            label={t(locale, "studio.field.title")}
            name="title"
            value={form.title}
            onChange={(event) => set("title", event.target.value)}
            required
            maxLength={200}
          />
          <Field
            label={t(locale, "studio.field.slug")}
            name="slug"
            value={form.slug}
            onChange={(event) => {
              setSlugTouched(true);
              set("slug", event.target.value);
            }}
            disabled={!creating}
            required
            maxLength={100}
            pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
            hint={t(locale, "studio.field.slugHint")}
          />
          <label className="block">
            <span className={FM_LAB}>{t(locale, "studio.contest.description")}</span>
            <textarea
              value={form.description}
              onChange={(event) => set("description", event.target.value)}
              rows={6}
              className={FM_INP}
            />
          </label>
        </div>
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label={t(locale, "studio.col.start")}
              name="start"
              type="datetime-local"
              value={form.start}
              onChange={(event) => set("start", event.target.value)}
              required
            />
            <Field
              label={t(locale, "studio.contest.end")}
              name="end"
              type="datetime-local"
              value={form.end}
              onChange={(event) => set("end", event.target.value)}
              required
            />
          </div>
          <p className="text-theme-xs rw-faint">{t(locale, "studio.contest.zoneHint")}</p>
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField
              label={t(locale, "studio.contest.scoring")}
              options={SCORING.map((row) => ({ value: row.value, label: t(locale, row.key) }))}
              value={form.scoring}
              onChange={(value) => set("scoring", value as ContestScoring)}
            />
            <Field
              label={t(locale, "studio.contest.freeze")}
              name="freeze"
              type="number"
              min={0}
              value={form.freeze}
              onChange={(event) => set("freeze", event.target.value)}
              hint={t(locale, "studio.contest.freezeHint")}
            />
          </div>
          <Field
            label={t(locale, "studio.contest.testers")}
            name="testers"
            value={form.testers}
            onChange={(event) => set("testers", event.target.value)}
            hint={t(locale, "studio.contest.testersHint")}
          />
          <p className="text-theme-xs rw-faint">{t(locale, "studio.contest.staffDecides")}</p>
        </div>
      </div>
      <ErrorLine text={error} />
      <div className="sticky bottom-0 flex flex-wrap items-center justify-end gap-3 border-t rw-divider rw-surface py-3">
        {contest && !contest.is_public && (
          <Button
            type="button"
            variant="outline"
            className="me-auto rw-bad-ink"
            onClick={(event) => void remove(event.currentTarget)}
          >
            {t(locale, "studio.contest.delete")}
          </Button>
        )}
        <span aria-live="polite" className="text-theme-xs rw-dim">
          {done ? t(locale, "studio.saved") : dirty ? t(locale, "studio.unsaved") : ""}
        </span>
        {dirty && !creating && (
          <Button type="button" variant="outline" onClick={() => setForm(saved)}>
            {t(locale, "studio.cancel")}
          </Button>
        )}
        <Button type="submit" busy={busy} disabled={!creating && !dirty}>
          {t(locale, creating ? "studio.create" : "studio.save")}
        </Button>
      </div>
    </form>
  );
}

type Row = { problem: string; title: string; points: number };

/** The contest's problems, from the organizer's own unpublished drafts.
 *  Letters follow the order; the list is saved whole. */
function ProblemsPanel({
  contest,
  drafts,
  onSaved,
}: {
  contest: MineContest;
  drafts: MineProblem[];
  onSaved: (problems: MineContestProblem[]) => void;
}) {
  const locale = useLocale();
  const initial = contest.problems.map((row) => ({
    problem: row.problem,
    title: row.title,
    points: row.points,
  }));
  const [saved, setSaved] = useState<Row[]>(initial);
  const [rows, setRows] = useState<Row[]>(initial);
  const [pick, setPick] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const dirty = JSON.stringify(rows) !== JSON.stringify(saved);
  const locked = contest.is_public;
  const ioi = contest.scoring_type === "ioi";
  const free = drafts.filter((draft) => !rows.some((row) => row.problem === draft.slug));

  function move(index: number, step: number) {
    setRows((prev) => {
      const next = [...prev];
      const target = index + step;
      const moved = next[index];
      const other = next[target];
      if (!moved || !other) return prev;
      next[index] = other;
      next[target] = moved;
      return next;
    });
  }

  function add() {
    const draft = drafts.find((row) => row.slug === pick);
    if (!draft) return;
    setRows((prev) => [...prev, { problem: draft.slug, title: draft.title, points: 100 }]);
    setPick("");
  }

  async function save() {
    setBusy(true);
    setError("");
    try {
      const result = await studioContests.setProblems(
        contest.slug,
        rows.map((row, index) => ({ problem: row.problem, index_letter: letterAt(index), points: row.points })),
      );
      const next = result.map((row) => ({ problem: row.problem, title: row.title, points: row.points }));
      setSaved(next);
      setRows(next);
      onSaved(result);
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-theme-sm rw-dim">
        {t(locale, locked ? "studio.contest.problemsLocked" : "studio.contest.problemsIntro")}
      </p>
      <Table>
        <THead>
          <TH>{t(locale, "studio.contest.letter")}</TH>
          <TH>{t(locale, "studio.col.problem")}</TH>
          {ioi && <TH align="right">{t(locale, "studio.contest.points")}</TH>}
          {!locked && <TH align="right">{t(locale, "studio.tests.actions")}</TH>}
        </THead>
        <TBody>
          {rows.length === 0 ? (
            <EmptyRow colSpan={4}>{t(locale, "studio.contest.noProblems")}</EmptyRow>
          ) : (
            rows.map((row, index) => (
              <TR key={row.problem}>
                <TD className="font-semibold">{letterAt(index)}</TD>
                <TD>
                  {row.title}
                  <span className="block font-mono text-theme-xs rw-faint">{row.problem}</span>
                </TD>
                {ioi && (
                  <TD align="right">
                    <input
                      type="number"
                      min={0}
                      value={row.points}
                      disabled={locked}
                      aria-label={fill(t(locale, "studio.contest.pointsOf"), { letter: letterAt(index) })}
                      onChange={(event) =>
                        setRows((prev) =>
                          prev.map((item, at) =>
                            at === index ? { ...item, points: Number(event.target.value) || 0 } : item,
                          ),
                        )
                      }
                      className={`${FM_INP} max-w-[6rem] text-right`}
                    />
                  </TD>
                )}
                {!locked && (
                  <TD align="right">
                    <span className="inline-flex flex-wrap justify-end gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        disabled={index === 0}
                        aria-label={fill(t(locale, "studio.contest.moveUp"), { letter: letterAt(index) })}
                        onClick={() => move(index, -1)}
                      >
                        ↑
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={index === rows.length - 1}
                        aria-label={fill(t(locale, "studio.contest.moveDown"), { letter: letterAt(index) })}
                        onClick={() => move(index, 1)}
                      >
                        ↓
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        className="rw-bad-ink"
                        onClick={() => setRows((prev) => prev.filter((_, at) => at !== index))}
                      >
                        {t(locale, "studio.contest.remove")}
                      </Button>
                    </span>
                  </TD>
                )}
              </TR>
            ))
          )}
        </TBody>
      </Table>
      {!locked && (
        <>
          {free.length > 0 ? (
            <div className="flex flex-wrap items-end gap-3">
              <div className="min-w-[14rem] flex-1">
                <SelectField
                  label={t(locale, "studio.contest.addProblem")}
                  placeholder={t(locale, "studio.contest.pickProblem")}
                  options={free.map((draft) => ({ value: draft.slug, label: draft.title, hint: draft.slug }))}
                  value={pick}
                  onChange={setPick}
                />
              </div>
              <Button type="button" variant="outline" disabled={!pick} onClick={add}>
                {t(locale, "studio.contest.add")}
              </Button>
            </div>
          ) : (
            <p className="text-theme-xs rw-faint">{t(locale, "studio.contest.noDrafts")}</p>
          )}
          <ErrorLine text={error} />
          <div className="flex justify-end">
            <Button type="button" busy={busy} disabled={!dirty} onClick={() => void save()}>
              {t(locale, "studio.save")}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

function ParticipantsPanel({ participants }: { participants: ContestParticipant[] }) {
  const locale = useLocale();
  return (
    <Table>
      <THead>
        <TH>{t(locale, "studio.contest.participant")}</TH>
        <TH>{t(locale, "studio.contest.registeredAt")}</TH>
      </THead>
      <TBody>
        {participants.length === 0 ? (
          <EmptyRow colSpan={2}>{t(locale, "studio.contest.noParticipants")}</EmptyRow>
        ) : (
          participants.map((row) => (
            <TR key={row.username}>
              <TD>
                {row.display_name || row.username}
                <span className="block font-mono text-theme-xs rw-faint">@{row.username}</span>
              </TD>
              <TD className="whitespace-nowrap font-mono text-theme-xs rw-dim">
                {numericStamp(row.registered_at)}
              </TD>
            </TR>
          ))
        )}
      </TBody>
    </Table>
  );
}

/** One contest: settings, problems and who registered. `?tab=` is kept
 *  in the address like the problem editor's. */
export function ContestEditor({
  initial,
  drafts,
  participants,
  initialTab,
}: {
  initial: MineContest | null;
  drafts: MineProblem[];
  participants: ContestParticipant[];
  initialTab: ContestTab;
}) {
  const locale = useLocale();
  const base = useId();
  const [contest, setContest] = useState<MineContest | null>(initial);
  const [tab, setTab] = useState<ContestTab>(initial ? initialTab : DEFAULT_CONTEST_TAB);

  function choose(next: ContestTab) {
    setTab(next);
    const url = new URL(window.location.href);
    if (next === DEFAULT_CONTEST_TAB) url.searchParams.delete("tab");
    else url.searchParams.set("tab", next);
    window.history.replaceState(null, "", url);
  }

  function onKey(event: React.KeyboardEvent<HTMLButtonElement>) {
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    const index = (CONTEST_TABS.indexOf(tab) + step + CONTEST_TABS.length) % CONTEST_TABS.length;
    const next = CONTEST_TABS[index] ?? DEFAULT_CONTEST_TAB;
    choose(next);
    document.getElementById(`${base}-${next}`)?.focus();
  }

  const heading = contest ? contest.title : t(locale, "studio.contests.new");
  return (
    <div className="space-y-4">
      <h1 className="text-title-sm font-bold rw-strong">{heading}</h1>
      {contest ? (
        <>
          <div
            role="tablist"
            aria-label={heading}
            className="rw-kit-tabs !flex-wrap !overflow-x-visible shadow-[inset_0_-1px_0_var(--rw-divider)]"
            data-kit-tabs="scroll"
          >
            {CONTEST_TABS.map((name) => (
              <button
                key={name}
                id={`${base}-${name}`}
                type="button"
                role="tab"
                aria-selected={tab === name}
                aria-controls={`${base}-panel`}
                tabIndex={tab === name ? 0 : -1}
                onClick={() => choose(name)}
                onKeyDown={onKey}
                className={`rw-kit-tab ${tab === name ? "rw-accent-ink" : "rw-dim rw-hover-strong"}`}
              >
                {t(locale, TAB_LABEL[name])}
              </button>
            ))}
          </div>
          <Card>
            <div id={`${base}-panel`} role="tabpanel" aria-labelledby={`${base}-${tab}`}>
              {tab === "settings" && <SettingsForm contest={contest} onSaved={setContest} />}
              {tab === "problems" && (
                <ProblemsPanel
                  contest={contest}
                  drafts={drafts}
                  onSaved={(problems) => setContest((prev) => prev && { ...prev, problems })}
                />
              )}
              {tab === "participants" && <ParticipantsPanel participants={participants} />}
            </div>
          </Card>
        </>
      ) : (
        <Card>
          <SettingsForm contest={null} onSaved={setContest} />
        </Card>
      )}
    </div>
  );
}
