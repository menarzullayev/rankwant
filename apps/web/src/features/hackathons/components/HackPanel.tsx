"use client";

import { useCallback, useEffect, useState } from "react";

import { Select, TextArea } from "@/components/form/SettingsKit";
import { Status } from "@/components/kit/Feedback";
import { useAction } from "@/lib/hooks";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Segmented } from "@/components/ui/Segmented";
import { Verdict } from "@/components/ui/Verdict";
import { UserName } from "@/components/ui/Identity";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { dateTime, t } from "@/i18n/messages";
import {
  fetchAttemptHacks,
  fetchHackEligibility,
  fetchLanguages,
  lockProblem,
  submitHack,
  type AttemptDetail,
  type Hack,
  type HackEligibility,
  type Language,
} from "@/lib/api";

/** Natija kutilayotgan hack shu oraliqda qayta so'raladi. Hack uchta
 *  judge ishidan o'tadi, ya'ni javob bir necha soniya kechikadi —
 *  sahifani qo'lda yangilash kerak bo'lsa, xususiyat singan kabi
 *  ko'rinardi. */
const POLL_MS = 5_000;

/** Hack yuzasi — ADR-0020.
 *
 * Sabab HAR DOIM ko'rsatiladi: «hack qila olmaysiz» deb tugmani
 * yashirish odamni nima yetishmayotganini taxmin qilishga majburlardi
 * (2-tamoyil). Shuning uchun yuza uch holatni biladi: oyna yopiq,
 * huquq yo'q (sababi bilan) va forma.
 */
export function HackPanel({ attempt }: { attempt: AttemptDetail }) {
  const locale = useLocale();
  const { user } = useSession();
  const action = useAction();
  const [gate, setGate] = useState<HackEligibility | null>(null);
  const [hacks, setHacks] = useState<Hack[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [mode, setMode] = useState<"input" | "generator">("input");
  const [input, setInput] = useState("");
  const [source, setSource] = useState("");
  const [language, setLanguage] = useState("");

  const loadHacks = useCallback(() => {
    void fetchAttemptHacks(attempt.id)
      .then((page) => setHacks(page.results))
      .catch(() => undefined);
  }, [attempt.id]);

  const loadGate = useCallback(() => {
    if (!user) return;
    void fetchHackEligibility(attempt.id)
      .then(setGate)
      .catch(() => setGate(null));
  }, [attempt.id, user]);

  useEffect(loadHacks, [loadHacks]);
  useEffect(loadGate, [loadGate]);

  // Tillar faqat generator kerak bo'lganda — hack qila olmaydigan odamga
  // bu so'rov ortiqcha.
  useEffect(() => {
    if (!gate?.can_hack || mode !== "generator" || languages.length) return;
    void fetchLanguages()
      .then((page) => {
        setLanguages(page.results);
        setLanguage((current) => current || page.results[0]?.code || "");
      })
      .catch(() => undefined);
  }, [gate?.can_hack, mode, languages.length]);

  // Tekshiruvdagi hack bor ekan — natijani kutamiz.
  useEffect(() => {
    if (!hacks.some((hack) => hack.status === "TESTING")) return;
    const timer = setInterval(loadHacks, POLL_MS);
    return () => clearInterval(timer);
  }, [hacks, loadHacks]);

  async function send() {
    const ok = await action.run(async () => {
      await submitHack(
        mode === "input"
          ? { attempt: attempt.id, test_input: input }
          : {
              attempt: attempt.id,
              generator_language: language,
              generator_source: source,
            },
      );
    });
    if (ok) {
      setInput("");
      setSource("");
      loadHacks();
      loadGate();
    }
  }

  async function lock() {
    if (!attempt.contest) return;
    const ok = await action.run(() =>
      lockProblem(attempt.contest ?? "", attempt.problem),
    );
    if (ok) loadGate();
  }

  // Mehmonga ham, hack umuman tegishli bo'lmagan urinishga ham yuza
  // ko'rsatilmaydi — lekin qilingan hacklar ko'rinib turadi.
  if (!user) return null;
  if (!gate) return null;
  if (gate.policy === null && hacks.length === 0) return null;

  return (
    <Card title={t(locale, "hack.title")}>
      {gate.can_hack ? (
        <div className="space-y-4">
          <p className="text-theme-sm rw-dim">
            {t(locale, `hack.policy.${gate.policy ?? "practice"}`)}
          </p>
          <Segmented
            label={t(locale, "hack.title")}
            value={mode}
            onChange={setMode}
            options={[
              { value: "input", label: t(locale, "hack.mode.input") },
              { value: "generator", label: t(locale, "hack.mode.generator") },
            ]}
          />
          {mode === "input" ? (
            <TextArea
              label={t(locale, "hack.input")}
              hint={t(locale, "hack.inputHint")}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={8}
              spellCheck={false}
              className="font-mono"
            />
          ) : (
            <>
              <Select
                label={t(locale, "attempts.language")}
                value={language}
                onChange={setLanguage}
                options={languages.map((item) => ({
                  value: item.code,
                  label: `${item.name} ${item.version}`,
                }))}
              />
              <TextArea
                label={t(locale, "hack.generatorSource")}
                hint={t(locale, "hack.generatorHint")}
                value={source}
                onChange={(e) => setSource(e.target.value)}
                rows={10}
                spellCheck={false}
                className="font-mono"
              />
            </>
          )}
          <Button
            busy={action.busy}
            disabled={mode === "input" ? !input.trim() : !source.trim()}
            onClick={() => void send()}
          >
            {t(locale, "hack.send")}
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-theme-sm rw-dim">
            {gate.reason || t(locale, "hack.closed")}
          </p>
          {gate.needs_lock && !gate.locked && attempt.contest && (
            <>
              <p className="text-theme-xs rw-faint">
                {t(locale, "hack.lockHint")}
              </p>
              <Button
                variant="outline"
                busy={action.busy}
                onClick={() => void lock()}
              >
                {t(locale, "hack.lock")}
              </Button>
            </>
          )}
        </div>
      )}

      <div className="mt-3">
        <Status
          error={action.error}
          done={action.done}
          text={t(locale, "hack.sent")}
        />
      </div>

      {hacks.length > 0 && (
        <ul className="mt-4 space-y-3 border-t rw-divider pt-4">
          {hacks.map((hack) => (
            <li key={hack.id} className="flex flex-wrap items-center gap-2">
              <UserName
                username={hack.hacker}
                title={hack.hacker_title}
                locale={locale}
              />
              <span className="text-theme-sm rw-dim">
                {t(locale, `hack.status.${hack.status}`)}
              </span>
              {hack.defender_verdict && (
                <Verdict verdict={hack.defender_verdict} />
              )}
              {hack.points !== 0 && (
                <span
                  className={`text-theme-sm tabular-nums ${
                    hack.points > 0 ? "rw-ok-ink" : "rw-bad-ink"
                  }`}
                >
                  {hack.points > 0 ? `+${hack.points}` : hack.points}
                </span>
              )}
              <time
                dateTime={hack.created_at}
                className="ml-auto text-theme-xs rw-faint"
              >
                {dateTime(hack.created_at, locale)}
              </time>
              {hack.detail && (
                <p className="w-full text-theme-xs rw-faint">{hack.detail}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
