"use client";

import { useState } from "react";

import { Card } from "@/components/ui/Card";
import type { Sample } from "@/lib/api";

function CopyButton({ text, label }: { text: string; label: string }) {
  const [done, setDone] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // HTTPS bo'lmagan yoki ruxsat berilmagan kontekst — matn baribir
      // ko'rinib turibdi, qo'lda belgilash mumkin.
      return;
    }
    setDone(true);
    setTimeout(() => setDone(false), 1500);
  }

  return (
    <button
      type="button"
      onClick={copy}
      aria-label={label}
      className="rw-radius-sm px-2 py-0.5 text-theme-xs font-medium rw-dim transition rw-hover-bg"
    >
      {done ? "Nusxalandi" : "Nusxalash"}
    </button>
  );
}

function Block({
  title,
  text,
  copyLabel,
}: {
  title: string;
  text: string;
  copyLabel: string;
}) {
  return (
    <div className="min-w-0">
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="text-theme-xs font-medium rw-faint">{title}</span>
        <CopyButton text={text} label={copyLabel} />
      </div>
      <pre className="max-h-48 overflow-auto rw-radius-sm rw-field-bg p-3 font-mono text-theme-xs rw-strong">
        {text}
      </pre>
    </div>
  );
}

export function SampleTests({ samples }: { samples: Sample[] }) {
  if (samples.length === 0) return null;

  return (
    <Card title="Namunalar" bodyClassName="space-y-5">
      {samples.map((sample) => (
        <div key={sample.order} className="space-y-2">
          {samples.length > 1 && (
            <p className="text-theme-sm font-medium rw-dim-2">
              Namuna {sample.order}
            </p>
          )}
          <div className="grid gap-3 sm:grid-cols-2">
            <Block
              title="Kirish"
              text={sample.input}
              copyLabel={`${sample.order}-namuna kirishini nusxalash`}
            />
            <Block
              title="Chiqish"
              text={sample.expected}
              copyLabel={`${sample.order}-namuna chiqishini nusxalash`}
            />
          </div>
        </div>
      ))}
    </Card>
  );
}
