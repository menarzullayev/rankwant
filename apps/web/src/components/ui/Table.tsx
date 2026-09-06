/** TailAdmin jadval patterni.
 *
 *  `<table>` va `<tbody>` saqlanadi: E2E `tbody tr a` va `table`
 *  selektorlariga tayanadi (tests/e2e/specs). */
export function Table({ children }: { children: React.ReactNode }) {
  return (
    <div className="custom-scrollbar overflow-x-auto">
      <table className="min-w-full text-left">{children}</table>
    </div>
  );
}

export function THead({ children }: { children: React.ReactNode }) {
  return (
    <thead className="border-b border-gray-100 dark:border-[#232936]">
      <tr>{children}</tr>
    </thead>
  );
}

export function TH({
  children,
  align = "left",
}: {
  children: React.ReactNode;
  align?: "left" | "right" | "center";
}) {
  return (
    <th
      className={`px-4 py-3 text-theme-xs font-medium text-gray-500 uppercase dark:text-gray-400
        ${align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left"}`}
    >
      {children}
    </th>
  );
}

export function TBody({ children }: { children: React.ReactNode }) {
  return (
    <tbody className="divide-y divide-gray-100 dark:divide-[#232936]">{children}</tbody>
  );
}

export function TR({ children }: { children: React.ReactNode }) {
  return <tr className="transition hover:bg-gray-50 dark:hover:bg-white/[0.03]">{children}</tr>;
}

export function TD({
  children,
  align = "left",
  className = "",
}: {
  children: React.ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}) {
  return (
    <td
      className={`px-4 py-3 text-theme-sm text-gray-700 dark:text-gray-300
        ${align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left"}
        ${className}`}
    >
      {children}
    </td>
  );
}

export function EmptyRow({ colSpan, children }: { colSpan: number; children: React.ReactNode }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-10 text-center text-theme-sm text-gray-400">
        {children}
      </td>
    </tr>
  );
}
