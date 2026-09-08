import { Card } from "@/components/ui/Card";
import type { Attachment } from "@/lib/api";

const unit = (bytes: number) =>
  bytes >= 1024 * 1024
    ? `${(bytes / 1024 / 1024).toFixed(1)} MB`
    : `${Math.max(1, Math.round(bytes / 1024))} KB`;

/** Masalaga biriktirilgan fayllar — katta kiruvchi ma'lumot, shablon
 * yoki chizma. Matnga sig'maydigani shu yerda turadi. */
export function Attachments({ items }: { items: Attachment[] }) {
  if (items.length === 0) return null;

  return (
    <Card title="Biriktirilgan fayllar" bodyClassName="p-0">
      <ul className="rw-divide divide-y">
        {items.map((item) => (
          <li key={item.url}>
            <a
              href={item.url}
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-5 py-2.5 text-theme-sm transition rw-hover-bg"
            >
              <span className="font-medium rw-strong">{item.name}</span>
              {item.size_bytes > 0 && (
                <span className="ml-auto rw-faint tabular-nums">
                  {unit(item.size_bytes)}
                </span>
              )}
            </a>
          </li>
        ))}
      </ul>
    </Card>
  );
}
