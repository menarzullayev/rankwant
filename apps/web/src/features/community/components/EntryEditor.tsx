"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Markdown } from "@/components/ui/Markdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { editEntry, parseTags, writeEntry, type EntryDetail } from "../api";

const TITLE_MAX = 200;
const BODY_MAX = 20000;

const FIELD =
  "w-full rw-radius-sm border rw-line rw-field-bg px-3 py-2 text-theme-sm rw-strong outline-none rw-focus-ring";

/** Write or edit a blog entry: Markdown with a preview (decision ④). */
export function EntryEditor({ entry }: { entry?: EntryDetail }) {
  const locale = useLocale();
  const router = useRouter();
  const [title, setTitle] = useState(entry?.title ?? "");
  const [body, setBody] = useState(entry?.body ?? "");
  const [tags, setTags] = useState(entry?.tags.join(", ") ?? "");
  const [preview, setPreview] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const draft = { title, body, tags: parseTags(tags) };
    try {
      const saved = entry ? await editEntry(entry.id, draft) : await writeEntry(draft);
      router.push(`/blogs/${saved.id}` as Route);
      router.refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? errorText(locale, caught.code, caught.message) : String(caught));
      setBusy(false);
    }
  }

  return (
    <form onSubmit={save} className="space-y-4">
      <label className="block space-y-1">
        <span className="text-theme-sm font-medium rw-strong">{t(locale, "blogs.form.title")}</span>
        <input
          value={title}
          maxLength={TITLE_MAX}
          required
          onChange={(event) => setTitle(event.target.value)}
          className={FIELD}
        />
      </label>

      <div className="space-y-1">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span id="entry-body-label" className="text-theme-sm font-medium rw-strong">
            {t(locale, "blogs.form.body")}
          </span>
          <Button type="button" variant="outline" aria-pressed={preview} onClick={() => setPreview(!preview)}>
            {t(locale, preview ? "blogs.form.write" : "blogs.form.preview")}
          </Button>
        </div>
        {preview ? (
          <div className="min-h-64 rw-radius-sm border rw-line p-4">
            <Markdown>{body || t(locale, "blogs.form.empty")}</Markdown>
          </div>
        ) : (
          <textarea
            value={body}
            maxLength={BODY_MAX}
            rows={16}
            aria-labelledby="entry-body-label"
            placeholder={t(locale, "blogs.form.bodyHint")}
            onChange={(event) => setBody(event.target.value)}
            className={`${FIELD} resize-y font-mono`}
          />
        )}
        <p className="text-theme-xs rw-faint">{fill(t(locale, "blogs.form.count"), { count: body.length, max: BODY_MAX })}</p>
      </div>

      <label className="block space-y-1">
        <span className="text-theme-sm font-medium rw-strong">{t(locale, "blogs.form.tags")}</span>
        <input
          value={tags}
          placeholder={t(locale, "blogs.form.tagsHint")}
          onChange={(event) => setTags(event.target.value)}
          className={FIELD}
        />
      </label>

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={!title.trim() || !body.trim()}>
        {t(locale, entry ? "blogs.form.save" : "blogs.form.publish")}
      </Button>
    </form>
  );
}
