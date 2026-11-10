import { StudioNav } from "@/features/studio";

/** `/studio` — the author's workspace (2026-11-10). Each page guards
 *  itself with `requireUser` so the sign-in comes back to that page. */
export default function StudioLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      <StudioNav />
      {children}
    </div>
  );
}
