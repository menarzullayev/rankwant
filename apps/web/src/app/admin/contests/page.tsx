import type { Metadata } from "next";

import { ContestsAdmin } from "@/components/admin/ContestsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · contests" };

export default function AdminContestsPage() {
  return <ContestsAdmin />;
}
