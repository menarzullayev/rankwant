"use client";

import {
  StatementSectionBody,
  useStatementSectionMode,
} from "./StatementSectionMode";
import { StatementSize } from "./StatementSize";

/** Matn kartasi — bo‘lim ajratish rejimi bilan (prototip `#stmtcard`). */
export function ProblemStatementCard({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mode] = useStatementSectionMode();

  return (
    <StatementSectionBody mode={mode} className="space-y-5">
      <StatementSize>{children}</StatementSize>
    </StatementSectionBody>
  );
}
