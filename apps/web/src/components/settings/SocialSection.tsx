"use client";

import { Suspense } from "react";

import { SocialAccounts } from "@/components/SocialAccounts";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { putJson, type ExternalKind, type ExternalProfile } from "@/lib/api";
import { Hint, Loading, Status, useAction, useLoad } from "./kit";

const KINDS: { kind: ExternalKind; label: string }[] = [
  { kind: "codeforces", label: "Codeforces" },
  { kind: "atcoder", label: "AtCoder" },
  { kind: "leetcode", label: "LeetCode" },
  { kind: "linkedin", label: "LinkedIn" },
];

type Row = ExternalProfile & { fetched_at: string | null };

function ExternalCard() {
  const locale = useLocale();
  const external = useLoad<Row[]>("/me/external/");
  const action = useAction();
  const byKind = new Map((external.data ?? []).map((row) => [row.kind, row]));

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const rows = KINDS.map(({ kind }) => ({
      kind,
      handle: String(form.get(kind) ?? "").trim(),
    })).filter((row) => row.handle);
    await action.run(async () => {
      external.setData(await putJson<Row[]>("/me/external/", rows));
    });
  }

  function hintFor(kind: ExternalKind): string | undefined {
    if (kind === "linkedin") return t(locale, "settings.linkedinHint");
    const row = byKind.get(kind);
    if (!row) return undefined;
    if (row.rating !== null)
      return fill(t(locale, "settings.externalRating"), {
        rating: row.rating,
        max: row.max_rating ?? row.rating,
      });
    return row.fetched_at
      ? t(locale, "settings.externalNoRating")
      : t(locale, "settings.externalPending");
  }

  return (
    <Card title={t(locale, "settings.external")}>
      <Hint>{t(locale, "settings.externalHint")}</Hint>
      {!external.data && !external.error ? (
        <div className="mt-3">
          <Loading />
        </div>
      ) : (
        <form onSubmit={save} className="mt-4 flex flex-col gap-4">
          {KINDS.map(({ kind, label }) => (
            <Field
              key={kind}
              label={label}
              name={kind}
              defaultValue={byKind.get(kind)?.handle ?? ""}
              hint={hintFor(kind)}
              autoComplete="off"
              spellCheck={false}
              maxLength={200}
            />
          ))}
          <Status error={action.error || external.error} done={action.done} />
          <Button type="submit" busy={action.busy} className="self-start">
            {t(locale, "settings.save")}
          </Button>
        </form>
      )}
    </Card>
  );
}

export function SocialSection() {
  return (
    <>
      <Suspense>
        <SocialAccounts />
      </Suspense>
      <ExternalCard />
    </>
  );
}
