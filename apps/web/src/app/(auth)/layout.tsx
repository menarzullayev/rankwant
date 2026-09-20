import "../auth.css";

/** Guest auth chrome. `auth.css` is the site tokens + a narrow Tailwind
 *  `@source` — not the full `globals.css` scan of every page. */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
