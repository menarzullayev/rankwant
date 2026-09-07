import Link from "next/link";

type Variant = "primary" | "outline";

const STYLES: Record<Variant, string> = {
  primary: "rw-accent-bg ",
  outline: "border rw-line rw-strong rw-hover-bg " + " ",
};

const BASE =
  "inline-flex h-11 items-center justify-center gap-2 rw-btn-radius px-4 text-theme-sm " +
  "font-medium transition rw-btn-label disabled:opacity-60";

export function Button({
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button className={`${BASE} ${STYLES[variant]} ${className}`} {...props} />
  );
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
