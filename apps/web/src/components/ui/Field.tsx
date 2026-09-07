export function Field({
  label,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
        {label}
      </span>
      <input
        className="h-11 w-full rw-radius-sm border rw-line px-4 text-theme-sm rw-strong outline-none transition rw-placeholder rw-focus-line rw-focus-ring rw-field-bg"
        {...props}
      />
    </label>
  );
}
