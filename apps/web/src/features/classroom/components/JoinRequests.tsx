"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { numericDate } from "@rankwant/shared/format";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson, postJson, type ClassroomJoinRequest } from "@/lib/api";

import { failure } from "./failure";

/** Students waiting to get in. The owner and assistants answer them; the
 *  answer reaches the student as a notification (ADR-0061 § 3). */
export function JoinRequests({ slug, onDecided }: { slug: string; onDecided: () => void }) {
  const locale = useLocale();
  const [rows, setRows] = useState<ClassroomJoinRequest[] | null>(null);
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState("");
  const base = `/classrooms/${encodeURIComponent(slug)}/requests/`;

  useEffect(() => {
    getJson<ClassroomJoinRequest[]>(base)
      .then(setRows)
      .catch(() => setRows([]));
  }, [base]);

  async function decide(id: number, verb: "approve" | "reject") {
    setBusy(id);
    setError("");
    try {
      await postJson(`${base}${id}/${verb}/`, {});
      setRows((all) => (all ?? []).filter((row) => row.id !== id));
      onDecided();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(null);
    }
  }

  if (rows === null) return null;

  return (
    <Card title={t(locale, "classroom.requests")} bodyClassName="p-0">
      {error && (
        <p role="alert" className="px-5 pt-3 text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <ul className="divide-y rw-divide">
        {rows.map((row) => (
          <li key={row.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
            <div className="min-w-0 flex-1">
              <Link href={`/users/${row.username}`} className="font-medium rw-link-hover">
                {row.username}
              </Link>
              <span className="ml-2 text-theme-xs rw-faint">
                Skills {row.rating_skills} · {numericDate(row.created_at)}
              </span>
            </div>
            <div className="flex gap-2">
              <Button busy={busy === row.id} onClick={() => void decide(row.id, "approve")}>
                {t(locale, "classroom.approve")}
              </Button>
              <Button
                variant="outline"
                disabled={busy === row.id}
                onClick={() => void decide(row.id, "reject")}
              >
                {t(locale, "classroom.reject")}
              </Button>
            </div>
          </li>
        ))}
        {rows.length === 0 && (
          <li className="px-5 py-6 text-center text-theme-sm rw-faint">
            {t(locale, "classroom.requests.none")}
          </li>
        )}
      </ul>
    </Card>
  );
}
