import type { LegalDoc } from "@/content/legal";

export function LegalPage({ doc }: { doc: LegalDoc }) {
  return (
    <article className="mx-auto max-w-2xl py-10">
      <h1 className="mb-2 text-2xl font-bold rw-strong">{doc.title}</h1>
      <p className="mb-6 text-theme-xs rw-dim">{doc.updated}</p>
      <p className="mb-8 text-theme-sm rw-strong">{doc.intro}</p>
      {doc.sections.map((s) => (
        <section key={s.h} className="mb-7">
          <h2 className="mb-2 text-lg font-semibold rw-strong">{s.h}</h2>
          {s.p.map((line) => (
            <p key={line} className="mb-2 text-theme-sm rw-dim">
              {line}
            </p>
          ))}
        </section>
      ))}
    </article>
  );
}
