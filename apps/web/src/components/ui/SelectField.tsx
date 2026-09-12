/** Tanlash maydoni — `Field` bilan bir xil ko'rinish.
 *
 * Nega alohida komponent: `Field` `<input>` ga qurilgan, ya'ni unga
 * `<select>` uzatib bo'lmaydi. Vizual til bir xil bo'lishi shart —
 * aks holda mamlakat tanlash qolgan maydonlardan ajralib qolardi.
 */

export function SelectField({
  label,
  hint,
  leading,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & {
  label: string;
  hint?: string;
  /** Maydon CHAPIDA turgan element — mamlakat bayrog'i uchun.
   *
   * Nega `<option>` ichida emas: native `<select>` faqat MATN qabul
   * qiladi, SVG esa uning ichida ko'rinmaydi. Shu sababli bayroq
   * tanlagichning yonida turadi — u ham Windows'da ishlaydi, ham
   * klaviatura va mobil xatti-harakati o'zgarmaydi. */
  leading?: React.ReactNode;
  children: React.ReactNode;
}) {
  const noteId = hint ? `${props.name}-note` : undefined;
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <span className="flex items-center gap-2">
        {leading}
        <select
          aria-describedby={noteId}
          className="h-11 min-w-0 flex-1 rw-radius-sm border rw-line px-4 text-theme-sm rw-strong outline-none transition rw-focus-line rw-focus-ring rw-field-bg"
          {...props}
        >
          {children}
        </select>
      </span>
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
