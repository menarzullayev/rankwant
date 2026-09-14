"use client";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";

type ShopItem = {
  id: number;
  code: string;
  category:
    "streak_freeze" | "avatar_frame" | "profile_cover" | "username_badge";
  title_uz: string;
  title_ru: string;
  title_en: string;
  price: number;
  asset_ref: string;
  is_active: boolean;
  is_consumable: boolean;
  owner_count: number;
  [key: string]: unknown;
};

const CATEGORY_LABEL: Record<ShopItem["category"], MessageKey> = {
  streak_freeze: "admin.label.shopCategory.streakFreeze",
  avatar_frame: "admin.label.shopCategory.avatarFrame",
  profile_cover: "admin.label.shopCategory.profileCover",
  username_badge: "admin.label.shopCategory.usernameBadge",
};

const columns: ColumnDef<ShopItem>[] = [
  {
    key: "code",
    labelKey: "admin.label.text.code",
    render: (i) => <span className="font-mono">{i.code}</span>,
  },
  {
    key: "category",
    labelKey: "admin.label.text.category",
    render: (i, _reload, locale) => t(locale, CATEGORY_LABEL[i.category]),
  },
  { key: "title_uz", labelKey: "admin.label.text.name" },
  {
    key: "price",
    labelKey: "admin.label.text.price",
    align: "right",
    render: (i) => `${i.price} Qvant`,
  },
  {
    key: "is_consumable",
    labelKey: "admin.label.flag.repeatable",
    render: (i) => (i.is_consumable ? <Badge color="info">Ha</Badge> : "—"),
  },
  { key: "owner_count", labelKey: "admin.label.misc.owners", align: "right" },
  {
    key: "is_active",
    labelKey: "admin.label.text.status",
    render: (i) => (
      <Badge color={i.is_active ? "success" : "neutral"}>
        {i.is_active ? "Faol" : "O'chiq"}
      </Badge>
    ),
  },
];

const fields: FieldDef[] = [
  {
    name: "code",
    labelKey: "admin.label.text.code",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "category",
    labelKey: "admin.label.text.category",
    type: "select",
    required: true,
    options: Object.entries(CATEGORY_LABEL).map(([value, labelKey]) => ({
      value,
      labelKey,
    })),
    helpKey: "admin.help.cosmeticOnly",
  },
  {
    name: "price",
    labelKey: "admin.label.value.priceQvant",
    type: "number",
    required: true,
    min: 0,
  },
  {
    name: "asset_ref",
    labelKey: "admin.label.text.asset",
    helpKey: "admin.help.assetRef",
  },
  { name: "is_active", labelKey: "admin.label.flag.active", type: "checkbox" },
  {
    name: "is_consumable",
    labelKey: "admin.label.flag.repeatPurchase",
    type: "checkbox",
    helpKey: "admin.help.repeatPerItem",
  },
  { name: "title_uz", labelKey: "admin.label.name.uz", required: true },
  { name: "title_ru", labelKey: "admin.label.name.ru" },
  { name: "title_en", labelKey: "admin.label.name.en" },
];

export function ShopAdmin() {
  const locale = useLocale();
  return (
    <CrudPage<ShopItem>
      title="Do'kon"
      path="/staff/shop-items/"
      idField="code"
      columns={columns}
      fields={fields}
      fromItem={(i) => ({ ...i })}
    />
  );
}
