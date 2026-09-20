import { FormDate } from "@/components/form/FormKit";
import { FM_CTL, FM_INP, FM_LAB } from "@/components/form/chrome";

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
  // Label maydonni O'RAB turadi, ya'ni bog'lanish o'rashdan ham kelib
  // chiqadi. `htmlFor` qo'shimcha: parol menejerlari va avtomatik
  // to'ldirish `id` ni qidiradi, va maydon kelajakda label ichidan
  // chiqarilsa bog'lanish jimgina yo'qolmaydi.
  const fieldId = props.id ?? props.name;
  const noteId = hint || status ? `${props.name}-note` : undefined;
  // Rang YOLG'IZ tashuvchi bo'lmasligi kerak (WCAG 1.4.1): belgisi ham bor.
  const mark = status && { ok: "✓", bad: "✕", busy: "…" }[status.kind];
  const tone =
    status && { ok: "rw-ok-ink", bad: "rw-bad-ink", busy: "rw-dim" }[status.kind];

  if (props.type === "date") {
    return (
      <FormDate
        label={label}
        hint={status ? `${mark} ${status.text}` : hint}
        name={props.name}
        id={typeof fieldId === "string" ? fieldId : undefined}
        value={typeof props.value === "string" ? props.value : undefined}
        defaultValue={
          typeof props.defaultValue === "string" ? props.defaultValue : undefined
        }
        min={typeof props.min === "string" ? props.min : undefined}
        max={typeof props.max === "string" ? props.max : undefined}
        required={props.required}
        disabled={props.disabled}
        onChange={(iso) => {
          props.onChange?.({
            target: { value: iso, name: props.name ?? "" },
          } as React.ChangeEvent<HTMLInputElement>);
        }}
      />
    );
  }

  return (
    <label className={FM_CTL} htmlFor={fieldId}>
      <span className={FM_LAB}>{label}</span>
      <span className="relative block">
        <input
          id={fieldId}
          aria-describedby={noteId}
          aria-invalid={status?.kind === "bad" || undefined}
          className={`${FM_INP} ${trailing ? "pr-12" : ""}`}
          {...props}
        />
        {trailing && (
          <span className="absolute inset-y-0 right-1 flex items-center">
            {trailing}
          </span>
        )}
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
      </span>
    </label>
  );
}
