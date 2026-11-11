"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { CrudPage, type ColumnDef } from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Discussion moderation — `/admin/comments` (decision 2026-11-11 ⑥).
 *
 *  Moderation comes after: a comment appears at once, three reports hide
 *  it, staff decide here. "Hide" accepts the open reports, "Bring back"
 *  rejects them. Nothing is deleted — the reply chain under a comment
 *  stays attached.
 */

type StaffComment = {
  id: number;
  link: string;
  author: string | null;
  body: string;
  score: number;
  report_count: number;
  reasons: string[];
  is_hidden: boolean;
  is_deleted: boolean;
  created_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/community/comments/";

function HiddenToggle({ row, reload }: { row: StaffComment; reload?: () => void }) {
  const locale = useLocale();
  const [hidden, setHidden] = useState(row.is_hidden);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<StaffComment>(
        `${PATH}${row.id}/${hidden ? "unhide" : "hide"}/`,
      );
      setHidden(updated.is_hidden);
      reload?.();
    } catch (caught) {
      setError(caught instanceof ApiError ? errorText(locale, caught.code, caught.message) : String(caught));
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      title={error || (hidden ? t(locale, "admin.text.rollback") : t(locale, "admin.text.hide"))}
    >
      <Badge color={error ? "error" : hidden ? "warning" : "success"}>
        {error
          ? t(locale, "admin.text.error")
          : hidden
            ? t(locale, "admin.text.hidden")
            : t(locale, "admin.text.visible")}
      </Badge>
    </button>
  );
}

function Reasons({ row }: { row: StaffComment }) {
  const locale = useLocale();
  if (row.report_count === 0) return <span className="rw-faint">0</span>;
  return (
    <span className="flex flex-wrap gap-1">
      <Badge color="error">{row.report_count}</Badge>
      {row.reasons.map((reason, i) => (
        <Badge key={i} color="neutral">
          {t(locale, `discussion.reason.${reason}`)}
        </Badge>
      ))}
    </span>
  );
}

const COLUMNS: ColumnDef<StaffComment>[] = [
  {
    key: "body",
    labelKey: "admin.label.text.comment",
    render: (row) =>
      row.link ? (
        <Link href={row.link as Route} className="line-clamp-2 max-w-md rw-link-hover" title={row.body}>
          {row.body}
        </Link>
      ) : (
        <span className="line-clamp-2 max-w-md" title={row.body}>
          {row.body}
        </span>
      ),
  },
  { key: "author", labelKey: "admin.label.text.author", render: (row) => row.author ?? "—" },
  { key: "report_count", labelKey: "admin.label.text.reports", render: (row) => <Reasons row={row} /> },
  {
    key: "is_hidden",
    labelKey: "admin.label.text.status",
    render: (row, reload) => <HiddenToggle key={`${row.id}-${row.is_hidden}`} row={row} reload={reload} />,
  },
  {
    key: "created_at",
    labelKey: "admin.label.text.date",
    render: (row) => row.created_at.slice(0, 10),
  },
];

export function CommentsAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<StaffComment>
      title={t(locale, "admin.title.comments")}
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={[]}
      searchable
      ordering="-report_count"
      // A comment is someone else's words: staff hide it, they do not edit it.
      canCreate={false}
      readOnly
    />
  );
}
