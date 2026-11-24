"""Rebuild patches/obscurant-full.patch, the package assets and the PKGBUILD checksums.

Compares src/firefox-153.7.0 against a pristine extract of the ESR tarball
(cached in work/pristine), so nothing depends on a remembered file list.
Refuses to write anything if the result looks wrong.
"""
import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "firefox-153.7.0"
TARBALL = ROOT / "src" / "firefox-153.7.0esr.source.tar.xz"
PRISTINE = ROOT / "work" / "pristine" / "firefox-153.7.0"
PKG = ROOT / "pkg"
PATCH = ROOT / "patches" / "obscurant-full.patch"

SKIP_DIRS = {"__pycache__", ".claude"}
# Shipped through the assets or branding tarballs, or copied by PKGBUILD, not by the patch.
SKIP_PREFIXES = (
    "browser/branding/obscurant/",
    "browser/base/content/fonts/",
)
SKIP_FILES = {
    "mozconfig",
    "browser/components/aboutwelcome/content/obscurant-logo.png",
}
BINARY_SUFFIXES = {".png", ".woff2", ".ttf", ".ico", ".icns"}


def ensure_pristine():
    if PRISTINE.is_dir():
        return
    PRISTINE.parent.mkdir(parents=True, exist_ok=True)
    print("extracting pristine source (about 20 seconds)...", flush=True)
    with tarfile.open(TARBALL, "r:xz") as t:
        t.extractall(PRISTINE.parent)


def walk(base):
    out = set()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            out.add(str(Path(dirpath, f).relative_to(base)))
    return out


def changed_files():
    """Modified files (present in both and different) and new files, in text form."""
    rels = []
    out = subprocess.run(
        ["diff", "-rq", "-x", "__pycache__", "-x", ".claude", str(PRISTINE), str(SRC)],
        capture_output=True,
        text=True,
    ).stdout
    for line in out.splitlines():
        m = re.match(r"^Files (.+) and (.+) differ$", line)
        if m:
            rels.append(str(Path(m.group(2)).relative_to(SRC)))
            continue
        m = re.match(r"^Only in (.+?): (.+)$", line)
        if m and m.group(1).startswith(str(SRC)):
            p = Path(m.group(1)) / m.group(2)
            if p.is_dir():
                rels.extend(str(Path(p, r).relative_to(SRC)) for r in sorted(walk(p)))
            else:
                rels.append(str(p.relative_to(SRC)))
        elif m and m.group(1).startswith(str(PRISTINE)):
            sys.exit(f"a file was deleted from the source tree: {m.group(2)}; not supported")
    keep = []
    for r in sorted(set(rels)):
        if r in SKIP_FILES or r.startswith(SKIP_PREFIXES):
            continue
        if Path(r).suffix.lower() in BINARY_SUFFIXES:
            sys.exit(f"binary file in the patch set, add it to the assets instead: {r}")
        keep.append(r)
    return keep


def make_patch(files):
    chunks = []
    for r in files:
        new = (SRC / r).read_text(encoding="utf-8").splitlines(keepends=True)
        old_path = PRISTINE / r
        if old_path.exists():
            old = old_path.read_text(encoding="utf-8").splitlines(keepends=True)
            d = difflib.unified_diff(old, new, f"a/{r}", f"b/{r}")
        else:
            d = difflib.unified_diff([], new, "/dev/null", f"b/{r}")
        text = "".join(d)
        if text:
            if not text.endswith("\n"):
                text += "\n"
            chunks.append(text.replace("\n\\ No newline at end of file\n", "\n"))
    return "".join(chunks)


def check_applies(patch_text, files):
    with tempfile.TemporaryDirectory() as tmp:
        for r in files:
            src = PRISTINE / r
            if src.exists():
                dst = Path(tmp, r)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        pf = Path(tmp, "p.patch")
        pf.write_text(patch_text, encoding="utf-8")
        r = subprocess.run(["patch", "-p1", "--dry-run", "-s", "-i", str(pf)], cwd=tmp, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("patch does not apply cleanly:\n" + r.stdout + r.stderr)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ensure_pristine()
    files = changed_files()
    if len(files) < 60:
        sys.exit(f"only {len(files)} changed files found; expected about 90. Not writing anything.")
    text = make_patch(files)
    if text.count("\n") < 8000:
        sys.exit("patch looks too small. Not writing anything.")
    check_applies(text, files)
    PATCH.write_text(text, encoding="utf-8")
    (PKG / "obscurant-full.patch").write_text(text, encoding="utf-8")
    print(f"patch: {len(files)} files, {text.count(chr(10))} lines, applies cleanly")

    subprocess.run([sys.executable, str(ROOT / "tools" / "make_pkg_assets.py")], check=True)

    pk = (PKG / "PKGBUILD").read_text()
    m = re.search(r"sha256sums=\((.*?)\)", pk, re.S)
    hs = re.findall(r"'([0-9a-f]{64})'", m.group(1))
    # Index 0 is Mozilla's tarball (pinned by its signature); the rest are our own files.
    for i, name in enumerate(
        ["mozconfig", "obscurant-full.patch", "obscurant-logo.png", "obscurant-branding.tar.xz", "obscurant-assets.tar.xz", "policies.json", "obscurant-pgo.profdata"],
        start=1,
    ):
        if i >= len(hs):
            hs.append("0" * 64)
        hs[i] = sha(PKG / name)
    new = "sha256sums=(" + "\n            ".join(f"'{h}'" for h in hs) + ")"
    (PKG / "PKGBUILD").write_text(pk[: m.start()] + new + pk[m.end():])
    print("PKGBUILD checksums updated")


main()
