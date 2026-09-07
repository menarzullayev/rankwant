import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · problems" };

// STUB — admin/problems bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminProblemsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">problems — tez orada</p>
    </Card>
  );
}
