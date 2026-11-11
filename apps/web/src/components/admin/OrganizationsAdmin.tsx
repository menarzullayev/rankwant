"use client";

import { CrudPage, type ColumnDef, type FieldDef } from "@/components/admin/CrudPage";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

type OrganizationRow = {
  id: number;
  slug: string;
  name: string;
  kind: string;
  logo_url: string;
  website: string;
  about: string;
  contest_count: number;
  [key: string]: unknown;
};

const KINDS = ["school", "university", "center", "company", "community", "government"] as const;

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    labelKey: "admin.label.text.slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  { name: "name", labelKey: "admin.label.text.name", required: true },
  {
    name: "kind",
    labelKey: "admin.label.text.kind",
    type: "select",
    required: true,
    options: KINDS.map((kind) => ({ value: kind, labelKey: `org.kind.${kind}` as const })),
  },
  // An address, not an upload (ADR-0063 § 2.7): a site path or https.
  {
    name: "logo_url",
    labelKey: "admin.label.tech.imageUrl",
    helpKey: "admin.help.organizationLogo",
  },
  { name: "website", labelKey: "admin.label.tech.website" },
  { name: "about", labelKey: "admin.label.text.about", type: "textarea", rows: 4 },
];

const COLUMNS: ColumnDef<OrganizationRow>[] = [
  { key: "name", labelKey: "admin.label.text.name" },
  { key: "slug", labelKey: "admin.label.text.slug" },
  { key: "contest_count", labelKey: "admin.section.contests", align: "right" },
];

/** Partner organizations (ADR-0063). Staff only: a partner's name on a
 *  contest is a claim the platform makes, so organizers cannot set it. */
export function OrganizationsAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<OrganizationRow>
      title={t(locale, "admin.section.organizations")}
      path="/staff/organizations/"
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="name"
      toPayload={(values) => ({ ...values, kind: values.kind || "center" })}
    />
  );
}
