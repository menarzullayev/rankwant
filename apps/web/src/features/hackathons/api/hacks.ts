/** Hacks and problem locks (ADR-0020). */

import { getJson, postJson, type Paginated } from "@/lib/api/client";
import type { UserTitle } from "@/lib/identity";

/** Hack holati — `hacks.models.Hack.Status`.
 *
 * Union sifatida yozilgan, `string` emas: shunda `hack.status.${status}`
 * kaliti TypeScript darajasida tekshiriladi va tarjimasi yo'q holat
 * kompilyatsiyada tutiladi. */
export type HackStatus =
  | "TESTING"
  | "SUCCESSFUL"
  | "UNSUCCESSFUL"
  | "INVALID_INPUT"
  | "GENERATOR_CRASHED"
  | "IGNORED"
  | "RATE_LIMITED";

/** Siyosat kodi — `hacks.policies`. Server yorlig'i (`policy_label`)
 *  faqat o'zbekcha, shuning uchun UI o'z kalitidan tarjima qiladi. */
export type HackPolicy = "contest_room" | "open_phase" | "practice" | "uphack";

export type Hack = {
  id: number;
  hacker: string;
  hacker_title: UserTitle | null;
  defender: string;
  defender_attempt: number;
  problem: string;
  contest: string | null;
  policy: HackPolicy;
  status: HackStatus;
  stage: string;
  /** Himoyachining kodi hack testida olgan HAQIQIY verdikt (`WA`, `TLE`). */
  defender_verdict: string;
  /** Rad etish sababi — begonaga bo'sh satr keladi (backend yashiradi). */
  detail: string;
  points: number;
  input_size: number;
  created_at: string;
  judged_at: string | null;
};

/** «Hack qila olamanmi va NEGA yo'q» — sabab har doim keladi (ADR-0020,
 *  2-tamoyil): jimgina yashirilgan tugma odamni savol bilan qoldiradi. */
export type HackEligibility = {
  can_hack: boolean;
  reason: string;
  policy: HackPolicy | null;
  policy_label: string;
  needs_lock: boolean;
  locked: boolean;
};

/** Hack yuborish: YO tayyor kiritma, YO generator dasturi (ikkalasi
 *  birga bo'lsa server rad etadi — qaysi biri ishlatilgani noaniq). */
export const submitHack = (body: {
  attempt: number;
  test_input?: string;
  generator_language?: string;
  generator_source?: string;
}) => postJson<Hack>("/hacks/", body);

export const fetchHackEligibility = (attempt: number) =>
  getJson<HackEligibility>(`/hacks/eligibility/?attempt=${attempt}`);

export const fetchAttemptHacks = (attempt: number) =>
  getJson<Paginated<Hack>>(`/hacks/?attempt=${attempt}`);

/** Masalani lock qilish — QAYTARIB BO'LMAYDI: shundan keyin o'sha
 *  masalaga qayta yuborib bo'lmaydi (ADR-0020). Ochish yo'li yo'q. */
export const lockProblem = (contest: string, problem: string) =>
  postJson<{ id: number }>("/hack-locks/", { contest, problem });
