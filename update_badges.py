"""Pulls public badges from Credly and rewrites the badge grid in README.md."""
import html
import json
import re
import urllib.request

CREDLY_USERNAME = "vishal-prajapati.ca00f01c"  # <-- change this (the part after credly.com/users/)
BADGE_WIDTH = 100
README = "README.md"


def fetch_badges(username):
    badges, page = [], 1
    while True:
        url = f"https://www.credly.com/users/{username}/badges.json?page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
        data = payload.get("data", [])
        if not data:
            break
        badges.extend(data)
        total_pages = payload.get("metadata", {}).get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1
    return badges


def render(badges):
    lines = ["<p>"]
    for b in badges:
        tpl = b.get("badge_template", {})
        name = html.escape(tpl.get("name", "Badge"))
        issuer = ""
        issuers = b.get("issuer", {}).get("entities", [])
        if issuers:
            issuer = " – " + html.escape(issuers[0].get("entity", {}).get("name", ""))
        img = b.get("image_url") or tpl.get("image_url")
        link = f"https://www.credly.com/badges/{b['id']}/public_url"
        lines.append(
            f'  <a href="{link}"><img src="{img}" alt="{name}" '
            f'title="{name}{issuer}" width="{BADGE_WIDTH}"></a>'
        )
    lines.append("</p>")
    lines.append(
        f"\n[View all my badges on Credly →](https://www.credly.com/users/{CREDLY_USERNAME})"
    )
    return "\n".join(lines)


def main():
    badges = fetch_badges(CREDLY_USERNAME)
    block = render(badges)
    text = open(README, encoding="utf-8").read()
    new = re.sub(
        r"(<!-- BADGES:START -->).*?(<!-- BADGES:END -->)",
        lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}",
        text,
        flags=re.S,
    )
    open(README, "w", encoding="utf-8").write(new)
    print(f"Wrote {len(badges)} badges")


if __name__ == "__main__":
    main()
