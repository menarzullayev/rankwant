import { type CSSProperties, type ReactElement, useId } from "react";

/** The 16 contest-title icons (ADR-0027), one per tier.
 *
 *  Drawn on a -32..32 grid, coloured with `currentColor` so the tier colour
 *  (`rw-rank-{group}` on a parent) paints them, and animated with CSS only.
 *  Motion runs only inside `.rw-ticon-live`; everywhere else (tables, lists)
 *  the same drawing is a still. Classes carry a `ti-` prefix to stay clear of
 *  Tailwind; keyframes live in `app/title-icons.css`.
 *
 *  Hand-drawn art, not a pack: there is nothing to swap, so it does not go
 *  through the icon registry (D4). */

const s = (o: Record<string, string>) => o as CSSProperties;

type Draw = (uid: string) => ReactElement;

const ICONS: Record<string, Draw> = {
  quark: (uid) => (
    <>
      <circle className="ti-pulse ti-fb" r="5.5" fill="currentColor" />
      <g className="ti-spin" style={s({ "--t": "7s" })}>
        <circle cx="0" cy="-11" r="2.2" fill="currentColor" className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0s" })} />
        <circle cx="9.5" cy="5.5" r="2.2" fill="currentColor" className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0.8s" })} />
        <circle cx="-9.5" cy="5.5" r="2.2" fill="currentColor" className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "1.6s" })} />
        <circle r="11" fill="none" stroke="currentColor" strokeWidth="1.2" strokeDasharray="2 5" opacity=".5" />
      </g>
      <g className="ti-spinr" style={s({ "--t": "11s" })}>
        <circle r="21" fill="none" stroke="currentColor" strokeWidth="1" strokeDasharray="1 8" opacity=".35" />
      </g>
    </>
  ),
  atom: (uid) => (
    <>
      <g transform="rotate(-30)">
        <ellipse rx="25" ry="9" fill="none" stroke="currentColor" strokeWidth="1.4" opacity="0.5" />
        <g style={s({ "--ax": "25px", "--ay": "9px", "--t": "3.2s" })}>
          <g className="ti-ox">
            <g className="ti-oy">
              <circle r="3" fill="currentColor" />
            </g>
          </g>
        </g>
      </g>
      <g transform="rotate(30)">
        <ellipse rx="25" ry="9" fill="none" stroke="currentColor" strokeWidth="1.4" opacity="0.5" />
        <g style={s({ "--ax": "25px", "--ay": "9px", "--t": "4.4s" })}>
          <g className="ti-ox">
            <g className="ti-oy">
              <circle r="3" fill="currentColor" />
            </g>
          </g>
        </g>
      </g>
      <g transform="rotate(90)">
        <ellipse rx="25" ry="9" fill="none" stroke="currentColor" strokeWidth="1.4" opacity="0.5" />
        <g style={s({ "--ax": "25px", "--ay": "9px", "--t": "5.6s" })}>
          <g className="ti-ox">
            <g className="ti-oy">
              <circle r="3" fill="currentColor" />
            </g>
          </g>
        </g>
      </g>
      <circle className="ti-pulse ti-fb" r="6" fill="currentColor" />
      <circle cx="-1.8" cy="-1.8" r="1.8" fill="var(--ti-glint)" opacity=".5" />
    </>
  ),
  molecule: (uid) => (
    <>
      <g className="ti-wob" style={s({ "--t": "6s" })}>
        <line x1="0" y1="0" x2="-18" y2="-12" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" opacity=".55" />
        <line x1="0" y1="0" x2="18" y2="-12" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" opacity=".55" />
        <line x1="0" y1="0" x2="0" y2="20" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" opacity=".55" />
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.6s", "animationDelay": "0s" })}>
          <circle cx="0" cy="0" r="9" fill="currentColor" />
          <circle cx="-3.1" cy="-3.1" r="2.5" fill="var(--ti-glint)" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.6s", "animationDelay": "0.5s" })}>
          <circle cx="-18" cy="-12" r="6" fill="currentColor" />
          <circle cx="-20.1" cy="-14.1" r="1.7" fill="var(--ti-glint)" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.6s", "animationDelay": "1s" })}>
          <circle cx="18" cy="-12" r="6" fill="currentColor" />
          <circle cx="15.9" cy="-14.1" r="1.7" fill="var(--ti-glint)" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.6s", "animationDelay": "1.5s" })}>
          <circle cx="0" cy="20" r="6" fill="currentColor" />
          <circle cx="-2.1" cy="17.9" r="1.7" fill="var(--ti-glint)" opacity=".5" />
        </g>
      </g>
    </>
  ),
  droplet: (uid) => (
    <>
      <g className="ti-bob" style={s({ "--t": "3s" })}>
        <path d="M0 -23C0 -23 -14 -5 -14 5a14 14 0 0 0 28 0C14 -5 0 -23 0 -23Z" fill="currentColor" opacity=".92" />
        <path d="M-8 3a8 8 0 0 0 5 9" fill="none" stroke="var(--ti-glint)" strokeWidth="2.2" strokeLinecap="round" opacity=".6" />
      </g>
      <ellipse className="ti-rip ti-fb" style={s({ "--t": "2.8s" })} cy="25" rx="24" ry="5" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <ellipse className="ti-rip ti-fb" style={s({ "--t": "2.8s", "animationDelay": "-1.4s" })} cy="25" rx="24" ry="5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    </>
  ),
  meteorite: (uid) => (
    <>
      <g className="ti-shake" style={s({ "--t": ".5s" })}>
        <path d="M-2 -2L-30 -30" className="ti-flowd" style={s({ "--t": "0.9s" })} fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round" strokeDasharray="9 6" opacity=".6" />
        <path d="M-8 6L-32 -10" className="ti-flowd" style={s({ "--t": "1.1s" })} fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeDasharray="9 6" opacity=".6" />
        <path d="M6 -8L-10 -32" className="ti-flowd" style={s({ "--t": "1.3s" })} fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeDasharray="9 6" opacity=".6" />
        <circle className="ti-drift ti-fb" style={s({ "--t": "1.6s", "animationDelay": "0s" })} cx="-8" cy="-8" r="1.6" fill="currentColor" />
        <circle className="ti-drift ti-fb" style={s({ "--t": "1.9s", "animationDelay": "-0.6s" })} cx="-14" cy="-6" r="1.6" fill="currentColor" />
        <circle className="ti-drift ti-fb" style={s({ "--t": "1.7s", "animationDelay": "-1.1s" })} cx="-6" cy="-15" r="1.6" fill="currentColor" />
        <g transform="translate(9 9)">
          <polygon points="-4,-12 8,-10 14,-2 12,10 2,15 -9,10 -13,0" fill="currentColor" />
          <circle cx="-2" cy="-1" r="3.2" fill="var(--rw-surface)" opacity=".55" />
          <circle cx="6" cy="6" r="2" fill="var(--rw-surface)" opacity=".55" />
          <circle cx="-6" cy="7" r="1.6" fill="var(--rw-surface)" opacity=".55" />
        </g>
      </g>
    </>
  ),
  comet: (uid) => (
    <>
      <g className="ti-cruise" style={s({ "--t": "3.4s" })}>
        <polygon points="18,8 -30,-30 8,18" fill="currentColor" opacity=".28" />
        <polygon points="15,10 -20,-20 10,15" fill="currentColor" opacity=".5" className="ti-brth" style={s({ "--t": "1.8s" })} />
        <path d="M14 14L-22 -22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="6 8" className="ti-flowd" style={s({ "--t": ".8s" })} opacity=".9" />
        <circle className="ti-pulse ti-fb" style={s({ "--t": "2s" })} cx="14" cy="14" r="12" fill="currentColor" opacity=".22" />
        <circle cx="14" cy="14" r="7" fill="currentColor" />
        <circle cx="12" cy="12" r="2" fill="var(--ti-glint)" opacity=".6" />
        <circle className="ti-drift ti-fb" style={s({ "--t": "1.6s" })} cx="-6" cy="-6" r="1.4" fill="currentColor" />
        <circle className="ti-drift ti-fb" style={s({ "--t": "2s", "animationDelay": "-.8s" })} cx="-12" cy="-4" r="1.2" fill="currentColor" />
      </g>
    </>
  ),
  moon: (uid) => (
    <>
      <mask id={`url(#${uid}-mk)`}>
        <rect x="-32" y="-32" width="64" height="64" fill="white" />
        <circle cx="10" cy="-7" r="18" fill="black" />
      </mask>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "4s" })} r="27" fill="none" stroke="currentColor" strokeWidth="1.4" opacity=".4" />
      <g className="ti-sway" style={s({ "--t": "6s" })}>
        <circle cx="-3" cy="3" r="22" fill="currentColor" mask={`url(#${uid}-mk)`} />
        <circle cx="-12" cy="8" r="2.6" fill="var(--rw-surface)" opacity=".45" mask={`url(#${uid}-mk)`} />
        <circle cx="-6" cy="19" r="1.8" fill="var(--rw-surface)" opacity=".45" />
      </g>
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0s" })} fill="currentColor" d="M18 -20Q18 -16 22 -16Q18 -16 18 -12Q18 -16 14 -16Q18 -16 18 -20Z" />
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0.9s" })} fill="currentColor" d="M24 6Q24 9 27 9Q24 9 24 12Q24 9 21 9Q24 9 24 6Z" />
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "1.6s" })} fill="currentColor" d="M10 19.6Q10 22 12.4 22Q10 22 10 24.4Q10 22 7.6 22Q10 22 10 19.6Z" />
    </>
  ),
  planet: (uid) => (
    <>
      <clipPath id={`url(#${uid}-cp)`}>
        <circle r="13" />
      </clipPath>
      <g className="ti-sway" style={s({ "--t": "7s", "--r": "4deg" })}>
        <g transform="rotate(-18)">
          <path d="M-28 0A28 8 0 0 1 28 0" fill="none" stroke="currentColor" strokeWidth="3" opacity=".5" />
          <path d="M-22 0A22 6 0 0 1 22 0" fill="none" stroke="currentColor" strokeWidth="1.4" opacity=".35" />
        </g>
        <circle r="13" fill="currentColor" />
        <g clipPath={`url(#${uid}-cp)`}>
          <rect x="-14" y="-6" width="28" height="3" fill="var(--ti-glint)" opacity=".22" />
          <rect x="-14" y="2" width="28" height="4" fill="var(--ti-shade)" opacity=".16" />
          <ellipse className="ti-slide" style={s({ "--t": "3.6s" })} cx="0" cy="-1" rx="4" ry="2.6" fill="var(--ti-glint)" opacity=".4" />
          <ellipse className="ti-slide" style={s({ "--t": "3.6s", "animationDelay": "-1.8s" })} cx="0" cy="7" rx="3" ry="2" fill="var(--ti-shade)" opacity=".25" />
        </g>
        <g transform="rotate(-18)">
          <path d="M-28 0A28 8 0 0 0 28 0" fill="none" stroke="currentColor" strokeWidth="3" />
          <path d="M-22 0A22 6 0 0 0 22 0" fill="none" stroke="currentColor" strokeWidth="1.4" opacity=".7" />
        </g>
      </g>
    </>
  ),
  star: (uid) => (
    <>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "3s" })} r="27" fill="none" stroke="currentColor" strokeWidth="1.2" opacity=".35" />
      <g className="ti-twst ti-fb" style={s({ "--t": "3.2s" })}>
        <polygon points="0,-23 5.6,-7.7 21.9,-7.1 9,2.9 13.5,18.6 0,9.5 -13.5,18.6 -9,2.9 -21.9,-7.1 -5.6,-7.7" fill="currentColor" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
        <polygon points="0,-9 3,-3 9,-1 4,3 5,9 0,6 -5,9 -4,3 -9,-1 -3,-3" fill="var(--ti-glint)" opacity=".28" />
      </g>
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0s" })} fill="currentColor" d="M-24 -22Q-24 -18 -20 -18Q-24 -18 -24 -14Q-24 -18 -28 -18Q-24 -18 -24 -22Z" />
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0.9s" })} fill="currentColor" d="M25 -15Q25 -12 28 -12Q25 -12 25 -9Q25 -12 22 -12Q25 -12 25 -15Z" />
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "1.7s" })} fill="currentColor" d="M22 19Q22 22 25 22Q22 22 22 25Q22 22 19 22Q22 22 22 19Z" />
      <path className="ti-tw ti-fb" style={s({ "--t": "2.4s", "animationDelay": "0.4s" })} fill="currentColor" d="M-22 17.6Q-22 20 -19.6 20Q-22 20 -22 22.4Q-22 20 -24.4 20Q-22 20 -22 17.6Z" />
    </>
  ),
  supernova: (uid) => (
    <>
      <circle className="ti-rip ti-fb" style={s({ "--t": "2.6s" })} r="29" fill="none" stroke="currentColor" strokeWidth="2" />
      <circle className="ti-rip ti-fb" style={s({ "--t": "2.6s", "animationDelay": "-1.3s" })} r="29" fill="none" stroke="currentColor" strokeWidth="2" />
      <g className="ti-spin" style={s({ "--t": "30s" })}>
        <g className="ti-burst ti-fb" style={s({ "--t": "1.8s" })}>
          <line x1="11" y1="0" x2="27" y2="0" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="10.2" y1="4.2" x2="18.5" y2="7.7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="7.8" y1="7.8" x2="19.1" y2="19.1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="4.2" y1="10.2" x2="7.7" y2="18.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="0" y1="11" x2="0" y2="27" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="-4.2" y1="10.2" x2="-7.7" y2="18.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="-7.8" y1="7.8" x2="-19.1" y2="19.1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="-10.2" y1="4.2" x2="-18.5" y2="7.7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="-11" y1="0" x2="-27" y2="0" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="-10.2" y1="-4.2" x2="-18.5" y2="-7.7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="-7.8" y1="-7.8" x2="-19.1" y2="-19.1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="-4.2" y1="-10.2" x2="-7.7" y2="-18.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="-0" y1="-11" x2="-0" y2="-27" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="4.2" y1="-10.2" x2="7.7" y2="-18.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
          <line x1="7.8" y1="-7.8" x2="19.1" y2="-19.1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
          <line x1="10.2" y1="-4.2" x2="18.5" y2="-7.7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
        </g>
      </g>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "1.8s" })} r="8" fill="currentColor" />
      <circle r="3.4" fill="var(--ti-glint)" opacity=".7" />
    </>
  ),
  pulsar: (uid) => (
    <>
      <circle className="ti-rip ti-fb" style={s({ "--t": "2s" })} r="28" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <g className="ti-spin" style={s({ "--t": "2.8s" })}>
        <polygon points="0,0 -4.2,-30 4.2,-30" fill="currentColor" opacity=".8" />
        <polygon points="0,0 -4.2,30 4.2,30" fill="currentColor" opacity=".8" />
        <polygon points="0,0 -9,-30 9,-30" fill="currentColor" opacity=".18" />
        <polygon points="0,0 -9,30 9,30" fill="currentColor" opacity=".18" />
      </g>
      <circle r="13" fill="none" stroke="currentColor" strokeWidth="1.2" strokeDasharray="2 4" opacity=".5" />
      <circle className="ti-pulse ti-fb" style={s({ "--t": ".9s" })} r="5.5" fill="currentColor" />
      <circle r="2" fill="var(--ti-glint)" opacity=".7" />
    </>
  ),
  magnetar: (uid) => (
    <>
      <path className="ti-flowd" style={s({ "--t": "1.2s" })} d="M0 -6C-17.5 -15.400000000000002 -17.5 15.400000000000002 0 6" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeDasharray="7 5" opacity="0.95" />
      <path className="ti-flowd" style={s({ "--t": "1.2s" })} d="M0 -6C17.5 -15.400000000000002 17.5 15.400000000000002 0 6" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeDasharray="7 5" opacity="0.95" />
      <path className="ti-flowd" style={s({ "--t": "1.5499999999999998s" })} d="M0 -6C-30.0 -26.400000000000002 -30.0 26.400000000000002 0 6" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeDasharray="7 5" opacity="0.65" />
      <path className="ti-flowd" style={s({ "--t": "1.5499999999999998s" })} d="M0 -6C30.0 -26.400000000000002 30.0 26.400000000000002 0 6" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeDasharray="7 5" opacity="0.65" />
      <path className="ti-flowd" style={s({ "--t": "1.9s" })} d="M0 -6C-38.75 -34.1 -38.75 34.1 0 6" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeDasharray="7 5" opacity="0.4" />
      <path className="ti-flowd" style={s({ "--t": "1.9s" })} d="M0 -6C38.75 -34.1 38.75 34.1 0 6" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeDasharray="7 5" opacity="0.4" />
      <g className="ti-sway" style={s({ "--t": "5s", "--r": "6deg" })}>
        <ellipse rx="3.5" ry="9" fill="none" stroke="currentColor" strokeWidth="1.2" opacity=".6" />
      </g>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "1.2s" })} r="6.5" fill="currentColor" />
      <circle r="2.4" fill="var(--ti-glint)" opacity=".7" />
      <path className="ti-flick" style={s({ "--t": ".9s" })} d="M0 -12L-3 -19L1 -19L-2 -27" fill="none" stroke="var(--ti-glint)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      <path className="ti-flick" style={s({ "--t": "1.3s", "animationDelay": "-.5s" })} d="M0 12L3 19L-1 19L2 27" fill="none" stroke="var(--ti-glint)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </>
  ),
  black_hole: (uid) => (
    <>
      <g transform="rotate(-14)">
        <ellipse rx="29" ry="9.5" fill="none" stroke="currentColor" strokeWidth="5" opacity=".5" />
        <ellipse className="ti-flowd" style={s({ "--t": "2.4s" })} rx="29" ry="9.5" fill="none" stroke="var(--ti-glint)" strokeWidth="1.4" strokeDasharray="3 14" opacity=".8" />
      </g>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "3s" })} r="14" fill="none" stroke="currentColor" strokeWidth="2.4" opacity=".9" />
      <circle r="11" fill="var(--ti-void)" />
      <g transform="rotate(-14)">
        <path d="M-29 0A29 9.5 0 0 0 29 0" fill="none" stroke="currentColor" strokeWidth="5" />
        <path className="ti-flowd" style={s({ "--t": "2s" })} d="M-29 0A29 9.5 0 0 0 29 0" fill="none" stroke="var(--ti-glint)" strokeWidth="1.4" strokeDasharray="3 14" opacity=".9" />
      </g>
      <path d="M-15 -7A16 16 0 0 1 15 -7" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" className="ti-brth" style={s({ "--t": "2.4s" })} />
    </>
  ),
  galaxy: (uid) => (
    <>
      <g className="ti-spin" style={s({ "--t": "16s" })}>
        <path d="M2.4 1.8 L2.5 2.5 L2.5 3.2 L2.4 4 L2.1 4.8 L1.7 5.5 L1.1 6.3 L0.3 6.9 L-0.6 7.4 L-1.6 7.9 L-2.8 8.1 L-4 8.2 L-5.3 8.1 L-6.6 7.9 L-7.9 7.4 L-9.2 6.7" fill="none" stroke="currentColor" strokeWidth="4.2" strokeLinecap="round" strokeLinejoin="round" opacity="1" />
        <path d="M-7.9 7.4 L-9.2 6.7 L-10.4 5.8 L-11.6 4.6 L-12.6 3.3 L-13.5 1.8 L-14.2 0.1 L-14.6 -1.7 L-14.9 -3.6 L-14.8 -5.6 L-14.5 -7.6 L-13.9 -9.7 L-13.1 -11.7 L-11.9 -13.6 L-10.4 -15.4 L-8.7 -17.1" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" opacity="0.8" />
        <path d="M-10.4 -15.4 L-8.7 -17.1 L-6.7 -18.6 L-4.5 -19.8 L-2.1 -20.8 L0.5 -21.4 L3.2 -21.7 L6 -21.7 L8.8 -21.3 L11.7 -20.6 L14.5 -19.4 L17.1 -17.9 L19.6 -16 L21.9 -13.8 L24 -11.2 L25.7 -8.3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" />
        <path d="M-2.4 -1.8 L-2.5 -2.5 L-2.5 -3.2 L-2.4 -4 L-2.1 -4.8 L-1.7 -5.5 L-1.1 -6.3 L-0.3 -6.9 L0.6 -7.4 L1.6 -7.9 L2.8 -8.1 L4 -8.2 L5.3 -8.1 L6.6 -7.9 L7.9 -7.4 L9.2 -6.7" fill="none" stroke="currentColor" strokeWidth="4.2" strokeLinecap="round" strokeLinejoin="round" opacity="1" />
        <path d="M7.9 -7.4 L9.2 -6.7 L10.4 -5.8 L11.6 -4.6 L12.6 -3.3 L13.5 -1.8 L14.2 -0.1 L14.6 1.7 L14.9 3.6 L14.8 5.6 L14.5 7.6 L13.9 9.7 L13.1 11.7 L11.9 13.6 L10.4 15.4 L8.7 17.1" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" opacity="0.8" />
        <path d="M10.4 15.4 L8.7 17.1 L6.7 18.6 L4.5 19.8 L2.1 20.8 L-0.5 21.4 L-3.2 21.7 L-6 21.7 L-8.8 21.3 L-11.7 20.6 L-14.5 19.4 L-17.1 17.9 L-19.6 16 L-21.9 13.8 L-24 11.2 L-25.7 8.3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" />
        <circle cx="-12.3" cy="4.6" r="0.5" fill="currentColor" opacity=".7" />
        <circle cx="10.7" cy="-21.6" r="0.5" fill="currentColor" opacity=".7" />
        <circle cx="-16.8" cy="-3.4" r="0.8" fill="currentColor" opacity=".7" />
        <circle cx="4.8" cy="-10.2" r="0.8" fill="currentColor" opacity=".7" />
        <circle cx="25.9" cy="-7" r="0.7" fill="currentColor" opacity=".7" />
        <circle cx="27.2" cy="-4" r="0.6" fill="currentColor" opacity=".7" />
        <circle cx="-14.5" cy="-4.5" r="0.8" fill="currentColor" opacity=".7" />
        <circle cx="0.4" cy="-21" r="0.9" fill="currentColor" opacity=".7" />
        <circle cx="-14.2" cy="-0.9" r="0.9" fill="currentColor" opacity=".7" />
        <circle cx="10.5" cy="13.3" r="0.8" fill="currentColor" opacity=".7" />
        <circle cx="-20.4" cy="16.7" r="1" fill="currentColor" opacity=".7" />
        <circle cx="-9.2" cy="-19.3" r="0.7" fill="currentColor" opacity=".7" />
        <circle cx="11.2" cy="12.6" r="0.7" fill="currentColor" opacity=".7" />
        <circle cx="27.1" cy="-4.8" r="0.6" fill="currentColor" opacity=".7" />
        <circle cx="13.1" cy="-3.2" r="1.1" fill="currentColor" opacity=".7" />
        <circle cx="-0.3" cy="-7.7" r="0.7" fill="currentColor" opacity=".7" />
        <circle cx="16.8" cy="2.1" r="0.6" fill="currentColor" opacity=".7" />
        <circle cx="-6.6" cy="10" r="0.9" fill="currentColor" opacity=".7" />
      </g>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "2.6s" })} r="5" fill="currentColor" />
      <circle r="2" fill="var(--ti-glint)" opacity=".7" />
    </>
  ),
  supercluster: (uid) => (
    <>
      <g className="ti-spin" style={s({ "--t": "60s" })}>
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="0" y1="0" x2="-17" y2="-10" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.6s" })} x1="0" y1="0" x2="-8" y2="-22" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="0" y1="0" x2="12" y2="-18" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="0" y1="0" x2="22" y2="-3" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="0" y1="0" x2="-18" y2="14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="-17" y1="-10" x2="-8" y2="-22" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="-17" y1="-10" x2="-26" y2="2" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.6s" })} x1="-17" y1="-10" x2="-30" y2="-14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.6s" })} x1="-8" y1="-22" x2="12" y2="-18" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="-8" y1="-22" x2="-30" y2="-14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="12" y1="-18" x2="22" y2="-3" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="12" y1="-18" x2="28" y2="-20" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="22" y1="-3" x2="18" y2="16" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="22" y1="-3" x2="28" y2="-20" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.6s" })} x1="18" y1="16" x2="2" y2="24" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "2.1s" })} x1="2" y1="24" x2="-18" y2="14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="-18" y1="14" x2="-26" y2="2" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <line className="ti-flowd" style={s({ "--t": "1.6s" })} x1="-26" y1="2" x2="-30" y2="-14" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 5" opacity=".55" />
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.2s", "animationDelay": "0.0s" })}>
          <circle cx="0" cy="0" r="3.6" fill="currentColor" />
          <circle cx="0" cy="0" r="7.2" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.8000000000000003s", "animationDelay": "-0.3s" })}>
          <circle cx="-17" cy="-10" r="2.6" fill="currentColor" />
          <circle cx="-17" cy="-10" r="5.2" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.4000000000000004s", "animationDelay": "-0.6s" })}>
          <circle cx="-8" cy="-22" r="2.2" fill="currentColor" />
          <circle cx="-8" cy="-22" r="4.4" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.2s", "animationDelay": "-0.8999999999999999s" })}>
          <circle cx="12" cy="-18" r="2.8" fill="currentColor" />
          <circle cx="12" cy="-18" r="5.6" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.8000000000000003s", "animationDelay": "-1.2s" })}>
          <circle cx="22" cy="-3" r="2.4" fill="currentColor" />
          <circle cx="22" cy="-3" r="4.8" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.4000000000000004s", "animationDelay": "-1.5s" })}>
          <circle cx="18" cy="16" r="2.8" fill="currentColor" />
          <circle cx="18" cy="16" r="5.6" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.2s", "animationDelay": "-1.7999999999999998s" })}>
          <circle cx="2" cy="24" r="2.2" fill="currentColor" />
          <circle cx="2" cy="24" r="4.4" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.8000000000000003s", "animationDelay": "-2.1s" })}>
          <circle cx="-18" cy="14" r="2.6" fill="currentColor" />
          <circle cx="-18" cy="14" r="5.2" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "3.4000000000000004s", "animationDelay": "-2.4s" })}>
          <circle cx="-26" cy="2" r="1.8" fill="currentColor" />
          <circle cx="-26" cy="2" r="3.6" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.2s", "animationDelay": "-2.6999999999999997s" })}>
          <circle cx="28" cy="-20" r="1.6" fill="currentColor" />
          <circle cx="28" cy="-20" r="3.2" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
        <g className="ti-pulse ti-fb" style={s({ "--t": "2.8000000000000003s", "animationDelay": "-3.0s" })}>
          <circle cx="-30" cy="-14" r="1.6" fill="currentColor" />
          <circle cx="-30" cy="-14" r="3.2" fill="none" stroke="currentColor" strokeWidth=".8" opacity=".5" />
        </g>
      </g>
    </>
  ),
  cosmos: (uid) => (
    <>
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.0s", "animationDelay": "0.0s" })} cx="-26" cy="-22" r="1.2" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.7s", "animationDelay": "-0.45s" })} cx="24" cy="-24" r="1.4" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "3.4s", "animationDelay": "-0.9s" })} cx="28" cy="6" r="1" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.0s", "animationDelay": "-1.35s" })} cx="-28" cy="12" r="1.3" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.7s", "animationDelay": "-1.8s" })} cx="8" cy="28" r="1.1" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "3.4s", "animationDelay": "-2.25s" })} cx="-10" cy="-29" r="1" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.0s", "animationDelay": "-2.7s" })} cx="30" cy="24" r="1.2" fill="currentColor" />
      <circle className="ti-tw ti-fb" style={s({ "--t": "2.7s", "animationDelay": "-3.15s" })} cx="-20" cy="28" r="1" fill="currentColor" />
      <g className="ti-spinr" style={s({ "--t": "80s" })}>
        <circle r="30" fill="none" stroke="currentColor" strokeWidth="1.4" strokeDasharray="1 5" opacity=".6" />
      </g>
      <g transform="rotate(-28)">
        <ellipse rx="25" ry="9" fill="none" stroke="currentColor" strokeWidth="1.1" opacity="0.35" />
        <g style={s({ "--ax": "25px", "--ay": "9px", "--t": "7s" })}>
          <g className="ti-ox">
            <g className="ti-oy">
              <circle r="2.8" fill="currentColor" />
            </g>
          </g>
        </g>
      </g>
      <g transform="rotate(34)">
        <ellipse rx="16" ry="6" fill="none" stroke="currentColor" strokeWidth="1.1" opacity="0.35" />
        <g style={s({ "--ax": "16px", "--ay": "6px", "--t": "4.6s" })}>
          <g className="ti-ox">
            <g className="ti-oy">
              <circle r="2.2" fill="currentColor" />
            </g>
          </g>
        </g>
      </g>
      <g className="ti-spin" style={s({ "--t": "10s" })}>
        <path d="M0.3 3 L0.1 3.2 L-0.2 3.4 L-0.6 3.5 L-0.9 3.6 L-1.3 3.7 L-1.7 3.7 L-2.1 3.7 L-2.6 3.7 L-3 3.6 L-3.4 3.4 L-3.9 3.2 L-4.3 3 L-4.7 2.6 L-5.1 2.3 L-5.5 1.9" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" opacity="1" />
        <path d="M-5.1 2.3 L-5.5 1.9 L-5.8 1.4 L-6.1 0.9 L-6.3 0.4 L-6.5 -0.2 L-6.7 -0.8 L-6.8 -1.5 L-6.8 -2.1 L-6.7 -2.8 L-6.6 -3.5 L-6.4 -4.1 L-6.2 -4.8 L-5.8 -5.5 L-5.5 -6.1 L-5 -6.8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.8" />
        <path d="M-5.5 -6.1 L-5 -6.8 L-4.5 -7.3 L-3.9 -7.9 L-3.2 -8.4 L-2.5 -8.8 L-1.7 -9.2 L-0.9 -9.5 L-0 -9.7 L0.9 -9.8 L1.8 -9.9 L2.7 -9.9 L3.7 -9.8 L4.6 -9.6 L5.5 -9.3 L6.5 -8.9" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" />
        <path d="M-0.3 -3 L-0.1 -3.2 L0.2 -3.4 L0.6 -3.5 L0.9 -3.6 L1.3 -3.7 L1.7 -3.7 L2.1 -3.7 L2.6 -3.7 L3 -3.6 L3.4 -3.4 L3.9 -3.2 L4.3 -3 L4.7 -2.6 L5.1 -2.3 L5.5 -1.9" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" opacity="1" />
        <path d="M5.1 -2.3 L5.5 -1.9 L5.8 -1.4 L6.1 -0.9 L6.3 -0.4 L6.5 0.2 L6.7 0.8 L6.8 1.5 L6.8 2.1 L6.7 2.8 L6.6 3.5 L6.4 4.1 L6.2 4.8 L5.8 5.5 L5.5 6.1 L5 6.8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" opacity="0.8" />
        <path d="M5.5 6.1 L5 6.8 L4.5 7.3 L3.9 7.9 L3.2 8.4 L2.5 8.8 L1.7 9.2 L0.9 9.5 L0 9.7 L-0.9 9.8 L-1.8 9.9 L-2.7 9.9 L-3.7 9.8 L-4.6 9.6 L-5.5 9.3 L-6.5 8.9" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" opacity="0.55" />
      </g>
      <circle className="ti-pulse ti-fb" style={s({ "--t": "2.2s" })} r="3.4" fill="currentColor" />
      <circle r="1.4" fill="var(--ti-glint)" opacity=".8" />
    </>
  ),
};

export const TITLE_ICON_CODES = Object.keys(ICONS);

/** Decorative: the tier name is always written beside it. */
export function TitleIcon({
  code,
  live = false,
  className = "size-6",
}: {
  code: string;
  live?: boolean;
  className?: string;
}) {
  const uid = useId();
  const draw = ICONS[code];
  if (!draw) return null;
  return (
    <svg
      viewBox="-32 -32 64 64"
      aria-hidden="true"
      focusable="false"
      className={`rw-ticon ${live ? "rw-ticon-live" : ""} shrink-0 ${className}`}
    >
      {draw(uid)}
    </svg>
  );
}
