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
  fetchProblemAttempts,
  runCustomTest,
  submitAttempt,
  type Attempt,
  type AttemptDetail,
  type CustomRun,
  type Language,
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

type Tab = "verdict" | "custom" | "history";

export default function SubmitPanel({
  problem,
  languages,
  contest,
}: {
  problem: string;
  languages: Language[];
  contest?: string;
}) {
  const { user, ready } = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("verdict");

  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [history, setHistory] = useState<Attempt[]>([]);

  const [stdin, setStdin] = useState("");
  const [customRun, setCustomRun] = useState<CustomRun | null>(null);

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

  const loadHistory = useCallback(() => {
    if (!user) return;
    fetchProblemAttempts(problem)
      .then((page) =>
        setHistory(page.results.filter((a) => a.username === user.username)),
      )
      .catch(() => {});
  }, [problem, user]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

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
              loadHistory();
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
          <Button
            variant="outline"
            onClick={runCustom}
            disabled={!canSubmit || busy || !source.trim()}
          >
            Sinab ko&apos;rish
          </Button>
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
                ["custom", "O'z testim"],
                [
                  "history",
                  `Urinishlar${history.length ? ` (${history.length})` : ""}`,
                ],
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
        {tab === "custom" && (
          <CustomView stdin={stdin} onStdin={setStdin} run={customRun} />
        )}
        {tab === "history" && <HistoryView items={history} />}
      </Card>
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
}: {
  stdin: string;
  onStdin: (value: string) => void;
  run: CustomRun | null;
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

function HistoryView({ items }: { items: Attempt[] }) {
  if (items.length === 0)
    return (
      <p className="text-theme-sm rw-faint">
        Bu masala bo&apos;yicha urinishlaringiz hali yo&apos;q.
      </p>
    );

  return (
    <ul className="rw-divide divide-y">
      {items.map((item) => (
        <li
          key={item.id}
          className="flex flex-wrap items-center gap-3 py-2 text-theme-sm"
        >
          <VerdictBadge verdict={item.verdict} />
          <span className="rw-dim">{item.language}</span>
          <span className="rw-faint">
            {item.time_ms} ms · {Math.round(item.memory_kb / 1024)} MB
          </span>
          <time className="ml-auto rw-faint" dateTime={item.created_at}>
            {new Date(item.created_at).toLocaleString("uz")}
          </time>
        </li>
      ))}
    </ul>
  );
}
