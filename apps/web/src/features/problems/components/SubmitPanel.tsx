"use client";

import type { Route } from "next";
import { playSuccess } from "@/lib/prefs";
import Link from "next/link";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, type Locale, t } from "@/i18n/messages";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import { CopyButton } from "@/components/kit/CopyControl";
import { FormFile } from "@/components/form/FormKit";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dropdown } from "@/components/ui/Dropdown";
import { Loading } from "@/components/ui/Loading";
import { Status } from "@/components/ui/Status";
import { Verdict } from "@/components/ui/Verdict";
import { defaultLanguage, editorLanguage, starterSource } from "@/lib/editor-language";
import { isPendingVerdict } from "@/lib/theme/verdict";
import {
  EVENT_ATTEMPT_PROGRESS,
  EVENT_ATTEMPT_QUEUED,
  EVENT_ATTEMPT_FINISHED,
  EVENT_COMPILATION_FINISHED,
  EVENT_COMPILATION_STARTED,
  EVENT_RESYNC,
  EVENT_TEST_FINISHED,
  EVENT_TEST_STARTED,
  EVENT_VERDICT,
  useEventStream,
} from "@/lib/useEventStream";
import { AttemptLiveProgress } from "@/features/submissions/components/AttemptLiveProgress";
import {
  emptyLiveState,
  reduceLiveState,
  type AttemptLiveState,
} from "@/features/submissions/attemptLiveState";
import { useSession } from "@/context/SessionContext";
import { ApiError } from "@/lib/api";
import { fieldErrors, SOURCE_MAX_BYTES, sourceSchema } from "@rankwant/shared/validation";
import {
  fetchAttempt,
  fetchCustomRun,
  runCustomTest,
  submitAttempt,
  type AttemptDetail,
  type CustomRun,
  type ProblemLanguage,
  type Sample,
} from "@/lib/api";
import CodeEditor from "./CodeEditor";
import {
  SampleTestConsole,
  sampleConsoleIdleState,
  type SampleConsoleState,
} from "./SampleTestConsole";
import { AttemptVerdictPanel } from "./AttemptVerdictPanel";
import {
  useProblemSolve,
  useVerdictLayoutMode,
} from "./problem-solve-context";

const MAX_SOURCE_BYTES = SOURCE_MAX_BYTES;

/** Ikki ustunli ko'rinishda muharrir MATN BILAN BIRGA aylanmasin.
 *
 * O'lchandi: 1440×900 da matn ustuni 1825 px, muharrir esa 772 px.
 * Namunalargacha aylantirilganda muharrir ekrandan 949 px yuqoriga
 * chiqib ketardi — ya'ni masalani o'qib bo'lib, kod yozish uchun
 * qaytib yuqoriga ko'tarilish kerak edi. KEP va RoboContest ikkalasi
 * ham panellarni alohida aylantiradi.
 *
 * Faqat `xl` da: undan pastda muharrir matn ostida turadi va u yerda
 * yopishtirish noto'g'ri bo'lardi. Balandligi ekranga sig'masa
 * (uzun verdikt ro'yxati) panelning o'zi aylanadi.
 */
// `min-w-0` — grid farzandining standart `min-width: auto` uni
// MAZMUNIDAN kichik qilmaydi, ya'ni Monaco butun sahifani cho'zib
// yuboradi. O'lchandi: 412 px li telefonda masala sahifasi 600 px
// bo'lib, yon tomonga siljirdi va tab tugmalarini bosib bo'lmasdi.
const PANEL =
  // The editor takes what the screen leaves: 100vh minus the header and
  // everything else in the panel (35.25rem, measured). The panel then
  // fits without a scrollbar of its own on a laptop screen.
  "min-w-0 space-y-4 xl:sticky xl:top-20 xl:max-h-[calc(100vh-5.5rem)] xl:rw-scroll-y xl:[--rw-editor-h:clamp(240px,calc(100vh-35.25rem),640px)]";

/** Verdikt uchun SSE (ADR-0029) + polling zaxirasi — oqim uzilsa ham yangilanadi.
 * Birinchi soniyalarda tez, keyin siyrak: kompilyatsiya + testlar odatda
 * 1–3 s, lekin navbat band bo'lsa uzoq kutish ham bo'ladi. */
const POLL_FAST_MS = 800;
const POLL_SLOW_MS = 2500;
const POLL_FAST_COUNT = 12;
const POLL_LIMIT = 90;

const draftKey = (problem: string, language: string) =>
  `rw:draft:${problem}:${language}`;

const testsKey = (problem: string) => `rw:tests:${problem}`;

/** Saqlangan o'z testlari. Buzuq qiymat bo'lsa bitta bo'sh test. */
function parseTests(raw: string | null): string[] {
  if (!raw) return [""];
  try {
    const value: unknown = JSON.parse(raw);
    if (Array.isArray(value) && value.every((v) => typeof v === "string")) {
      return value.length ? value : [""];
    }
  } catch {
    // Eski format yoki buzuq yozuv — bo'sh testdan boshlaymiz.
  }
  return [""];
}

function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Private rejim — qoralama saqlanmaydi, tahrirlash baribir ishlaydi.
  }
}

/** `localStorage` o'zi xabar bermaydi (`storage` hodisasi faqat boshqa
 * tabdan keladi) — obuna bo'sh. `useSyncExternalStore` bu yerda SSR
 * uchun kerak: server `null` beradi, hidratsiyadan keyin brauzerdagi
 * qiymat qo'yiladi, ya'ni effektda setState chaqirilmaydi. */
const NO_SUBSCRIBE = () => () => {};

function useStored(key: string): string | null {
  return useSyncExternalStore(
    NO_SUBSCRIBE,
    () => readStorage(key),
    () => null,
  );
}

type Tab = "verdict" | "samples" | "custom";

type SampleResult = {
  order: number;
  ok: boolean;
  got: string;
  expected: string;
  verdict: string;
};

/** Standart checker satr oxiridagi bo'shliqni va oxirgi bo'sh qatorni
 * hisobga olmaydi — namunani taqqoslash ham shunday bo'lishi kerak,
 * aks holda to'g'ri yechim «xato» ko'rinardi. */
const normalise = (text: string) =>
  text
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.trimEnd())
    .join("\n")
    .trimEnd();

export function SubmitPanel({
  problem,
  languages,
  samples,
  contest,
  hasTests,
}: {
  problem: string;
  languages: ProblemLanguage[];
  samples: Sample[];
  contest?: string;
  hasTests: boolean;
}) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const solve = useProblemSolve();
  const [verdictLayout] = useVerdictLayoutMode();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("verdict");

  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);

  // Bir nechta o'z testi: chegaraviy holatlarni sinashda bitta maydon
  // yetmaydi — yangisini yozish eskisini o'chirib yuborardi. Kod
  // qoralamasi kabi brauzerda saqlanadi.
  const tests = testsKey(problem);
  const storedTests = useStored(tests);
  const [editedTests, setEditedTests] = useState<string[] | null>(null);
  const customTests = editedTests ?? parseTests(storedTests);
  const [activeTest, setActiveTest] = useState(0);
  const current = Math.min(activeTest, customTests.length - 1);

  const [customRun, setCustomRun] = useState<CustomRun | null>(null);
  // Natija qaysi testniki — tab almashganda begona natija ko'rinmasin.
  const [runFor, setRunFor] = useState<number | null>(null);
  const [sampleResults, setSampleResults] = useState<SampleResult[]>([]);
  const [selectedSample, setSelectedSample] = useState(
    () => samples[0]?.order ?? 1,
  );
  const [consoleState, setConsoleState] = useState<SampleConsoleState>(() =>
    sampleConsoleIdleState(locale),
  );

  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const watchAttemptId = useRef<number | null>(null);
  const seenStreamEventIds = useRef(new Set<string>());
  const [streamAttemptId, setStreamAttemptId] = useState<number | undefined>();
  const [liveSubmit, setLiveSubmit] = useState<AttemptLiveState>(() => emptyLiveState());

  const finishAttempt = useCallback((next: AttemptDetail) => {
    setAttempt(next);
    if (!isPendingVerdict(next.verdict)) {
      setBusy(false);
      if (next.verdict === "AC") playSuccess();
    }
  }, []);

  const refreshWatchAttempt = useCallback(
    (id: number) => {
      fetchAttempt(id).then(finishAttempt).catch(() => setBusy(false));
    },
    [finishAttempt],
  );

  useEventStream({
    enabled: ready && !!user && busy && streamAttemptId !== undefined,
    attempt: streamAttemptId,
    onEvent: (name, data, meta) => {
      const id = watchAttemptId.current;
      if (id === null) return;
      if (meta?.eventId) {
        if (seenStreamEventIds.current.has(meta.eventId)) return;
        seenStreamEventIds.current.add(meta.eventId);
        if (seenStreamEventIds.current.size > 4096) {
          seenStreamEventIds.current.clear();
        }
      }
      if (name === EVENT_RESYNC) {
        refreshWatchAttempt(id);
        return;
      }
      const payload = data as { attempt_id?: number } | null;
      if (payload?.attempt_id !== id) return;
      const liveEvents = [
        EVENT_ATTEMPT_QUEUED,
        EVENT_ATTEMPT_PROGRESS,
        EVENT_TEST_STARTED,
        EVENT_COMPILATION_STARTED,
        EVENT_COMPILATION_FINISHED,
        EVENT_TEST_FINISHED,
        EVENT_VERDICT,
        EVENT_ATTEMPT_FINISHED,
      ];
      if (liveEvents.includes(name)) {
        setLiveSubmit((prev) =>
          reduceLiveState(prev, name, data as Record<string, unknown>),
        );
      }
      if (name === EVENT_VERDICT || name === EVENT_ATTEMPT_FINISHED) {
        refreshWatchAttempt(id);
      } else if (name === EVENT_TEST_FINISHED) {
        refreshWatchAttempt(id);
      }
    },
  });

  // Tanlangan til qurilmada eslab qolinadi — har masalada qayta
  // tanlash asosiy oqimdagi eng ko'p takrorlanadigan ortiqcha qadam.
  const [pickedLanguage, setPickedLanguage] = useState<string | null>(null);
  const storedLanguage = useStored("rw:language");
  const language =
    pickedLanguage ??
    (storedLanguage && languages.some((l) => l.code === storedLanguage)
      ? storedLanguage
      : defaultLanguage(languages));

  function pickLanguage(code: string) {
    setPickedLanguage(code);
    writeStorage("rw:language", code);
  }

  // Qoralama til bo'yicha alohida — C++ dan Python'ga o'tib qaytganda
  // avvalgi kod joyida turadi.
  const key = draftKey(problem, language);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const storedDraft = useStored(key);
  const picked = languages.find((l) => l.code === language);
  // Masala shabloni umumiy zagotovkadan ustun: Django/SQL masalasida
  // yechim aynan berilgan funksiya imzosini to'ldirishdan iborat.
  const source =
    edits[key] ??
    storedDraft ??
    picked?.code_template ??
    starterSource(language);

  const setSource = useCallback(
    (next: string) => setEdits((current) => ({ ...current, [key]: next })),
    [key],
  );

  useEffect(() => {
    if (!language || edits[key] === undefined) return;
    const handle = setTimeout(() => writeStorage(key, edits[key]), 500);
    return () => clearTimeout(handle);
  }, [language, key, edits]);

  useEffect(() => {
    if (editedTests === null) return;
    const handle = setTimeout(
      () => writeStorage(tests, JSON.stringify(editedTests)),
      500,
    );
    return () => clearTimeout(handle);
  }, [tests, editedTests]);

  useEffect(
    () => () => {
      if (pollRef.current) clearTimeout(pollRef.current);
    },
    [],
  );

  function poll(id: number, tries: number) {
    pollRef.current = setTimeout(
      () => {
        fetchAttempt(id)
          .then((next) => {
            finishAttempt(next);
            if (isPendingVerdict(next.verdict) && tries < POLL_LIMIT) {
              poll(id, tries + 1);
            }
          })
          .catch(() => setBusy(false));
      },
      tries < POLL_FAST_COUNT ? POLL_FAST_MS : POLL_SLOW_MS,
    );
  }

  function describe(caught: unknown): string {
    if (caught instanceof ApiError) {
      if (caught.status === 429)
        return "Submit limiti — biroz kutib qayta urinib ko'ring";
      if (caught.status === 401 || caught.status === 403)
        return "Yuborish uchun hisobingizga kiring";
      return caught.message;
    }
    return "Yuborib bo'lmadi — aloqani tekshiring";
  }

  async function submit() {
    if (!language || busy) return;
    // Tekshiruv `lib/validation.ts` da — hajm BAYTLARDA o'lchanadi, aks
    // holda kirill/emoji 413 javobiga olib kelardi.
    const errors = fieldErrors<"source" | "bytes">(
      sourceSchema.safeParse({
        source,
        bytes: new TextEncoder().encode(source).length,
      }),
    );
    if (errors.source || errors.bytes) {
      setError(t(locale, errors.bytes ?? errors.source ?? "auth.required"));
      return;
    }
    setError(null);
    setBusy(true);
    setTab("verdict");
    setLiveSubmit(emptyLiveState());
    seenStreamEventIds.current.clear();
    setStreamAttemptId(undefined);
    try {
      const created = await submitAttempt({
        problem,
        language,
        source_code: source,
        ...(contest ? { contest } : {}),
      });
      watchAttemptId.current = created.id;
      setStreamAttemptId(created.id);
      setAttempt({
        ...created,
        running_test_index: created.running_test_index ?? null,
        test_results: [],
        tests_total: 0,
      });
      poll(created.id, 0);
    } catch (caught) {
      setError(describe(caught));
      setBusy(false);
    }
  }

  function waitForRun(id: number): Promise<CustomRun> {
    return new Promise((resolve, reject) => {
      let tries = 0;
      const tick = () => {
        fetchCustomRun(id)
          .then((run) => {
            if (!isPendingVerdict(run.verdict) || tries >= POLL_LIMIT)
              return resolve(run);
            tries += 1;
            pollRef.current = setTimeout(
              tick,
              tries < POLL_FAST_COUNT ? POLL_FAST_MS : POLL_SLOW_MS,
            );
          })
          .catch(reject);
      };
      pollRef.current = setTimeout(tick, POLL_FAST_MS);
    });
  }

  /** Tanlangan yoki jadvaldagi namuna — konsol + inline qator (prototip). */
  const runSampleByOrder = useCallback(
    async (order: number) => {
      if (!language || busy) return;
      const sample = samples.find((s) => s.order === order);
      if (!sample) return;
      setSelectedSample(order);
      setError(null);
      setBusy(true);
      solve?.setSubmitBusy(true);
      setTab("samples");
      solve?.setInlineSample(order, { status: "running" });
      setConsoleState({
        status: "running",
        log: t(locale, "submit.sampleConsoleRunning"),
        got: "—",
        outputMatched: null,
      });
      try {
        const created = await runCustomTest({
          language,
          source_code: source,
          stdin: sample.input,
        });
        const finished = await waitForRun(created.id);
        const ok =
          finished.verdict === "AC" &&
          normalise(finished.stdout) === normalise(sample.expected);
        const got = finished.stdout || "—";
        const log = ok
          ? fill(t(locale, "submit.samplePassLog"), { order: sample.order })
          : fill(t(locale, "submit.sampleFailLog"), { order: sample.order });
        setSampleResults([
          {
            order: sample.order,
            ok,
            got,
            expected: sample.expected,
            verdict: finished.verdict,
          },
        ]);
        setConsoleState({
          status: "done",
          log,
          got,
          outputMatched: ok,
        });
        solve?.setInlineSample(order, {
          status: "done",
          ok,
          message: log,
        });
      } catch (caught) {
        setError(describe(caught));
        setConsoleState(sampleConsoleIdleState(locale));
        solve?.setInlineSample(order, { status: "idle" });
      } finally {
        setBusy(false);
        solve?.setSubmitBusy(false);
      }
    },
    [
      language,
      busy,
      samples,
      source,
      locale,
      solve,
    ],
  );

  useEffect(() => {
    if (!solve) return;
    solve.registerRunSample((order) => {
      void runSampleByOrder(order);
    });
    return () => solve.registerRunSample(null);
  }, [solve, runSampleByOrder]);

  useEffect(() => {
    solve?.setAttempt(attempt);
  }, [attempt, solve]);

  useEffect(() => {
    solve?.setSubmitBusy(busy);
  }, [busy, solve]);

  async function runSelectedSample() {
    await runSampleByOrder(selectedSample);
  }

  function pollCustom(id: number, tries: number) {
    pollRef.current = setTimeout(
      () => {
        fetchCustomRun(id)
          .then((next) => {
            setCustomRun(next);
            if (isPendingVerdict(next.verdict) && tries < POLL_LIMIT)
              pollCustom(id, tries + 1);
            else setBusy(false);
          })
          .catch(() => setBusy(false));
      },
      tries < POLL_FAST_COUNT ? POLL_FAST_MS : POLL_SLOW_MS,
    );
  }

  async function runCustom() {
    if (!language || busy) return;
    setError(null);
    setBusy(true);
    setTab("custom");
    try {
      const created = await runCustomTest({
        language,
        source_code: source,
        stdin: customTests[current] ?? "",
      });
      setCustomRun(created);
      setRunFor(current);
      pollCustom(created.id, 0);
    } catch (caught) {
      setError(describe(caught));
      setBusy(false);
    }
  }

  const canSubmit = ready && !!user && hasTests;

  // Testsiz masalada judge tekshiradigan narsa yo'q — tugmani ochiq
  // qoldirish foydalanuvchining vaqtini olib, ichki xato qaytarardi.
  if (!hasTests)
    return (
      <div className={PANEL}>
        <Card title={t(locale, "submit.solution")}>
          <p className="text-theme-sm rw-dim">
            {t(locale, "submit.testsNotReadyBody")}
          </p>
        </Card>
      </div>
    );

  return (
    <div className={PANEL}>
      <Card
        title={t(locale, "submit.solution")}
        action={
          <Dropdown
            size="sm"
            hideLabel
            label={t(locale, "attempts.language")}
            value={language}
            onChange={pickLanguage}
            options={languages.map((l) => ({
              value: l.code,
              label: `${l.name} ${l.version}`,
            }))}
            className="w-44"
          />
        }
        bodyClassName="space-y-3"
      >
        {picked && (
          <p className="text-theme-xs rw-faint">
            {picked.name} {picked.version} uchun: {picked.time_limit_ms} ms ·{" "}
            {Math.round(picked.memory_limit_kb / 1024)} MB
            {languages.length === 1 && " · bu masala faqat shu tilda"}
          </p>
        )}

        <EditorTools
          locale={locale}
          source={source}
          onSource={setSource}
          onError={setError}
        />

        <CodeEditor
          language={editorLanguage(language)}
          value={source}
          onChange={setSource}
        />

        <SampleTestConsole
          samples={samples}
          selectedOrder={selectedSample}
          onSelect={setSelectedSample}
          onRun={runSelectedSample}
          busy={busy}
          disabled={!canSubmit || !source.trim()}
          state={consoleState}
        />

        {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}

        <div className="flex flex-wrap items-center gap-2">
          {canSubmit ? (
            <Button onClick={submit} disabled={busy || !source.trim()}>
              {busy ? t(locale, "roadmap.sending") : t(locale, "roadmap.suggestSend")}
            </Button>
          ) : (
            <Link
              href={"/login?tab=login" as Route}
              className="inline-flex h-11 items-center rw-btn-radius rw-accent-bg px-4 text-theme-sm font-medium rw-btn-label"
            >
              {t(locale, "submit.signInToSubmit")}
            </Link>
          )}
          <span className="ml-auto text-theme-xs rw-faint">
            {t(locale, "submit.draftSavedLocally")}
          </span>
        </div>
      </Card>

      <Card
        title={
          <div className="flex gap-1">
            {(
              [
                ["verdict", t(locale, "submit.tabVerdict")],
                ...(samples.length > 0
                  ? ([["samples", t(locale, "submit.tabSamples")]] as const)
                  : []),
                ["custom", t(locale, "submit.tabCustom")],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                type="button"
                onClick={() => setTab(key)}
                className={`rw-radius-sm px-3 py-1.5 text-theme-sm font-medium transition ${
                  tab === key
                    ? "rw-accent-soft rw-accent-ink"
                    : "rw-dim rw-hover-bg"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        }
      >
        {tab === "verdict" &&
          (verdictLayout === "tab" ? (
            <div className="space-y-3">
              {attempt?.id != null &&
                (busy || isPendingVerdict(attempt?.verdict ?? "PENDING")) && (
                  <AttemptLiveProgress attemptId={attempt.id} state={liveSubmit} />
                )}
              <AttemptVerdictPanel
                attempt={attempt}
                pending={busy && (!attempt || isPendingVerdict(attempt.verdict))}
                locale={locale}
              />
            </div>
          ) : (
            <p className="text-theme-sm rw-faint">
              {t(locale, "submit.verdictShownElsewhere")}
            </p>
          ))}
        {tab === "samples" && (
          <SamplesView
            locale={locale}
            results={sampleResults}
            total={samples.length}
            busy={busy}
          />
        )}
        {tab === "custom" && (
          <CustomView
            locale={locale}
            tests={customTests}
            active={current}
            onActive={setActiveTest}
            onChange={setEditedTests}
            run={runFor === current ? customRun : null}
            onRun={runCustom}
            disabled={!canSubmit || busy || !source.trim()}
          />
        )}
      </Card>
    </div>
  );
}

/** Muharrir asboblari — uchala taqqoslangan platformada ham bor:
 * fayldan yuklash, nusxalash, tozalash va manba hajmi. */
function EditorTools({
  locale,
  source,
  onSource,
  onError,
}: {
  locale: Locale;
  source: string;
  onSource: (next: string) => void;
  onError: (message: string | null) => void;
}) {
  const bytes = new TextEncoder().encode(source).length;

  async function upload(file: File | undefined) {
    if (!file) return;
    if (file.size > MAX_SOURCE_BYTES) {
      onError(`Fayl ${MAX_SOURCE_BYTES / 1024} KB dan oshmasligi kerak`);
      return;
    }
    onError(null);
    onSource(await file.text());
  }

  const action =
    "rw-radius-sm px-2 py-1 text-theme-xs font-medium rw-dim transition rw-hover-bg";

  return (
    <div className="flex flex-wrap items-center gap-1">
      <FormFile
        accept=".cpp,.cc,.cxx,.c,.py,.java,.kt,.go,.rs,.cs,.js,.ts,.txt"
        onFile={(file) => void upload(file)}
      />
      <CopyButton
        text={source}
        tone="kbd"
        kbd="Ctrl+C"
        label={t(locale, "settings.teamCopy")}
        copiedLabel={t(locale, "settings.teamCopied")}
        className={action}
      />
      <button type="button" onClick={() => onSource("")} className={action}>
        {t(locale, "common.clear")}
      </button>
      <span className="ml-auto font-mono text-theme-xs rw-faint">
        {bytes} / {MAX_SOURCE_BYTES}
      </span>
    </div>
  );
}

const MAX_TESTS = 8;

function CustomView({
  locale,
  tests,
  active,
  onActive,
  onChange,
  run,
  onRun,
  disabled,
}: {
  locale: Locale;
  tests: string[];
  active: number;
  onActive: (index: number) => void;
  onChange: (tests: string[]) => void;
  run: CustomRun | null;
  onRun: () => void;
  disabled: boolean;
}) {
  function edit(value: string) {
    onChange(tests.map((test, i) => (i === active ? value : test)));
  }

  function add() {
    onChange([...tests, ""]);
    onActive(tests.length);
  }

  function remove() {
    onChange(tests.filter((_, i) => i !== active));
    onActive(Math.max(0, active - 1));
  }

  const tab =
    "rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition rw-hover-bg";

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-1">
        {tests.map((_, index) => (
          <button
            key={index}
            type="button"
            onClick={() => onActive(index)}
            aria-current={index === active}
            className={`${tab} ${
              index === active ? "rw-accent-soft rw-accent-ink" : "rw-dim"
            }`}
          >
            {fill(t(locale, "submit.customTestTab"), { index: index + 1 })}
          </button>
        ))}
        {tests.length < MAX_TESTS && (
          <button
            type="button"
            onClick={add}
            aria-label={t(locale, "submit.addTest")}
            className={`${tab} rw-faint`}
          >
            +
          </button>
        )}
        {tests.length > 1 && (
          <button
            type="button"
            onClick={remove}
            aria-label={fill(t(locale, "submit.removeTest"), { index: active + 1 })}
            className={`${tab} ml-auto rw-faint`}
          >
            {t(locale, "submit.removeCustomTest")}
          </button>
        )}
      </div>

      <label className="block">
        <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
          {t(locale, "submit.stdinLabel")}
        </span>
        <textarea
          value={tests[active] ?? ""}
          onChange={(e) => edit(e.target.value)}
          rows={4}
          spellCheck={false}
          className="w-full rw-radius-sm border rw-line rw-field-bg p-3 font-mono text-theme-xs rw-strong outline-none rw-focus-line rw-fm-inp"
        />
      </label>

      <div className="flex flex-wrap items-center gap-3">
        <Button variant="outline" onClick={onRun} disabled={disabled}>
          {t(locale, "submit.run")}
        </Button>
        <span className="text-theme-xs rw-faint">
          {t(locale, "submit.testsSavedLocally")}
        </span>
      </div>

      {run && (
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <Verdict verdict={run.verdict} />
            {!isPendingVerdict(run.verdict) && (
              <span className="text-theme-sm rw-dim">
                {run.time_ms} ms · {Math.round(run.memory_kb / 1024)} MB
              </span>
            )}
          </div>
          {run.compile_output && (
            <pre tabIndex={0} className="max-h-40 rw-scroll rw-radius-sm rw-field-bg p-3 text-theme-xs rw-bad-ink">
              {run.compile_output}
            </pre>
          )}
          <div>
            <p className="mb-1 text-theme-xs rw-faint">{t(locale, "col.output")}</p>
            <pre tabIndex={0} className="max-h-56 rw-scroll rw-radius-sm rw-field-bg p-3 text-theme-xs rw-strong">
              {run.stdout || "—"}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function SamplesView({
  locale,
  results,
  total,
  busy,
}: {
  locale: Locale;
  results: SampleResult[];
  total: number;
  busy: boolean;
}) {
  // Yuklanish — alohida shoxobcha, matn ichida emas: `Loading` o'z holatini
  // ekran o'quvchiga e'lon qiladi (`role="status"`), oddiy matn esa buni
  // qilmaydi.
  if (results.length === 0)
    return busy ? (
      <Loading variant="dotsBounce" label={t(locale, "submit.runningSamples")} />
    ) : (
      <p className="text-theme-sm rw-faint">{t(locale, "submit.samplesHint")}</p>
    );

  const failed = results.find((result) => !result.ok);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {results.map((result) => (
          <span
            key={result.order}
            className={`rw-radius-sm px-2 py-0.5 text-theme-xs font-medium ${
              result.ok ? "rw-ok-soft rw-ok-ink" : "rw-bad-soft rw-bad-ink"
            }`}
          >
            {fill(t(locale, "submit.sample"), { order: result.order })}{" "}
            {result.ok
              ? t(locale, "submit.matches")
              : result.verdict === "AC"
                ? t(locale, "submit.outputMismatch")
                : result.verdict}
          </span>
        ))}
        {busy && <Loading variant="dotsFade" label={t(locale, "submit.running")} />}
        {!busy && !failed && results.length === total && (
          <Status status="ok" variant="iconText" live label={t(locale, "submit.allSamplesPass")} />
        )}
      </div>

      {failed && (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="min-w-0">
            <p className="mb-1 text-theme-xs rw-faint">
              {t(locale, "submit.yourOutput")}
            </p>
            <pre tabIndex={0} className="max-h-48 rw-scroll rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-bad-ink">
              {failed.got || "—"}
            </pre>
          </div>
          <div className="min-w-0">
            <p className="mb-1 text-theme-xs rw-faint">{t(locale, "submit.expected")}</p>
            <pre tabIndex={0} className="max-h-48 rw-scroll rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-strong">
              {failed.expected}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

/** Boshqalarning urinishlari — kim yechganini va qaysi tilda ekanini
 * ko'rish uchun. Manba ko'rsatilmaydi: backend uni faqat egasiga va
 * xodimga qaytaradi. */
