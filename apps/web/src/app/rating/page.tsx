import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Reyting qanday hisoblanadi",
  description:
    "RankWant reytinglarining to'liq formulalari: Skills, Contests, Activity, Challenges.",
};

/**
 * Launch gate sharti: 4 reyting formulasi UI da OCHIQ bo'lishi kerak
 * (09-development-plan). Vision principle #2 — «yashirin algoritm emas».
 *
 * Formulalar 04-prd 🔒 dan; kod `apps/api/ratings/formulas.py` da.
 */

function Section({
  title,
  phase,
  active,
  children,
}: {
  title: string;
  phase: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <section
      className="rounded-lg border p-5"
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
    >
      <h2 className="flex items-center gap-3 font-medium">
        {title}
        <span
          className="rounded px-2 py-0.5 text-xs"
          style={{
            background: active ? "var(--accent)" : "var(--border)",
            color: active ? "#06101f" : "var(--muted)",
          }}
        >
          {phase}
        </span>
      </h2>
      <div className="mt-3 space-y-2 text-sm" style={{ color: "var(--muted)" }}>
        {children}
      </div>
    </section>
  );
}

function Formula({ children }: { children: React.ReactNode }) {
  return (
    <pre
      className="overflow-x-auto rounded p-3 text-xs"
      style={{ background: "var(--bg)", color: "var(--text)" }}
    >
      <code>{children}</code>
    </pre>
  );
}

export default function RatingPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Reyting qanday hisoblanadi</h1>
        <p className="mt-2 text-sm" style={{ color: "var(--muted)" }}>
          Barcha formulalar ochiq. Yashirin og&apos;irlik yoki e&apos;lon
          qilinmagan bonus yo&apos;q. Har bir o&apos;zgarish sababi bilan
          profilingizda yozib boriladi.
        </p>
      </header>

      <Section title="Skills" phase="Faol" active>
        <p>
          Birinchi marta yechgan masalalaringiz ball bo&apos;yicha kamayish
          tartibida saralanadi va kamayuvchi koeffitsient bilan qo&apos;shiladi.
          Ball — masalaning <strong>joriy</strong> qiyinligi.
        </p>
        <Formula>{`Skills = Σ  pᵢ × 0.95^(i−1)     (p₁ ≥ p₂ ≥ … , pᵢ = qiyinlik)`}</Formula>
        <ul className="list-disc space-y-1 pl-5">
          <li>
            Yangi masala yechish reytingni <strong>hech qachon</strong>{" "}
            kamaytirmaydi.
          </li>
          <li>Natija eng qiyin masalangizdan 20 baravardan oshmaydi.</li>
          <li>
            Bir xil qiyinlikda ~45 masaladan keyin to&apos;yinadi — undan keyin
            faqat <strong>qiyinroq</strong> masala o&apos;stiradi.
          </li>
          <li>
            Masala qayta baholansa reyting o&apos;zgarishi mumkin. Bu
            foydalanuvchi harakati emas, platforma qarori — sizga xabar
            beriladi va sabab tarixda yoziladi.
          </li>
        </ul>
        <p className="text-xs">
          Misol: 500 ta 800-ball = 16 000 · 20 ta 2500-ball = 32 076. Ya&apos;ni
          chuqurlik miqdordan ustun.
        </p>
      </Section>

      <Section title="Contests" phase="Faol" active>
        <p>
          Codeforces uslubidagi Elo. Faqat <strong>reytingli</strong> va
          kamida 10 ishtirokchili musobaqalar hisoblanadi.
        </p>
        <Formula>{`P(i,j) = 1 / (1 + 10^((Rⱼ − Rᵢ) / 400))
seedᵢ  = 1 + Σ P(j, i)              kutilgan o'rin
mᵢ     = √(seedᵢ × rankᵢ)           kutilgan va haqiqiy o'rin o'rtachasi
dᵢ     = (R*ᵢ − Rᵢ) / 2             R*ᵢ — mᵢ ga mos reyting
soʻng: barcha dᵢ dan Σd/n ayiriladi (musobaqa reytingni shishirmaydi)`}</Formula>
        <ul className="list-disc space-y-1 pl-5">
          <li>Boshlang&apos;ich reyting — 1400.</li>
          <li>Birinchi 6 reytingli musobaqada o&apos;zgarish 1.5 baravar tezroq.</li>
          <li>Reyting 0 dan pastga tushmaydi.</li>
        </ul>
      </Section>

      <Section title="Activity" phase="Faol" active>
        <p>Oxirgi 30 kunlik siljuvchi oyna.</p>
        <Formula>{`Activity = 10 × faol_kun + 5 × bajarilgan_quest + min(2 × streak_kun, 60)`}</Formula>
        <p>
          Qvant <strong>balansi</strong> ataylab hisobga olinmaydi: aks holda
          do&apos;konda xarid qilish reytingni tushirardi.
        </p>
      </Section>

      <Section title="Challenges" phase="Phase 3" active={false}>
        <p>1v1 duel uchun klassik Elo.</p>
        <Formula>{`E  = 1 / (1 + 10^((R_raqib − R) / 400))
R' = R + K × (S − E)        S ∈ {1 = g'alaba, 0.5 = durang, 0}
K  = 32 (birinchi 10 duel), keyin 16`}</Formula>
      </Section>

      <p className="text-xs" style={{ color: "var(--muted)" }}>
        Formulani o&apos;zgartirish alohida qaror (ADR) talab qiladi va barcha
        reytinglar qayta hisoblanishidan oldin e&apos;lon qilinadi.
      </p>
    </div>
  );
}
