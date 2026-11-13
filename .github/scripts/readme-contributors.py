import json
import os
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

headers = {"User-Agent": "nzik-contributors"}
if token := os.getenv("GH_TOKEN"):
    headers["Authorization"] = "Bearer " + token

def api(endpoint):
    url = "https://api.github.com/" + endpoint + "?per_page=100"
    while url:
        with urlopen(Request(url, headers=headers), timeout=25) as response:
            yield from json.load(response)
            url = next((part.split(">")[0].strip()[1:] for part in response.headers.get("Link", "").split(",") if 'rel="next"' in part), None)

def grid(rows):
    return '<p align="center">\n' + "\n".join(
        f'<a href="{escape(profile)}"><img src="{escape(avatar)}" width="54" height="54" alt="{escape(name)}" title="{escape(name)}" /></a>'
        for name, profile, avatar in rows
    ) + "\n</p>"

def replace(text, marker, content):
    start, end = f"<!-- {marker}:start -->", f"<!-- {marker}:end -->"
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + "\n" + content + "\n" + end + after

path = Path(os.environ.get("README_PATH", "README.md"))
text = path.read_text(encoding="utf-8")
repo = os.environ["GITHUB_REPOSITORY"]
rows = [
    (user["login"], user["html_url"], user["avatar_url"])
    for user in api(f"repos/{repo}/contributors")
    if user["type"] == "User"
]
if not rows:
    raise SystemExit("No contributors returned")
text = replace(text, "project-contributors", grid(rows))
path.write_text(text, encoding="utf-8", newline="\n")