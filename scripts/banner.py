import random, sys
W, H = 1200, 300
CX, FY, CY = 960, 228, 118          # chip x, footprint y, chip y
random.seed(4)
iso = lambda cx, cy, hw: [(cx, cy - hw * .577), (cx + hw, cy), (cx, cy + hw * .577), (cx - hw, cy)]
pts = lambda P: " ".join(f"{x:.1f},{y:.1f}" for x, y in P)

# traces: start on footprint edges, run out with 45° jogs
traces = []
for i in range(9):                                   # left side
    t = (i + .5) / 9; T, L, B = iso(CX, FY, 100)[0], iso(CX, FY, 100)[3], iso(CX, FY, 100)[2]
    a, b = (T, L) if i < 5 else (L, B); t = (i + .5) / 5 if i < 5 else (i - 4.5) / 4
    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    P = [(x, y), (x - 20 - (i if i < 5 else 8 - i) * 14, y)]
    dy = -(5 - i) * 9 if i < 5 else (i - 4) * 11
    P.append((P[-1][0] - abs(dy), P[-1][1] + dy)); P.append((random.randint(-20, 640), P[-1][1]))
    traces.append(P)
for i in range(6):                                   # right side
    T, R, B = iso(CX, FY, 100)[0], iso(CX, FY, 100)[1], iso(CX, FY, 100)[2]
    a, b = (T, R) if i < 3 else (R, B); t = (i % 3 + .5) / 3
    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    dy = -(3 - i) * 10 if i < 3 else (i - 2) * 10
    o = 20 + (i if i < 3 else 5 - i) * 12
    traces.append([(x, y), (x + o, y), (x + o + abs(dy), y + dy), (W + 20, y + dy)])

tr_svg = "".join(f'<polyline points="{pts(P)}" class="tr"/>' for P in traces)
via_svg = "".join(f'<circle cx="{P[-1][0]:.1f}" cy="{P[-1][1]:.1f}" r="4" class="via"/>' for P in traces if 0 < P[-1][0] < W)
pulse_svg = "".join(
    f'<polyline points="{pts(P[::-1])}" class="pl" style="animation-duration:{random.uniform(1.8, 3.2):.2f}s;animation-delay:-{random.uniform(0, 3):.2f}s"/>'
    for P in traces)

# isometric chip
hw, dep = 78, 20
T, R, B, L = iso(0, 0, hw)
top = pts([T, R, B, L]); right = pts([R, B, (B[0], B[1] + dep), (R[0], R[1] + dep)]); left = pts([L, B, (B[0], B[1] + dep), (L[0], L[1] + dep)])
pins = ""
for k in range(1, 8):
    t = k / 8
    for (a, b), dx in (((L, B), -1), ((B, R), 1)):
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + dep
        pins += f'<path d="M{x:.1f} {y:.1f}l{dx * 5:.1f} 3v7" class="pin"/>'
ci = pts(iso(0, 0, 40))

roles = ["SOFTWARE", "AUTOMATION", "AI TOOLS", "HARDWARE"]
role_svg = "".join(f'<text x="64" y="176" class="role r{i}"><tspan fill="#4ade80">[ OK ]</tspan> init {r.lower().replace(" ", "_")}<tspan class="cur">█</tspan></text>' for i, r in enumerate(roles))
role_css = "".join(f".r{i}{{animation-delay:{i * 2}s}}" for i in range(4))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.tr{{fill:none;stroke:#134e3a;stroke-width:3;stroke-linejoin:round}}
.via{{fill:#03120d;stroke:#b8873b;stroke-width:2.5}}
.pl{{fill:none;stroke:#4ade80;stroke-width:3;stroke-linecap:round;stroke-dasharray:26 900;stroke-dashoffset:926;animation:run linear infinite}}
@keyframes run{{to{{stroke-dashoffset:0}}}}
.pin{{fill:none;stroke:#cbd5e1;stroke-width:2.5}}
.name{{font:800 64px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:#ecfdf5;letter-spacing:-1px}}
.sub{{font:600 15px ui-monospace,Menlo,Consolas,monospace;letter-spacing:5px;fill:#86efac}}
.tag{{font:600 12px ui-monospace,Menlo,Consolas,monospace;fill:#b8873b;letter-spacing:2px}}
.role{{font:600 16px ui-monospace,Menlo,Consolas,monospace;fill:#d1fae5;opacity:0;animation:rl 8s infinite}}
{role_css}
@keyframes rl{{0%{{opacity:0}}2%,21%{{opacity:1}}23.5%,100%{{opacity:0}}}}
.cur{{fill:#4ade80;animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
.core{{animation:co 2.4s ease-in-out infinite}} @keyframes co{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
.led{{animation:bl 1.3s steps(1) infinite}}
</style>
<defs>
<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="1" fill="#0f3d2c"/></pattern>
<radialGradient id="bg" cx=".8" cy=".6" r=".9"><stop offset="0" stop-color="#062a1d"/><stop offset="1" stop-color="#020b08"/></radialGradient>
<radialGradient id="beam" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#4ade80" stop-opacity=".45"/><stop offset="1" stop-color="#4ade80" stop-opacity="0"/></radialGradient>
<linearGradient id="ctop" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f2937"/><stop offset="1" stop-color="#0b1120"/></linearGradient>
<filter id="neon" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="txtfade" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".45" stop-color="#000"/><stop offset=".62" stop-color="#fff"/></linearGradient>
<mask id="tm"><rect width="{W}" height="{H}" fill="#fff"/><rect x="40" y="40" width="660" height="160" fill="#000" opacity=".92" rx="20"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)"/>
<g mask="url(#tm)">{tr_svg}<g filter="url(#neon)">{pulse_svg}</g>{via_svg}</g>
<polygon points="{pts(iso(CX, FY, 100))}" fill="#03120d" stroke="#b8873b" stroke-width="2"/>
<polygon points="{pts(iso(CX, FY, 86))}" fill="none" stroke="#b8873b" stroke-width="1" stroke-dasharray="4 5" opacity=".7"/>
<ellipse cx="{CX}" cy="{FY}" rx="90" ry="40" fill="url(#beam)" class="core"/>
<g>
  <animateTransform attributeName="transform" type="translate" values="{CX} {CY};{CX} {CY - 12};{CX} {CY}" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
  {pins}
  <polygon points="{left}" fill="#0b1120"/><polygon points="{right}" fill="#111827"/>
  <polygon points="{top}" fill="url(#ctop)" stroke="#334155" stroke-width="1"/>
  <polygon points="{ci}" fill="#4ade80" opacity=".12" class="core"/>
  <polygon points="{ci}" fill="none" stroke="#4ade80" stroke-width="1.5" class="core" filter="url(#neon)"/>
  <text transform="matrix(.866 .5 -.866 .5 0 0)" text-anchor="middle" y="5" class="tag" fill="#86efac" style="fill:#86efac;font-size:13px">HS-21</text>
  <circle cx="{-hw + 22}" cy="0" r="3" fill="#f87171" class="led" filter="url(#neon)"/>
</g>
<text x="60" y="100" class="name" style="text-shadow:0 0 18px #22c55e88">Hrishank Soni</text>
<text x="64" y="132" class="sub">BUILDER · DEVELOPER · MAKER</text>
{role_svg}
<text x="64" y="268" class="tag">REV 2026 · U1 · DESIGNED &amp; BUILT BY HAND</text>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="#b8873b" stroke-opacity=".5" stroke-width="2"/>
<circle cx="22" cy="22" r="6" class="via"/><circle cx="{W - 22}" cy="22" r="6" class="via"/><circle cx="22" cy="{H - 22}" r="6" class="via"/><circle cx="{W - 22}" cy="{H - 22}" r="6" class="via"/>
</g>
</svg>'''
open(sys.argv[1], "w").write(svg)
