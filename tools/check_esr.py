import json
import re
import sys
import urllib.request
from pathlib import Path

PKGBUILD = Path(__file__).resolve().parent.parent / "pkg" / "PKGBUILD"


def main():
    ours = re.search(r"^pkgver=(\S+)", PKGBUILD.read_text(), re.M).group(1)
    url = "https://product-details.mozilla.org/1.0/firefox_versions.json"
    with urllib.request.urlopen(url, timeout=60) as r:
        latest = json.load(r)["FIREFOX_ESR"].removesuffix("esr")
    key = lambda v: [int(p) for p in v.split(".")]
    if key(latest) > key(ours):
        print(f"UPDATE NEEDED: Mozilla ESR is {latest}, Obscurant is on {ours}. Rebuild and reinstall.")
        sys.exit(1)
    print(f"Up to date: ESR {latest} (Obscurant {ours}).")


main()
