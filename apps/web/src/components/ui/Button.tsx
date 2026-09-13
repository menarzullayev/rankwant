import Link from "next/link";

type Variant = "primary" | "outline";

const STYLES: Record<Variant, string> = {
  primary: "rw-accent-bg ",
  outline: "border rw-line rw-strong rw-hover-bg " + " ",
};

/** Umumiy tugma asosi.
 *
 *  `rw-focus-ring` SHART (WCAG 2.4.11). Ilgari u yo'q edi va klaviatura
 *  bilan yurgan odam faqat brauzerning ingichka standart halqasini
 *  ko'rardi — o'lchandi: `/kirish` da 17 ta fokuslanadigan elementdan
 *  9 tasida halqa yo'q edi, shu jumladan ASOSIY tugmada. `Button`
 *  butun ilova bo'ylab ishlatiladi, ya'ni bu bitta qator butun saytni
 *  tuzatadi.
 *
 *  `--rw-accent-ink` `check_contrast.py` da `FOCUS_MIN` (3:1) bo'yicha
 *  tekshiriladi — eng yomon palitrada ham 4.31:1. */
const BASE =
  "inline-flex h-11 items-center justify-center gap-2 rw-btn-radius px-4 text-theme-sm " +
  "font-medium transition rw-btn-label rw-focus-ring disabled:opacity-60";

/** Aylanuvchi halqa. `prefers-reduced-motion` da aylanmaydi, lekin
 *  ko'rinib turadi — harakat o'chirilgani holat yashirilishini
 *  anglatmasligi kerak. */
function Spinner() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="size-4 motion-safe:animate-spin"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2.5" opacity=".3" fill="none" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="2.5" fill="none" strokeLinecap="round" />
    </svg>
  );
}

export function Button({
  variant = "primary",
  className = "",
  busy = false,
  busyLabel,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  /** So'rov ketayotgani. Tugma o'chadi va halqa aylanadi — sekin
   *  ulanishda odam nima bo'layotganini bilmay qayta bosardi. */
  busy?: boolean;
  busyLabel?: string;
}) {
  return (
    <button
      className={`${BASE} ${STYLES[variant]} ${className}`}
      aria-busy={busy || undefined}
      disabled={busy || props.disabled}
      {...props}
    >
      {busy && <Spinner />}
      {busy && busyLabel ? busyLabel : children}
    </button>
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
