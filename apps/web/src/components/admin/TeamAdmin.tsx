"use client";

import { useEffect, useState } from "react";

import { CrudPage, type ColumnDef, type FieldDef } from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { staff } from "@/lib/staff";

type Row = { id: number; [key: string]: unknown };
type Department = Row & { name_uz: string; order: number; role_count: number };
type Role = Row & {
  title_uz: string;
  department: number;
  department_name: string;
  badge: string;
  order: number;
  is_published: boolean;
};
type Member = Row & {
  name: string;
  section: "core" | "contributor";
  title_uz: string;
  photo_url: string;
  holds_all_roles: boolean;
  order: number;
  is_published: boolean;
};

const LANGS = ["uz", "ru", "en"] as const;
/** An empty cell. */
const NONE = "—";

/** One text in the three languages the page is written in. Uzbek is
 *  required: it is what a blank translation falls back to. */
function trio(name: string, key: string, type: FieldDef["type"] = "text", optional = false): FieldDef[] {
  return LANGS.map((lang) => ({
    name: `${name}_${lang}`,
    labelKey: `admin.team.${key}.${lang}` as MessageKey,
    type,
    required: lang === "uz" && !optional,
  }));
}

const DEPARTMENT_FIELDS: FieldDef[] = [
  { name: "name_uz", labelKey: "admin.label.name.uz", type: "text", required: true },
  { name: "name_ru", labelKey: "admin.label.name.ru", type: "text" },
  { name: "name_en", labelKey: "admin.label.name.en", type: "text" },
  { name: "order", labelKey: "admin.label.text.order", type: "number", min: 0 },
];

const DEPARTMENT_COLUMNS: ColumnDef<Department>[] = [
  { key: "order", labelKey: "admin.label.text.order" },
  { key: "name_uz", labelKey: "admin.label.text.name" },
  { key: "role_count", labelKey: "admin.team.roles", align: "right" },
];

const ROLE_COLUMNS: ColumnDef<Role>[] = [
  { key: "department_name", labelKey: "admin.team.department" },
  { key: "order", labelKey: "admin.label.text.order" },
  { key: "title_uz", labelKey: "admin.team.title.uz" },
  { key: "badge", labelKey: "admin.team.badge" },
  {
    key: "is_published",
    labelKey: "admin.label.text.status",
    render: (role, _reload, locale) => (
      <Badge color={role.is_published ? "success" : "neutral"}>
        {t(locale, role.is_published ? "admin.label.status.published" : "admin.label.status.draft")}
      </Badge>
    ),
  },
];

const MEMBER_FIELDS: FieldDef[] = [
  { name: "name", labelKey: "admin.label.text.displayName", type: "text", required: true },
  {
    name: "section",
    labelKey: "admin.team.section",
    type: "select",
    required: true,
    options: [
      { value: "core", labelKey: "admin.team.section.core" },
      { value: "contributor", labelKey: "admin.team.section.contributor" },
    ],
  },
  ...trio("title", "title"),
  ...trio("context", "context", "text", true),
  {
    name: "photo_url",
    labelKey: "admin.label.tech.imageUrl",
    type: "text",
    helpKey: "admin.team.photoHelp",
  },
  { name: "telegram_url", labelKey: "admin.team.telegram", type: "text" },
  { name: "github_url", labelKey: "admin.label.tech.githubUrl", type: "text" },
  { name: "linkedin_url", labelKey: "admin.team.linkedin", type: "text" },
  { name: "instagram_url", labelKey: "admin.team.instagram", type: "text" },
  { name: "website_url", labelKey: "admin.team.website", type: "text" },
  { name: "order", labelKey: "admin.label.text.order", type: "number", min: 0 },
  {
    name: "holds_all_roles",
    labelKey: "admin.team.holdsAllRoles",
    type: "checkbox",
    helpKey: "admin.team.holdsAllRolesHelp",
  },
  { name: "is_published", labelKey: "admin.label.flag.published", type: "checkbox" },
];

const MEMBER_COLUMNS: ColumnDef<Member>[] = [
  {
    key: "photo_url",
    labelKey: "admin.label.tech.imageUrl",
    render: (member) =>
      member.photo_url ? (
        // The address is whatever the editor typed; a plain <img> previews it.
        // eslint-disable-next-line @next/next/no-img-element
        <img src={member.photo_url} alt="" className="size-10 rounded-full object-cover" />
      ) : (
        NONE
      ),
  },
  { key: "name", labelKey: "admin.label.text.displayName" },
  {
    key: "section",
    labelKey: "admin.team.section",
    render: (member, _reload, locale) => (
      <Badge color={member.section === "core" ? "brand" : "info"}>
        {t(locale, `admin.team.section.${member.section}` as MessageKey)}
      </Badge>
    ),
  },
  { key: "title_uz", labelKey: "admin.team.title.uz" },
  {
    key: "holds_all_roles",
    labelKey: "admin.team.holdsAllRoles",
    render: (member, _reload, locale) => {
      if (!member.holds_all_roles) return NONE;
      return <Badge color="warning">{t(locale, "admin.team.holdsAllRoles")}</Badge>;
    },
  },
  {
    key: "is_published",
    labelKey: "admin.label.text.status",
    render: (member, _reload, locale) => (
      <Badge color={member.is_published ? "success" : "neutral"}>
        {t(locale, member.is_published ? "admin.label.status.published" : "admin.label.status.draft")}
      </Badge>
    ),
  },
];

/** Blank links and blank translations are sent as empty strings, which is
 *  what the API stores; `order` left blank means "first". */
function clean(values: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = { ...values };
  if (out.order === "" || out.order === null || out.order === undefined) out.order = 0;
  return out;
}

/** A choice left untouched in the create form arrives as "" and the API
 *  answers 400 for it (measured). The form's first option is what the
 *  editor was looking at, so that is what an untouched choice means. */
function fallback(values: Record<string, unknown>, field: string, value: string | number) {
  if (values[field] === "" || values[field] === null || values[field] === undefined) {
    values[field] = value;
  }
  return values;
}

/** The team page's three lists: people, the joke's titles, its departments. */
export function TeamAdmin() {
  const locale = useLocale();
  // A role's department is chosen by name. The list is read once per visit
  // to this page; a department added below shows up after a reload.
  const [departments, setDepartments] = useState<Department[]>([]);
  useEffect(() => {
    let alive = true;
    staff
      .list<Department>("/staff/team/departments/", { page_size: 100, ordering: "order" })
      .then((page) => {
        if (alive) setDepartments(page.results);
      })
      .catch(() => {
        // The role form then shows an empty list; the table below still works.
      });
    return () => {
      alive = false;
    };
  }, []);

  const roleFields: FieldDef[] = [
    {
      name: "department",
      labelKey: "admin.team.department",
      type: "select",
      required: true,
      options: departments.map((item) => ({ value: String(item.id), label: item.name_uz })),
    },
    ...trio("title", "title"),
    ...trio("about", "about", "textarea"),
    ...trio("reports_to", "reports", "text", true),
    ...trio("status", "status", "text", true),
    { name: "badge", labelKey: "admin.team.badge", type: "text", helpKey: "admin.team.badgeHelp" },
    { name: "hue", labelKey: "admin.team.hue", type: "number", min: 0, max: 359 },
    {
      name: "tone",
      labelKey: "admin.team.tone",
      type: "select",
      required: true,
      options: [
        { value: "ok", labelKey: "admin.team.tone.ok" },
        { value: "warn", labelKey: "admin.team.tone.warn" },
      ],
    },
    { name: "order", labelKey: "admin.label.text.order", type: "number", min: 0 },
    { name: "is_published", labelKey: "admin.label.flag.published", type: "checkbox" },
  ];

  return (
    <div className="space-y-10" data-team-admin>
      <CrudPage<Member>
        title={t(locale, "admin.team.members")}
        path="/staff/team/members/"
        idField="id"
        columns={MEMBER_COLUMNS}
        fields={MEMBER_FIELDS}
        ordering="section,order"
        toPayload={(values) => fallback(clean(values), "section", "core")}
      />
      <CrudPage<Role>
        title={t(locale, "admin.team.roles")}
        path="/staff/team/roles/"
        idField="id"
        columns={ROLE_COLUMNS}
        fields={roleFields}
        ordering="department__order,order"
        toPayload={(values) => {
          return fallback(fallback(clean(values), "hue", 262), "tone", "ok");
        }}
      />
      <CrudPage<Department>
        title={t(locale, "admin.team.departments")}
        path="/staff/team/departments/"
        idField="id"
        columns={DEPARTMENT_COLUMNS}
        fields={DEPARTMENT_FIELDS}
        ordering="order"
        toPayload={clean}
      />
    </div>
  );
}
