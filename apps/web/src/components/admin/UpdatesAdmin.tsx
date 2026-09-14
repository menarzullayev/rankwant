"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey, errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Changelog boshqaruvi — `/admin/updates`.
 *
 *  ⚠️ TARJIMALAR bu formada tahrirlanmaydi. Ular oqim bo'yicha AI dan
 *  keladi (qaror 16: AI qoralama → jamoa tahriri → AI tarjima ×10), ya'ni
 *  qo'lda yozish asosiy yo'l emas. Ustun qaysi tillar tayyor ekanini
 *  ko'rsatadi — bo'sh qolganini ko'rish uchun.
 *
 *  Forma `translations` yubormaydi, ya'ni serializer ularga TEGMAYDI
 *  (u faqat maydon berilganda sinxronlaydi) — mavjud tarjimalar saqlanadi.
 */

type UpdateKind =
  | "new"
  | "improved"
  | "fixed"
  | "performance"
  | "security"
  | "design"
  | "content"
  | "infrastructure"
  | "breaking"
  | "deprecated";

type UpdateModule =
  | "problems"
  | "contests"
  | "arena"
  | "judge"
  | "ratings"
  | "qvant"
  | "profile"
  | "classroom"
  | "quizzes"
  | "content"
  | "design"
  | "core";

type SystemUpdate = {
  id: number;
  kind: UpdateKind;
  module: UpdateModule;
  status: "draft" | "published" | "withdrawn";
  version: string;
  title: string;
  body: string;
  locale: string;
  image: string;
  source_repo: string;
  source_refs: string[];
  source_url: string;
  released_at: string;
  published_at: string | null;
  is_enabled: boolean;
  author: string | null;
  translations: { locale: string; is_machine: boolean }[];
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/updates/";

/** `apps/api/updates/models.py` `Kind` bilan bir xil tartibda. */
// Kalitlar allaqachon mavjud (`update.kind.*`) — nusxa emas.
const KIND: Record<UpdateKind, MessageKey> = {
  new: "update.kind.new",
  improved: "update.kind.improved",
  fixed: "update.kind.fixed",
  performance: "update.kind.performance",
  security: "update.kind.security",
  design: "update.kind.design",
  content: "update.kind.content",
  infrastructure: "update.kind.infrastructure",
  breaking: "update.kind.breaking",
  deprecated: "update.kind.deprecated",
};

// Kalitlar allaqachon mavjud (`update.module.*`) — nusxa emas.
const MODULE: Record<UpdateModule, MessageKey> = {
  problems: "update.module.problems",
  contests: "update.module.contests",
  arena: "update.module.arena",
  judge: "update.module.judge",
  ratings: "update.module.ratings",
  qvant: "update.module.qvant",
  profile: "update.module.profile",
  classroom: "update.module.classroom",
  quizzes: "update.module.quizzes",
  content: "update.module.content",
  design: "update.module.design",
  core: "update.module.core",
};

const STATUS_LABEL: Record<SystemUpdate["status"], MessageKey> = {
  draft: "admin.label.status.draft",
  published: "admin.label.status.published",
  withdrawn: "admin.label.status.withdrawn",
};

const options = <T extends string>(table: Record<T, MessageKey>) =>
  (Object.keys(table) as T[]).map((value) => ({ value, labelKey: table[value] }));

const FIELDS: FieldDef[] = [
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  {
    name: "kind",
    labelKey: "admin.label.text.kind",
    type: "select",
    required: true,
    options: options(KIND),
  },
  {
    name: "module",
    labelKey: "admin.label.text.module",
    type: "select",
    required: true,
    options: options(MODULE),
  },
  {
    name: "status",
    labelKey: "admin.label.text.status",
    type: "select",
    required: true,
    options: options(STATUS_LABEL),
    helpKey: "admin.help.publishedAtAuto",
  },
  {
    name: "released_at",
    labelKey: "admin.label.date.releasedAt",
    type: "datetime",
    required: true,
    helpKey: "admin.help.releasedAtReal",
  },
  { name: "version", labelKey: "admin.label.text.version", type: "text", helpKey: "admin.help.versionOptional" },
  {
    name: "source_refs",
    labelKey: "admin.label.tech.sourceLinks",
    type: "list",
    helpKey: "admin.help.refsFormat",
  },
  { name: "source_repo", labelKey: "admin.label.text.repo", type: "text", helpKey: "admin.help.ownerRepo" },
  { name: "source_url", labelKey: "admin.label.tech.githubUrl", type: "text" },
  {
    name: "image",
    labelKey: "admin.label.tech.imageUrl",
    type: "text",
    helpKey: "admin.help.screenshotWhenNeeded",
  },
  { name: "is_enabled", labelKey: "admin.label.status.enabled", type: "checkbox" },
  { name: "body", labelKey: "admin.label.text.markdown", type: "textarea", rows: 12 },
];

/** Nashr / nashrdan olish — bitta tugma, jadvalni yangilaydi.
 *
 *  `reload` SHART: usiz qator eski `status` bilan qolardi va keyingi
 *  tahrir shu eski qiymatni yuborib, nashrni jimgina qaytarib qo'yardi. */
function PublishToggle({
  row,
  reload,
}: {
  row: SystemUpdate;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [status, setStatus] = useState(row.status);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<SystemUpdate>(
        `${PATH}${row.id}/${status === "published" ? "withdraw" : "publish"}/`,
      );
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

  const color = error
    ? "error"
    : status === "published"
      ? "success"
      : status === "withdrawn"
        ? "warning"
        : "neutral";

  return (
    <button
      type="button"
      onClick={toggle}
      title={
        error ||
        t(locale, status === "published" ? "admin.text.unpublish" : "admin.text.publishVerb")
      }
    >
      <Badge color={color}>
        {error ? t(locale, "admin.text.error") : t(locale, STATUS_LABEL[status])}
      </Badge>
    </button>
  );
}

/** Feature flag — modul darajasidagi rollback (qaror 17). */
function EnabledToggle({
  row,
  reload,
}: {
  row: SystemUpdate;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [enabled, setEnabled] = useState(row.is_enabled);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<SystemUpdate>(
        `${PATH}${row.id}/${enabled ? "disable" : "enable"}/`,
      );
      setEnabled(updated.is_enabled);
      reload?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? errorText(locale, caught.code, caught.message)
          : String(caught),
      );
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      title={error || (enabled ? t(locale, "admin.text.deleteRollback") : t(locale, "admin.text.enable"))}
    >
      <Badge color={error ? "error" : enabled ? "success" : "warning"}>
        {error ? t(locale, "admin.text.error") : enabled ? t(locale, "admin.label.status.enabled") : t(locale, "admin.text.disabled")}
      </Badge>
    </button>
  );
}

const COLUMNS: ColumnDef<SystemUpdate>[] = [
  { key: "title", labelKey: "admin.label.text.title" },
  {
    key: "kind",
    labelKey: "admin.label.text.kind",
    render: (row, _reload, locale) => (
      <Badge color={row.kind === "breaking" || row.kind === "deprecated" ? "error" : "info"}>
        {t(locale, KIND[row.kind])}
      </Badge>
    ),
  },
  {
    key: "module",
    labelKey: "admin.label.text.module",
    render: (row, _reload, locale) => t(locale, MODULE[row.module]),
  },
  {
    key: "status",
    labelKey: "admin.label.text.status",
    render: (row, reload) => (
      <PublishToggle key={`${row.id}-${row.status}`} row={row} reload={reload} />
    ),
  },
  {
    key: "is_enabled",
    labelKey: "admin.label.text.flag",
    render: (row, reload) => (
      <EnabledToggle key={`${row.id}-${row.is_enabled}`} row={row} reload={reload} />
    ),
  },
  { key: "released_at", labelKey: "admin.label.text.date" },
  {
    key: "translations",
    labelKey: "admin.label.name.translation",
    render: (row) => (
      <span title={row.translations.map((tr) => tr.locale).join(", ")}>
        {row.translations.length}/10
      </span>
    ),
  },
];

export function UpdatesAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<SystemUpdate>
      title={t(locale, "admin.section.updates")}
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={FIELDS}
      searchable
      ordering="-released_at"
    />
  );
}
