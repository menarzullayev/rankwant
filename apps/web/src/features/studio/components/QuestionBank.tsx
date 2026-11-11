"use client";

import { useCallback, useEffect, useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type MessageKey } from "@/i18n/messages";
import { ApiError, deleteJson, getJson, postJson, type Paginated, type QuestionKind } from "@/lib/api";

import { KIND_KEYS, type AuthorQuestion, type Folder } from "../api/quizzes";
import { QuestionForm } from "./QuestionForm";

/** "all", "none" (no folder) or a folder id. */
type Filter = string;

/** The teacher's own question bank, in folders (ADR-0061 § 5). */
export function QuestionBank() {
  const locale = useLocale();
  const confirm = useConfirm();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [rows, setRows] = useState<AuthorQuestion[] | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [editing, setEditing] = useState<AuthorQuestion | "new" | null>(null);
  const [folderName, setFolderName] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(() => {
    void getJson<Folder[]>("/question-folders/")
      .then(setFolders)
      .catch(() => setFolders([]));
    const query = filter === "all" ? "" : `&folder=${filter}`;
    void getJson<Paginated<AuthorQuestion>>(`/questions/mine/?page_size=100${query}`)
      .then((page) => setRows(page.results))
      .catch(() => setRows([]));
  }, [filter]);

  useEffect(() => load(), [load]);

  const fail = (err: unknown) =>
    setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));

  async function addFolder(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!folderName.trim()) return;
    try {
      await postJson("/question-folders/", { name: folderName.trim() });
      setFolderName("");
      load();
    } catch (err) {
      fail(err);
    }
  }

  async function remove(question: AuthorQuestion, origin: HTMLElement) {
    const ok = await confirm(t(locale, "studio.questions.deleteConfirm"), {
      danger: true,
      kind: "popover",
      origin,
      confirmLabel: t(locale, "studio.questions.delete"),
    });
    if (!ok) return;
    try {
      await deleteJson(`/questions/mine/${question.id}/`);
      load();
    } catch (err) {
      fail(err);
    }
  }

  const chips: { value: Filter; label: string }[] = [
    { value: "all", label: t(locale, "studio.questions.allFolders") },
    { value: "none", label: t(locale, "studio.questions.noFolder") },
    ...folders.map((f) => ({ value: String(f.id), label: `${f.name} · ${f.question_count}` })),
  ];

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.questions")}</h1>
          <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "studio.questions.intro")}</p>
        </div>
        {editing === null && (
          <Button onClick={() => setEditing("new")}>{t(locale, "studio.questions.new")}</Button>
        )}
      </header>

      <div className="flex flex-wrap items-center gap-2">
        {chips.map((chip) => (
          <button
            key={chip.value}
            type="button"
            aria-pressed={filter === chip.value}
            onClick={() => setFilter(chip.value)}
            className={`min-h-9 rounded-full border px-3 text-theme-sm ${filter === chip.value ? "rw-accent-line rw-accent-soft rw-accent-ink" : "rw-line rw-dim"}`}
          >
            {chip.label}
          </button>
        ))}
        <form onSubmit={addFolder} className="flex items-end gap-2">
          <Field
            name="folder_name"
            label={t(locale, "studio.questions.newFolder")}
            value={folderName}
            onChange={(event) => setFolderName(event.target.value)}
            maxLength={100}
          />
          <Button type="submit" variant="outline" disabled={!folderName.trim()}>
            +
          </Button>
        </form>
      </div>

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}

      {editing !== null && (
        <Card title={t(locale, editing === "new" ? "studio.questions.new" : "studio.questions.edit")}>
          <QuestionForm
            key={editing === "new" ? "new" : editing.id}
            question={editing === "new" ? null : editing}
            folders={folders}
            folder={filter !== "all" && filter !== "none" ? Number(filter) : null}
            onSaved={() => {
              setEditing(null);
              load();
            }}
            onCancel={() => setEditing(null)}
          />
        </Card>
      )}

      <Card bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {(rows ?? []).map((row) => (
            <li key={row.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
              {/* Full width on a phone: the buttons go under the text. */}
              <div className="w-full min-w-0 sm:w-auto sm:flex-1">
                <p className="line-clamp-2 text-theme-sm rw-strong">{row.text}</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  <Badge>{t(locale, KIND_KEYS[row.kind])}</Badge>
                  {row.used > 0 && (
                    <Badge color="info">
                      {fill(t(locale, "studio.questions.used"), { count: row.used })}
                    </Badge>
                  )}
                </div>
              </div>
              <Button variant="outline" onClick={() => setEditing(row)}>
                {t(locale, "studio.questions.edit")}
              </Button>
              <Button variant="outline" onClick={(event) => void remove(row, event.currentTarget)}>
                {t(locale, "studio.questions.delete")}
              </Button>
            </li>
          ))}
          {rows !== null && rows.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "studio.questions.empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
