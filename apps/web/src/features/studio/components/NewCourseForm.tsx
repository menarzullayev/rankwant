"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, LOCALE_NAMES, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { CONTENT_LOCALES, studioCourses, type ContentLocale } from "../api/courses";

/** A course starts from a title in its own language; everything else is
 *  written on the course's page. */
export function NewCourseForm() {
  const locale = useLocale();
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [baseLocale, setBaseLocale] = useState<ContentLocale>(
    CONTENT_LOCALES.find((code) => code === locale) ?? "uz",
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const course = await studioCourses.create({ title, base_locale: baseLocale, level: "beginner" });
      router.push(`/studio/courses/${encodeURIComponent(course.slug)}` as Route);
    } catch (err) {
      if (err instanceof ApiError && err.details && "slug" in err.details) {
        setError(t(locale, "studio.error.slug"));
      } else {
        setError(err instanceof ApiError ? errorText(locale, err.code) : String(err));
      }
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4 rw-radius border rw-line rw-surface p-5">
      <h2 className="text-theme-base font-semibold rw-strong">{t(locale, "studio.courses.new")}</h2>
      <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_12rem]">
        <Field
          name="title"
          label={t(locale, "studio.field.title")}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
          maxLength={200}
        />
        <SelectField
          name="base_locale"
          label={t(locale, "studio.course.baseLocale")}
          hint={t(locale, "studio.course.baseLocaleHint")}
          options={CONTENT_LOCALES.map((code) => ({ value: code, label: LOCALE_NAMES[code] }))}
          value={baseLocale}
          onChange={(value) => setBaseLocale(value as ContentLocale)}
        />
      </div>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={!title.trim()}>
        {t(locale, "studio.courses.create")}
      </Button>
    </form>
  );
}
