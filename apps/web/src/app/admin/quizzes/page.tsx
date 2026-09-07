import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · quizzes" };

// STUB — admin/quizzes bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminQuizzesPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">quizzes — tez orada</p>
    </Card>
  );
}
