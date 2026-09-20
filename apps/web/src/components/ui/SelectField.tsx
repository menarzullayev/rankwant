"use client";

import { FormCheck } from "@/components/form/FormKit";
import { Dropdown, type DropdownOption, type DropdownSize } from "@/components/ui/Dropdown";

/** Tanlash maydoni — yagona qidiruvli `Dropdown`.
 *
 *  Native `<select>` qoldirilmaydi: OS paneli qorong'i mavzuda oq
 *  chiqadi, qidiruv yo'q, tanlangan belgi yo'q.
 */

export function SelectField({
  label,
  hint,
  options,
  value,
  defaultValue,
  onChange,
  name,
  disabled,
  placeholder,
  size = "md",
}: {
  label: string;
  hint?: string;
  options: readonly DropdownOption[];
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  name?: string;
  disabled?: boolean;
  placeholder?: string;
  size?: DropdownSize;
}) {
  return (
    <Dropdown
      label={label}
      hint={hint}
      options={options}
      value={value}
      defaultValue={defaultValue}
      onChange={onChange}
      name={name}
      disabled={disabled}
      placeholder={placeholder}
      size={size}
    />
  );
}

/** Belgilash katagi — rozilik uchun.
 *
 * Matn `children` da: shartlar havolasi ham shu yerda turadi, ya'ni
 * butun satr bosiladigan bo'lishi kerak (`<label>` o'zi shuni beradi).
 *
 * `rw-focus-ring` katakning O'ZIDA turadi (label'da emas): fokus
 * `<input>` ga tushadi, ya'ni halqa ham shunda chizilishi kerak.
 * Usiz klaviatura bilan yurgan odam shartlar roziligini belgilayotgan
 * paytda fokus qayerdaligini ko'rmasdi — `:focus-visible` standart
 * `size-4` katakda deyarli bilinmaydi. */
export function Checkbox({
  children,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  children: React.ReactNode;
}) {
  return <FormCheck {...props}>{children}</FormCheck>;
}
