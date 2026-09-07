import type { Metadata } from "next";

import { HackathonsAdmin } from "@/components/admin/HackathonsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · hackathons" };

export default function AdminHackathonsPage() {
  return <HackathonsAdmin />;
}
