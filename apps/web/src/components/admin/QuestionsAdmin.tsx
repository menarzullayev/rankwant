"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Status } from "@/components/ui/Status";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Variantlar savol bilan birga yuboriladi va serverda TO'LIQ almashtiriladi
 * (`quizzes/staff_serializers.py`). Shuning uchun CrudPage'ning FormData
 * formasi to'g'ri kelmaydi — sahifa o'zi boshqariladigan forma bilan qurilgan. */

type Choice = { id?: number; order: number; text: string; is_correct: boolean };

type Question = {
  id: number;
  text: string;
  explanation: string;
  difficulty: number;
  topics: string[];
  is_active: boolean;
  choices: Choice[];
  created_at: string;
};

type FormState = {
  text: string;
  explanation: string;
  difficulty: number;
  topics: string;
  is_active: boolean;
  choices: Choice[];
};

const PATH = "/staff/questions/";

const EMPTY: FormState = {
  text: "",
  explanation: "",
  difficulty: 800,
  topics: "",
  is_active: true,
  choices: [
    { order: 1, text: "", is_correct: true },
    { order: 2, text: "", is_correct: false },
  ],
};

const INPUT =
  "h-10 w-full rw-radius-sm border rw-line rw-surface px-3 text-theme-sm outline-none " +
  "rw-focus-line rw-field-bg ";

const LABEL = "mb-1 block text-theme-xs font-medium rw-dim-2 ";

function fromItem(item: Question): FormState {
  return {
    text: item.text,
    explanation: item.explanation,
    difficulty: item.difficulty,
    topics: item.topics.join(", "),
    is_active: item.is_active,
    choices: item.choices.map((c) => ({ ...c })),
  };
}

export function QuestionsAdmin() {
  const locale = useLocale();
  const [rows, setRows] = useState<Question[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<Question | null>(null);
  const [form, setForm] = useState<FormState | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const params: Record<string, string | number> = { page };
      if (q) params.search = q;
      const data = await staff.list<Question>(PATH, params);
      setRows(data.results);
      setCount(data.count);
      setError("");
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    }
  }, [page, q, locale]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  function open(item: Question | null) {
    setEditing(item);
    setForm(
      item
        ? fromItem(item)
        : { ...EMPTY, choices: EMPTY.choices.map((c) => ({ ...c })) },
    );
    setError("");
  }

  function close() {
    setForm(null);
    setEditing(null);
  }

  function patchChoice(i: number, patch: Partial<Choice>) {
    setForm((f) =>
      f
        ? {
            ...f,
            choices: f.choices.map((c, j) =>
              j === i ? { ...c, ...patch } : c,
            ),
          }
        : f,
    );
  }

  function markCorrect(i: number) {
    setForm((f) =>
      f
        ? {
            ...f,
            choices: f.choices.map((c, j) => ({ ...c, is_correct: j === i })),
          }
        : f,
    );
  }

  function addChoice() {
    setForm((f) => {
      if (!f) return f;
      const order = Math.max(0, ...f.choices.map((c) => c.order)) + 1;
      return {
        ...f,
        choices: [...f.choices, { order, text: "", is_correct: false }],
      };
    });
  }

  function removeChoice(i: number) {
    setForm((f) =>
      f ? { ...f, choices: f.choices.filter((_, j) => j !== i) } : f,
    );
  }

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!form) return;
    setBusy(true);
    setError("");
    const payload = {
      text: form.text,
      explanation: form.explanation,
      difficulty: form.difficulty,
      topics: form.topics
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      is_active: form.is_active,
      choices: form.choices.map(({ order, text, is_correct }) => ({
        order,
        text,
        is_correct,
      })),
    };
    try {
      if (editing) await staff.update(`${PATH}${editing.id}/`, payload);
      else await staff.create(PATH, payload);
      close();
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    } finally {
      setBusy(false);
    }
  }

  async function remove(item: Question) {
    if (!window.confirm(t(locale, "admin.confirmDelete"))) return;
    try {
      await staff.remove(`${PATH}${item.id}/`);
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  return (
    <div className="space-y-4">
      {error && <Status status="bad" variant="alert" alert label={error} />}

      <Card
        title={t(locale, "admin.section.questions")}
        action={
          <div className="flex items-center gap-2">
            <input
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setPage(1);
              }}
              placeholder={t(locale, "admin.search")}
              className={`${INPUT} w-48`}
            />
            <Badge>{count}</Badge>
            <Button className="h-9" onClick={() => open(null)}>
              {t(locale, "admin.create")}
            </Button>
          </div>
        }
        bodyClassName="p-0"
      >
        {form && (
          <form
            key={editing ? editing.id : "new"}
            onSubmit={submit}
            className="grid gap-3 border-b rw-divider p-5 md:grid-cols-2"
          >
            <label className="block md:col-span-2">
              <span className={LABEL}>Savol matni (Markdown + LaTeX) *</span>
              <textarea
                value={form.text}
                onChange={(e) => setForm({ ...form, text: e.target.value })}
                rows={4}
                required
                className={`${INPUT} h-auto py-2 font-mono`}
              />
            </label>
            <label className="block md:col-span-2">
              <span className={LABEL}>
                Izoh (javobdan keyin ko&apos;rsatiladi)
              </span>
              <textarea
                value={form.explanation}
                onChange={(e) =>
                  setForm({ ...form, explanation: e.target.value })
                }
                rows={3}
                className={`${INPUT} h-auto py-2 font-mono`}
              />
            </label>
            <label className="block">
              <span className={LABEL}>Qiyinlik (800–3500) *</span>
              <input
                type="number"
                min={800}
                max={3500}
                required
                value={form.difficulty}
                onChange={(e) =>
                  setForm({ ...form, difficulty: Number(e.target.value) })
                }
                className={INPUT}
              />
            </label>
            <label className="block">
              <span className={LABEL}>Mavzular (slug, vergul bilan)</span>
              <input
                value={form.topics}
                onChange={(e) => setForm({ ...form, topics: e.target.value })}
                placeholder="math, graphs"
                className={INPUT}
              />
            </label>
            <label className="flex items-center gap-2 md:col-span-2">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) =>
                  setForm({ ...form, is_active: e.target.checked })
                }
                className="size-4"
              />
              <span className="text-theme-sm rw-strong">{t(locale, "admin.label.flag.active")}</span>
            </label>

            <div className="md:col-span-2">
              <div className="mb-2 flex items-center justify-between">
                <span className={LABEL}>
                  Variantlar (kamida 2, aynan bittasi to&apos;g&apos;ri) *
                </span>
                <button
                  type="button"
                  onClick={addChoice}
                  className="text-theme-xs rw-accent-ink hover:underline"
                >
                  {t(locale, "admin.text.addVariant")}
                </button>
              </div>
              <div className="space-y-2">
                {form.choices.map((c, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <input
                      type="number"
                      min={1}
                      required
                      value={c.order}
                      onChange={(e) =>
                        patchChoice(i, { order: Number(e.target.value) })
                      }
                      className={`${INPUT} w-16`}
                      aria-label={t(locale, "admin.title.order")}
                    />
                    <input
                      required
                      maxLength={500}
                      value={c.text}
                      onChange={(e) => patchChoice(i, { text: e.target.value })}
                      placeholder={fill(t(locale, "admin.text.variant"), { order: c.order })}
                      className={INPUT}
                    />
                    <label className="flex shrink-0 items-center gap-1 text-theme-xs rw-dim-2">
                      <input
                        type="radio"
                        name="correct"
                        checked={c.is_correct}
                        onChange={() => markCorrect(i)}
                        className="size-4"
                      />
                      To&apos;g&apos;ri
                    </label>
                    <button
                      type="button"
                      onClick={() => removeChoice(i)}
                      disabled={form.choices.length <= 2}
                      className="text-theme-xs rw-bad-ink hover:underline disabled:opacity-40"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-2 md:col-span-2">
              <Button type="submit" disabled={busy}>
                {t(locale, "admin.save")}
              </Button>
              <Button type="button" variant="outline" onClick={close}>
                {t(locale, "admin.cancel")}
              </Button>
            </div>
          </form>
        )}

        <Table>
          <THead>
            <TH>ID</TH>
            <TH>{t(locale, "col.question")}</TH>
            <TH>{t(locale, "problems.difficulty")}</TH>
            <TH>{t(locale, "problems.topics")}</TH>
            <TH>{t(locale, "col.options")}</TH>
            <TH>{t(locale, "admin.label.flag.active")}</TH>
            <TH align="right">{t(locale, "admin.actions")}</TH>
          </THead>
          <TBody>
            {rows.map((item) => (
              <TR key={item.id}>
                <TD>{item.id}</TD>
                <TD className="max-w-md">
                  <span className="line-clamp-2 font-mono text-theme-xs">
                    {item.text}
                  </span>
                </TD>
                <TD>
                  <DifficultyBadge value={item.difficulty} />
                </TD>
                <TD>
                  <div className="flex flex-wrap gap-1">
                    {item.topics.map((s) => (
                      <Badge key={s}>{s}</Badge>
                    ))}
                  </div>
                </TD>
                <TD>
                  <div className="flex flex-wrap gap-1">
                    {item.choices.map((c) => (
                      <Badge
                        key={c.id ?? c.order}
                        color={c.is_correct ? "success" : "neutral"}
                      >
                        {c.order}.{" "}
                        {c.text.length > 30
                          ? `${c.text.slice(0, 30)}…`
                          : c.text}
                      </Badge>
                    ))}
                  </div>
                </TD>
                <TD>
                  <Badge color={item.is_active ? "success" : "neutral"}>
                    {item.is_active ? t(locale, "admin.text.yes") : t(locale, "admin.text.no")}
                  </Badge>
                </TD>
                <TD align="right">
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => open(item)}
                      className="text-theme-xs rw-accent-ink hover:underline"
                    >
                      {t(locale, "admin.edit")}
                    </button>
                    <button
                      type="button"
                      onClick={() => remove(item)}
                      className="text-theme-xs rw-bad-ink hover:underline"
                    >
                      {t(locale, "admin.delete")}
                    </button>
                  </div>
                </TD>
              </TR>
            ))}
            {rows.length === 0 && (
              <EmptyRow colSpan={7}>{t(locale, "admin.noRows")}</EmptyRow>
            )}
          </TBody>
        </Table>
        {count > rows.length && (
          <div className="flex items-center justify-end gap-2 border-t rw-divider px-4 py-2 text-theme-xs">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="disabled:opacity-40"
            >
              ←
            </button>
            <span>{page}</span>
            <button
              type="button"
              disabled={page * rows.length >= count}
              onClick={() => setPage((p) => p + 1)}
              className="disabled:opacity-40"
            >
              →
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}
