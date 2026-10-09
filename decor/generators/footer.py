import sys
W, H, T = 1200, 100, 10                       # size, loop seconds
MONO = "ui-monospace,Menlo,Consolas,monospace"
FX, SLOTS, SG = 130, [330, 460, 590], 22      # reel x, pad x's, % per placement
HOT, COOL, DONE = 70, 88, 100

# placement timeline (percent of loop)
head = "@keyframes hd{"; placed = []
for i, sx in enumerate(SLOTS):
    a = i * SG
    head += (f"{a:.1f}%,{a+SG*.15:.1f}%{{transform:translate({FX}px,0)}}{a+SG*.55:.1f}%{{transform:translate({sx}px,0)}}"
             f"{a+SG*.65:.1f}%{{transform:translate({sx}px,14px)}}{a+SG*.75:.1f}%{{transform:translate({sx}px,0)}}")
    placed.append(a + SG * .65)
head += f"{3*SG:.1f}%,100%{{transform:translate({FX}px,0)}}}}"
P3 = placed[-1]
carry = "@keyframes cr{" + "".join(f"{i*SG:.1f}%{{opacity:0}}{i*SG+SG*.15:.1f}%,{placed[i]:.1f}%{{opacity:1}}{placed[i]+.1:.1f}%{{opacity:0}}" for i in range(3)) + "100%{opacity:0}}"
drops = "".join(f"@keyframes p{i}{{0%,{p:.1f}%{{opacity:0}}{p+.1:.1f}%,97%{{opacity:1}}100%{{opacity:0}}}}" for i, p in enumerate(placed))

def phases(name, spans):                      # show element only within [a, b)
    a, b = spans
    return f"@keyframes {name}{{0%,{max(a-.01,0):.2f}%{{opacity:0}}{a:.2f}%,{b-.01:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"

# temperature readout + bar
tl = [(0, placed[0], 36), (placed[0], placed[1], 44), (placed[1], P3, 52), (P3, HOT, 61), (HOT, 76, 55), (76, 82, 48), (82, DONE, 40)]
col = lambda v: "#f87171" if v > 56 else "#fbbf24" if v > 45 else "#86efac"
temps = "".join(f'<text x="{W-36}" y="50" text-anchor="end" class="m" style="font-size:22px;fill:{col(v)};animation:t{i} {T}s infinite">{v}°C</text>' for i, (a, b, v) in enumerate(tl))
tkf = "".join(phases(f"t{i}", (a, b)) for i, (a, b, _) in enumerate(tl))
bar = "@keyframes br{" + "".join(f"{a:.2f}%{{transform:scaleX({(v-30)/35:.2f});fill:{col(v)}}}{b-.02:.2f}%{{transform:scaleX({(v-30)/35:.2f});fill:{col(v)}}}" for a, b, v in tl) + "}"

# status line
st = [(0, P3, "ASSEMBLING…", "#86efac"), (P3, HOT, "THERMAL LOAD", "#f87171"), (HOT, COOL, "COOLING", "#67e8f9"), (COOL, DONE, "STABLE ✓", "#4ade80")]
status = "".join(f'<text x="{W-36}" y="84" text-anchor="end" class="m" style="font-size:10px;fill:{c};animation:s{i} {T}s infinite">{s}</text>' for i, (a, b, s, c) in enumerate(st))
skf = "".join(phases(f"s{i}", (a, b)) for i, (a, b, *_ ) in enumerate(st))

# fan: angle integrated from a speed profile (rev per loop-%), so it spins up when hot
speed = lambda p: 1.2 if p < HOT else 9 if p < COOL else 3
ang, pts = 0.0, []
for p in range(0, 101):
    pts.append((p, ang)); ang += speed(p) * 3.6 * 3
step = 360 / 7; scale = round(ang / step) * step / ang   # end on blade symmetry → seamless loop
fan = "@keyframes fan{" + "".join(f"{p}%{{transform:rotate({a*scale:.1f}deg)}}" for p, a in pts) + "}"

core = f"@keyframes core{{0%,{P3:.1f}%{{fill:#4ade80}}{P3+3:.1f}%,{HOT:.1f}%{{fill:#f87171}}{COOL-6:.1f}%{{fill:#fbbf24}}{COOL:.1f}%,100%{{fill:#4ade80}}}}"
glow = f"@keyframes gl{{0%,{P3:.1f}%{{opacity:0}}{P3+3:.1f}%,{HOT:.1f}%{{opacity:.5}}{COOL:.1f}%,100%{{opacity:0}}}}"
air = phases("air", (HOT, COOL + 2)) + phases("heat", (P3, COOL))

chip = lambda x, y, attr="": f'<g {attr}><rect x="{x-14}" y="{y}" width="28" height="16" rx="2" fill="#111827" stroke="#334155"/><rect x="{x-10}" y="{y+5}" width="6" height="6" class="core"/></g>'
blades = "".join(f'<path d="M0 0C10 -8 26 -6 30 4C20 4 10 6 0 0Z" fill="#64748b" transform="rotate({i*360/7:.0f})"/>' for i in range(7))
fins = "".join(f'<rect x="{700+i*10}" y="20" width="5" height="60" rx="1" fill="#475569"/>' for i in range(9))
airlines = "".join(f'<line x1="{915}" y1="{y}" x2="{985}" y2="{y}" class="al" style="animation-delay:-{d}s"/>' for y, d in ((34, 0), (50, .2), (66, .1)))
holes = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#03120d" stroke="#b8873b" stroke-width="2"/>' for x in (18, W-18) for y in (18, H-18))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.m{{font:600 12px {MONO};letter-spacing:2px}}
.hd{{animation:hd {T}s ease-in-out infinite}}.cr{{animation:cr {T}s infinite}}
.core{{animation:core {T}s infinite}}.gl{{opacity:0;filter:blur(7px);animation:gl {T}s infinite}}
.fan{{animation:fan {T}s linear infinite}}
.al{{stroke:#67e8f9;stroke-width:2;stroke-linecap:round;stroke-dasharray:14 10;opacity:0;animation:air {T}s infinite,flow .4s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-24}}}}
.ht{{stroke:#f97316;stroke-width:3;stroke-linecap:round;stroke-dasharray:16 120;opacity:0;animation:heat {T}s infinite,run 1s linear infinite;filter:drop-shadow(0 0 4px #f97316)}}
@keyframes run{{from{{stroke-dashoffset:136}}to{{stroke-dashoffset:0}}}}
.bar{{transform-box:fill-box;transform-origin:left;animation:br {T}s infinite}}
text{{opacity:0}}.lbl{{opacity:1}}
{head}{carry}{drops}{tkf}{bar}{skf}{fan}{core}{glow}{air}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="#03140e" stroke="#b8873b" stroke-opacity=".4" stroke-width="2"/>{holes}
<line x1="50" y1="20" x2="650" y2="20" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
<circle cx="{FX}" cy="62" r="24" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="6 6"><animateTransform attributeName="transform" type="rotate" from="0 {FX} 62" to="-360 {FX} 62" dur="6s" repeatCount="indefinite"/></circle><circle cx="{FX}" cy="62" r="6" fill="#94a3b8"/>
<text x="{FX}" y="96" text-anchor="middle" class="m lbl" style="font-size:9px;fill:#4b7a63">REEL</text>
{"".join(f'<rect x="{sx-30}" y="48" width="60" height="38" rx="6" fill="#f97316" class="gl"/>' for sx in SLOTS)}
<line x1="{SLOTS[0]}" y1="80" x2="700" y2="80" stroke="#134e3a" stroke-width="3"/><line x1="{SLOTS[0]}" y1="80" x2="700" y2="80" class="ht"/>
{"".join(f'<rect x="{sx-18}" y="74" width="36" height="6" fill="#b8873b" opacity=".7"/>' for sx in SLOTS)}
{"".join(chip(sx, 58, f'style="opacity:0;animation:p{i} {T}s infinite"') for i, sx in enumerate(SLOTS))}
<g class="hd"><rect x="-12" y="14" width="24" height="16" rx="3" fill="#cbd5e1"/><rect x="-2" y="30" width="4" height="20" fill="#94a3b8"/>{chip(0, 50, 'class="cr"')}</g>
{fins}
<g transform="translate(860 50)"><circle r="38" fill="#0b1120" stroke="#334155" stroke-width="3"/><g class="fan">{blades}</g><circle r="8" fill="#1e293b"/></g>
{airlines}
<rect x="{W-176}" y="60" width="140" height="6" rx="3" fill="#0f2e22"/><rect x="{W-176}" y="60" width="140" height="6" rx="3" class="bar"/>
{temps}{status}
</svg>'''
open(sys.argv[1], "w").write(svg)
