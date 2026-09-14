"use client";

import Link from "next/link";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { date, t, type MessageKey } from "@/i18n/messages";

type Report = {
  id: number;
  problem: string;
  username: string;
  reason: string;
  comment: string;
  status: "open" | "accepted" | "rejected";
  created_at: string;
  [key: string]: unknown;
};

const REASON_LABEL: Record<string, MessageKey> = {
  statement: "admin.text.reportReasonStatement",
  tests: "admin.text.reportReasonTests",
  translation: "admin.text.reportReasonTranslation",
  duplicate: "admin.text.reportReasonDuplicate",
  other: "admin.text.reportReasonOther",
};

const STATUS_LABEL: Record<Report["status"], MessageKey> = {
  open: "admin.label.flag.open",
  accepted: "admin.label.status.accepted",
  rejected: "admin.label.status.rejectedShort",
};

const columns: ColumnDef<Report>[] = [
  {
    key: "problem",
    labelKey: "admin.label.text.problem",
    render: (r) => (
      <Link
        href={`/problems/${r.problem}`}
        className="font-mono text-theme-xs rw-accent-ink hover:underline"
      >
        {r.problem}
      </Link>
    ),
  },
  {
    key: "reason",
    labelKey: "admin.label.text.reason",
    render: (r, _reload, locale) => (
      <Badge>
        {REASON_LABEL[r.reason]
          ? t(locale, REASON_LABEL[r.reason])
          : r.reason}
      </Badge>
    ),
  },
  {
    key: "comment",
    labelKey: "admin.label.text.comment",
    // Izoh uzun bo'lishi mumkin — ro'yxatda kesiladi, to'lig'i hoverda.
    render: (r) =>
      r.comment ? (
        <span title={r.comment} className="line-clamp-2 rw-dim">
          {r.comment}
        </span>
      ) : (
        <span className="rw-faint">—</span>
      ),
  },
  { key: "username", labelKey: "admin.label.text.who" },
  {
    key: "status",
    labelKey: "admin.label.text.status",
    render: (r, _reload, locale) => (
      <Badge
        color={
          r.status === "open"
            ? "warning"
            : r.status === "accepted"
              ? "success"
              : "neutral"
        }
      >
        {t(locale, STATUS_LABEL[r.status])}
      </Badge>
    ),
  },
  {
    key: "created_at",
    labelKey: "admin.label.text.date",
    align: "right",
    render: (r, _reload, locale) => (
      <span className="rw-faint tabular-nums">
        {date(r.created_at, locale)}
      </span>
    ),
  },
];

/** Faqat holat tahrirlanadi: sabab va izoh — xabar beruvchining so'zi,
 *  uni o'zgartirish yozuvni ma'nosiz qilardi (backend ham rad etadi). */
const fields: FieldDef[] = [
  {
    name: "status",
    labelKey: "admin.label.text.status",
    type: "select",
    required: true,
    options: (["open", "accepted", "rejected"] as const).map((value) => ({
      value,
      labelKey: STATUS_LABEL[value],
    })),
  },
];

export function ReportsAdmin() {
  return (
    <CrudPage<Report>
      title="Nuqson xabarlari"
      path="/staff/problem-reports/"
      columns={columns}
      fields={fields}
      canCreate={false}
      fromItem={(r) => ({ status: r.status })}
    />
  );
}
