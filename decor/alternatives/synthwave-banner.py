import math, random, sys
W, H = 1200, 300
HZ, VX = 190, 960          # horizon y, vanishing x
random.seed(7)
f = lambda v: f"{v:.1f}"

# --- scrolling floor: horizontal lines at perspective depths, shifted one spacing per loop
def floor_frame(t, n=14):
    d = []
    for i in range(n):
        z = (i + 1 - t) * 0.6 + 0.25          # depth
        y = HZ + 38 / z
        if y > H + 2: continue
        d.append(f"M0 {f(y)}H{W}")
    return "".join(d)
floor_vals = ";".join(floor_frame(k / 24) for k in range(25))
verts = "".join(f"M{VX} {HZ}L{f(VX + (x - VX) * 1)} {H}" for x in range(-3000, 4200, 150))

# --- rotating icosahedron
p = (1 + 5 ** .5) / 2
V = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0), (0, -1, p), (0, 1, p), (0, -1, -p), (0, 1, -p), (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
E = [(i, j) for i in range(12) for j in range(i + 1, 12)
     if abs(sum((V[i][k] - V[j][k]) ** 2 for k in range(3)) - 4) < .01]
def ico_frame(a, cx=VX, cy=112, s=34):
    pts = []
    for x, y, z in V:
        x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        t = .45; y, z = y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t)
        k = 6 / (6 + z)
        pts.append((cx + x * s * k, cy + y * s * k))
    return "".join(f"M{f(pts[i][0])} {f(pts[i][1])}L{f(pts[j][0])} {f(pts[j][1])}" for i, j in E)
NF = 90
ico_vals = ";".join(ico_frame(2 * math.pi / 5 * k / NF) for k in range(NF + 1))  # 72° = symmetric loop

stars = "".join(
    f'<circle cx="{random.randint(0, W)}" cy="{random.randint(6, HZ - 10)}" r="{random.choice([.8, 1, 1.3])}" '
    f'class="st" style="animation-delay:-{random.random() * 4:.2f}s"/>' for _ in range(70))
sun_bars = "".join(f'<rect x="{VX - 90}" y="{HZ - 46 + i * 10}" width="180" height="{1.5 + i * 1.3:.1f}" fill="#0b0624"/>' for i in range(5))

roles = ["SOFTWARE", "AUTOMATION", "AI TOOLS", "HARDWARE"]
role_svg = "".join(f'<text x="64" y="172" class="role r{i}">&gt; {r}<tspan class="cur">_</tspan></text>' for i, r in enumerate(roles))
role_css = "".join(f".r{i}{{animation-delay:{i * 2}s}}" for i in range(4))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.st{{fill:#fff;animation:tw 4s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.name{{font:800 66px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;letter-spacing:-1px}}
.sub{{font:600 15px ui-monospace,Menlo,Consolas,monospace;letter-spacing:5px;fill:#a5b4fc}}
.role{{font:700 17px ui-monospace,Menlo,Consolas,monospace;fill:#5eead4;opacity:0;animation:rl 8s infinite}}
{role_css}
@keyframes rl{{0%{{opacity:0;transform:translateY(6px)}}2%,21%{{opacity:1;transform:none}}23.5%,100%{{opacity:0}}}}
.cur{{animation:bl 1s steps(1) infinite}} @keyframes bl{{50%{{opacity:0}}}}
.glow{{animation:gl 3s ease-in-out infinite}} @keyframes gl{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
</style>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05031a"/><stop offset=".75" stop-color="#1e0b4b"/><stop offset="1" stop-color="#3b0f5c"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fde047"/><stop offset=".55" stop-color="#fb7185"/><stop offset="1" stop-color="#c026d3"/></linearGradient>
<linearGradient id="nm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f0abfc"/><stop offset=".5" stop-color="#c4b5fd"/><stop offset="1" stop-color="#67e8f9"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="fm"><rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#fade)"/></mask>
<filter id="neon" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="18"/></filter>
<clipPath id="sunc"><circle cx="{VX}" cy="{HZ}" r="84"/></clipPath>
<clipPath id="above"><rect width="{W}" height="{HZ}"/></clipPath>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars}
<g clip-path="url(#above)">
  <circle cx="{VX}" cy="{HZ}" r="120" fill="#e879f9" opacity=".35" filter="url(#soft)" class="glow"/>
  <circle cx="{VX}" cy="{HZ}" r="84" fill="url(#sun)"/><g clip-path="url(#sunc)">{sun_bars}</g>
</g>
<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="#0b0624"/>
<g mask="url(#fm)" stroke="#e879f9" stroke-width="1.4" fill="none" filter="url(#neon)">
  <path d="{verts}"/>
  <path><animate attributeName="d" dur="1.6s" repeatCount="indefinite" values="{floor_vals}"/></path>
</g>
<line x1="0" y1="{HZ}" x2="{W}" y2="{HZ}" stroke="#f0abfc" stroke-width="2" filter="url(#neon)"/>
<path fill="none" stroke="#67e8f9" stroke-width="1.8" stroke-linecap="round" filter="url(#neon)">
  <animate attributeName="d" dur="9s" repeatCount="indefinite" values="{ico_vals}"/>
  <animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="4s" repeatCount="indefinite"/>
</path>
<text x="60" y="104" class="name" fill="url(#nm)" filter="url(#neon)">Hrishank Soni</text>
<text x="64" y="136" class="sub">BUILDER · DEVELOPER · MAKER</text>
{role_svg}
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="#a78bfa" stroke-opacity=".35" stroke-width="2"/>
</g>
</svg>'''
open(sys.argv[1], "w").write(svg)
