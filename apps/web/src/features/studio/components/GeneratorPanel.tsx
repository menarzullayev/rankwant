"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type MessageKey } from "@/i18n/messages";
import { ApiError, getJson, postJson, putJson, type Paginated } from "@/lib/api";

import type { DraftTest } from "../api/problems";

type Language = { code: string; name: string; version: string };
type Program = { language: string; source: string; updated_at: string };
type Run = {
  id: number;
  status: "running" | "done" | "failed";
  group: string;
  total: number;
  current: number;
  made: number;
  bytes_written: number;
  error: string;
  created_at: string;
  finished_at: string | null;
};

/** The three programs of a generated test: the generator writes the input,
 *  the validator checks it, the reference solution answers it. */
const PROGRAMS: readonly { path: string; key: MessageKey; hint: MessageKey; required: boolean }[] = [
  { path: "generator", key: "studio.gen.generator", hint: "studio.gen.generatorHint", required: true },
  { path: "reference-solution", key: "studio.gen.reference", hint: "studio.gen.referenceHint", required: true },
  { path: "validator", key: "studio.gen.validator", hint: "studio.gen.validatorHint", required: false },
];

const GROUPS: readonly { value: string; key: MessageKey }[] = [
  { value: "random", key: "studio.gen.group.random" },
  { value: "boundary", key: "studio.gen.group.boundary" },
  { value: "maximum", key: "studio.gen.group.maximum" },
  { value: "stress", key: "studio.gen.group.stress" },
  { value: "special", key: "studio.gen.group.special" },
];

const STATUS: Record<Run["status"], { key: MessageKey; color: BadgeColor }> = {
  running: { key: "studio.gen.status.running", color: "warning" },
  done: { key: "studio.gen.status.done", color: "success" },
  failed: { key: "studio.gen.status.failed", color: "error" },
};

function ProgramEditor({
  base,
  path,
  label,
  hint,
  languages,
}: {
  base: string;
  path: string;
  label: string;
  hint: string;
  languages: Language[];
}) {
  const locale = useLocale();
  const [language, setLanguage] = useState("");
  const [source, setSource] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<Program>(`${base}${path}/`)
      .then((program) => {
        setLanguage(program.language);
        setSource(program.source);
        setSaved(true);
      })
      .catch(() => setSaved(false));
  }, [base, path]);

  async function save() {
    setBusy(true);
    setError("");
    try {
      await putJson(`${base}${path}/`, { language, source });
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    // The hint grows so the three editors line up whatever the hint's length.
    <div className="flex flex-col gap-2 rw-radius-sm border rw-line p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-theme-sm font-semibold rw-strong">{label}</h3>
        {saved && <Badge color="success">{t(locale, "studio.gen.saved")}</Badge>}
      </div>
      <p className="grow text-theme-xs rw-dim">{hint}</p>
      <SelectField
        name={`${path}-language`}
        label={t(locale, "studio.questions.codeLanguage")}
        placeholder={t(locale, "classroom.course.pickPlaceholder")}
        options={languages.map((l) => ({ value: l.code, label: `${l.name} ${l.version}` }))}
        value={language}
        onChange={setLanguage}
      />
      <textarea
        rows={8}
        value={source}
        aria-label={label}
        onChange={(event) => {
          setSource(event.target.value);
          setSaved(false);
        }}
        className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 font-mono text-theme-xs"
      />
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <div>
        <Button
          variant="outline"
          busy={busy}
          disabled={!language || !source.trim()}
          onClick={() => void save()}
        >
          {t(locale, "studio.gen.save")}
        </Button>
      </div>
    </div>
  );
}

/** The test generator of one draft (ADR-0061 § 6): one line of parameters
 *  per test; the made tests join the draft's tests. */
export function GeneratorPanel({
  slug,
  locked,
  onTests,
}: {
  slug: string;
  locked: boolean;
  onTests: (tests: DraftTest[]) => void;
}) {
  const locale = useLocale();
  const base = `/staff/problems/${encodeURIComponent(slug)}/`;
  const [languages, setLanguages] = useState<Language[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [lines, setLines] = useState("");
  const [group, setGroup] = useState("random");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const linesId = useId();
  const made = useRef<number | null>(null);
  // The editor passes a new function each render; the poll must not restart.
  const report = useRef(onTests);
  useEffect(() => {
    report.current = onTests;
  }, [onTests]);

  const loadRuns = useCallback(() => {
    getJson<Run[]>(`${base}generate/`)
      .then((rows) => {
        setRuns(rows);
        // A run made new tests: the tests tab and its count follow.
        const total = rows.reduce((sum, row) => sum + row.made, 0);
        if (made.current !== null && total !== made.current) {
          getJson<DraftTest[]>(`${base}tests/`)
            .then((tests) => report.current(tests))
            .catch(() => {});
        }
        made.current = total;
      })
      .catch(() => setRuns([]));
  }, [base]);

  useEffect(() => {
    getJson<Paginated<Language>>("/languages/?page_size=100")
      .then((page) => setLanguages(page.results))
      .catch(() => setLanguages([]));
    loadRuns();
  }, [loadRuns]);

  const running = runs.some((run) => run.status === "running");
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(loadRuns, 3000);
    return () => window.clearInterval(timer);
  }, [running, loadRuns]);

  const count = lines.split("\n").filter((line) => line.trim()).length;

  async function start() {
    setBusy(true);
    setError("");
    try {
      await postJson(`${base}generate/`, { lines, group });
      loadRuns();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
      // A refused start may still have left a run behind: show it.
      loadRuns();
    }
  }

  if (locked) return <p className="text-theme-sm rw-dim">{t(locale, "studio.review.public")}</p>;

  return (
    <div className="space-y-5">
      <p className="text-theme-sm rw-dim">{t(locale, "studio.gen.intro")}</p>
      <div className="grid gap-4 lg:grid-cols-3">
        {PROGRAMS.map((program) => (
          <ProgramEditor
            key={program.path}
            base={base}
            path={program.path}
            label={t(locale, program.key)}
            hint={t(locale, program.hint)}
            languages={languages}
          />
        ))}
      </div>

      <div className="space-y-3">
        <div className="space-y-1">
          <label htmlFor={linesId} className="block text-theme-sm font-medium rw-strong">
            {t(locale, "studio.gen.lines")}
          </label>
          <p id={`${linesId}-hint`} className="text-theme-xs rw-dim">
            {t(locale, "studio.gen.linesHint")}
          </p>
          <textarea
            id={linesId}
            aria-describedby={`${linesId}-hint`}
            rows={6}
            value={lines}
            onChange={(event) => setLines(event.target.value)}
            className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 font-mono text-theme-xs"
          />
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-48">
            <SelectField
              name="group"
              label={t(locale, "studio.gen.group")}
              options={GROUPS.map((g) => ({ value: g.value, label: t(locale, g.key) }))}
              value={group}
              onChange={setGroup}
            />
          </div>
          <Button busy={busy} disabled={running || count === 0 || count > 100} onClick={() => void start()}>
            {fill(t(locale, "studio.gen.start"), { count })}
          </Button>
          {count > 100 && <span className="text-theme-xs rw-bad-ink">{t(locale, "error.generation_too_many")}</span>}
        </div>
        {error && (
          <p role="alert" className="text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}
      </div>

      {runs.length > 0 && (
        <ul className="divide-y rw-divide rw-radius-sm border rw-line">
          {runs.map((run) => (
            <li key={run.id} className="space-y-1 px-4 py-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge color={STATUS[run.status].color}>{t(locale, STATUS[run.status].key)}</Badge>
                <span className="text-theme-sm tabular-nums rw-strong">
                  {fill(t(locale, "studio.gen.progress"), { made: run.made, total: run.total })}
                </span>
                <span className="text-theme-xs rw-faint">
                  {fill(t(locale, "studio.gen.size"), {
                    size: (run.bytes_written / (1024 * 1024)).toFixed(2),
                  })}
                </span>
              </div>
              {run.error && <p className="text-theme-xs rw-bad-ink">{run.error}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
