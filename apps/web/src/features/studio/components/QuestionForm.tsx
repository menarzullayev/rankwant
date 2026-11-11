"use client";

import { useState } from "react";

import { FormBox } from "@/components/form/FormKit";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t, type MessageKey } from "@/i18n/messages";
import { ApiError, patchJson, postJson, type QuestionKind } from "@/lib/api";

import {
  KIND_KEYS,
  QUESTION_KINDS,
  type AuthorChoice,
  type AuthorQuestion,
  type Folder,
} from "../api/quizzes";

const BLANK: AuthorChoice[] = [
  { order: 1, text: "", is_correct: true },
  { order: 2, text: "", is_correct: false },
];

/** One question of the teacher's bank, new or edited. */
export function QuestionForm({
  question,
  folders,
  folder,
  onSaved,
  onCancel,
}: {
  question: AuthorQuestion | null;
  folders: Folder[];
  /** The folder a new question goes into. */
  folder: number | null;
  onSaved: () => void;
  onCancel: () => void;
}) {
  const locale = useLocale();
  const [kind, setKind] = useState<QuestionKind>(question?.kind ?? "single");
  const [text, setText] = useState(question?.text ?? "");
  const [code, setCode] = useState(question?.code ?? "");
  const [codeLanguage, setCodeLanguage] = useState(question?.code_language ?? "");
  const [explanation, setExplanation] = useState(question?.explanation ?? "");
  const [folderId, setFolderId] = useState<string>(String(question?.folder ?? folder ?? ""));
  const [choices, setChoices] = useState<AuthorChoice[]>(
    question?.choices.length ? question.choices : BLANK,
  );
  const [number, setNumber] = useState(
    question?.answer_number !== null && question?.answer_number !== undefined
      ? String(question.answer_number)
      : "",
  );
  const [tolerance, setTolerance] = useState(String(question?.tolerance ?? 0));
  const [answerText, setAnswerText] = useState(question?.answer_text ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const withChoices = kind === "single" || kind === "multiple";

  function mark(index: number, value: boolean) {
    setChoices((rows) =>
      rows.map((row, i) =>
        i === index
          ? { ...row, is_correct: value }
          : kind === "single" && value
            ? { ...row, is_correct: false }
            : row,
      ),
    );
  }

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const body: Record<string, unknown> = {
      kind,
      text,
      code,
      code_language: codeLanguage,
      explanation,
      folder: folderId ? Number(folderId) : null,
    };
    if (withChoices) body.choices = choices.map((c, i) => ({ ...c, order: i + 1 }));
    if (kind === "number") {
      body.answer_number = number === "" ? null : Number(number.replace(",", "."));
      body.tolerance = Number(tolerance.replace(",", ".")) || 0;
    }
    if (kind === "text") body.answer_text = answerText;
    try {
      if (question) await patchJson(`/questions/mine/${question.id}/`, body);
      else await postJson("/questions/mine/", body);
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={save} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <SelectField
          name="kind"
          label={t(locale, "studio.questions.kind")}
          options={QUESTION_KINDS.map((value) => ({ value, label: t(locale, KIND_KEYS[value]) }))}
          value={kind}
          onChange={(value) => setKind(value as QuestionKind)}
        />
        <SelectField
          name="folder"
          label={t(locale, "studio.questions.folder")}
          placeholder={t(locale, "studio.questions.noFolder")}
          options={[
            { value: "", label: t(locale, "studio.questions.noFolder") },
            ...folders.map((f) => ({ value: String(f.id), label: f.name })),
          ]}
          value={folderId}
          onChange={setFolderId}
        />
      </div>
      <label className="block space-y-1">
        <span className="text-theme-sm font-medium rw-strong">{t(locale, "studio.questions.text")}</span>
        <textarea
          required
          rows={4}
          value={text}
          onChange={(event) => setText(event.target.value)}
          className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm"
        />
      </label>
      <div className="grid gap-4 md:grid-cols-[1fr_12rem]">
        <label className="block space-y-1">
          <span className="text-theme-sm font-medium rw-strong">{t(locale, "studio.questions.code")}</span>
          <textarea
            rows={3}
            value={code}
            onChange={(event) => setCode(event.target.value)}
            className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 font-mono text-theme-xs"
          />
        </label>
        <Field
          name="code_language"
          label={t(locale, "studio.questions.codeLanguage")}
          value={codeLanguage}
          onChange={(event) => setCodeLanguage(event.target.value)}
          maxLength={20}
        />
      </div>

      {withChoices && (
        <fieldset className="space-y-2">
          <legend className="text-theme-sm font-medium rw-strong">
            {t(locale, "studio.questions.choices")}
          </legend>
          {choices.map((choice, index) => (
            <div key={index} className="flex items-center gap-3">
              <FormBox
                shape="square"
                checked={choice.is_correct}
                aria-label={t(locale, "studio.questions.correct")}
                onChange={(event) => mark(index, event.target.checked)}
              />
              <input
                value={choice.text}
                required
                aria-label={`${t(locale, "studio.questions.choices")} ${index + 1}`}
                onChange={(event) =>
                  setChoices((rows) =>
                    rows.map((row, i) => (i === index ? { ...row, text: event.target.value } : row)),
                  )
                }
                className="min-w-0 flex-1 rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm"
              />
              {choices.length > 2 && (
                <Button
                  variant="outline"
                  onClick={() => setChoices((rows) => rows.filter((_, i) => i !== index))}
                >
                  ×
                </Button>
              )}
            </div>
          ))}
          <Button
            variant="outline"
            onClick={() =>
              setChoices((rows) => [
                ...rows,
                { order: rows.length + 1, text: "", is_correct: false },
              ])
            }
          >
            {t(locale, "studio.questions.addChoice")}
          </Button>
        </fieldset>
      )}

      {kind === "number" && (
        <div className="grid gap-4 md:grid-cols-2">
          <Field
            name="answer_number"
            label={t(locale, "studio.questions.answerNumber")}
            inputMode="decimal"
            value={number}
            onChange={(event) => setNumber(event.target.value)}
            required
          />
          <Field
            name="tolerance"
            label={t(locale, "studio.questions.tolerance")}
            inputMode="decimal"
            value={tolerance}
            onChange={(event) => setTolerance(event.target.value)}
          />
        </div>
      )}

      {kind === "text" && (
        <label className="block space-y-1">
          <span className="text-theme-sm font-medium rw-strong">
            {t(locale, "studio.questions.answerText")}
          </span>
          <textarea
            required
            rows={3}
            value={answerText}
            onChange={(event) => setAnswerText(event.target.value)}
            className="w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm"
          />
        </label>
      )}

      <Field
        name="explanation"
        label={t(locale, "studio.questions.explanation")}
        value={explanation}
        onChange={(event) => setExplanation(event.target.value)}
      />

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        <Button type="submit" busy={busy}>
          {t(locale, "studio.questions.save")}
        </Button>
        <Button variant="outline" onClick={onCancel}>
          {t(locale, "studio.questions.cancel")}
        </Button>
      </div>
    </form>
  );
}
