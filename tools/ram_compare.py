import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOME = Path.home()
PROJECT = HOME / "Projects" / "browser"
OURS = PROJECT / "src" / "obj-baseline" / "dist" / "bin" / "firefox"
OURS_V1 = PROJECT / "src" / "obj-pgo-use" / "dist" / "bin" / "obscurant"
HARDEN = PROJECT / "config" / "user.js"

PAGES = [
    "https://en.wikipedia.org/wiki/Linux",
    "https://github.com/torvalds/linux",
    "https://news.ycombinator.com/",
    "https://www.bbc.com/",
    "https://www.theguardian.com/international",
    "https://stackoverflow.com/",
    "https://archlinux.org/",
    "https://www.youtube.com/",
]

SAMPLE_AT = [int(x) for x in os.environ.get("RAM_SAMPLES", "45,90,150").split(",")]

FF_BASE_PREFS = """
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("datareporting.policy.firstRunURL", "");
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.couldRestoreSession.count", 0);
"""


def children_map():
    out = subprocess.run(["ps", "-eo", "pid=,ppid="], capture_output=True, text=True).stdout
    m = {}
    for line in out.split("\n"):
        parts = line.split()
        if len(parts) == 2:
            m.setdefault(int(parts[1]), []).append(int(parts[0]))
    return m


def tree(root):
    m = children_map()
    seen, stack = [], [root]
    while stack:
        p = stack.pop()
        seen.append(p)
        stack.extend(m.get(p, []))
    return seen


def pss_kb(pid):
    try:
        for line in Path(f"/proc/{pid}/smaps_rollup").read_text().split("\n"):
            if line.startswith("Pss:"):
                return int(line.split()[1])
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
    return 0


def measure(root):
    pids = tree(root)
    return len(pids), sum(pss_kb(p) for p in pids) / 1024


def run_one(name, cmd, profile_prep=None):
    prof = Path(tempfile.mkdtemp(prefix="ramtest-"))
    full = profile_prep(prof) if profile_prep else cmd
    env = dict(os.environ, MOZ_ENABLE_WAYLAND="1")
    log = open(PROJECT / "logs" / f"ram-{name.replace(' ', '_')}.log", "w")
    proc = subprocess.Popen(full(prof) if callable(full) else full, env=env, stdout=log, stderr=log, start_new_session=True)
    t0 = time.time()
    samples = []
    for t in SAMPLE_AT:
        time.sleep(max(0, t - (time.time() - t0)))
        samples.append((t,) + measure(proc.pid))
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        time.sleep(4)
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    shutil.rmtree(prof, ignore_errors=True)
    return samples


def ff_cmd(binary, prefs_files):
    def prep(prof):
        txt = FF_BASE_PREFS + "".join(Path(f).read_text() for f in prefs_files)
        (prof / "user.js").write_text(txt)
        return lambda p: [str(binary), "--no-remote", "--profile", str(p)] + PAGES
    return prep


def brave_cmd():
    def prep(prof):
        return lambda p: ["/usr/bin/brave", "--ozone-platform=wayland", f"--user-data-dir={p}", "--no-first-run", "--no-default-browser-check"] + PAGES
    return prep


def main():
    cfg = PROJECT / "config"
    safe = cfg / "diet-safe.js"
    aggr = cfg / "diet-aggressive.js"
    runs = [
        ("Obscurant", ff_cmd(OURS_V1, [])),
        ("Stock Firefox", ff_cmd("/usr/bin/firefox", [])),
        ("Brave", brave_cmd()),
    ]
    only = sys.argv[1:]
    results = []
    for name, prep in runs:
        if only and not any(o.lower() in name.lower() for o in only):
            continue
        print(f"running {name}", flush=True)
        s = run_one(name, None, prep)
        results.append((name, s))
        print(f"  {name}: " + ", ".join(f"{t}s={n}proc/{mb:.0f}MB" for t, n, mb in s), flush=True)
        time.sleep(3)
    outdir = PROJECT / "results"
    outdir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    lines = ["# RAM measurement", "", f"{len(PAGES)} pages, fresh profile each, PSS summed over all processes the browser started.", "", "| Browser | " + " | ".join(f"{t}s" for t in SAMPLE_AT) + " | processes @ last |", "|---|" + "---|" * (len(SAMPLE_AT) + 1)]
    for name, s in results:
        lines.append(f"| {name} | " + " | ".join(f"{mb:.0f} MB" for _, _, mb in s) + f" | {s[-1][1]} |")
    (outdir / f"ram-{stamp}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


main()
