"""Make our baked prefs (config/*.js) win over Firefox's own browser/app/profile/firefox.js.
firefox.js loads after the baked defaults file, so any pref it also sets would undo ours.
Rewrites those lines in firefox.js to our values. Safe to run repeatedly."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FX = ROOT / "src/firefox-153.7.0/browser/app/profile/firefox.js"
baked = {}
for f in ["user.js", "diet-safe.js", "blocker.js", "no-phone-home.js"]:
    for m in re.finditer(r'user_pref\("([^"]+)",\s*(.+?)\);\s*$', (ROOT / "config" / f).read_text(), re.M):
        baked[m.group(1)] = m.group(2).strip()
lines = FX.read_text().split("\n")
changed = 0
for i, line in enumerate(lines):
    m = re.match(r'^(\s*)pref\("([^"]+)",\s*(.+?)\);(.*)$', line)
    if not m or m.group(2) not in baked:
        continue
    new = baked[m.group(2)]
    old = m.group(3).split("//")[0].strip()
    if old == new or "sticky" in old:
        if "sticky" in old and old.split(",")[0].strip() != new:
            new = new + ", sticky"
        else:
            continue
    lines[i] = f'{m.group(1)}pref("{m.group(2)}", {new});{m.group(4)}'
    changed += 1
FX.write_text("\n".join(lines))
print("rewrote", changed, "pref lines in firefox.js")
