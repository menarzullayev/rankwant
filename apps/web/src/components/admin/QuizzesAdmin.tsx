"use client";

import { useCallback, useEffect, useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type Quiz = {
  id: number;
  slug: string;
  title: string;
  description: string;
  reward_qvant: number;
  is_published: boolean;
  /** Savol ID'lari, tartib bilan */
  questions: number[];
  created_at: string;
  [key: string]: unknown;
};

/** `staff/questions/` javobidan faqat shu ikkitasiga tayanamiz. */
type QuestionRef = { id: number; text: string };

const PATH = "/staff/quizzes/";

const COLUMNS: ColumnDef<Quiz>[] = [
  {
    key: "slug",
    label: "Slug",
    render: (q) => <span className="font-mono">{q.slug}</span>,
  },
  { key: "title", label: "Nomi" },
  {
    key: "questions",
    label: "Savollar",
    align: "right",
    render: (q) => q.questions.length,
  },
  { key: "reward_qvant", label: "Qvant", align: "right" },
  {
    key: "is_published",
    label: "Holat",
    render: (q) =>
      q.is_published ? (
        <Badge color="success">Nashr</Badge>
      ) : (
        <Badge>Qoralama</Badge>
      ),
  },
];

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "title", label: "Nomi", required: true },
  {
    name: "reward_qvant",
    label: "Mukofot (Qvant)",
    type: "number",
    min: 0,
    required: true,
  },
  { name: "is_published", label: "Nashr qilingan", type: "checkbox" },
  { name: "description", label: "Tavsif", type: "textarea", rows: 4 },
];

async function fetchQuestion(id: number): Promise<QuestionRef> {
  const q = await staff.get<QuestionRef>(`/staff/questions/${id}/`);
  return { id: q.id, text: q.text };
}

function QuestionsPanel({ quiz, reload }: { quiz: Quiz; reload: () => void }) {
  const locale = DEFAULT_LOCALE;
  const [ids, setIds] = useState<number[]>(quiz.questions);
  const [texts, setTexts] = useState<Record<number, string>>({});
  const [newId, setNewId] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadTexts = useCallback(async (wanted: number[]) => {
    const found = await Promise.all(
      wanted.map((id) => fetchQuestion(id).catch(() => ({ id, text: "" }))),
    );
    setTexts((prev) => ({
      ...prev,
      ...Object.fromEntries(found.map((q) => [q.id, q.text])),
    }));
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadTexts(quiz.questions);
  }, [quiz.questions, loadTexts]);

  function move(index: number, delta: -1 | 1) {
    const next = [...ids];
    const target = index + delta;
    if (target < 0 || target >= next.length) return;
    [next[index], next[target]] = [next[target], next[index]];
    setIds(next);
  }

  async function add() {
    const id = Number(newId);
    setError("");
    setMsg("");
    if (!Number.isInteger(id) || id <= 0)
      return setError("Savol ID butun son bo'lsin");
    if (ids.includes(id)) return setError(`#${id} allaqachon ro'yxatda`);
    try {
      const q = await fetchQuestion(id);
      setTexts((prev) => ({ ...prev, [q.id]: q.text }));
      setIds((prev) => [...prev, q.id]);
      setNewId("");
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 404
          ? `#${id} topilmadi`
          : String(e),
      );
    }
  }

  async function save() {
    setBusy(true);
    setError("");
    setMsg("");
    try {
      await staff.update(`${PATH}${quiz.slug}/`, { questions: ids });
      setMsg(t(locale, "admin.saved"));
      reload();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const dirty = ids.join(",") !== quiz.questions.join(",");
  const iconBtn =
    "rounded px-1.5 text-theme-xs text-gray-500 hover:bg-gray-100 disabled:opacity-30 dark:hover:bg-white/10";

  return (
    <div className="space-y-3">
      <p className="text-theme-xs font-medium text-gray-500 uppercase dark:text-gray-400">
        Savollar ({ids.length})
      </p>
      {ids.length === 0 ? (
        <p className="text-theme-sm text-gray-400">
          {t(locale, "admin.noRows")}
        </p>
      ) : (
        <ol className="space-y-1">
          {ids.map((id, i) => (
            <li key={id} className="flex items-center gap-2 text-theme-sm">
              <span className="w-6 text-right text-gray-400">{i + 1}.</span>
              <span className="font-mono text-gray-500">#{id}</span>
              <span className="min-w-0 flex-1 truncate text-gray-700 dark:text-gray-300">
                {texts[id] ?? "…"}
              </span>
              <button
                type="button"
                onClick={() => move(i, -1)}
                disabled={i === 0}
                className={iconBtn}
                title="Yuqoriga"
              >
                ↑
              </button>
              <button
                type="button"
                onClick={() => move(i, 1)}
                disabled={i === ids.length - 1}
                className={iconBtn}
                title="Pastga"
              >
                ↓
              </button>
              <button
                type="button"
                onClick={() => setIds(ids.filter((x) => x !== id))}
                className={`${iconBtn} text-error-500`}
                title="Olib tashlash"
              >
                ✕
              </button>
            </li>
          ))}
        </ol>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <input
          value={newId}
          onChange={(e) => setNewId(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              void add();
            }
          }}
          inputMode="numeric"
          placeholder="Savol ID"
          className="h-9 w-32 rounded-lg border border-gray-200 bg-white px-3 text-theme-sm outline-none focus:border-brand-400 dark:border-[#232936] dark:bg-[#0b0d12] dark:text-white/90"
        />
        <Button
          type="button"
          variant="outline"
          className="h-9"
          onClick={() => void add()}
        >
          Qo&apos;shish
        </Button>
        <Button
          type="button"
          className="h-9"
          disabled={busy || !dirty}
          onClick={() => void save()}
        >
          {t(locale, "admin.save")}
        </Button>
        {msg && <span className="text-theme-xs text-success-600">{msg}</span>}
        {error && <span className="text-theme-xs text-error-500">{error}</span>}
      </div>
    </div>
  );
}

export function QuizzesAdmin() {
  return (
    <CrudPage<Quiz>
      title="Testlar"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-created_at"
      rowExtra={(quiz, reload) => (
        <QuestionsPanel key={quiz.slug} quiz={quiz} reload={reload} />
      )}
    />
  );
}
