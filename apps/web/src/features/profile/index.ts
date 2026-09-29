/** `profile` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/profile"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { AboutTab } from "./components/AboutTab";

/** ⚠️ `AchievementsTab`, `ActivityTab`, `PeopleTab`, `PurchasesTab`,
 *  `CertificatesTab`, `CertificateCard` — SERVER komponentlari
 *  (`@/lib/api.server` ishlatadi). Ular bu barrel'dan chiqmaydi:
 *  aks holda mijoz komponenti barrel'ni import qilganda server API
 *  mijoz to'plamiga tortilib, Next.js build yiqilardi.
 *  Ular — `@/features/profile/server`. */

/** Umumiy identitet primitivlari endi global qatlamda — qulaylik uchun
 *  shu yerdan ham ko'rinadi (import yo'li o'zgarmasin). */
export { Avatar, MarkerText, UserName, rankClass, splitMarker } from "@/components/ui/Identity";
export type { TitleBand, UserTitle } from "@/lib/identity";

export { ActivityHeatmap } from "./components/ActivityHeatmap";


export { AttemptsTab } from "./components/AttemptsTab";



export { ContestsTab } from "./components/ContestsTab";

export { FollowButton } from "./components/FollowButton";

export { LanguageCards } from "./components/LanguageCards";


export { Medal, MedalDot, achievementLabel } from "./components/Medal";

export { PinButton } from "./components/PinButton";

export { ProblemMap } from "./components/ProblemMap";

export { ProfileCard } from "./components/ProfileCard";

export { PROFILE_TABS, ProfileNav } from "./components/ProfileNav";

export { RankTitle } from "./components/RankTitle";

export { RatingChart } from "./components/RatingChart";

export { RatingHistoryTable } from "./components/RatingHistoryTable";

export { SectionHint } from "./components/SectionHint";

export { ShareButton } from "./components/ShareButton";

export { SolvedOverview } from "./components/SolvedOverview";

export { SolvedTab } from "./components/SolvedTab";

/** ⚠️ Ism to'qnashuvi: `TopicStrength` — ham KOMPONENT, ham TIP.
 *  Komponent shu nomda, tip esa `TopicStrengthData` taxallusida
 *  chiqadi (aks holda barrel o'zi bilan ziddiyatga tushadi). */
export { TopicStrength } from "./components/TopicStrength";
export type { TopicStrength as TopicStrengthData } from "./api/users";


export type { Achievement, AchievementTier, ActivityEvent, Calendar, CalendarDay, Certificate, CertificateTier, CoachRef, ContestRow, Cosmetics, Education, ExternalKind, ExternalProfile, Follower, LanguageStat, LevelStat, PinnedAchievement, ProblemTile, ProfileRole, PublicProfile, RatingChange, RatingKind, RatingPoint, RatingSeries, School, SkillBadge, SkillName, SolvedProblem, Team, TeamRole, Technology, UserMini, UserPublic, UserStats, WorkRow } from "./api/users";
