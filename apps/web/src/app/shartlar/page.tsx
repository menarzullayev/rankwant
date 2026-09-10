import type { Metadata } from "next";

import { LegalPage } from "@/components/LegalPage";
import { TERMS, pickLegal } from "@/content/legal";
import { getLocale } from "@/i18n/server";

export async function generateMetadata(): Promise<Metadata> {
  return { title: TERMS[pickLegal(await getLocale())].title };
}

export default async function Page() {
  return <LegalPage doc={TERMS[pickLegal(await getLocale())]} />;
}
