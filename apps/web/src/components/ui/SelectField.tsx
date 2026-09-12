/** Tanlash maydoni — `Field` bilan bir xil ko'rinish.
 *
 * Nega alohida komponent: `Field` `<input>` ga qurilgan, ya'ni unga
 * `<select>` uzatib bo'lmaydi. Vizual til bir xil bo'lishi shart —
 * aks holda mamlakat tanlash qolgan maydonlardan ajralib qolardi.
 */

export function SelectField({
  label,
  hint,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  const noteId = hint ? `${props.name}-note` : undefined;
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <select
        aria-describedby={noteId}
        className="h-11 w-full rw-radius-sm border rw-line px-4 text-theme-sm rw-strong outline-none transition rw-focus-line rw-focus-ring rw-field-bg"
        {...props}
      >
        {children}
      </select>
      {hint && (
        <span id={noteId} className="mt-1.5 block text-theme-xs rw-dim">
          {hint}
        </span>
      )}
    </label>
  );
}

/** Belgilash katagi — rozilik uchun.
 *
 * Matn `children` da: shartlar havolasi ham shu yerda turadi, ya'ni
 * butun satr bosiladigan bo'lishi kerak (`<label>` o'zi shuni beradi).
 */
export function Checkbox({
  children,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  children: React.ReactNode;
}) {
  return (
    <label className="flex cursor-pointer items-start gap-2.5 text-theme-sm rw-dim">
      <input
        type="checkbox"
        className="mt-0.5 size-4 shrink-0 rw-accent-control"
        {...props}
      />
      <span className="min-w-0">{children}</span>
    </label>
  );
}
