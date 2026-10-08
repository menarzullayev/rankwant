import type { AboutSectionId } from "../sections";

/** One section of the guide: a panel with a heading that can be linked to.
 *
 *  The `#` beside the heading is a plain link to the section's own anchor:
 *  following it puts the address in the bar, ready to copy, and needs no
 *  script. `scroll-mt` keeps the heading clear of the sticky contents bar
 *  that sits under the header below `xl`. */
export function GuideSection({
  id,
  title,
  note,
  anchorLabel,
  children,
}: {
  id: AboutSectionId;
  title: string;
  /** A short fact beside the title: "35 languages". */
  note?: string;
  anchorLabel: string;
  children: React.ReactNode;
}) {
  const heading = `about-${id}-title`;
  return (
    <section id={id} aria-labelledby={heading} className="scroll-mt-16 rw-panel xl:scroll-mt-2">
      <div className="flex items-center gap-2 border-b rw-divider px-5 py-4">
        <h2 id={heading} className="text-theme-xl font-semibold rw-strong">
          {title}
        </h2>
        {note ? <span className="text-theme-sm rw-dim">{note}</span> : null}
        <a
          href={`#${id}`}
          aria-label={`${anchorLabel}: ${title}`}
          title={anchorLabel}
          className="ms-auto grid size-11 shrink-0 place-items-center rw-radius-sm font-mono text-theme-sm rw-faint rw-hover-bg rw-focus-ring"
        >
          #
        </a>
      </div>
      <div className="px-5 py-4">{children}</div>
    </section>
  );
}
