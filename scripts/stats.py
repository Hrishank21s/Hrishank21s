"""Totals-only stats card (public + private). Never emits repo names or content."""
import datetime as dt, json, os, urllib.request

USER = "Hrishank21s"
TOKEN = os.environ["STATS_TOKEN"]

def gql(q):
    r = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                               {"Authorization": f"bearer {TOKEN}"})
    d = json.load(urllib.request.urlopen(r))
    assert "errors" not in d, d["errors"]
    return d["data"]["user"]

u = gql(f'{{user(login:"{USER}"){{createdAt followers{{totalCount}} repositories(ownerAffiliations:OWNER){{totalCount nodes{{stargazerCount}}}}}}}}')
tot = dict(commits=0, prs=0, issues=0, reviews=0)
for y in range(int(u["createdAt"][:4]), dt.date.today().year + 1):
    c = gql(f'{{user(login:"{USER}"){{contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z"){{'
            'totalCommitContributions restrictedContributionsCount totalPullRequestContributions '
            'totalIssueContributions totalPullRequestReviewContributions}}}')["contributionsCollection"]
    tot["commits"] += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    tot["prs"] += c["totalPullRequestContributions"]
    tot["issues"] += c["totalIssueContributions"]
    tot["reviews"] += c["totalPullRequestReviewContributions"]

rows = [("Total Commits (public + private)", tot["commits"]), ("Pull Requests", tot["prs"]),
        ("Issues", tot["issues"]), ("Code Reviews", tot["reviews"]),
        ("Repositories", u["repositories"]["totalCount"]),
        ("Stars Earned", sum(n["stargazerCount"] for n in u["repositories"]["nodes"]))]
body = "".join(f'<text x="25" y="{65+i*26}" class="l">{k}</text><text x="395" y="{65+i*26}" class="v" text-anchor="end">{v}</text>'
               for i, (k, v) in enumerate(rows))
open("stats.svg", "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{85+len(rows)*26}" role="img" aria-label="GitHub stats">
<style>.t{{font:600 18px 'Segoe UI',Ubuntu,sans-serif;fill:#70a5fd}}.l{{font:400 14px 'Segoe UI',Ubuntu,sans-serif;fill:#a9b1d6}}.v{{font:600 14px 'Segoe UI',Ubuntu,sans-serif;fill:#9ece6a}}</style>
<rect width="100%" height="100%" rx="6" fill="#1a1b27"/><text x="25" y="35" class="t">{USER}'s GitHub Stats</text>{body}</svg>''')
