"use client";

import { FormCheck } from "@/components/form/FormKit";
import { FM_CTL, FM_INP, FM_LAB } from "@/components/form/chrome";
import { Dropdown, type DropdownOption } from "@/components/ui/Dropdown";

/** Sozlamalar/amal formalari uchun umumiy maydonlar.
 *
 *  Ilgari `features/account/components/section-kit.tsx` ichida edi, lekin
 *  `TextArea`, `Select`, `Check` — sozlamalarga xos EMAS: har qanday
 *  forma ishlatadi (`hackathons` hozir shunday qiladi). Umumiy narsa
 *  umumiy qatlamda turadi (25-prinsip: layer qoidasi). */

export function TextArea({
  label,
  hint,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label: string;
  hint?: string;
}) {
  return (
    <label className={FM_CTL}>
      <span className={FM_LAB}>{label}</span>
      <span>
        <textarea className={`${FM_INP} min-h-24`} {...props} />
        {hint && <span className="mt-1.5 block text-theme-xs rw-dim">{hint}</span>}
      </span>
    </label>
  );
}

export function Select({
  label,
  hint,
  options,
  value,
  defaultValue,
  onChange,
  name,
  disabled,
  placeholder,
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
    />
  );
}

export function Check({
  label,
  hint,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
}) {
  return <FormCheck label={label} hint={hint} {...props} />;
}
