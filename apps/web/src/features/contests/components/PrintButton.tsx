"use client";

import { Button } from "@/components/ui/Button";

/** Opens the browser's print dialog, where «Save as PDF» is one of the
 *  destinations. The page itself is the document: formulas are KaTeX and
 *  images are the statement's own, which a server-side PDF could not draw
 *  (measured 2026-11-12: 1 690 of 2 336 public statements carry a formula). */
export function PrintButton({ label }: { label: string }) {
  return (
    <Button type="button" onClick={() => window.print()} data-print-button="">
      {label}
    </Button>
  );
}
