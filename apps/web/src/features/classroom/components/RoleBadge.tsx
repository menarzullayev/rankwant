"use client";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import type { ClassroomRole } from "@/lib/api";

const ROLES: Record<Exclude<ClassroomRole, "">, { key: MessageKey; color: BadgeColor }> = {
  owner: { key: "classroom.role.owner", color: "brand" },
  assistant: { key: "classroom.role.assistant", color: "info" },
  student: { key: "classroom.role.student", color: "neutral" },
};

/** The reader's or a member's place in a classroom. */
export function RoleBadge({ role }: { role: ClassroomRole }) {
  const locale = useLocale();
  if (!role) return null;
  const { key, color } = ROLES[role];
  return <Badge color={color}>{t(locale, key)}</Badge>;
}
