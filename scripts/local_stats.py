"""Totals-only stats for local work. Writes local-stats.json (numbers only, no names/paths).
Usage: python3 scripts/local_stats.py ~/Desktop/Projects"""
import hashlib, json, os, sys

ROOT = os.path.expanduser(sys.argv[1])
SKIP = {"node_modules", ".git", ".venv", "venv", "target", "dist", "build", "__pycache__", ".next", ".wrangler", ".claude", ".memory-index", "python_modules", "vendor", "site-packages", "pyodide-venv", ".pytest_cache", "coverage", "playwright-report"}
CODE = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".rs", ".java", ".kt", ".html", ".css", ".ino", ".sql", ".sh", ".toml"}
projects, lines, files, sessions, seen = 0, 0, 0, set(), set()

for name in sorted(os.listdir(ROOT)):
    top = os.path.join(ROOT, name)
    if not os.path.isdir(top) or name.startswith("."):
        continue
    n = 0
    for d, dirs, fs in os.walk(top):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".venv")]
        for f in fs:
            p = os.path.join(d, f)
            if f.endswith("_SESSION_SUMMARY.md"):
                sessions.add(hashlib.md5(open(p, "rb").read()).hexdigest())  # dedupe copies across repos
            if os.path.splitext(f)[1] in CODE and not f.endswith(".min.js") and os.path.getsize(p) < 1_000_000:
                try:
                    data = open(p, "rb").read()
                    h = hashlib.md5(data).hexdigest()
                    if h in seen:  # same file copied across project versions: count once
                        continue
                    seen.add(h); lines += data.count(b"\n"); files += 1; n += 1
                except OSError:
                    pass
    projects += n > 0
json.dump({"projects": projects, "lines": lines, "files": files, "sessions": len(sessions)}, open("local-stats.json", "w"))
print(projects, lines, files, len(sessions))
