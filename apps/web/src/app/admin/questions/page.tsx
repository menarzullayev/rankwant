import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · questions" };

// STUB — admin/questions bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminQuestionsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">questions — tez orada</p>
    </Card>
  );
}
