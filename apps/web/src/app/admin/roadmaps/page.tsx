import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · roadmaps" };

// STUB — admin/roadmaps bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminRoadmapsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">roadmaps — tez orada</p>
    </Card>
  );
}
