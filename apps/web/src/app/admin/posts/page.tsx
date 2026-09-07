import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · posts" };

// STUB — admin/posts bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminPostsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">posts — tez orada</p>
    </Card>
  );
}
