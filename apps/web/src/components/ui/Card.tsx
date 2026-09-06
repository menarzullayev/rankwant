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
    <section
      className={`rounded-2xl border border-gray-200 bg-white shadow-theme-xs
        dark:border-[#232936] dark:bg-[#141821] ${className}`}
    >
      {(title || action) && (
        <div className="flex items-center justify-between gap-3 border-b border-gray-100 px-5 py-4 dark:border-[#232936]">
          {typeof title === "string" ? (
            <h2 className="text-theme-xl font-semibold text-gray-800 dark:text-white/90">
              {title}
            </h2>
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
}: {
  label: string;
  value: React.ReactNode;
  hint?: string;
  icon?: React.ReactNode;
}) {
  return (
    <div
      className="rounded-2xl border border-gray-200 bg-white p-5 shadow-theme-xs
        dark:border-[#232936] dark:bg-[#141821]"
    >
      {icon && (
        <div
          className="mb-4 flex size-11 items-center justify-center rounded-xl bg-brand-50
            text-brand-600 dark:bg-brand-500/12 dark:text-brand-400"
        >
          {icon}
        </div>
      )}
      <p className="text-theme-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className="mt-1 text-title-sm font-bold text-gray-800 dark:text-white/90">{value}</p>
      {hint && <p className="mt-1 text-theme-xs text-gray-400 dark:text-gray-500">{hint}</p>}
    </div>
  );
}
