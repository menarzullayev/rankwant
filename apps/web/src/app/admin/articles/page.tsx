import type { Metadata } from "next";

import { ArticlesAdmin } from "@/components/admin/ArticlesAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Maqolalar" };

export default function AdminArticlesPage() {
  return <ArticlesAdmin />;
}
