#!/usr/bin/env python3
# Turns the cross-built Windows package zip into the distributable portable zip.
# Adds the Microsoft C++ runtime DLLs, scrubs build paths out of omni.ja, and refuses to finish if
# the local username or any personal string is still present anywhere in the output.
import io, json, os, re, shutil, sys, zipfile

BUILD_ZIP, CRT_DIR, OUT_ZIP = sys.argv[1:4]
VOICE_DIR = sys.argv[4] if len(sys.argv) > 4 else None
DEFAULTS_JS = sys.argv[5] if len(sys.argv) > 5 else None
TOR_DIR = sys.argv[6] if len(sys.argv) > 6 else None
ROOT = "Obscurant"
RUNTIME = ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll", "msvcp140_atomic_wait.dll"]
HOME = os.path.expanduser("~")
USER = os.path.basename(HOME)
SECRETS = [USER.encode(), HOME.encode()]
EXTRA = [s.encode() for s in os.environ.get("OBSCURANT_SCAN_EXTRA", "").split(",") if s]


def scrub_omni(data):
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    changed = 0
    with zipfile.ZipFile(out, "w") as dst:
        for info in src.infolist():
            raw = src.read(info.filename)
            if HOME.encode() in raw:
                raw = raw.replace(HOME.encode(), b"/build")
                changed += 1
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            dst.writestr(zi, raw)
    return out.getvalue(), changed


def main():
    work = OUT_ZIP + ".stage"
    shutil.rmtree(work, ignore_errors=True)
    with zipfile.ZipFile(BUILD_ZIP) as z:
        z.extractall(work)
    top = os.path.join(work, os.listdir(work)[0])
    for name in RUNTIME:
        found = None
        for root, _, files in os.walk(CRT_DIR):
            if name in files and "debug" not in root.lower():
                found = os.path.join(root, name)
        if not found:
            sys.exit("missing runtime dll " + name)
        shutil.copy(found, os.path.join(top, name))
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pol = os.path.join(repo, "config", "policies.json")
    if not os.path.isfile(pol):
        sys.exit("config/policies.json not found: the search engines and AI switches would be missing")
    json.load(open(pol))
    os.makedirs(os.path.join(top, "distribution"), exist_ok=True)
    shutil.copy(pol, os.path.join(top, "distribution", "policies.json"))
    lic = os.path.join(top, "licenses")
    os.makedirs(os.path.join(lic, "fonts"), exist_ok=True)
    for name in ("LICENSE", "THIRD-PARTY-NOTICES.md"):
        shutil.copy(os.path.join(repo, name), lic)
    for d in (os.path.join(repo, "pkg", "src", "obscurant-assets", "fonts"), os.path.join(repo, "assets", "fonts")):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith("OFL") and f.endswith(".txt"):
                    shutil.copy(os.path.join(d, f), os.path.join(lic, "fonts", f))
    for name in ("default-browser-agent.exe",):
        path = os.path.join(top, name)
        if os.path.exists(path):
            os.remove(path)
    if DEFAULTS_JS:
        d = os.path.join(top, "browser", "defaults", "preferences")
        os.makedirs(d, exist_ok=True)
        shutil.copy(DEFAULTS_JS, os.path.join(d, "obscurant.js"))
    if TOR_DIR:
        shutil.copytree(TOR_DIR, os.path.join(top, "tor"))
    if VOICE_DIR:
        shutil.copytree(VOICE_DIR, os.path.join(top, "voice"), ignore=shutil.ignore_patterns("__pycache__", "*.verified", "*.pyc"))
    for root, _, files in os.walk(top):
        for f in files:
            if f == "omni.ja":
                p = os.path.join(root, f)
                data, n = scrub_omni(open(p, "rb").read())
                open(p, "wb").write(data)
                print("scrubbed", os.path.relpath(p, top), n, "entries")
    bad = []
    for root, _, files in os.walk(work):
        for f in files:
            p = os.path.join(root, f)
            raw = open(p, "rb").read()
            if f.endswith((".ja", ".jar", ".zip", ".xpi")):
                try:
                    with zipfile.ZipFile(p) as z:
                        raw += b"".join(z.read(i) for i in z.infolist())
                except zipfile.BadZipFile:
                    pass
            for s in SECRETS + EXTRA:
                if s in raw:
                    bad.append((os.path.relpath(p, work), s.decode()))
    if bad:
        for b in bad:
            print("PERSONAL STRING FOUND:", b)
        sys.exit("refusing to finish: personal strings present")
    os.makedirs(os.path.dirname(os.path.abspath(OUT_ZIP)), exist_ok=True)
    final = os.path.join(work, ROOT)
    os.rename(top, final)
    if os.path.exists(OUT_ZIP):
        os.remove(OUT_ZIP)
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for root, _, files in os.walk(final):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, work))
    shutil.rmtree(work)
    print("wrote", OUT_ZIP, os.path.getsize(OUT_ZIP) // 1048576, "MB; personal-string scan clean")


main()
