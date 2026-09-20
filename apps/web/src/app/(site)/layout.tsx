import "../globals.css";

/** Public site sheet. `/login` is not under this group, so it does not
 *  inline this file (desktop Lighthouse FCP budget). */
export default function SiteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
