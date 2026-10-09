import math, random, sys, os
out = sys.argv[1]; random.seed(3)
W, H = 1200, 100
MONO = "ui-monospace,Menlo,Consolas,monospace"
def svg(body, style="", defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>.m{{font:600 12px {MONO};letter-spacing:2px;fill:#86efac}}.g{{fill:#b8873b}}{style}</style>
<defs><pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse"><path d="M40 0H0V20" fill="none" stroke="#0f3d2c" stroke-width="1"/></pattern>
<filter id="n" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>{defs}</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="#03140e" stroke="#b8873b" stroke-opacity=".4" stroke-width="2"/>
{body}</svg>'''

# A — oscilloscope
P = 160
wave = "M" + " L".join(f"{x} {50 + 22 * math.sin(2 * math.pi * x / P) * (0.6 + 0.4 * math.sin(2 * math.pi * x / (P * 4))):.1f}" for x in range(0, W + 4 * P, 4))
A = svg(f'''<clipPath id="scr"><rect x="16" y="12" width="{W-32}" height="76" rx="8"/></clipPath>
<g clip-path="url(#scr)"><rect width="{W}" height="{H}" fill="url(#grid)"/>
<line x1="0" y1="50" x2="{W}" y2="50" stroke="#14532d"/>
<path d="{wave}" fill="none" stroke="#4ade80" stroke-width="2" filter="url(#n)"><animateTransform attributeName="transform" type="translate" from="0 0" to="-{4*P} 0" dur="4s" repeatCount="indefinite"/></path></g>
<rect x="24" y="16" width="130" height="20" rx="4" fill="#03140e"/><rect x="{W-310}" y="66" width="286" height="20" rx="4" fill="#03140e"/><text x="32" y="30" class="m">CH1 · 5V/div</text><text x="{W-32}" y="80" text-anchor="end" class="m">SIGNAL OK · LET’S BUILD SOMETHING</text>''')

# B — component chain: pulse travels, LED lights as it passes
T, X0, X1 = 3.0, 40, W - 40
f = lambda x: (x - X0) / (X1 - X0) * 100
led_x = 700
B = svg(f'''<line x1="{X0}" y1="50" x2="{X1}" y2="50" stroke="#134e3a" stroke-width="3"/>
<line x1="{X0}" y1="50" x2="{X1}" y2="50" stroke="#4ade80" stroke-width="3" stroke-linecap="round" class="p"/>
<circle cx="{X0}" cy="50" r="5" fill="#03120d" stroke="#b8873b" stroke-width="2.5"/><circle cx="{X1}" cy="50" r="5" fill="#03120d" stroke="#b8873b" stroke-width="2.5"/>
<g transform="translate(240 50)"><rect x="-30" y="-10" width="60" height="20" rx="9" fill="#d6c3a0"/><rect x="-18" y="-10" width="5" height="20" fill="#7c2d12"/><rect x="-7" y="-10" width="5" height="20" fill="#000"/><rect x="4" y="-10" width="5" height="20" fill="#dc2626"/><rect x="18" y="-10" width="4" height="20" fill="#b8873b"/></g>
<g transform="translate(460 50)" stroke="#cbd5e1" stroke-width="4"><line x1="-6" y1="-18" x2="-6" y2="18"/><line x1="6" y1="-18" x2="6" y2="18"/></g><rect x="455" y="40" width="10" height="20" fill="#03140e"/>
<g transform="translate({led_x} 50)"><circle r="11" class="led"/><circle r="11" fill="none" stroke="#86efac" stroke-opacity=".5"/></g>
<g transform="translate(940 50)"><rect x="-40" y="-22" width="80" height="44" rx="4" fill="#111827" stroke="#334155"/>{"".join(f'<rect x="{-32+i*13}" y="-28" width="5" height="6" fill="#cbd5e1"/><rect x="{-32+i*13}" y="22" width="5" height="6" fill="#cbd5e1"/>' for i in range(6))}<text y="5" text-anchor="middle" class="m" style="font-size:11px">HS-21</text></g>
<text x="{W/2}" y="88" text-anchor="middle" class="m" style="font-size:11px;fill:#4b7a63">R1 · C1 · D1 · U1 — THANKS FOR VISITING</text>''',
style=f'''.p{{stroke-dasharray:40 2000;stroke-dashoffset:40;animation:r {T}s linear infinite;filter:drop-shadow(0 0 4px #4ade80)}}@keyframes r{{to{{stroke-dashoffset:-1160}}}}
.led{{fill:#14532d;animation:l {T}s linear infinite}}@keyframes l{{0%,{f(led_x)-1:.0f}%{{fill:#14532d}}{f(led_x):.0f}%{{fill:#4ade80;filter:drop-shadow(0 0 10px #4ade80)}}{f(led_x)+20:.0f}%,100%{{fill:#14532d}}}}''')

# C — logic analyzer, 3 channels scrolling
def sq(bits, y, w=40, h=14):
    d, lv = f"M0 {y + h}", 0
    for i, b in enumerate(bits * 2):
        if b != lv: d += f"V{y + (0 if b else h)}"; lv = b
        d += f"H{(i + 1) * w}"
    return d
n = 30
chans = [("CLK", [i % 2 for i in range(n)]), ("TX", [random.randint(0, 1) for _ in range(n)]), ("RX", [random.randint(0, 1) for _ in range(n)])]
labels = "".join(f'<text x="28" y="{30 + k*22}" class="m">{nm}</text>' for k, (nm, _) in enumerate(chans))
rows = "".join(f'<path d="{sq(b, 18 + k*22)}" transform="translate(90 0)" fill="none" stroke="{c}" stroke-width="2"><animateTransform attributeName="transform" type="translate" from="90 0" to="{90 - n*40} 0" dur="12s" repeatCount="indefinite"/></path>'
               for k, ((nm, b), c) in enumerate(zip(chans, ["#4ade80", "#67e8f9", "#fbbf24"])))
C = svg(f'''<clipPath id="la"><rect x="80" y="8" width="{W-100}" height="84"/></clipPath>
<line x1="80" y1="8" x2="80" y2="92" stroke="#134e3a"/>{labels}<g clip-path="url(#la)">{rows}</g>
<text x="{W-28}" y="90" text-anchor="end" class="m" style="font-size:11px;fill:#4b7a63">TRIGGER: VISITOR DETECTED</text>''')

# D — terminal sign-off with typed command
cmd = "./goodbye --build-something"
cw = 7.8; steps = len(cmd)
vals = ";".join(f"{i*cw:.1f}" for i in range(steps + 1)) + ";" + f"{steps*cw:.1f}"
kt = ";".join(f"{i/steps*0.5:.3f}" for i in range(steps + 1)) + ";1"
D_ = svg(f'''<clipPath id="ty"><rect x="172" y="20" height="30" width="0"><animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="6s" calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>
<circle cx="30" cy="22" r="5" fill="#f87171"/><circle cx="48" cy="22" r="5" fill="#fbbf24"/><circle cx="66" cy="22" r="5" fill="#4ade80"/>
<text x="30" y="44" class="m" style="font-size:13px;letter-spacing:0"><tspan fill="#4ade80">hrishank@board</tspan><tspan fill="#cbd5e1">:</tspan><tspan fill="#67e8f9">~</tspan><tspan fill="#cbd5e1">$</tspan></text>
<text x="172" y="44" clip-path="url(#ty)" style="font:600 13px {MONO};fill:#ecfdf5">{cmd}</text>
<text x="30" y="72" class="m o" style="font-size:13px;letter-spacing:0;fill:#86efac">→ thanks for visiting · hrishank21s.github.io</text>''',
style=".o{animation:o 6s steps(1) infinite}@keyframes o{0%{opacity:0}55%,100%{opacity:1}}")

names = {"A-oscilloscope": A, "B-components": B, "C-logic-analyzer": C, "D-terminal": D_}
# E — seven-segment display alternating HELLO / bUILd
SEG = {"H":"bcefg","E":"adefg","L":"def","O":"abcdef","b":"cdefg","U":"bcdef","I":"bc","d":"bcdeg"}
def seg7(ch, x, y, on):
    w, h, t = 26, 24, 5
    geo = {"a":(x+t,y,w,t),"g":(x+t,y+h,w,t),"d":(x+t,y+2*h,w,t),"f":(x,y+t,t,h-t),"b":(x+w+t,y+t,t,h-t),"e":(x,y+h+t,t,h-t),"c":(x+w+t,y+h+t,t,h-t)}
    return "".join(f'<rect x="{a}" y="{b}" width="{c}" height="{d}" rx="2" class="{"on" if k in SEG.get(ch,"") and on else "off"}"/>' for k,(a,b,c,d) in geo.items())
def word(wd, cls):
    x0 = W/2 - len(wd)*48/2
    return f'<g class="{cls}">' + "".join(seg7(c, x0 + i*48, 22, True) for i, c in enumerate(wd)) + "</g>"
ghost = "".join(seg7("8", W/2 - 5*48/2 + i*48, 22, False) for i in range(5))
E = svg(f'{ghost}{word("HELLO","w1")}{word("bUILd","w2")}<text x="28" y="56" class="m g" style="fill:#b8873b">U3 · DISPLAY</text><text x="{W-28}" y="56" text-anchor="end" class="m">THANKS FOR VISITING</text>',
style=".on{fill:#4ade80;filter:drop-shadow(0 0 4px #4ade80)}.off{fill:#0f2e22}.w1{animation:a 4s steps(1) infinite}.w2{animation:a 4s steps(1) -2s infinite}@keyframes a{0%{opacity:1}50%,100%{opacity:0}}")

# F — battery cells charging
cells = "".join(f'<rect x="{430+i*36}" y="34" width="30" height="32" rx="3" class="c" style="animation-delay:{i*.35:.2f}s"/>' for i in range(10))
F = svg(f'<rect x="422" y="26" width="364" height="48" rx="8" fill="none" stroke="#86efac" stroke-width="2.5"/><rect x="788" y="40" width="10" height="20" rx="2" fill="#86efac"/>{cells}<text x="28" y="56" class="m">⚡ RECHARGED</text><text x="{W-28}" y="56" text-anchor="end" class="m">SEE YOU NEXT TIME</text>',
style=".c{fill:#0f2e22;animation:c 4.5s steps(1) infinite}@keyframes c{0%{fill:#0f2e22}10%,85%{fill:#4ade80;filter:drop-shadow(0 0 3px #4ade80)}86%,100%{fill:#0f2e22}}")

# G — scrolling 5x7 dot-matrix
FONT = {"T":["11111","00100","00100","00100","00100","00100","00100"],"H":["10001","10001","10001","11111","10001","10001","10001"],
"A":["01110","10001","10001","11111","10001","10001","10001"],"N":["10001","11001","10101","10011","10001","10001","10001"],
"K":["10001","10010","10100","11000","10100","10010","10001"],"S":["01111","10000","10000","01110","00001","00001","11110"],
"F":["11111","10000","10000","11110","10000","10000","10000"],"O":["01110","10001","10001","10001","10001","10001","01110"],
"R":["11110","10001","10001","11110","10100","10010","10001"],"V":["10001","10001","10001","10001","10001","01010","00100"],
"I":["01110","00100","00100","00100","00100","00100","01110"],"G":["01110","10001","10000","10111","10001","10001","01110"],
"B":["11110","10001","10001","11110","10001","10001","11110"],"U":["10001","10001","10001","10001","10001","10001","01110"],
"E":["11111","10000","10000","11110","10000","10000","11111"],"L":["10000","10000","10000","10000","10000","10000","11111"],"D":["11110","10001","10001","10001","10001","10001","11110"],
" ":["00000"]*7,"*":["00000","00000","00100","01110","00100","00000","00000"]}
msg = "THANKS FOR VISITING * LETS BUILD * "
P_ = 9; col = 0; dots = []
for ch in msg:
    g = FONT[ch]
    for r in range(7):
        for c in range(5):
            if g[r][c] == "1": dots.append((col + c, r))
    col += 6
span = col * P_
dot_svg = "".join(f'<circle cx="{x*P_}" cy="{y*P_}" r="3.4"/>' for x, y in dots)
G = svg(f'''<pattern id="dm" width="{P_}" height="{P_}" patternUnits="userSpaceOnUse" x="20" y="17.5"><circle cx="0" cy="0" r="3.4" fill="#0f2e22"/></pattern>
<clipPath id="dc"><rect x="16" y="12" width="{W-32}" height="76" rx="8"/></clipPath>
<g clip-path="url(#dc)"><rect x="16" y="12" width="{W-32}" height="76" fill="url(#dm)" transform="translate(4.5 4.5)"/>
<g fill="#4ade80" filter="url(#n)" transform="translate(20 22)"><g>{dot_svg}<g transform="translate({span} 0)">{dot_svg}</g>
<animateTransform attributeName="transform" type="translate" from="0 0" to="-{span} 0" dur="{span/90:.1f}s" repeatCount="indefinite"/></g></g></g>''')

# H — breadboard with jumpers and blinking LED
holes = "".join(f'<rect x="{x}" y="{y}" width="5" height="5" rx="1" fill="#0b2a1f"/>' for x in range(30, W-30, 14) for y in (22, 34, 62, 74))
jump = [(100, 34, 330, 62, "#f87171"), (260, 22, 520, 74, "#67e8f9"), (600, 34, 760, 62, "#fbbf24"), (820, 22, 1100, 74, "#4ade80")]
jw = "".join(f'<path d="M{a+2.5} {b+2.5}C{a+2.5} {b-30},{c+2.5} {d+30},{c+2.5} {d+2.5}" fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" opacity=".9"/>' for a, b, c, d, col in jump)
H_ = svg(f'''<rect x="16" y="46" width="{W-32}" height="8" fill="#062a1d"/>{holes}{jw}
<g transform="translate(560 48)"><path d="M-8 6V-6a8 8 0 0 1 16 0V6Z" class="led"/><line x1="-4" y1="6" x2="-4" y2="16" stroke="#cbd5e1" stroke-width="2"/><line x1="4" y1="6" x2="4" y2="14" stroke="#cbd5e1" stroke-width="2"/></g>
<text x="{W/2}" y="94" text-anchor="middle" class="m" style="font-size:10px;fill:#4b7a63">PROTOTYPED WITH ♥ · HRISHANK21S.GITHUB.IO</text>''',
style=".led{fill:#7f1d1d;animation:b 1.4s steps(1) infinite}@keyframes b{50%{fill:#f87171;filter:drop-shadow(0 0 8px #f87171)}}")

names.update({"E-seven-segment": E, "F-battery": F, "G-dot-matrix": G, "H-breadboard": H_})

# I — soldering iron
pads = list(range(300, 1000, 70)); T_I = 7
def pc(x): return (x - 200) / 840 * 88
blobs = "".join(f'<rect x="{x-10}" y="60" width="20" height="10" rx="2" fill="#b8873b"/><ellipse cx="{x}" cy="62" rx="8" ry="5" class="sb" style="animation-name:s{i}"/>' for i, x in enumerate(pads))
bk = "".join(f"@keyframes s{i}{{0%,{pc(x):.1f}%{{opacity:0}}{pc(x)+1:.1f}%,95%{{opacity:1}}100%{{opacity:0}}}}" for i, x in enumerate(pads))
I = svg(f'''<line x1="180" y1="65" x2="1040" y2="65" stroke="#134e3a" stroke-width="3"/>{blobs}
<g class="iron"><g transform="translate(0 60) rotate(28)"><polygon points="0,0 -4,-12 4,-12" fill="#e2e8f0"/><rect x="-4" y="-26" width="8" height="14" fill="#94a3b8"/><rect x="-7" y="-56" width="14" height="30" rx="5" fill="#2563eb"/></g>
<circle cx="4" cy="48" r="4" class="smk"/><circle cx="-2" cy="44" r="3" class="smk" style="animation-delay:-.3s"/></g>
<text x="28" y="30" class="m" style="fill:#b8873b">J2 · HAND SOLDERED</text><text x="{W-28}" y="30" text-anchor="end" class="m">MADE WITH CARE</text>''',
style=f".sb{{fill:#e2e8f0;filter:drop-shadow(0 0 3px #fff);animation-duration:{T_I}s;animation-iteration-count:infinite}}{bk}"
f".iron{{animation:iw {T_I}s linear infinite}}@keyframes iw{{0%{{transform:translateX(200px)}}88%{{transform:translateX(1040px)}}95%,100%{{transform:translateX(1040px);opacity:0}}}}"
f".smk{{fill:#cbd5e1;animation:sm .8s ease-out infinite}}@keyframes sm{{0%{{opacity:.6;transform:translate(0,0)}}100%{{opacity:0;transform:translate(6px,-30px)}}}}")

# J — morse code BYE
MORSE = {"B": "-...", "Y": "-.--", "E": "."}
seq = []; t = 0; marks = []; x = 420
for li, ch in enumerate("BYE"):
    for si, sym in enumerate(MORSE[ch]):
        u = 3 if sym == "-" else 1
        seq.append((t, t + u)); marks.append((x, sym)); t += u + 1; x += 40 if sym == "-" else 26
    t += 2; x += 30
total = t + 4; pct = lambda v: v / total * 100
def kf(name, a, b): return f"@keyframes {name}{{0%,{pct(a)-.01:.2f}%{{opacity:.15}}{pct(a):.2f}%,{pct(b):.2f}%{{opacity:1}}{pct(b)+.01:.2f}%,100%{{opacity:.15}}}}"
led_kf = "@keyframes led{" + "".join(f"{pct(a):.2f}%{{fill:#4ade80}}{pct(b):.2f}%{{fill:#14532d}}" for a, b in seq) + "}"
mk = "".join((f'<rect x="{mx}" y="44" width="30" height="12" rx="6"' if s == "-" else f'<circle cx="{mx+6}" cy="50" r="6"') + f' fill="#4ade80" style="animation:k{i} {total*.2:.1f}s infinite"/>' for i, (mx, s) in enumerate(marks))
J = svg(f'''<circle cx="320" cy="50" r="14" class="ml"/><circle cx="320" cy="50" r="14" fill="none" stroke="#86efac" stroke-opacity=".5"/>{mk}
<text x="28" y="56" class="m">TX · MORSE</text><text x="{W-28}" y="56" text-anchor="end" class="m">-... -.-- .  =  BYE</text>''',
style="".join(kf(f"k{i}", a, b) for i, (a, b) in enumerate(seq)) + led_kf + f".ml{{fill:#14532d;animation:led {total*.2:.1f}s steps(1) infinite;filter:drop-shadow(0 0 6px #4ade80)}}")

# K — pick-and-place
slots = [520, 680, 840, 1000]; FX = 150; T_K = 10; seg = 100 / len(slots)
hk = "@keyframes hd{"; ck = []
for i, sx in enumerate(slots):
    a = i * seg
    hk += f"{a:.1f}%{{transform:translate({FX}px,0)}}{a+seg*.15:.1f}%{{transform:translate({FX}px,0)}}{a+seg*.55:.1f}%{{transform:translate({sx}px,0)}}{a+seg*.65:.1f}%{{transform:translate({sx}px,14px)}}{a+seg*.75:.1f}%{{transform:translate({sx}px,0)}}"
    ck.append(f"@keyframes p{i}{{0%,{a+seg*.65:.1f}%{{opacity:0}}{a+seg*.66:.1f}%,97%{{opacity:1}}100%{{opacity:0}}}}")
hk += f"100%{{transform:translate({FX}px,0)}}}}"
carry = "@keyframes cr{" + "".join(f"{i*seg:.1f}%{{opacity:0}}{i*seg+seg*.15:.1f}%{{opacity:1}}{i*seg+seg*.65:.1f}%{{opacity:1}}{i*seg+seg*.66:.1f}%{{opacity:0}}" for i in range(len(slots))) + "100%{opacity:0}}"
chip = lambda x, y, cls="", st="": f'<g class="{cls}" style="{st}"><rect x="{x-14}" y="{y}" width="28" height="16" rx="2" fill="#111827" stroke="#334155"/><rect x="{x-10}" y="{y+5}" width="6" height="6" fill="#4ade80" opacity=".6"/></g>'
K = svg(f'''<line x1="40" y1="20" x2="{W-40}" y2="20" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
<g><circle cx="{FX}" cy="62" r="24" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="6 6"><animateTransform attributeName="transform" type="rotate" from="0 {FX} 62" to="-360 {FX} 62" dur="6s" repeatCount="indefinite"/></circle><circle cx="{FX}" cy="62" r="6" fill="#94a3b8"/></g>
{"".join(f'<rect x="{sx-18}" y="74" width="36" height="6" fill="#b8873b" opacity=".6"/>' for sx in slots)}
{"".join(chip(sx, 58, "", f"animation:p{i} {T_K}s infinite") for i, sx in enumerate(slots))}
<g class="head"><rect x="-12" y="14" width="24" height="16" rx="3" fill="#cbd5e1"/><rect x="-2" y="30" width="4" height="20" fill="#94a3b8"/>{chip(0, 50, "car")}</g>
<text x="300" y="56" class="m" style="fill:#4b7a63">PNP · ASSEMBLING</text>''',
style=hk + carry + "".join(ck) + f".head{{animation:hd {T_K}s ease-in-out infinite}}.car{{animation:cr {T_K}s infinite}}")

# L — cooling fan
blades = "".join(f'<path d="M0 0C10 -8 26 -6 30 4C20 4 10 6 0 0Z" fill="#475569" transform="rotate({i*360/7:.0f})"/>' for i in range(7))
fins = "".join(f'<rect x="{80+i*10}" y="18" width="5" height="64" fill="#64748b"/>' for i in range(10))
temps = [62, 55, 48, 42, 38, 42, 48, 55]
tv = "".join(f'<text x="{W-28}" y="58" text-anchor="end" class="m tp" style="font-size:22px;animation-delay:{i*.75}s">{t}°C</text>' for i, t in enumerate(temps))
L = svg(f'''{fins}<g transform="translate(330 50)"><circle r="36" fill="#0b1120" stroke="#334155" stroke-width="3"/>
<g>{blades}<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur=".6s" repeatCount="indefinite"/></g><circle r="8" fill="#1e293b"/></g>
<text x="{W/2}" y="56" text-anchor="middle" class="m">COOLING DOWN · SEE YOU NEXT TIME</text>{tv}''',
style=".tp{opacity:0;animation:tp 6s steps(1) infinite}@keyframes tp{0%{opacity:1}12.5%,100%{opacity:0}}")

# M — equalizer
bars = "".join(f'<rect x="{40+i*28}" y="16" width="18" height="68" rx="3" class="eq" style="animation-duration:{random.uniform(.5,1.2):.2f}s;animation-delay:-{random.random():.2f}s"/>' for i in range(40) if not 420 < 40+i*28 < 780)
M = svg(f'''<defs><linearGradient id="eg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#4ade80"/><stop offset=".7" stop-color="#fbbf24"/><stop offset="1" stop-color="#f87171"/></linearGradient></defs>{bars}
<rect x="{W/2-150}" y="38" width="300" height="24" rx="6" fill="#03140e" stroke="#134e3a"/><text x="{W/2}" y="55" text-anchor="middle" class="m">♪ DAC OUT · THANKS FOR LISTENING</text>''',
style=".eq{fill:url(#eg);transform-box:fill-box;transform-origin:bottom;animation:eq ease-in-out infinite alternate}@keyframes eq{0%{transform:scaleY(.15)}100%{transform:scaleY(1)}}")

names.update({"I-soldering": I, "J-morse": J, "K-pick-and-place": K, "L-cooling-fan": L, "M-equalizer": M})

# N — K + L: machine places chips, board heats up, fan cools it
slots_n = [330, 460, 590]; FXn = 130; T_N = 9; sg = 88 / len(slots_n)
hkn = "@keyframes hn{"; ckn = []; placed = []
for i, sx in enumerate(slots_n):
    a = i * sg
    hkn += f"{a:.1f}%{{transform:translate({FXn}px,0)}}{a+sg*.15:.1f}%{{transform:translate({FXn}px,0)}}{a+sg*.55:.1f}%{{transform:translate({sx}px,0)}}{a+sg*.65:.1f}%{{transform:translate({sx}px,14px)}}{a+sg*.75:.1f}%{{transform:translate({sx}px,0)}}"
    p = a + sg * .65; placed.append(p)
    ckn.append(f"@keyframes q{i}{{0%,{p:.1f}%{{opacity:0}}{p+.1:.1f}%,97%{{opacity:1}}100%{{opacity:0}}}}")
hkn += f"88%,100%{{transform:translate({FXn}px,0)}}}}"
crn = "@keyframes cn{" + "".join(f"{i*sg:.1f}%{{opacity:0}}{i*sg+sg*.15:.1f}%{{opacity:1}}{placed[i]:.1f}%{{opacity:1}}{placed[i]+.1:.1f}%{{opacity:0}}" for i in range(3)) + "100%{opacity:0}}"
bounds = [0] + placed + [90, 100]; tvals = [36, 44, 53, 61, 40]
tk = ""; tt = ""
for i, v in enumerate(tvals):
    a, b = bounds[i], bounds[i + 1]
    tk += f"@keyframes t{i}{{0%,{max(a-.01,0):.2f}%{{opacity:0}}{a:.2f}%,{b-.01:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
    col = "#f87171" if v > 55 else "#fbbf24" if v > 45 else "#86efac"
    tt += f'<text x="{W-28}" y="58" text-anchor="end" class="m" style="font-size:22px;fill:{col};opacity:0;animation:t{i} {T_N}s infinite">{v}°C</text>'
glow = "".join(f'<rect x="{sx-20}" y="52" width="40" height="28" rx="4" fill="#f97316" opacity="0" style="filter:blur(6px);animation:g {T_N}s infinite"/>' for sx in slots_n)
bl = "".join(f'<path d="M0 0C10 -8 26 -6 30 4C20 4 10 6 0 0Z" fill="#475569" transform="rotate({i*360/7:.0f})"/>' for i in range(7))
fn = "".join(f'<rect x="{700+i*10}" y="18" width="5" height="64" fill="#64748b"/>' for i in range(9))
N = svg(f'''<line x1="40" y1="20" x2="650" y2="20" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
<circle cx="{FXn}" cy="62" r="24" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="6 6"><animateTransform attributeName="transform" type="rotate" from="0 {FXn} 62" to="-360 {FXn} 62" dur="6s" repeatCount="indefinite"/></circle><circle cx="{FXn}" cy="62" r="6" fill="#94a3b8"/>
{glow}{"".join(f'<rect x="{sx-18}" y="74" width="36" height="6" fill="#b8873b" opacity=".6"/>' for sx in slots_n)}
{"".join(chip(sx, 58, "", f"animation:q{i} {T_N}s infinite") for i, sx in enumerate(slots_n))}
<g class="hn"><rect x="-12" y="14" width="24" height="16" rx="3" fill="#cbd5e1"/><rect x="-2" y="30" width="4" height="20" fill="#94a3b8"/>{chip(0, 50, "cn")}</g>
<line x1="610" y1="66" x2="700" y2="66" stroke="#134e3a" stroke-width="3"/>{fn}
<g transform="translate(870 50)"><circle r="36" fill="#0b1120" stroke="#334155" stroke-width="3"/><g>{bl}<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur=".5s" repeatCount="indefinite"/></g><circle r="8" fill="#1e293b"/></g>
{tt}<text x="{W-28}" y="84" text-anchor="end" class="m" style="font-size:10px;fill:#4b7a63">BUILT · COOLED · SHIPPED</text>''',
style=hkn + crn + "".join(ckn) + tk + f".hn{{animation:hn {T_N}s ease-in-out infinite}}.cn{{animation:cn {T_N}s infinite}}"
      f"@keyframes g{{0%,{placed[2]:.1f}%{{opacity:0}}{placed[2]+3:.1f}%,88%{{opacity:.35}}95%,100%{{opacity:0}}}}")
names["N-assemble-and-cool"] = N
open(f"{out}/kl.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>K + L + combo</title>
<style>body{{background:#0d1117;color:#e6edf3;font:15px -apple-system,sans-serif;max-width:1000px;margin:40px auto;padding:0 16px}}img{{width:100%;display:block;margin-bottom:36px}}h2{{font-size:15px;font-weight:600;color:#7d8590;text-transform:uppercase;letter-spacing:2px}}</style>
<h1 style="font-size:20px">K, L and the combined version</h1>
<h2>K · pick and place</h2><img src="K-pick-and-place.svg"><h2>L · cooling fan</h2><img src="L-cooling-fan.svg"><h2>N · K + L combined — assemble, heat up, cool down</h2><img src="N-assemble-and-cool.svg">''')

for k, v in names.items(): open(f"{out}/{k}.svg", "w").write(v)
cards = "".join(f'<h2>{k.replace("-", " ", 1).replace("-", " ")}</h2><img src="{k}.svg">' for k in names)
open(f"{out}/index.html", "w").write(f'''<!doctype html><meta charset="utf-8"><title>Footer options</title>
<style>body{{background:#0d1117;color:#e6edf3;font:15px -apple-system,sans-serif;max-width:1000px;margin:40px auto;padding:0 16px}}img{{width:100%;display:block;margin-bottom:36px}}h2{{font-size:15px;font-weight:600;color:#7d8590;text-transform:uppercase;letter-spacing:2px}}</style>
<h1 style="font-size:20px">Footer options — on GitHub dark background</h1>{cards}''')
