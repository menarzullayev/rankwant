/** `coaching` — feature'ning ommaviy yuzasi (`/coaching`, ADR-0061 § 4).
 *
 * A student's coaches and a coach's students. Tashqaridan faqat shu fayl
 * orqali import qilinadi: `import { X } from "@/features/coaching"`.
 */

export { CoachingPage } from "./components/CoachingPage";

export { Recommendations } from "./components/Recommendations";

export { OpenRecommendations } from "./components/OpenRecommendations";

export type { Recommendation } from "./api";
