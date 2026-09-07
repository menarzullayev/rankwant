import type { Metadata } from "next";

import { QuizzesAdmin } from "@/components/admin/QuizzesAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Testlar" };

export default function AdminQuizzesPage() {
  return <QuizzesAdmin />;
}
