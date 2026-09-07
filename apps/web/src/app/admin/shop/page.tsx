import type { Metadata } from "next";

import { ShopAdmin } from "@/components/admin/ShopAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Do'kon" };

export default function AdminShopPage() {
  return <ShopAdmin />;
}
