import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · articles" };

// STUB — admin/articles bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminArticlesPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">articles — tez orada</p>
    </Card>
  );
}
