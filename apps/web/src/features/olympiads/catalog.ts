/** Labels of the olympiad archive's values (ADR-0062 § 2.6). Keys are written
 *  out so the dictionary checker sees every one. */

import type { BadgeColor } from "@/components/ui/Badge";
import type { MessageKey } from "@/i18n/messages";

export const KIND_LABEL: Record<string, MessageKey> = {
  international: "olympiads.kind.international",
  selection: "olympiads.kind.selection",
  stage: "olympiads.kind.stage",
  training: "olympiads.kind.training",
  unofficial: "olympiads.kind.unofficial",
};

export const STATUS_LABEL: Record<string, MessageKey> = {
  completed: "olympiads.status.completed",
  scheduled: "olympiads.status.scheduled",
  tba: "olympiads.status.tba",
};

export const MEDAL_LABEL: Record<string, MessageKey> = {
  gold: "olympiads.medal.gold",
  silver: "olympiads.medal.silver",
  bronze: "olympiads.medal.bronze",
  honourable_mention: "olympiads.medal.honourable",
};

export const MEDAL_COLOR: Record<string, BadgeColor> = {
  gold: "warning",
  silver: "neutral",
  bronze: "brand",
  honourable_mention: "info",
};

export function eventPath(slug: string): string {
  return `/olympiads/${slug}`;
}

export function taskPath(event: string, task: string): string {
  return `/olympiads/${event}/${task}`;
}

export function participantPath(slug: string): string {
  return `/olympiads/participants/${slug}`;
}

/** The site some selection statements come from; a name, the same in every language. */
export const KEP_NAME = "KEP.uz";
