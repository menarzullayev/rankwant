import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · shop" };

// STUB — admin/shop bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminShopPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">shop — tez orada</p>
    </Card>
  );
}
