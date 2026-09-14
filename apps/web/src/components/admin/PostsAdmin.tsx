"use client";

import { useState } from "react";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey, errorText } from "@/i18n/messages";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type PostKind = "news" | "announcement" | "editorial";

type Post = {
  slug: string;
  kind: PostKind;
  title: string;
  summary: string;
  body: string;
  locale: string;
  author: string | null;
  is_published: boolean;
  published_at: string | null;
  notify_users: boolean;
  notified_at: string | null;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/posts/";

const KIND: Record<PostKind, { labelKey: MessageKey; color: BadgeColor }> = {
  news: { labelKey: "admin.label.misc.news", color: "info" },
  announcement: { labelKey: "admin.label.misc.announcement", color: "warning" },
  editorial: { labelKey: "admin.label.text.editorNote", color: "brand" },
};

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "kind",
    labelKey: "admin.label.text.kind",
    type: "select",
    required: true,
    options: (Object.keys(KIND) as PostKind[]).map((k) => ({
      value: k,
      labelKey: KIND[k].labelKey,
    })),
  },
  { name: "title", labelKey: "admin.label.text.title", type: "text", required: true },
  { name: "summary", labelKey: "admin.label.text.summary", type: "text", helpKey: "admin.help.upTo300Chars" },
  {
    name: "locale",
    labelKey: "admin.label.text.language",
    type: "select",
    required: true,
    options: [
      { value: "uz", labelKey: "admin.label.lang.uz" },
      { value: "ru", labelKey: "admin.label.lang.ru" },
      { value: "en", labelKey: "admin.label.lang.en" },
    ],
  },
  { name: "is_published", labelKey: "admin.label.flag.published", type: "checkbox" },
  {
    name: "published_at",
    labelKey: "admin.label.date.publishedAt",
    type: "datetime",
    helpKey: "admin.help.autoPublishAt",
  },
  {
    name: "notify_users",
    labelKey: "admin.label.flag.notifyUsers",
    type: "checkbox",
    helpKey: "admin.help.notifyOnce",
  },
  {
    name: "body",
    labelKey: "admin.label.text.markdown",
    type: "textarea",
    required: true,
    rows: 14,
  },
];

function fmtDate(iso: string | null): string {
  return iso
    ? new Date(iso).toLocaleString("uz-UZ", {
        dateStyle: "short",
        timeStyle: "short",
      })
    : "—";
}

/** Nashr holati tugmasi.
 *
 * Jadvalni ham qayta yuklaydi: aks holda faqat tugma yangilanib, qator
 * eski `is_published` bilan qolardi va keyingi «Tahrirlash» formasi shu
 * eski qiymatni yuborib nashrni jimgina qaytarib qo'yardi. */
function PublishToggle({ post, reload }: { post: Post; reload?: () => void }) {
  const locale = useLocale();
  const [published, setPublished] = useState(post.is_published);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function toggle() {
    setBusy(true);
    setError("");
    try {
      const updated = await staff.action<Post>(
        `${PATH}${post.slug}/${published ? "unpublish" : "publish"}/`,
      );
      setPublished(updated.is_published);
      reload?.();
    } catch (e) {
      setError(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={busy}
      title={error || (published ? t(locale, "admin.text.unpublish") : t(locale, "admin.text.publishVerb"))}
      className="disabled:opacity-60"
    >
      <Badge color={error ? "error" : published ? "success" : "neutral"}>
        {error ? t(locale, "admin.text.error") : published ? t(locale, "admin.label.status.published") : t(locale, "admin.label.status.draft")}
      </Badge>
    </button>
  );
}

const COLUMNS: ColumnDef<Post>[] = [
  { key: "slug", labelKey: "admin.label.text.slug" },
  {
    key: "kind",
    labelKey: "admin.label.text.kind",
    render: (p, _reload, locale) => (
      <Badge color={KIND[p.kind]?.color}>{KIND[p.kind] ? t(locale, KIND[p.kind]!.labelKey) : p.kind}</Badge>
    ),
  },
  { key: "title", labelKey: "admin.label.text.title" },
  { key: "locale", labelKey: "admin.label.text.language" },
  {
    key: "is_published",
    labelKey: "admin.label.text.status",
    // key: holat formadan o'zgarsa tugma qayta o'rnatiladi
    render: (p, reload) => (
      <PublishToggle
        key={`${p.slug}-${p.is_published}`}
        post={p}
        reload={reload}
      />
    ),
  },
  {
    key: "published_at",
    labelKey: "admin.label.date.publishedAt",
    render: (p) => fmtDate(p.published_at),
  },
  {
    key: "notify_users",
    labelKey: "admin.label.text.message",
    render: (p) =>
      !p.notify_users ? (
        "—"
      ) : p.notified_at ? (
        <Badge color="success">Yuborildi</Badge>
      ) : (
        <Badge color="warning">Kutilmoqda</Badge>
      ),
  },
];

export function PostsAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<Post>
      title={t(locale, "admin.section.posts")}
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-created_at"
    />
  );
}
