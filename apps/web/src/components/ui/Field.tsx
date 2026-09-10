export function Field({
  label,
  hint,
  trailing,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  /** Qoida — maydon TAGIDA, yozishdan oldin (ADR-0016). Xatoni keyin
   *  ko'rsatgandan ko'ra, aytilgan qoidani buzib bo'lmaydi. */
  hint?: string;
  /** Maydon ichidagi o'ng tugma — parolni ko'rsatish uchun. */
  trailing?: React.ReactNode;
}) {
  const hintId = hint ? `${props.name}-hint` : undefined;
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <span className="relative block">
        <input
          aria-describedby={hintId}
          className={`h-11 w-full rw-radius-sm border rw-line ${
            trailing ? "pr-12" : "pr-4"
          } pl-4 text-theme-sm rw-strong outline-none transition rw-placeholder rw-focus-line rw-focus-ring rw-field-bg`}
          {...props}
        />
        {trailing && (
          <span className="absolute inset-y-0 right-1 flex items-center">
            {trailing}
          </span>
        )}
      </span>
      {hint && (
        <span id={hintId} className="mt-1.5 block text-theme-xs rw-dim">
          {hint}
        </span>
      )}
    </label>
  );
}
