"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Dropdown } from "@/components/ui/Dropdown";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Yo'l xaritasi boshqaruvi — `/admin/platform-roadmap`.
 *
 *  ⚠️ `status` FORMADA YO'Q, ataylab: u `set-status` amali orqali
 *  o'zgaradi, chunki o'sha amal o'tish vaqtini ham yozadi
 *  (`planned_at`/`started_at`/`released_at`). To'g'ridan-to'g'ri yozish
 *  batafsil sahifadagi "holat tarixi" ni bo'sh qoldirardi.
 *
 *  Jamoa taklifni shu yerdan `planned` ga o'tkazadi — bu tasdiqning o'zi
 *  (alohida "nashr qilish" amali yo'q).
 */

type RoadmapStatus =
  | "suggested"
  | "planned"
  | "in_progress"
  | "released"
  | "declined";

type RoadmapItem = {
  id: number;
  title: string;
  body: string;
  status: RoadmapStatus;
  target_quarter: string;
  update: number | null;
  planned_at: string | null;
  started_at: string | null;
  released_at: string | null;
  is_enabled: boolean;
  author: string | null;
  vote_count: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/platform-roadmap/";

/** `apps/api/roadmap/models.py` `Status` bilan bir xil. */
const STATUS: Record<RoadmapStatus, { labelKey: MessageKey; color: BadgeColor }> = {
  suggested: { labelKey: "admin.label.status.inReview", color: "info" },
  planned: { labelKey: "admin.label.status.planned", color: "brand" },
  in_progress: { labelKey: "admin.label.status.inProgress", color: "warning" },
  released: { labelKey: "admin.label.status.shipped", color: "success" },
  declined: { labelKey: "admin.label.status.rejected", color: "neutral" },
};

const FIELDS: FieldDef[] = [
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  {
    name: "target_quarter",
    labelKey: "admin.label.text.deadline",
    type: "text",
    helpKey: "admin.help.targetQuarter",
  },
  {
    name: "update",
    labelKey: "admin.label.tech.changelogId",
    type: "number",
    helpKey: "admin.help.changelogId",
  },
  {
    name: "is_enabled",
    labelKey: "admin.label.status.enabled",
    type: "checkbox",
    helpKey: "admin.help.softDelete",
  },
  { name: "body", labelKey: "admin.label.text.descriptionMarkdown", type: "textarea", rows: 10 },
];

/** Holatni o'zgartirish — `set-status` amali orqali. */
function StatusSelect({
  row,
  reload,
}: {
  row: RoadmapItem;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [status, setStatus] = useState<RoadmapStatus>(row.status);
  const [error, setError] = useState("");

  async function change(next: RoadmapStatus) {
    if (next === status) return;
    setError("");
    try {
      const updated = await staff.action<RoadmapItem>(`${PATH}${row.id}/set-status/`, {
        status: next,
      });
      setStatus(updated.status);
      reload?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? errorText(locale, caught.code, caught.message)
          : String(caught),
      );
    }
  }

  if (error) {
    return (
      <span title={error}>
        <Badge color="error">{t(locale, "status.bad")}</Badge>
      </span>
    );
  }

  return (
    <Dropdown
      size="xs"
      hideLabel
      label={t(locale, "admin.label.text.status")}
      value={status}
      onChange={(next) => void change(next as RoadmapStatus)}
      options={(Object.keys(STATUS) as RoadmapStatus[]).map((value) => ({
        value,
        label: t(locale, STATUS[value].labelKey),
      }))}
      className="w-40"
    />
  );
}

const COLUMNS: ColumnDef<RoadmapItem>[] = [
  { key: "title", labelKey: "admin.label.text.title" },
  {
    key: "status",
    labelKey: "admin.label.text.status",
    render: (row, reload) => (
      <StatusSelect key={`${row.id}-${row.status}`} row={row} reload={reload} />
    ),
  },
  { key: "target_quarter", labelKey: "admin.label.text.deadline" },
  { key: "vote_count", labelKey: "admin.label.misc.votes", align: "right" },
  { key: "comment_count", labelKey: "admin.label.text.comment", align: "right" },
  {
    key: "author",
    labelKey: "admin.label.text.author",
    render: (row) => row.author ?? "—",
  },
  {
    key: "is_enabled",
    labelKey: "admin.label.text.flag",
    render: (row, _reload, locale) => (
      <Badge color={row.is_enabled ? "success" : "warning"}>
        {row.is_enabled ? t(locale, "admin.label.status.enabled") : t(locale, "admin.text.disabled")}
      </Badge>
    ),
  },
];

export function PlatformRoadmapAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<RoadmapItem>
      title={t(locale, "admin.section.platformRoadmap")}
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={FIELDS}
      searchable
      ordering="-created_at"
      // O'chirish RUXSAT ETILGAN, lekin u spam va haqorat uchun —
      // "kerak emas" degan taklif uchun emas. Ular `declined` bo'ladi va
      // ro'yxatda ko'rinib turadi: aks holda odam "yozdim, javob
      // bo'lmadi" degan taassurot bilan qoladi.
    />
  );
}
