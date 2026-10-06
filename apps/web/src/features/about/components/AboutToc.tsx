"use client";

import { useEffect, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

import { ABOUT_SECTIONS, type AboutSectionId } from "../sections";

/** `aria-current` for the section being read. Named, not inline:
 *  `check_hardcoded.py` reads a string in a ternary branch as text that
 *  skipped translation. */
const HERE = "location";

/** The guide's contents: a column beside the text from `xl`, a bar under
 *  the header below it. The links are plain anchors — they work before
 *  the script loads; the script only marks where the reader is. */
export function AboutToc() {
  const locale = useLocale();
  const [active, setActive] = useState<AboutSectionId>(ABOUT_SECTIONS[0].id);

  useEffect(() => {
    // A section is "current" while it crosses a band a little below the
    // header: the one being read, not the one that merely touches the top.
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActive(entry.target.id as AboutSectionId);
        }
      },
      { rootMargin: "-25% 0px -65% 0px" },
    );
    for (const { id } of ABOUT_SECTIONS) {
      const element = document.getElementById(id);
      if (element) observer.observe(element);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <nav
      aria-label={t(locale, "about.toc.label")}
      className="sticky top-16 z-10 -mx-4 rw-scroll-x px-4 py-2 rw-ground-bg md:-mx-6 md:px-6 xl:top-20 xl:mx-0 xl:overflow-visible xl:px-0 xl:py-0"
    >
      <ul className="flex gap-1 xl:flex-col">
        {ABOUT_SECTIONS.map(({ id, label }) => {
          const current = id === active;
          return (
            <li key={id} className="shrink-0">
              <a
                href={`#${id}`}
                aria-current={current ? HERE : undefined}
                className={`flex min-h-11 items-center rw-radius-sm px-3 text-theme-sm whitespace-nowrap rw-focus-ring xl:whitespace-normal ${
                  current ? "rw-surface font-semibold rw-accent-ink" : "rw-dim-2 rw-hover-bg"
                }`}
              >
                {t(locale, label)}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
