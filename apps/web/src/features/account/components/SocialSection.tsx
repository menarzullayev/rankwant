"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { dateTime, fill, t, type Locale } from "@/i18n/messages";
import {
  getJson,
  postJson,
  putJson,
  type ExternalKind,
  type ExternalProfile,
} from "@/lib/api";
import { EXTERNAL_LABEL } from "@/lib/external-links";
import { SavedForm } from "./SaveBar";
import { Hint, Loading, Status, useAction, useLoad } from "./section-kit";

/** Tartib va nom `EXTERNAL_LABEL` dan olinadi — ilgari bu ro'yxat
 *  o'sha jadvalni takrorlab, yana "Blog" ni ham qo'lda yozardi. Nomlarning
 *  aksari BREND (Codeforces, GitHub, ...) va tarjima qilinmaydi; "Blog"
 *  esa oddiy so'z, shuning uchun u tarjima qilinadi. */
const KIND_ORDER: ExternalKind[] = [
  "codeforces",
  "atcoder",
  "leetcode",
  "linkedin",
  "telegram",
  "github",
  "instagram",
  "x",
  "youtube",
  "kaggle",
  "blog",
];

const kindLabel = (locale: Locale, kind: ExternalKind) =>
  kind === "blog" ? t(locale, "external.blog") : EXTERNAL_LABEL[kind];

/** Reytingi ochiq API'dan olinadiganlar — qolganlari faqat havola. */
const RATED = new Set<ExternalKind>(["codeforces", "atcoder", "leetcode"]);
/** Ulangan kirish hisobidan taxallus olinadiganlar (ADR-0017). */
const CONNECTED = new Set<ExternalKind>(["telegram", "github"]);
/** How long after asking for a refresh the row is read again. The fetch
 *  runs in a worker; this is one look, not a poll. */
const REFRESH_WAIT_MS = 4000;

type Row = ExternalProfile & { fetched_at: string | null };

/** Profiles on other platforms: one row per platform that has a handle,
 *  with what was read from it, and the rest behind "add" buttons
 *  (decision of 2026-10-05).
 *
 *  It used to be eleven text fields. A mistyped handle looked exactly like
 *  a correct one, and nine of the eleven were usually empty. */
function ExternalCard() {
  const locale = useLocale();
  const external = useLoad<Row[]>("/me/external/");
  const connected = useLoad<Partial<Record<ExternalKind, string>>>("/me/external/connected/");
  const [filled, setFilled] = useState<Partial<Record<ExternalKind, string>>>({});
  const [added, setAdded] = useState<ExternalKind[]>([]);
  const [refreshing, setRefreshing] = useState<ExternalKind | null>(null);
  const action = useAction();
  const refresh = useAction();
  const byKind = new Map((external.data ?? []).map((row) => [row.kind, row]));
  const shown = KIND_ORDER.filter((kind) => byKind.has(kind) || added.includes(kind));
  const rest = KIND_ORDER.filter((kind) => !shown.includes(kind));

  function clear() {
    setAdded([]);
    setFilled({});
  }

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const rows = KIND_ORDER.map((kind) => ({
      kind,
      handle: String(form.get(kind) ?? "").trim(),
    })).filter((row) => row.handle);
    const ok = await action.run(async () => {
      external.setData(await putJson<Row[]>("/me/external/", rows));
    });
    if (ok) clear();
    return ok;
  }

  async function reread(kind: ExternalKind) {
    setRefreshing(kind);
    await refresh.run(async () => {
      await postJson(`/me/external/${kind}/refresh/`, {});
      await new Promise((done) => window.setTimeout(done, REFRESH_WAIT_MS));
      external.setData(await getJson<Row[]>("/me/external/"));
    });
    setRefreshing(null);
  }

  /** What was read from the platform — the proof that the handle is right. */
  function status(kind: ExternalKind): string | undefined {
    if (kind === "linkedin") return t(locale, "settings.linkedinHint");
    if (kind === "blog") return t(locale, "settings.blogHint");
    if (!RATED.has(kind)) return undefined;
    const row = byKind.get(kind);
    if (!row) return undefined;
    if (!row.fetched_at) return t(locale, "settings.externalPending");
    const when = fill(t(locale, "settings.externalUpdated"), {
      time: dateTime(row.fetched_at, locale),
    });
    if (row.rating === null) return `${t(locale, "settings.externalNoRating")} · ${when}`;
    const rating = fill(t(locale, "settings.externalRating"), {
      rating: row.rating,
      max: row.max_rating ?? row.rating,
    });
    return [rating, row.rank, when].filter(Boolean).join(" · ");
  }

  return (
    <Card title={t(locale, "settings.external")}>
      <Hint>{t(locale, "settings.externalHint")}</Hint>
      {!external.data && !external.error ? (
        <div className="mt-3">
          <Loading />
        </div>
      ) : (
        <SavedForm
          onSubmit={save}
          onReset={clear}
          dirty={added.length > 0 || Object.keys(filled).length > 0}
          className="mt-4 flex flex-col gap-4"
        >
          {shown.length > 0 && (
            <ul className="divide-y rw-divide">
              {shown.map((kind) => {
                const handle = CONNECTED.has(kind) ? connected.data?.[kind] : undefined;
                const current = filled[kind] ?? byKind.get(kind)?.handle ?? "";
                const label = kindLabel(locale, kind);
                return (
                  <li key={kind} className="flex flex-wrap items-end gap-3 py-4 first:pt-0">
                    <div className="min-w-0 flex-1 basis-64 space-y-1.5">
                      <Field
                        key={`${kind}:${filled[kind] ?? ""}`}
                        label={label}
                        name={kind}
                        defaultValue={current}
                        hint={status(kind)}
                        autoComplete="off"
                        spellCheck={false}
                        maxLength={200}
                      />
                      {handle && handle !== current && (
                        <button
                          type="button"
                          onClick={() => setFilled({ ...filled, [kind]: handle })}
                          className="inline-flex min-h-11 items-center text-theme-xs font-medium rw-accent-ink hover:underline"
                        >
                          {fill(t(locale, "settings.fromConnected"), { handle })}
                        </button>
                      )}
                    </div>
                    {RATED.has(kind) && byKind.has(kind) && (
                      <Button
                        type="button"
                        variant="outline"
                        busy={refreshing === kind}
                        disabled={refreshing !== null}
                        onClick={() => reread(kind)}
                        aria-label={`${label}: ${t(locale, "settings.externalRefresh")}`}
                      >
                        {t(locale, "settings.externalRefresh")}
                      </Button>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
          {rest.length > 0 && (
            <div className="space-y-2">
              <p className="text-theme-sm font-medium rw-strong">
                {t(locale, "settings.externalAdd")}
              </p>
              <div className="flex flex-wrap gap-2">
                {rest.map((kind) => (
                  <Button
                    key={kind}
                    type="button"
                    variant="outline"
                    onClick={() => setAdded([...added, kind])}
                  >
                    {kindLabel(locale, kind)}
                  </Button>
                ))}
              </div>
            </div>
          )}
          <Status error={action.error || refresh.error || external.error} done={action.done} />
        </SavedForm>
      )}
    </Card>
  );
}

export function SocialSection() {
  return <ExternalCard />;
}
