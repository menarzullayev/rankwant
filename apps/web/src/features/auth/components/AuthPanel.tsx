import Link from "next/link";

import { t, type MessageKey } from "@/i18n/messages";
import type { Locale } from "@/i18n/messages";

import { CODE, TAB_FILES, VERDICTS, heatCells } from "../auth-panel-data";
import { AuthCarousel } from "./AuthCarousel";
import { AuthMascot } from "./AuthMascot";

/** The `/login` brand panel: ten slides in a carousel.
 *
 *  STATIC on purpose (decision 18): no request, no data. Everything the
 *  slides show is illustration — sample results, a sample countdown (marked
 *  as a sample on the slide) — so the sign-in page depends on nothing and
 *  cannot come up empty when the API is slow. Styles are in
 *  `../auth-panel.css`; the copy is `auth.panel.*` in all ten locales. */

const P = (key: string) => `auth.panel.${key}` as MessageKey;

export function AuthPanel({ locale }: { locale: Locale }) {
  const text = (key: string) => t(locale, P(key));
  const heat = heatCells();

  const slides = [
    // 1 — the live judge
    <>
      <div>
        <h2 className="ap-title">
          {text("a")}
          <br />
          {text("b")} <span className="ap-grad">{text("c")}</span>
        </h2>
        <p className="ap-lead">{text("s1.lead")}</p>
      </div>
      <div className="ap-art">
        <div className="ap-mascot-box ap-bob">
          <AuthMascot />
        </div>
        <div className="ap-editor">
          <div className="ap-tabs" aria-hidden="true">
            <b>{TAB_FILES.active}</b>
            <span>{TAB_FILES.other}</span>
            <i>{TAB_FILES.language}</i>
          </div>
          <pre className="ap-code" aria-hidden="true">
            {CODE.map((line, row) => (
              <div key={row}>
                {line.map(([kind, piece], i) => (
                  <span key={i} className={kind || undefined}>
                    {piece}
                  </span>
                ))}
              </div>
            ))}
          </pre>
          <div className="ap-judging">
            <p>
              <span>{text("s1.check")}</span>
              <span>{text("s1.tests").replace("{n}", "12").replace("{total}", "12")}</span>
            </p>
            <div className="ap-segs" aria-hidden="true">
              {Array.from({ length: 12 }, (_, i) => (
                <i key={i} className="ap-seg" style={{ animationDelay: `${i * 0.1}s` }} />
              ))}
            </div>
          </div>
        </div>
        <div className="ap-board" aria-hidden="true">
          <header>
            {text("s1.results")}
            <span className="ap-live">{text("s1.live")}</span>
          </header>
          <div className="ap-row"><span>1</span><span /><b>5</b></div>
          <div className="ap-row is-you"><span>2</span><span>{text("s1.you")}</span><b>4</b></div>
          <div className="ap-row"><span>3</span><span /><b>4</b></div>
        </div>
      </div>
    </>,

    // 2 — the ranking stairs
    <>
      <div>
        <h2 className="ap-title">{text("s2.title")}</h2>
        <p className="ap-lead">{text("s2.lead")}</p>
      </div>
      <div className="ap-art">
        <p className="ap-bubble">{text("s2.bubble")}</p>
        <div className="ap-mascot-box ap-hop">
          <AuthMascot arms="up" eyes="happy" mouth="open" />
        </div>
        <div className="ap-stairs" aria-hidden="true">
          <div className="ap-step h1">{t(locale, "title.quark")}</div>
          <div className="ap-step h2 is-dim" />
          <div className="ap-step h3 is-dim" />
          <div className="ap-step h4 is-dim" />
          <div className="ap-step h5 is-top">{t(locale, "title.black_hole")}</div>
        </div>
      </div>
    </>,

    // 3 — the mascot says hello
    <>
      <div className="ap-art">
        <i className="ap-spark sp1" />
        <i className="ap-spark sp2" />
        <i className="ap-spark sp3" />
        <p className="ap-bubble">{text("s3.bubble")}</p>
        <div className="ap-mascot-box ap-bob">
          <AuthMascot arms="wave" label={text("mascot")} />
        </div>
        <ul className="ap-pills">
          <li>{t(locale, "nav.problems")}</li>
          <li>{t(locale, "nav.contests")}</li>
          <li>{t(locale, "nav.arena")}</li>
        </ul>
      </div>
    </>,

    // 4 — the podium
    <>
      <div>
        <h2 className="ap-title">{text("s4.title")}</h2>
        <p className="ap-lead">{text("s4.lead")}</p>
      </div>
      <div className="ap-art">
        <i className="ap-conf cf1" />
        <i className="ap-conf cf2" />
        <i className="ap-conf cf3" />
        <i className="ap-conf cf4" />
        <div className="ap-mascot-box">
          <AuthMascot arms="up" eyes="happy" mouth="open" />
        </div>
        <div className="ap-podium" aria-hidden="true">
          <div className="ap-pod p2"><span className="ap-av" />2</div>
          <div className="ap-pod p1"><span className="ap-av" />1</div>
          <div className="ap-pod p3"><span className="ap-av" />3</div>
          <div className="ap-pod p4"><span>↑</span>{text("s4.you")}</div>
        </div>
      </div>
    </>,

    // 5 — the next contest
    <>
      <div>
        <h2 className="ap-title">{text("s5.title")}</h2>
        <p className="ap-lead">{text("s5.lead")}</p>
      </div>
      <div className="ap-art">
        <div className="ap-cd" aria-hidden="true">
          <header>
            <span>{text("s5.next")}</span>
            <i>{text("s5.sample")}</i>
          </header>
          <h3>{text("s5.name")}</h3>
          <div className="ap-tiles">
            <div className="ap-tile"><b>02</b><span>{text("s5.days")}</span></div>
            <div className="ap-tile"><b>14</b><span>{text("s5.hours")}</span></div>
            <div className="ap-tile"><b>37</b><span>{text("s5.minutes")}</span></div>
          </div>
          <footer>{text("s5.open")}</footer>
        </div>
        <div className="ap-mascot-box ap-bob">
          <AuthMascot wide arms="hold">
            <circle className="m-watch" cx="206" cy="98" r="28" />
            <rect className="m-gold" x="200" y="62" width="12" height="8" rx="2" />
            <line className="m-line" x1="206" y1="98" x2="206" y2="78" strokeWidth="3" />
            <g className="ap-spin">
              <line className="m-hand" x1="206" y1="98" x2="206" y2="76" strokeWidth="2.5" />
            </g>
          </AuthMascot>
        </div>
      </div>
    </>,

    // 6 — the verdict stream
    <>
      <div>
        <h2 className="ap-title">{text("s6.title")}</h2>
        <p className="ap-lead">{text("s6.lead")}</p>
      </div>
      <div className="ap-art">
        <div className="ap-flow-mask" aria-hidden="true">
          <div className="ap-flow">
            {[0, 1].flatMap((copy) =>
              VERDICTS.map(([cls, code, key, n, time], i) => (
                <div key={`${copy}-${i}`} className="ap-v">
                  <code className={cls}>{code}</code>
                  {text(key).replace("{n}", n)}
                  <span className="ap-t">{time}</span>
                </div>
              )),
            )}
          </div>
        </div>
        <div className="ap-mascot-box">
          <AuthMascot wide arms="hold" mouth="flat">
            <circle className="m-gold-ring" cx="78" cy="108" r="20" strokeWidth="4" />
            <circle className="m-gold-ring" cx="122" cy="108" r="20" strokeWidth="4" />
            <line className="m-gold-ring" x1="98" y1="108" x2="102" y2="108" strokeWidth="4" />
            <g className="ap-gavel">
              <rect className="m-wood" x="188" y="104" width="10" height="44" rx="4" />
              <rect className="m-wood2" x="172" y="92" width="42" height="20" rx="6" />
            </g>
            <rect className="m-wood3" x="150" y="168" width="90" height="12" rx="4" />
          </AuthMascot>
        </div>
      </div>
    </>,

    // 7 — the streak
    <>
      <div>
        <h2 className="ap-title">{text("s7.title")}</h2>
        <p className="ap-lead">{text("s7.lead")}</p>
      </div>
      <div className="ap-art">
        <div className="ap-streak">
          <div className="ap-mascot-box ap-bob">
            <AuthMascot wide eyes="happy" mouth="open">
              <g className="ap-flick">
                <path
                  className="m-fire"
                  d="M206 40 C222 62 232 74 224 98 C218 114 196 116 190 98 C186 86 194 78 198 66 C200 80 208 80 208 70 C208 58 204 50 206 40 Z"
                />
              </g>
            </AuthMascot>
          </div>
          <p>
            <b>7</b>
            {text("s7.streak")}
          </p>
          <div className="ap-heat" aria-hidden="true">
            {heat.map((cls, i) => (
              <i key={i} className={cls} />
            ))}
          </div>
          <div className="ap-legend" aria-hidden="true">
            {text("s7.less")}
            <i />
            <i className="c1" />
            <i className="c2" />
            <i className="c3" />
            {text("s7.more")}
          </div>
        </div>
      </div>
    </>,

    // 8 — big type
    <>
      <div className="ap-art">
        <h2 className="ap-big">
          <span>{text("a")}</span>
          <span>{text("b")}</span>
          <span>{text("c")}</span>
        </h2>
        <p className="ap-lead">{t(locale, "footer.tagline")}</p>
        <div className="ap-mascot-box">
          <AuthMascot />
        </div>
      </div>
    </>,

    // 9 — three steps
    <>
      <div>
        <h2 className="ap-title">{text("s9.title")}</h2>
        <p className="ap-lead">{text("s9.lead")}</p>
      </div>
      <div className="ap-art">
        <ol className="ap-steps">
          <li className="ap-st done">
            <span className="ap-n" aria-hidden="true">✓</span>
            <div><strong>{text("s9.step1")}</strong><span className="d">{text("s9.step1d")}</span></div>
          </li>
          <li className="ap-st now">
            <span className="ap-n" aria-hidden="true">2</span>
            <div><strong>{text("s9.step2")}</strong><span className="d">{text("s9.step2d")}</span></div>
          </li>
          <li className="ap-st next">
            <span className="ap-n" aria-hidden="true">3</span>
            <div><strong>{text("s9.step3")}</strong><span className="d">{text("s9.step3d")}</span></div>
          </li>
        </ol>
        <div className="ap-mascot-box">
          <AuthMascot arms="point" gaze={-6} />
        </div>
      </div>
    </>,

    // 10 — the first achievement
    <>
      <h2 className="ap-title">{text("s10.title")}</h2>
      <div className="ap-art">
        <div className="ap-medal">
          <svg className="ap-rays" viewBox="-150 -150 300 300" aria-hidden="true">
            {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
              <path key={deg} className="m-ray" d="M0 0 L-12 -140 L12 -140Z" transform={`rotate(${deg})`} />
            ))}
          </svg>
          <div className="ap-mascot-box">
            <AuthMascot arms="up" eyes="happy" mouth="open" label={text("mascot")}>
              <path className="m-ribbon" d="M104 150 L96 190 L100 178 L120 190 L136 150Z" />
              <circle className="m-medal" cx="100" cy="150" r="24" />
              <path className="m-star" d="M100 136 L105 147 L117 148 L108 156 L111 168 L100 162 L89 168 L92 156 L83 148 L95 147Z" />
            </AuthMascot>
          </div>
        </div>
        <p className="ap-badge">{text("s10.badge")}</p>
        <ul className="ap-locks" aria-hidden="true">
          <li>{text("s10.l1")}</li>
          <li>{text("s10.l2")}</li>
          <li>{text("s10.l3")}</li>
        </ul>
      </div>
    </>,
  ];

  return (
    <aside className="ap">
      <svg className="ap-defs" aria-hidden="true" focusable="false">
        <defs>
          <linearGradient id="ap-body" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" className="ap-g1" />
            <stop offset="1" className="ap-g2" />
          </linearGradient>
          <linearGradient id="ap-fire" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0" className="ap-gf1" />
            <stop offset="1" className="ap-gf2" />
          </linearGradient>
          <linearGradient id="ap-gold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" className="ap-gg1" />
            <stop offset="1" className="ap-gg2" />
          </linearGradient>
        </defs>
      </svg>
      <Link href="/" className="ap-brand rw-focus-ring">
        RankWant
      </Link>
      <AuthCarousel
        slides={slides}
        labels={{
          region: text("carousel"),
          prev: text("prev"),
          next: text("next"),
          pause: text("pause"),
          play: text("play"),
          go: text("go"),
        }}
      />
    </aside>
  );
}
