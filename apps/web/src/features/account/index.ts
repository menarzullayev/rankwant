/** `account` — feature'ning ommaviy yuzasi.
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/account"`.
 * Ichki tuzilma (`components/`, `api/`) — xususiy.
 */

export { AccountSettings } from "./components/AccountSettings";

export { AppearanceSection } from "./components/AppearanceSection";

export { AuthForm } from "./components/AuthForm";

export { CareerSection } from "./components/CareerSection";

export { EmailVerify } from "./components/EmailVerify";


export { InfoSection } from "./components/InfoSection";

export { NotificationsSection } from "./components/NotificationsSection";

export { OnboardingForm } from "./components/OnboardingForm";

export { ProfileSection } from "./components/ProfileSection";

export { GithubMark, GoogleMark, TelegramMark } from "./components/ProviderMark";

export { ResetForm } from "./components/ResetForm";

export { SchoolField } from "./components/SchoolField";

export { SecuritySection } from "./components/SecuritySection";

export { SECTIONS, isSection, type SectionId } from "./components/sections";

export { SettingsShell } from "./components/SettingsShell";

export { SkillsSection } from "./components/SkillsSection";

export { SocialAccounts } from "./components/SocialAccounts";

export { SocialSection } from "./components/SocialSection";

export { TeamsSection } from "./components/TeamsSection";



export { fetchMe, fetchProviders } from "./api/account";
export type { A11yPrefs, AppearancePrefs, AuthProviders, BgPattern, CardStyle, Gender, Me, MySkill, NotifyPrefs, PrivacyField, SessionRow, ShirtSize, ShirtSizeEu, ThemeEffect, ThemeTemplate, UiPrefs } from "./api/account";

export type { Marathon, Purchase, Quest, ShopItem, Wallet } from "./api/qvant";
