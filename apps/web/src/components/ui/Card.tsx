/** TailAdmin karta patterni — sarlavha + ixtiyoriy amal, so'ng mazmun. */
export function Card({
  title,
  action,
  children,
  className = "",
  bodyClassName = "",
}: {
  title?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <section className={`rw-panel ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between gap-3 border-b rw-divider px-5 py-4">
          {typeof title === "string" ? (
            <h2 className="text-theme-xl font-semibold rw-strong">{title}</h2>
          ) : (
            title
          )}
          {action}
        </div>
      )}
      <div className={`px-5 py-4 ${bodyClassName}`}>{children}</div>
    </section>
  );
}

/** Raqamli ko'rsatkich kartasi — bosh sahifa va profil uchun. */
export function StatCard({
  label,
  value,
  hint,
  icon,
  about,
  valueClassName = "",
}: {
  label: string;
  value: React.ReactNode;
  hint?: string;
  icon?: React.ReactNode;
  /** Ko'rsatkich nimani o'lchaydi — izohsiz raqam hech narsa aytmaydi. */
  about?: string;
  /**
   * Raqam uchun qo'shimcha klass. To'r tor ustunlarga siqqanda sanoq chetga
   * chiqmasligi uchun kerak: 30 px bold raqamda har bir xona ~17.2 px, ya'ni
   * 4 ustunli to'rda (ichki kenglik 121 px, 1024 px ekranda) 8 xonali sanoq
   * toshib ketadi. Chaqiruvchi tomonda beriladi, chunki bir xil `StatCard`
   * uch xil to'rda ishlatiladi va faqat tor to'rda kichraytirish kerak.
   */
  valueClassName?: string;
}) {
  return (
    <div className="rw-panel p-5">
      {icon && (
        <div className="mb-4 flex size-11 items-center justify-center rw-radius rw-accent-soft rw-accent-ink">
          {icon}
        </div>
      )}
      <p className="text-theme-sm rw-dim">{label}</p>
      <p className={`mt-1 text-title-sm font-bold rw-strong ${valueClassName}`}>{value}</p>
      {hint && <p className="mt-1 text-theme-xs rw-faint">{hint}</p>}
      {about && <p className="mt-2 text-theme-xs rw-dim">{about}</p>}
    </div>
  );
}
