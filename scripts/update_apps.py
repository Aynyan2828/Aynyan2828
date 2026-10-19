"""bcnofne.com/apps.json から README の iOS アプリ欄を作り直す。

使い方: python3 scripts/update_apps.py [README のパス]
変化が無ければ README は書き換えない。
"""
import json
import logging
import sys
import urllib.request
from pathlib import Path

APPS_URL = "https://bcnofne.com/apps.json"
START = "<!-- APPS:START -->"
END = "<!-- APPS:END -->"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("update_apps")


def fetch_apps(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "github-profile-updater"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode("utf-8"))
    apps = data.get("apps", [])
    if not apps:
        raise ValueError("apps.json にアプリが 0 件")
    return apps


def render(apps: list) -> str:
    rows = ["| | App | |", "|---|---|---|"]
    for app in apps:
        icon = f'<img src="{app["icon"]}" width="48" alt="">' if app.get("icon") else ""
        name = app["name"]
        tagline = app.get("taglineEn") or app.get("tagline", "")
        rows.append(f'| {icon} | **[{name}]({app["url"]})** | {tagline} |')
    return "\n".join(rows)


def main() -> int:
    readme = Path(sys.argv[1] if len(sys.argv) > 1 else "README.md")
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        log.error("README に %s / %s が無い", START, END)
        return 1
    try:
        apps = fetch_apps(APPS_URL)
    except Exception as e:  # 取れん時は README を触らん
        log.error("apps.json を取れんかった: %s", e)
        return 1
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{render(apps)}\n{END}{tail}"
    if new == text:
        log.info("変化なし（%d 件）", len(apps))
        return 0
    with open(readme, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    log.info("アプリ欄を更新（%d 件）", len(apps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
