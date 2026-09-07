import type { Metadata } from "next";

import { TournamentsAdmin } from "@/components/admin/TournamentsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Chempionatlar" };

export default function AdminTournamentsPage() {
  return <TournamentsAdmin />;
}
