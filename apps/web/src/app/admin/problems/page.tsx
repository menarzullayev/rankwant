import type { Metadata } from "next";

import { ProblemsAdmin } from "@/components/admin/ProblemsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Masalalar" };

export default function AdminProblemsPage() {
  return <ProblemsAdmin />;
}
