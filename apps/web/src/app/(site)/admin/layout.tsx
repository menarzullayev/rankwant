import { AdminFrame } from "@/components/admin/AdminFrame";
import { requireStaff } from "@/lib/access.server";

/** Admin — staff only (ADR-0054).
 *
 *  The check runs on the server, before anything of the section is sent:
 *  a guest is redirected to sign in, a signed-in non-member gets the
 *  ordinary "not found" page. It used to be a client `<Can>` — every
 *  visitor received the admin shell with status 200 and the browser then
 *  hid it. The data was never exposed (the API answers 401/403), the
 *  section itself was.
 */
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  await requireStaff("/admin");
  return <AdminFrame>{children}</AdminFrame>;
}
