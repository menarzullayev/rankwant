/** `hackathons` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/hackathons"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { HackathonEntries } from "./components/HackathonEntries";

export { HackPanel } from "./components/HackPanel";

export { fetchAttemptHacks, fetchHackEligibility, lockProblem, submitHack } from "./api/hacks";
export type { Hack, HackEligibility, HackPolicy, HackStatus } from "./api/hacks";
