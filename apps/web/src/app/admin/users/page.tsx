import type { Metadata } from "next";

import { UsersAdmin } from "@/components/admin/UsersAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Foydalanuvchilar" };

export default function AdminUsersPage() {
  return <UsersAdmin />;
}
