/** `community` — discussions, blogs, karma, votes and reports (decision 2026-11-11).
 *
 * Tashqaridan faqat shu fayl orqali import qilinadi:
 * `import { X } from "@/features/community"`.
 */

export { Discussion } from "./components/Discussion";

export { EntryActions } from "./components/EntryActions";

export { EntryCard } from "./components/EntryCard";

export { EntryEditor } from "./components/EntryEditor";

export { ActiveAuthors, KarmaTable } from "./components/KarmaTable";

export { BLOG_TABS } from "./api";

export type { BlogTab, Entry, EntryDetail, KarmaRow, Target, ThreadPage } from "./api";
