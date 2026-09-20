"use client";

import { useState } from "react";

import { FormCheck, FormRadios } from "@/components/form/FormKit";
import { HoldButton, InlineConfirm } from "@/components/kit/ConfirmExtras";
import { CopyAllBar, CopyButton, CopyCell } from "@/components/kit/CopyControl";
import {
  FormIconSwitch,
  FormSeg3,
  FormStepper,
  FormTreeItem,
  InfoMark,
} from "@/components/kit/FormExtras";
import { TabBar } from "@/components/kit/TabBar";
import {
  Countdown,
  MiniCal,
  TimeLine,
  TimeStamp,
} from "@/components/kit/TimeStamp";
import { OverlayDialog, useConfirm, useOverlay } from "@/components/overlay/OverlayHost";
import { dateKit, isoDay } from "@/lib/format";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const SAMPLE_TSV = ["1", "A"].join("\t") + "\n" + ["2", "B"].join("\t");

function chip(on: boolean) {
  return `rw-radius-sm border px-2.5 py-1 text-theme-xs ${
    on ? "rw-accent-soft rw-accent-ink rw-accent-line" : "rw-line rw-dim rw-hover-bg"
  }`;
}

/** Customizer namuna — tanlangan kit variantlarining hammasi shu yerda
 *  ishlaydi. Ko'rinish oilasi emas: bu sath qoidalarining ko'rgazmasi. */
export function KitSection() {
  const locale = useLocale();
  const confirm = useConfirm();
  const overlay = useOverlay();
  const kit = dateKit(locale);
  const [anchor] = useState(() => Date.now());
  const now = new Date(anchor).toISOString();
  const hourAgo = new Date(anchor - 3600_000).toISOString();
  const yesterday = new Date(anchor - 86_400_000).toISOString();
  const weekAgo = new Date(anchor - 8 * 86_400_000).toISOString();
  const soon = new Date(anchor + 3_600_000).toISOString();
  const dayIso = isoDay(new Date(anchor));
  const [sw, setSw] = useState(true);
  const [seg, setSeg] = useState<"private" | "team" | "public">("team");
  const [step, setStep] = useState(1);
  const [tree, setTree] = useState(["child"]);
  const [tab, setTab] = useState("one");
  const [chips, setChips] = useState<string[]>(["ac"]);
  const [radio, setRadio] = useState("a");
  const [modal, setModal] = useState(false);

  const parentOn = tree.includes("parent");
  const childOn = tree.includes("child");

  return (
    <section className="space-y-4">
      <h3 className="text-theme-sm font-semibold rw-strong">
        {t(locale, "customizer.kit")}
      </h3>
      <p className="text-theme-xs rw-faint">{t(locale, "customizer.kitHint")}</p>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className={chip(false)}
          onClick={() =>
            void confirm(t(locale, "overlay.sample.confirmTitle"), {
              body: t(locale, "overlay.sample.confirmBody"),
              danger: true,
            })
          }
        >
          {1}
        </button>
        <button
          type="button"
          className={chip(false)}
          onClick={(event) =>
            void confirm(t(locale, "overlay.sample.confirmTitle"), {
              body: t(locale, "overlay.sample.confirmBody"),
              danger: true,
              kind: "popover",
              origin: event.currentTarget,
            })
          }
        >
          {4}
        </button>
        <InlineConfirm
          label="5"
          danger
          onConfirm={() => overlay.toast(t(locale, "problem.copied"))}
        />
        <HoldButton
          label="9"
          danger
          onConfirm={() => overlay.toast(t(locale, "common.yes"))}
        />
        <button
          type="button"
          className={chip(false)}
          onClick={() =>
            void confirm(t(locale, "overlay.sample.confirmTitle"), {
              danger: true,
              kind: "cmdk",
            })
          }
        >
          {10}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-theme-sm">
        <span data-tip={t(locale, "overlay.sample.tip")} data-tip-kind="balloon">
          {1}
        </span>
        <span data-tip={t(locale, "overlay.sample.tip")} data-tip-kind="soft">
          {2}
        </span>
        <span
          data-tip={t(locale, "overlay.sample.tip")}
          data-tip-kind="rich"
          data-tip-title={t(locale, "overlay.sample.problem")}
        >
          {3}
        </span>
        <InfoMark text={t(locale, "overlay.sample.tip")} title={t(locale, "overlay.sample.problem")} />
        <span
          data-tip={t(locale, "customizer.title")}
          data-tip-kind="kbd"
          data-tip-kbd="Ctrl+K"
        >
          {5}
        </span>
        <span data-tip={t(locale, "overlay.sample.tip")} data-tip-kind="flip">
          {6}
        </span>
        <span
          data-tip={t(locale, "overlay.sample.tip")}
          data-tip-follow=""
        >
          {7}
        </span>
        <span className="rw-kit-legend" data-tip={t(locale, "profile.less")} data-tip-kind="legend">
          {8}
        </span>
        <span data-tip="…" data-tip-kind="skeleton">
          {9}
        </span>
        <span data-tip={t(locale, "overlay.sample.tip")} data-tip-kind="theme">
          {10}
        </span>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        <FormCheck label="1" defaultChecked />
        <FormCheck label="2" shape="pill" defaultChecked />
        <FormCheck label="3" shape="card" />
        <FormCheck label="4" shape="switch" defaultChecked />
        <div className="flex items-center gap-2">
          <FormIconSwitch
            checked={sw}
            onChange={setSw}
            onLabel={t(locale, "theme.light")}
            offLabel={t(locale, "theme.dark")}
          />
          <span className="text-theme-xs rw-dim">{5}</span>
        </div>
        <FormSeg3
          label="6"
          value={seg}
          onChange={setSeg}
          options={[
            { value: "private", label: t(locale, "kit.seg.private") },
            { value: "team", label: t(locale, "kit.seg.team") },
            { value: "public", label: t(locale, "kit.seg.public") },
          ]}
        />
        <FormRadios
          name="kit-radio"
          label="7"
          tone="card"
          value={radio}
          onChange={setRadio}
          options={[
            { value: "a", label: "A" },
            { value: "b", label: "B" },
          ]}
        />
        <div className="rw-kit-tree">
          <FormTreeItem
            label="8"
            checked={parentOn}
            indeterminate={childOn && !parentOn}
            onChange={() =>
              setTree(parentOn ? tree.filter((x) => x !== "parent") : [...tree, "parent"])
            }
          />
          <FormTreeItem
            label="A"
            nested
            checked={childOn}
            onChange={() =>
              setTree(childOn ? tree.filter((x) => x !== "child") : [...tree, "child"])
            }
          />
        </div>
        <FormStepper
          label="9"
          value={step}
          options={[
            t(locale, "kit.seg.private"),
            t(locale, "kit.seg.team"),
            t(locale, "kit.seg.public"),
          ]}
          onChange={setStep}
        />
      </div>

      <div className="flex flex-col gap-1 text-theme-sm">
        <TimeStamp value={hourAgo} locale={locale} tone="relative" />
        <TimeStamp value={hourAgo} locale={locale} tone="dual" />
        <TimeStamp value={now} locale={locale} tone="badge" />
        <TimeLine
          locale={locale}
          events={[
            { at: yesterday, label: "4" },
            { at: hourAgo, label: "4" },
          ]}
        />
        <Countdown until={soon} locale={locale} />
        <TimeStamp value={hourAgo} locale={locale} tone="duration" durationMin={135} />
        <TimeStamp value={hourAgo} locale={locale} tone="iso" />
        <TimeStamp value={weekAgo} locale={locale} tone="fresh" />
        <TimeStamp value={now} locale={locale} tone="locale" />
        <MiniCal iso={dayIso} kit={kit} label="10" />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <CopyButton text="rankwant.uz" tone="text" />
        <CopyButton text="rankwant.uz" tone="ghost" />
        <CopyButton text="print(1)" tone="code" />
        <CopyButton text="https://rankwant.uz" tone="chip" />
        <span className="rw-kit-hover inline-flex items-center gap-1">
          {"id"}
          <CopyButton text="a-plus-b" tone="hover" />
        </span>
        <CopyButton text="Ctrl+C" tone="kbd" kbd="Ctrl+C" />
        <CopyCell text="1042" />
      </div>
      <CopyAllBar text={SAMPLE_TSV} />

      <TabBar
        tone="underline"
        label="1"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
        ]}
      />
      <TabBar
        tone="segment"
        label="2"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
        ]}
      />
      <TabBar
        tone="card"
        label="3"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
        ]}
      />
      <TabBar
        tone="icon"
        label="4"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
        ]}
      />
      <TabBar
        tone="badge"
        label="5"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1", count: 3 },
          { id: "two", label: "2", count: 0 },
        ]}
      />
      <TabBar
        tone="chips"
        label="10"
        multiple
        selected={chips}
        onChange={(id) =>
          setChips(chips.includes(id) ? chips.filter((x) => x !== id) : [...chips, id])
        }
        options={[
          { id: "ac", label: "AC" },
          { id: "wa", label: "WA" },
        ]}
      />
      <TabBar
        tone="step"
        label="9"
        value="two"
        options={[
          { id: "one", label: t(locale, "kit.step.account") },
          { id: "two", label: t(locale, "kit.step.profile") },
          { id: "three", label: t(locale, "kit.step.done") },
        ]}
      />
      <TabBar
        tone="scroll"
        label="8"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
          { id: "three", label: "3" },
          { id: "four", label: "4" },
        ]}
      />
      <TabBar
        tone="crumb"
        label="7"
        value="two"
        options={[
          { id: "one", label: t(locale, "settings.title") },
          { id: "two", label: t(locale, "settings.nav.profile") },
        ]}
      />
      <TabBar
        tone="vertical"
        label="6"
        value={tab}
        onChange={setTab}
        options={[
          { id: "one", label: "1" },
          { id: "two", label: "2" },
        ]}
      />

      <button type="button" className={chip(false)} onClick={() => setModal(true)}>
        {t(locale, "overlay.sample.problem")}
      </button>
      <OverlayDialog
        open={modal}
        onClose={() => setModal(false)}
        title={t(locale, "overlay.sample.modalTitle")}
      >
        <p className="rw-ov-copy">{t(locale, "overlay.sample.modalBody")}</p>
      </OverlayDialog>
    </section>
  );
}
