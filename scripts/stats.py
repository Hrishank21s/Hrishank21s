"""Totals-only stats card (public + private). Never emits repo names or content."""
import datetime as dt, json, os, urllib.parse, urllib.request

USER = "Hrishank21s"
TOKEN = os.environ["STATS_TOKEN"]

def gql(q):
    r = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                               {"Authorization": f"bearer {TOKEN}"})
    d = json.load(urllib.request.urlopen(r))
    assert "errors" not in d, d["errors"]
    return d["data"]["user"]

u = gql(f'{{user(login:"{USER}"){{createdAt followers{{totalCount}} repositories(first:100,ownerAffiliations:OWNER){{totalCount nodes{{stargazerCount}}}}}}}}')
tot = dict(commits=0, prs=0, issues=0, reviews=0)
for y in range(int(u["createdAt"][:4]), dt.date.today().year + 1):
    c = gql(f'{{user(login:"{USER}"){{contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z"){{'
            'totalCommitContributions restrictedContributionsCount totalPullRequestContributions '
            'totalIssueContributions totalPullRequestReviewContributions}}}')["contributionsCollection"]
    tot["commits"] += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    tot["prs"] += c["totalPullRequestContributions"]
    tot["issues"] += c["totalIssueContributions"]
    tot["reviews"] += c["totalPullRequestReviewContributions"]

def count(q):
    r = urllib.request.Request("https://api.github.com/search/issues?per_page=1&q=" + urllib.parse.quote(q),
                               headers={"Authorization": f"bearer {TOKEN}"})
    return json.load(urllib.request.urlopen(r))["total_count"]

# Search sees private repos the token can read; GraphQL folds private issues/PRs/reviews into
# restrictedContributionsCount, so subtract them out to keep "commits" a commit count.
iss, prs, rev = (count(f"author:{USER} type:issue"), count(f"author:{USER} type:pr"), count(f"reviewed-by:{USER} type:pr -author:{USER}"))
print("search counts (issues, prs, reviews):", iss, prs, rev)
priv_noncommit = max(0, (iss - tot["issues"]) + (prs - tot["prs"]) + (rev - tot["reviews"]))
tot["commits"] -= min(priv_noncommit, tot["commits"])
yr = gql(f'{{user(login:"{USER}"){{contributionsCollection{{contributionCalendar{{totalContributions}}}}}}}}')["contributionsCollection"]["contributionCalendar"]["totalContributions"]
rows = [("Total Commits (public + private)", tot["commits"]), ("Pull Requests", max(prs, tot["prs"])),
        ("Issues", max(iss, tot["issues"])), ("Code Reviews", max(rev, tot["reviews"])),
        ("Contributions (last 12 months)", yr),
        ("Repositories", u["repositories"]["totalCount"]),
        ("Stars Earned", sum(n["stargazerCount"] for n in u["repositories"]["nodes"]))]
if os.path.exists("local-stats.json"):  # written by scripts/local_stats.py on the author's Mac; numbers only
    L = json.load(open("local-stats.json"))
    rows += [("Local Projects", L["projects"]), ("Local Lines of Code (unique)", f'{L["lines"]:,}'),
             ("Work Sessions Logged", L["sessions"])]
half = (len(rows) + 1) // 2
def col(rs, x):
    return "".join(f'<text x="{x}" y="{65+i*26}" class="l">{k}</text><text x="{x+270}" y="{65+i*26}" class="v" text-anchor="end">{v}</text>'
                   for i, (k, v) in enumerate(rs))
body = col(rows[:half], 25) + col(rows[half:], 325)
open("stats.svg", "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="{85+half*26}" role="img" aria-label="GitHub stats">
<style>.t{{font:600 18px 'Segoe UI',Ubuntu,sans-serif;fill:#70a5fd}}.l{{font:400 14px 'Segoe UI',Ubuntu,sans-serif;fill:#a9b1d6}}.v{{font:600 14px 'Segoe UI',Ubuntu,sans-serif;fill:#9ece6a}}</style>
<rect width="100%" height="100%" rx="6" fill="#1a1b27"/><text x="25" y="35" class="t">{USER}'s GitHub Stats</text>{body}</svg>''')
