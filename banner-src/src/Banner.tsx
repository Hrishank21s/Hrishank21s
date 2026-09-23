import React from 'react';
import {useCurrentFrame} from 'remotion';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadPress} from '@remotion/google-fonts/PressStart2P';

export const FPS = 20;
export const LOOP_S = 9;
export const DURATION = FPS * LOOP_S;

const inter = loadInter('normal', {weights: ['800', '500']}).fontFamily;
const press = loadPress().fontFamily;

// ---- layout ----------------------------------------------------------------
const W = 1200, H = 300, LANE = 250, R = 17;
const TOKENS = ['</>', '{ }', '=>', '0x1f', '();', '</>', 'fn', '{ }', '=>', 'git', '();', '</>', '{ }', '=>', 'npm', '();', '</>', '{ }', '=>', 'ts', '();', '</>'];
const TX = TOKENS.map((_, i) => 80 + (i * (1040 - 80)) / (TOKENS.length - 1));
const PELLET_X = 1100;

// ---- timeline (seconds) -----------------------------------------------------
const T_RUN0 = 0.9, T_PELLET = 4.5, T_TURN = 4.7, RUN_SPEED = 450, GHOST_FLEE = 380;
const T_RESPAWN = 7.3, T_GLINT = 7.6;

const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const easeOut = (p: number) => 1 - Math.pow(1 - p, 3);

// Pac-Man x(t): accelerating run right (R2: speed from acceleration), pause on pellet, chase left.
const pacX = (t: number) => {
  if (t < T_RUN0) return -60;
  if (t < T_PELLET) return -60 + (PELLET_X + 60) * Math.pow((t - T_RUN0) / (T_PELLET - T_RUN0), 1.5);
  if (t < T_TURN) return PELLET_X;
  return PELLET_X - RUN_SPEED * (t - T_TURN);
};
const GHOSTS = [
  {color: '#ef4444', trail: 70, catchT: T_TURN + 1.0},
  {color: '#22d3ee', trail: 125, catchT: T_TURN + 125 / 70},
];
const ghostX = (g: typeof GHOSTS[number], t: number) =>
  t < T_TURN ? pacX(t) - g.trail : PELLET_X - g.trail - GHOST_FLEE * (t - T_TURN);

// ---- sprites ----------------------------------------------------------------
const mouth = (deg: number) => {
  const a = (deg * Math.PI) / 180, x = R * Math.cos(a), y = R * Math.sin(a);
  return `M0,0 L${x.toFixed(1)},${(-y).toFixed(1)} A${R},${R} 0 1 0 ${x.toFixed(1)},${y.toFixed(1)} Z`;
};
const Ghost: React.FC<{color: string; scared: boolean; frame: number; dir: number}> = ({color, scared, frame, dir}) => {
  const r = R, f = Math.floor(frame / 3) % 2;
  const foot = f ? [r * 0.65, r] : [r, r * 0.65];
  const body = `M${-r},${r} V0 A${r},${r} 0 0 1 ${r},0 V${r} L${(r * 2) / 3},${foot[0]} L${r / 3},${foot[1]} L0,${foot[0]} L${-r / 3},${foot[1]} L${(-r * 2) / 3},${foot[0]} Z`;
  const ex = scared ? 0 : 2 * dir;
  return (
    <g>
      <path d={body} fill={scared ? '#2f4bff' : color} />
      {scared ? (
        <>
          <circle cx={-5} cy={-3} r={2.4} fill="#fde68a" /><circle cx={5} cy={-3} r={2.4} fill="#fde68a" />
          <path d={`M-9,7 l3,-3 l3,3 l3,-3 l3,3 l3,-3`} stroke="#fde68a" strokeWidth={1.6} fill="none" />
        </>
      ) : (
        <>
          <circle cx={-5} cy={-3} r={4.2} fill="#fff" /><circle cx={5} cy={-3} r={4.2} fill="#fff" />
          <circle cx={-5 + ex} cy={-3} r={2.1} fill="#0b1020" /><circle cx={5 + ex} cy={-3} r={2.1} fill="#0b1020" />
        </>
      )}
    </g>
  );
};

const pad = (n: number) => String(n).padStart(6, '0');

export const Banner: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const px = pacX(t);
  const goingLeft = t >= T_TURN;
  const chomp = Math.floor(frame / 2) % 2 === 0 ? 36 : 4;

  // tokens eaten on the way right; respawn (staggered) after the chase
  const tokenOpacity = (i: number) => {
    const eaten = t >= T_RUN0 && t < T_TURN && px >= TX[i] - 4 || (t >= T_TURN && t < T_RESPAWN);
    if (t >= T_RESPAWN) return clamp((t - T_RESPAWN - i * 0.035) / 0.15);
    return eaten ? 0 : 1;
  };
  const pelletOn = t < T_PELLET || t >= T_RESPAWN + TOKENS.length * 0.035;
  const eatenCount = TOKENS.filter((_, i) => t >= T_RUN0 && px >= TX[i] - 4 && t < T_RESPAWN).length;
  const score = t >= T_RESPAWN ? 0 : eatenCount * 10 + (t >= T_PELLET ? 50 : 0) +
    (t >= GHOSTS[0].catchT ? 200 : 0) + (t >= GHOSTS[1].catchT ? 400 : 0);
  const scoreShown = t >= T_RESPAWN ? 0 : score;

  // one glint across the name (Q4: single hero highlight)
  const gp = clamp((t - T_GLINT) / 0.9);
  const glintX = 40 + easeOut(gp) * 600;
  const glintOn = gp > 0 && gp < 1;

  const skills = ['SOFTWARE', 'AUTOMATION', 'AI TOOLS', 'HARDWARE'];
  const bob = (i: number) => Math.sin((frame + i * 3) * 0.5) * 1.6;

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#080c19" /><stop offset="1" stopColor="#1a1745" /></linearGradient>
        <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stopColor="#000" stopOpacity="0" /><stop offset="1" stopColor="#000" stopOpacity=".45" /></radialGradient>
        <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="64" y1="0" x2="600" y2="0"><stop offset="0" stopColor="#f1f5f9" /><stop offset="1" stopColor="#a5b4fc" /></linearGradient>
        <linearGradient id="glint" gradientUnits="userSpaceOnUse" x1={glintX - 70} y1="0" x2={glintX + 70} y2="0">
          <stop offset="0" stopColor="#fff" stopOpacity="0" /><stop offset=".5" stopColor="#fff" stopOpacity=".95" /><stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="pg" cx=".35" cy=".3" r=".9"><stop offset="0" stopColor="#fde68a" /><stop offset="1" stopColor="#eab308" /></radialGradient>
        <filter id="glow" x="-40%" y="-80%" width="180%" height="260%"><feGaussianBlur stdDeviation="2" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        <filter id="wallglow"><feGaussianBlur stdDeviation="2.5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        {/* tunnel gaps in the maze wall at lane height */}
        <mask id="tunnel"><rect width={W} height={H} fill="#fff" /><rect x="0" y={LANE - 26} width="40" height="52" fill="#000" /><rect x={W - 40} y={LANE - 26} width="40" height="52" fill="#000" /></mask>
        <clipPath id="lane"><rect x="0" y="0" width={W} height={H} /></clipPath>
      </defs>

      <rect width={W} height={H} rx="14" fill="url(#bg)" />
      {/* maze wall */}
      <g mask="url(#tunnel)" filter="url(#wallglow)" fill="none">
        <rect x="14" y="14" width={W - 28} height={H - 28} rx="16" stroke="#3730a3" strokeWidth="2.5" />
        <rect x="21" y="21" width={W - 42} height={H - 42} rx="11" stroke="#4f46e5" strokeWidth="1" opacity=".55" />
      </g>
      <line x1="60" y1="204" x2={W - 60} y2="204" stroke="#3730a3" strokeWidth="2" strokeLinecap="round" opacity=".8" />

      {/* HUD */}
      <text x="64" y="50" fontFamily={press} fontSize="11" fill="#facc15" opacity={Math.floor(frame / 10) % 2 === 0 ? 1 : 0.55}>PLAYER 1</text>
      <text x={W - 64} y="50" textAnchor="end" fontFamily={press} fontSize="11" fill="#e2e8f0">SCORE <tspan fill="#facc15">{pad(scoreShown)}</tspan></text>

      {/* name block */}
      <text x="64" y="132" fontFamily={inter} fontWeight="800" fontSize="74" fill="url(#name)" letterSpacing="-1.5">Hrishank Soni</text>
      {glintOn && <text x="64" y="132" fontFamily={inter} fontWeight="800" fontSize="74" fill="url(#glint)" letterSpacing="-1.5">Hrishank Soni</text>}
      <text x="66" y="172" fontFamily={inter} fontWeight="500" fontSize="16" fill="#94a3b8" letterSpacing="6">BUILDER  •  DEVELOPER  •  MAKER</text>

      {/* skill list */}
      {skills.map((s, i) => (
        <g key={s}>
          <circle cx="838" cy={82 + i * 26 - 4} r="4" fill="#facc15" />
          <text x="856" y={82 + i * 26} fontFamily={press} fontSize="11" fill="#c7d2fe">{s}</text>
        </g>
      ))}

      {t < T_RUN0 && (
        <text x={W / 2} y={LANE - 20} textAnchor="middle" fontFamily={press} fontSize="12" fill="#facc15" opacity={Math.floor(frame / 4) % 2 === 0 ? 1 : 0.4}>READY!</text>
      )}

      {/* tokens + power pellet */}
      <g filter="url(#glow)">
        {TOKENS.map((tok, i) => (
          <text key={i} x={TX[i]} y={LANE + 5} textAnchor="middle" fontFamily="Menlo, monospace" fontWeight="700" fontSize="15" fill="#4ade80" opacity={tokenOpacity(i)}>{tok}</text>
        ))}
        {pelletOn && <circle cx={PELLET_X} cy={LANE} r={7 + (Math.floor(frame / 4) % 2)} fill="#86efac" opacity={t >= T_RESPAWN ? clamp((t - T_RESPAWN - 22 * 0.035) / 0.15) : 1} />}
      </g>

      {/* ghosts */}
      {GHOSTS.map((g, i) => {
        const x = ghostX(g, t);
        const eaten = t >= g.catchT;
        if (eaten || x < -60 || x > W + 60) return null;
        return (
          <g key={i} transform={`translate(${x},${LANE + bob(i)})`}>
            <Ghost color={g.color} scared={t >= T_PELLET} frame={frame} dir={goingLeft ? -1 : 1} />
          </g>
        );
      })}

      {/* score popups */}
      {GHOSTS.map((g, i) => {
        const age = t - g.catchT;
        if (age < 0 || age > 0.8) return null;
        const x = PELLET_X - g.trail - GHOST_FLEE * (g.catchT - T_TURN);
        return <text key={i} x={x} y={LANE - 14 - age * 30} textAnchor="middle" fontFamily={press} fontSize="11" fill="#22d3ee" opacity={1 - age / 0.8}>{i === 0 ? 200 : 400}</text>;
      })}

      {/* Pac-Man */}
      {px > -50 && px < W + 50 && (
        <g transform={`translate(${px},${LANE}) scale(${goingLeft ? -1 : 1},1)`}>
          <path d={mouth(chomp)} fill="url(#pg)" />
          <circle cx="1" cy="-9" r="2.2" fill="#0b1020" />
        </g>
      )}

      <rect width={W} height={H} rx="14" fill="url(#vig)" pointerEvents="none" />
    </svg>
  );
};
