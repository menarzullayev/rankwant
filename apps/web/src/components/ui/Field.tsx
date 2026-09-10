export type FieldStatus = {
  /** `ok` — yashil, `bad` — qizil, `busy` — kutilmoqda. */
  kind: "ok" | "bad" | "busy";
  text: string;
};

export function Field({
  label,
  hint,
  status,
  trailing,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  /** Qoida — maydon TAGIDA, yozishdan oldin (ADR-0016). Xatoni keyin
   *  ko'rsatgandan ko'ra, aytilgan qoidani buzib bo'lmaydi. */
  hint?: string;
  /** Yozayotgandagi javob. Qoidaning O'RNINI bosadi: ikkalasi birga
   *  tursa maydon tagida ikki satr matn paydo bo'lardi va ko'z qaysi
   *  biriga qarashni bilmasdi. */
  status?: FieldStatus;
  /** Maydon ichidagi o'ng tugma — parolni ko'rsatish uchun. */
  trailing?: React.ReactNode;
}) {
  const noteId = hint || status ? `${props.name}-note` : undefined;
  // Rang YOLG'IZ tashuvchi bo'lmasligi kerak (WCAG 1.4.1): belgisi ham bor.
  const mark = status && { ok: "✓", bad: "✕", busy: "…" }[status.kind];
  const tone =
    status && { ok: "rw-ok-ink", bad: "rw-bad-ink", busy: "rw-dim" }[status.kind];
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <span className="relative block">
        <input
          aria-describedby={noteId}
          aria-invalid={status?.kind === "bad" || undefined}
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
      {(hint || status) && (
        <span
          id={noteId}
          role={status ? "status" : undefined}
          aria-live={status ? "polite" : undefined}
          className={`mt-1.5 block text-theme-xs ${status ? tone : "rw-dim"}`}
        >
          {status ? `${mark} ${status.text}` : hint}
        </span>
      )}
    </label>
  );
}
