import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { AttemptView } from "@/components/AttemptView";
import { fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ id: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const locale = await getLocale();
  const { id } = await params;
  return { title: fill(t(locale, "attempt.title"), { id }) };
}

/** Bitta urinish sahifasi.
 *
 * Ilgari bunday sahifa YO'Q edi: urinishlar ro'yxati qatorlari hech
 * qayerga olib bormasdi va yuborilgan kodni ko'rishning yo'li faqat
 * yuborish panelidan o'tardi. Hack uchun esa boshqaning yechimini
 * ko'rish SHART (ADR-0020, 2-tamoyil).
 */
export default async function AttemptPage({ params }: Props) {
  const { id } = await params;
  const numeric = Number(id);
  if (!Number.isInteger(numeric) || numeric <= 0) notFound();
  return <AttemptView id={numeric} />;
}
