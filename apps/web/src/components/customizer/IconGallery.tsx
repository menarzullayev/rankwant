"use client";

import { useMemo, useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { groupKeysByDomain } from "@/icons/registry";

import { chip } from "./chrome";

/** Full 226-key gallery — lab / admin only. Closed by default. */
export function IconGallery() {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const groups = useMemo(() => groupKeysByDomain(), []);
  const total = useMemo(() => groups.reduce((n, [, ks]) => n + ks.length, 0), [groups]);

  return (
    <div className="mt-3">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className={`${chip(false)} w-full justify-center`}
      >
        {open
          ? t(locale, "customizer.iconGalleryHide")
          : fill(t(locale, "customizer.iconGalleryShow"), { n: total })}
      </button>
      {open && (
        <div className="mt-3 max-h-[420px] space-y-4 overflow-y-auto rw-radius-sm border rw-divider p-3">
          {groups.map(([domain, keys]) => (
            <div key={domain}>
              <div className="mb-1 text-theme-xs rw-faint">
                <code>{domain}</code> · {keys.length}
              </div>
              <div className="flex flex-wrap gap-2">
                {keys.map((k) => (
                  <span
                    key={k}
                    title={k}
                    className="inline-flex rw-radius-sm border rw-divider p-1"
                  >
                    <Icon name={k} size="sm" />
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
