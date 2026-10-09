# Profile decor

Everything decorative on the GitHub profile lives here. Animated SVGs only; GitHub plays CSS/SMIL animation inside `<img>`.

| File | Used in README | Made by |
| --- | --- | --- |
| `banner.svg` | top banner (circuit board + floating chip) | `python3 generators/banner.py banner.svg` |
| `footer.svg` | bottom banner (pick-and-place → heat → fan cools) | `python3 generators/footer.py footer.svg` |

Edit a generator, re-run it from this folder, open the SVG in a browser to check, then commit.

`alternatives/` keeps the designs that were tried but not used:
- `synthwave-banner.svg` (+ `.py`) — synthwave grid / sun / rotating icosahedron banner
- `footers/` — footer options A–M; open `footers/index.html` to see them all side by side

The stats card (`../stats.svg`) is not here: it is rebuilt hourly by `.github/workflows/stats.yml`.
