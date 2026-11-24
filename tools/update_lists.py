import re
import sys
import time
import urllib.request
from pathlib import Path

LISTS = Path(__file__).resolve().parent.parent / "config" / "lists"
SOURCES = {
    "easylist.txt": "https://easylist.to/easylist/easylist.txt",
    "easyprivacy.txt": "https://easylist.to/easylist/easyprivacy.txt",
    "phishing-filter.txt": "https://curbengh.github.io/malware-filter/phishing-filter.txt",
}


def fetch(url, attempts=4):
    req = urllib.request.Request(url, headers={"User-Agent": "obscurant-list-updater"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8")
        except Exception as ex:
            if attempt == attempts:
                raise
            print(f"retrying {url} after {type(ex).__name__}")
            time.sleep(3 * attempt)


HOSTNAME = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", re.I)
# A bad upstream line must never turn these sites into warning pages.
PROTECTED = ("mozilla.org", "mozilla.net", "mozilla.com", "virustotal.com", "duckduckgo.com", "startpage.com", "brave.com", "google.com", "github.com")


def to_abp(text):
    out = ["[Adblock Plus 2.0]", "! Title: Phishing URL Blocklist (converted to ABP rules)"]
    for line in text.splitlines():
        host = line.strip().lower()
        if not host or host.startswith(("!", "[")) or not HOSTNAME.match(host):
            continue
        if any(host == d or host.endswith("." + d) for d in PROTECTED):
            continue
        out.append(f"||{host}^")
    return "\n".join(out) + "\n"


UBLOCK_BASE = "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/"
UBLOCK_FILES = ["filters.txt", "privacy.txt", "badware.txt", "unbreak.txt", "quick-fixes.txt"]
UNSUPPORTED = re.compile(
    r"\$[^ ]*\b(redirect(-rule)?|removeparam|csp|replace|permissions|header|inline-script|inline-font|to=|denyallow=)\b"
    r"|##\+js|#@#\+js|#\?#|#\$#|:has-text|:xpath|:matches-|:upward|:remove|:style|:others|:watch-attr|:min-text-length|:-abp-"
)


BRAVE_BASE = "https://raw.githubusercontent.com/brave/adblock-lists/master/brave-lists/"
BRAVE_FILES = ["brave-specific.txt", "brave-unbreak.txt", "brave-firstparty.txt"]


def build_brave():
    out = ["[Adblock Plus 2.0]", "! Title: Brave lists (Obscurant build, script rules removed)"]
    for name in BRAVE_FILES:
        for line in fetch(BRAVE_BASE + name).splitlines():
            s = line.strip()
            if s and not s.startswith(("!", "[")) and not UNSUPPORTED.search(s) and "+js(" not in s:
                out.append(s)
    if len(out) < 1000:
        sys.exit("brave.txt: result looks too small, keeping the old file")
    tmp = LISTS / "brave.txt.new"
    tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
    tmp.replace(LISTS / "brave.txt")
    print(f"built brave.txt: {len(out) - 2} rules")


def build_ublock():
    out = ["[Adblock Plus 2.0]", "! Title: uBlock Origin filters (Obscurant build, unsupported rule types removed)"]
    for name in UBLOCK_FILES:
        for line in fetch(UBLOCK_BASE + name).splitlines():
            s = line.strip()
            if s and not s.startswith(("!", "[")) and not UNSUPPORTED.search(s):
                out.append(s)
    if len(out) < 5000:
        sys.exit("ublock.txt: result looks too small, keeping the old file")
    tmp = LISTS / "ublock.txt.new"
    tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
    tmp.replace(LISTS / "ublock.txt")
    print(f"built ublock.txt: {len(out) - 2} rules")


def main():
    LISTS.mkdir(parents=True, exist_ok=True)
    build_ublock()
    build_brave()
    for name, url in SOURCES.items():
        text = fetch(url)
        if len(text) < 10000:
            sys.exit(f"{name}: download looks too small ({len(text)} bytes), keeping the old file")
        old = LISTS / name
        if old.exists() and len(text) < 0.9 * old.stat().st_size:
            sys.exit(f"{name}: new list is more than 10% smaller than the old one, keeping the old file")
        tmp = LISTS / (name + ".new")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(LISTS / name)
        print(f"updated {name}: {len(text)} bytes")
        if name == "phishing-filter.txt":
            abp = to_abp(text)
            tmp2 = LISTS / "phishing-abp.txt.new"
            tmp2.write_text(abp, encoding="utf-8")
            tmp2.replace(LISTS / "phishing-abp.txt")
            print(f"converted phishing-abp.txt: {abp.count(chr(10)) - 2} rules")


main()
