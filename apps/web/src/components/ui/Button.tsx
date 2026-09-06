import Link from "next/link";

type Variant = "primary" | "outline";

const STYLES: Record<Variant, string> = {
  primary: "bg-brand-500 text-white hover:bg-brand-600",
  outline:
    "border border-gray-200 text-gray-700 hover:bg-gray-50 dark:border-[#232936] " +
    "dark:text-gray-300 dark:hover:bg-white/5",
};

const BASE =
  "inline-flex h-11 items-center justify-center gap-2 rounded-lg px-4 text-theme-sm " +
  "font-medium transition disabled:opacity-60";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return <button className={`${BASE} ${STYLES[variant]} ${className}`} {...props} />;
}

/** `href` tipi Next'ning o'zinikidan olinadi — typedRoutes tekshiruvi saqlanadi. */
export function ButtonLink({
  href,
  variant = "primary",
  className = "",
  children,
}: {
  href: React.ComponentProps<typeof Link>["href"];
  variant?: Variant;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <Link href={href} className={`${BASE} ${STYLES[variant]} ${className}`}>
      {children}
    </Link>
  );
}
