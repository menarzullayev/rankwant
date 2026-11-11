"use client";

import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { postJson } from "@/lib/api";

import type { CoachLink } from "../api";
import { failure } from "./failure";

/** Students asking the reader to coach them. */
export function CoachRequests({ rows, onChange }: { rows: CoachLink[]; onChange: () => void }) {
  const locale = useLocale();
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState("");

  async function answer(id: number, verb: "accept" | "decline") {
    setBusy(id);
    setError("");
    try {
      await postJson(`/coaching/${id}/${verb}/`, {});
      onChange();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <Card title={t(locale, "coaching.requests")} bodyClassName="p-0">
      {error && (
        <p role="alert" className="px-5 pt-3 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <ul className="divide-y rw-divide">
        {rows.map((row) => (
          <li key={row.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
            <Link
              href={`/users/${row.student.username}`}
              className="min-w-0 flex-1 font-medium rw-link-hover"
            >
              {row.student.display_name || row.student.username}
            </Link>
            <div className="flex gap-2">
              <Button busy={busy === row.id} onClick={() => void answer(row.id, "accept")}>
                {t(locale, "classroom.approve")}
              </Button>
              <Button
                variant="outline"
                disabled={busy === row.id}
                onClick={() => void answer(row.id, "decline")}
              >
                {t(locale, "classroom.reject")}
              </Button>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
