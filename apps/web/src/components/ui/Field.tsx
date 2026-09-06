export function Field({
  label,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </span>
      <input
        className="h-11 w-full rounded-lg border border-gray-200 bg-white px-4 text-theme-sm
          text-gray-800 outline-none transition placeholder:text-gray-400
          focus:border-brand-400 focus:shadow-focus-ring
          dark:border-[#232936] dark:bg-[#0b0d12] dark:text-white/90"
        {...props}
      />
    </label>
  );
}
