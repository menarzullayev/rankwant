"use client";

import Link from "next/link";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { VerdictBadge, isPending } from "@/components/VerdictBadge";
import { useSession } from "@/context/SessionContext";
import { ApiError } from "@/lib/api";
import {
  fetchAttempt,
  fetchCustomRun,
  runCustomTest,
  submitAttempt,
  type Attempt,
  type AttemptDetail,
  type CustomRun,
  type Language,
  type Sample,
} from "@/lib/api";
import CodeEditor from "./CodeEditor";

const MAX_SOURCE_BYTES = 64 * 1024;

/** Verdikt uchun SSE yo'q (musobaqa jadvalidan farqli) — pollinglaymiz.
 * Birinchi soniyalarda tez, keyin siyrak: kompilyatsiya + testlar odatda
 * 1–3 s, lekin navbat band bo'lsa uzoq kutish ham bo'ladi. */
const POLL_FAST_MS = 800;
const POLL_SLOW_MS = 2500;
const POLL_FAST_COUNT = 12;
const POLL_LIMIT = 90;

const DEFAULT_SOURCE: Record<string, string> = {
  cpp: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}\n`,
  python: ``,
  java: `import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        \n    }\n}\n`,
};

/** Judge til kodidan (`cpp23`, `py313`, `java21`) Monaco til nomiga. */
function editorLanguage(code: string): string {
  if (code.startsWith("cpp") || code.startsWith("c++")) return "cpp";
  if (code.startsWith("py")) return "python";
  if (code.startsWith("java")) return "java";
  if (code.startsWith("js") || code.startsWith("node")) return "javascript";
  if (code.startsWith("go")) return "go";
  if (code.startsWith("rs") || code.startsWith("rust")) return "rust";
  if (code.startsWith("kt")) return "kotlin";
  if (code.startsWith("cs")) return "csharp";
  return "plaintext";
}

const draftKey = (problem: string, language: string) =>
  `rw:draft:${problem}:${language}`;

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

export default function SubmitPanel({
  problem,
  languages,
  samples,
  contest,
}: {
  problem: string;
  languages: Language[];
  samples: Sample[];
  contest?: string;
}) {
  const { user, ready } = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("verdict");

  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);

  const [stdin, setStdin] = useState("");
  const [customRun, setCustomRun] = useState<CustomRun | null>(null);
  const [sampleResults, setSampleResults] = useState<SampleResult[]>([]);

  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Tanlangan til qurilmada eslab qolinadi — har masalada qayta
  // tanlash asosiy oqimdagi eng ko'p takrorlanadigan ortiqcha qadam.
  const [pickedLanguage, setPickedLanguage] = useState<string | null>(null);
  const storedLanguage = useStored("rw:language");
  const language =
    pickedLanguage ??
    (storedLanguage && languages.some((l) => l.code === storedLanguage)
      ? storedLanguage
      : (languages[0]?.code ?? ""));

  function pickLanguage(code: string) {
    setPickedLanguage(code);
    writeStorage("rw:language", code);
  }

  // Qoralama til bo'yicha alohida — C++ dan Python'ga o'tib qaytganda
  // avvalgi kod joyida turadi.
  const key = draftKey(problem, language);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const storedDraft = useStored(key);
  const source =
    edits[key] ?? storedDraft ?? DEFAULT_SOURCE[editorLanguage(language)] ?? "";

  const setSource = useCallback(
    (next: string) => setEdits((current) => ({ ...current, [key]: next })),
    [key],
  );

  useEffect(() => {
    if (!language || edits[key] === undefined) return;
    const handle = setTimeout(() => writeStorage(key, edits[key]), 500);
    return () => clearTimeout(handle);
  }, [language, key, edits]);

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
            setAttempt(next);
            if (isPending(next.verdict) && tries < POLL_LIMIT) {
              poll(id, tries + 1);
            } else {
              setBusy(false);
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
    if (new TextEncoder().encode(source).length > MAX_SOURCE_BYTES) {
      setError(`Manba ${MAX_SOURCE_BYTES / 1024} KB dan oshmasligi kerak`);
      return;
    }
    setError(null);
    setBusy(true);
    setTab("verdict");
    try {
      const created = await submitAttempt({
        problem,
        language,
        source_code: source,
        ...(contest ? { contest } : {}),
      });
      setAttempt({ ...created, test_results: [] });
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
            if (!isPending(run.verdict) || tries >= POLL_LIMIT)
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

  /** Namunalar ketma-ket yuritiladi va birinchi mos kelmaganda to'xtaydi:
   * custom-test submit bilan bitta limitni bo'lishadi (6/daq), va xato
   * odatda birinchi namunada ko'rinadi. */
  async function runSamples() {
    if (!language || busy) return;
    setError(null);
    setBusy(true);
    setTab("samples");
    setSampleResults([]);
    try {
      for (const sample of samples) {
        const created = await runCustomTest({
          language,
          source_code: source,
          stdin: sample.input,
        });
        const finished = await waitForRun(created.id);
        const ok =
          finished.verdict === "AC" &&
          normalise(finished.stdout) === normalise(sample.expected);
        setSampleResults((current) => [
          ...current,
          {
            order: sample.order,
            ok,
            got: finished.stdout,
            expected: sample.expected,
            verdict: finished.verdict,
          },
        ]);
        if (!ok) break;
      }
    } catch (caught) {
      setError(describe(caught));
    } finally {
      setBusy(false);
    }
  }

  function pollCustom(id: number, tries: number) {
    pollRef.current = setTimeout(
      () => {
        fetchCustomRun(id)
          .then((next) => {
            setCustomRun(next);
            if (isPending(next.verdict) && tries < POLL_LIMIT)
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
        stdin,
      });
      setCustomRun(created);
      pollCustom(created.id, 0);
    } catch (caught) {
      setError(describe(caught));
      setBusy(false);
    }
  }

  const canSubmit = ready && !!user;

  return (
    <div className="space-y-4">
      <Card
        title="Yechim"
        action={
          <select
            value={language}
            onChange={(e) => pickLanguage(e.target.value)}
            className="h-9 rw-radius-sm border rw-line rw-field-bg px-3 text-theme-sm rw-strong rw-focus-line"
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>
                {l.name} {l.version}
              </option>
            ))}
          </select>
        }
        bodyClassName="space-y-3"
      >
        <EditorTools source={source} onSource={setSource} onError={setError} />

        <CodeEditor
          language={editorLanguage(language)}
          value={source}
          onChange={setSource}
        />

        {error && <p className="text-theme-sm rw-bad-ink">{error}</p>}

        <div className="flex flex-wrap items-center gap-2">
          {canSubmit ? (
            <Button onClick={submit} disabled={busy || !source.trim()}>
              {busy ? "Yuborilmoqda…" : "Yuborish"}
            </Button>
          ) : (
            <Link
              href="/login"
              className="inline-flex h-11 items-center rw-btn-radius rw-accent-bg px-4 text-theme-sm font-medium rw-btn-label"
            >
              Yuborish uchun kiring
            </Link>
          )}
          {samples.length > 0 && (
            <Button
              variant="outline"
              onClick={runSamples}
              disabled={!canSubmit || busy || !source.trim()}
            >
              Namunada sinash
            </Button>
          )}
          <span className="ml-auto text-theme-xs rw-faint">
            Qoralama shu brauzerda saqlanadi
          </span>
        </div>
      </Card>

      <Card
        title={
          <div className="flex gap-1">
            {(
              [
                ["verdict", "Natija"],
                ...(samples.length > 0
                  ? ([["samples", "Namunalar"]] as const)
                  : []),
                ["custom", "O'z testim"],
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
        {tab === "verdict" && <VerdictView attempt={attempt} />}
        {tab === "samples" && (
          <SamplesView
            results={sampleResults}
            total={samples.length}
            busy={busy}
          />
        )}
        {tab === "custom" && (
          <CustomView
            stdin={stdin}
            onStdin={setStdin}
            run={customRun}
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
  source,
  onSource,
  onError,
}: {
  source: string;
  onSource: (next: string) => void;
  onError: (message: string | null) => void;
}) {
  const [copied, setCopied] = useState(false);
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

  async function copy() {
    try {
      await navigator.clipboard.writeText(source);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard ruxsati yo'q — kod muharrirda ko'rinib turibdi.
    }
  }

  const action =
    "rw-radius-sm px-2 py-1 text-theme-xs font-medium rw-dim transition rw-hover-bg";

  return (
    <div className="flex flex-wrap items-center gap-1">
      <label className={`${action} cursor-pointer`}>
        Fayldan yuklash
        <input
          type="file"
          accept=".cpp,.cc,.cxx,.c,.py,.java,.kt,.go,.rs,.cs,.js,.ts,.txt"
          className="hidden"
          onChange={(e) => {
            void upload(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </label>
      <button type="button" onClick={copy} className={action}>
        {copied ? "Nusxalandi" : "Nusxalash"}
      </button>
      <button type="button" onClick={() => onSource("")} className={action}>
        Tozalash
      </button>
      <span className="ml-auto font-mono text-theme-xs rw-faint">
        {bytes} / {MAX_SOURCE_BYTES}
      </span>
    </div>
  );
}

function VerdictView({ attempt }: { attempt: AttemptDetail | null }) {
  if (!attempt)
    return (
      <p className="text-theme-sm rw-faint">
        Hali yuborilmadi. Kod yozing va «Yuborish» ni bosing.
      </p>
    );

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <VerdictBadge verdict={attempt.verdict} />
        {!isPending(attempt.verdict) && (
          <span className="text-theme-sm rw-dim">
            {attempt.time_ms} ms · {Math.round(attempt.memory_kb / 1024)} MB
            {attempt.score > 0 && ` · ${attempt.score} ball`}
          </span>
        )}
        {attempt.failed_test_index !== null && (
          <span className="text-theme-sm rw-bad-ink">
            {attempt.failed_test_index}-testda to&apos;xtadi
          </span>
        )}
      </div>

      {attempt.compile_output && (
        <pre className="max-h-56 overflow-auto rw-radius-sm rw-field-bg p-3 text-theme-xs rw-dim-2">
          {attempt.compile_output}
        </pre>
      )}

      {attempt.test_results.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {attempt.test_results.map((test) => (
            <span
              key={test.index}
              title={`${test.index}: ${test.verdict} · ${test.time_ms} ms`}
              className={`flex size-7 items-center justify-center rw-radius-sm text-theme-xs font-medium ${
                test.verdict === "AC"
                  ? "rw-ok-soft rw-ok-ink"
                  : "rw-bad-soft rw-bad-ink"
              }`}
            >
              {test.index}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function CustomView({
  stdin,
  onStdin,
  run,
  onRun,
  disabled,
}: {
  stdin: string;
  onStdin: (value: string) => void;
  run: CustomRun | null;
  onRun: () => void;
  disabled: boolean;
}) {
  return (
    <div className="space-y-3">
      <label className="block">
        <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
          Kiritma (stdin)
        </span>
        <textarea
          value={stdin}
          onChange={(e) => onStdin(e.target.value)}
          rows={4}
          spellCheck={false}
          className="w-full rw-radius-sm border rw-line rw-field-bg p-3 font-mono text-theme-xs rw-strong outline-none rw-focus-line"
        />
      </label>

      <Button variant="outline" onClick={onRun} disabled={disabled}>
        Ishga tushirish
      </Button>

      {run && (
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <VerdictBadge verdict={run.verdict} />
            {!isPending(run.verdict) && (
              <span className="text-theme-sm rw-dim">
                {run.time_ms} ms · {Math.round(run.memory_kb / 1024)} MB
              </span>
            )}
          </div>
          {run.compile_output && (
            <pre className="max-h-40 overflow-auto rw-radius-sm rw-field-bg p-3 text-theme-xs rw-bad-ink">
              {run.compile_output}
            </pre>
          )}
          <div>
            <p className="mb-1 text-theme-xs rw-faint">Chiqish</p>
            <pre className="max-h-56 overflow-auto rw-radius-sm rw-field-bg p-3 text-theme-xs rw-strong">
              {run.stdout || "—"}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function SamplesView({
  results,
  total,
  busy,
}: {
  results: SampleResult[];
  total: number;
  busy: boolean;
}) {
  if (results.length === 0)
    return (
      <p className="text-theme-sm rw-faint">
        {busy
          ? "Namunalar yuritilmoqda…"
          : "«Namunada sinash» — kodni yuborishdan oldin namunalarda tekshiradi."}
      </p>
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
            Namuna {result.order} ·{" "}
            {result.ok
              ? "mos"
              : result.verdict === "AC"
                ? "chiqish mos emas"
                : result.verdict}
          </span>
        ))}
        {busy && <span className="text-theme-xs rw-faint">yuritilmoqda…</span>}
        {!busy && !failed && results.length === total && (
          <span className="text-theme-xs rw-ok-ink">
            Barcha namunalar mos — yuborishingiz mumkin
          </span>
        )}
      </div>

      {failed && (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="min-w-0">
            <p className="mb-1 text-theme-xs rw-faint">Sizning chiqishingiz</p>
            <pre className="max-h-48 overflow-auto rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-bad-ink">
              {failed.got || "—"}
            </pre>
          </div>
          <div className="min-w-0">
            <p className="mb-1 text-theme-xs rw-faint">Kutilgan</p>
            <pre className="max-h-48 overflow-auto rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-strong">
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
