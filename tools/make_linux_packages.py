#!/usr/bin/env python3
# Turns the portable build (mach package output) into: tarball, AppImage, .deb and .rpm.
# usage: make_linux_packages.py <mach package tar> <out dir> <whisper-cli> <obscurant-voice.py> <prefs js> <policies.json> <repo root>
# Needs nfpm and appimagetool (paths in NFPM and APPIMAGETOOL, or on PATH). Refuses to finish if the
# local username, home folder or any OBSCURANT_SCAN_EXTRA string is found in anything it ships.
import io, os, shutil, subprocess, sys, tarfile, tempfile, zipfile
from pathlib import Path

PKG_TAR, OUT, WHISPER, VOICE_PY, PREFS, POLICIES, REPO = [Path(a) for a in sys.argv[1:8]]
VERSION = os.environ.get("OBSCURANT_VERSION", "153.7.0")
REV = os.environ.get("OBSCURANT_REV", "1")
NFPM = os.environ.get("NFPM", "nfpm")
APPIMAGETOOL = os.environ.get("APPIMAGETOOL", "appimagetool")
HOME = str(Path.home())
SECRETS = [Path(HOME).name.encode(), HOME.encode()] + [s.encode() for s in os.environ.get("OBSCURANT_SCAN_EXTRA", "").split(",") if s]

LAUNCHER = r'''#!/bin/sh
DIR=$(dirname "$(readlink -f "$0")")
if [ "${OBSCURANT_GPU:-integrated}" = "integrated" ] && [ -f /usr/share/glvnd/egl_vendor.d/50_mesa.json ]; then
  V=$(cat /sys/class/drm/card*/device/vendor 2>/dev/null)
  case "$V" in
    *0x10de*) case "$V" in *0x1002*|*0x8086*)
      export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json ;;
    esac ;;
  esac
fi
if [ "$1" = "--quit" ]; then
  pgrep -x obscurant >/dev/null 2>&1 && exec "$DIR/obscurant" --quit
  exit 0
fi
exec "$DIR/obscurant" --class obscurant "$@"
'''

DESKTOP = """[Desktop Entry]
Version=1.0
Name=Obscurant
GenericName=Web Browser
Comment=Private, low-memory web browser
Exec={exec} %u
Icon=obscurant
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupWMClass=obscurant
Actions=new-window;private-window;

[Desktop Action new-window]
Name=New Window
Exec={exec} --new-window %u

[Desktop Action private-window]
Name=New Private Window
Exec={exec} --private-window %u
"""

INSTALL_SH = r'''#!/bin/sh
# Adds Obscurant to your applications menu (current user only). Run it from the unpacked folder.
set -e
DIR=$(dirname "$(readlink -f "$0")")
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/256x256/apps"
sed "s|Exec=obscurant|Exec=$DIR/start-obscurant|g" "$DIR/share/obscurant.desktop" > "$HOME/.local/share/applications/obscurant.desktop"
cp "$DIR/share/icons/obscurant-256.png" "$HOME/.local/share/icons/hicolor/256x256/apps/obscurant.png"
echo "Installed. Find Obscurant in your applications menu."
'''


def scrub_zip(data):
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    n = 0
    with zipfile.ZipFile(out, "w") as dst:
        for info in src.infolist():
            raw = src.read(info.filename)
            if HOME.encode() in raw:
                raw = raw.replace(HOME.encode(), b"/build")
                n += 1
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            dst.writestr(zi, raw)
    return out.getvalue(), n


def scan(root):
    bad = []
    for p in Path(root).rglob("*"):
        if not p.is_file() or p.is_symlink():
            continue
        raw = p.read_bytes()
        if p.suffix in (".ja", ".jar", ".zip", ".xpi"):
            try:
                with zipfile.ZipFile(p) as z:
                    raw += b"".join(z.read(i) for i in z.infolist())
            except zipfile.BadZipFile:
                pass
        for s in SECRETS:
            if s in raw:
                bad.append((str(p.relative_to(root)), s.decode()))
    return bad


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="obscurant-pkg-"))
    with tarfile.open(PKG_TAR) as t:
        t.extractall(work, filter="tar")
    top = next(p for p in work.iterdir() if p.is_dir())
    app = work / "Obscurant"
    top.rename(app)

    for ja in app.rglob("omni.ja"):
        data, n = scrub_zip(ja.read_bytes())
        ja.write_bytes(data)
        print("scrubbed", ja.relative_to(app), n, "entries")

    (app / "distribution").mkdir(exist_ok=True)
    shutil.copy(POLICIES, app / "distribution" / "policies.json")
    prefs_dir = app / "browser" / "defaults" / "preferences"
    prefs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(PREFS, prefs_dir / "obscurant.js")

    voice = app / "voice"
    voice.mkdir(exist_ok=True)
    shutil.copy(VOICE_PY, voice / "obscurant-voice.py")
    shutil.copy(WHISPER, voice / "whisper-cli")
    os.chmod(voice / "whisper-cli", 0o755)
    (voice / "README.txt").write_text(
        "The voice assistant also needs python3 with numpy, bubblewrap and parecord (pulseaudio-utils or libpulse),\n"
        "and the speech model: put ggml-base.en.bin in this folder or in ~/.local/share/obscurant/voice/\n"
        "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin\n"
    )

    lic = app / "licenses"
    (lic / "fonts").mkdir(parents=True, exist_ok=True)
    for name in ("LICENSE", "THIRD-PARTY-NOTICES.md"):
        shutil.copy(REPO / name, lic)
    fonts = REPO / "pkg" / "src" / "obscurant-assets" / "fonts"
    if fonts.is_dir():
        for f in fonts.glob("OFL*.txt"):
            shutil.copy(f, lic / "fonts")

    share = app / "share"
    (share / "icons").mkdir(parents=True, exist_ok=True)
    icons = REPO / "pkg" / "src" / "obscurant-assets" / "icons"
    for f in icons.glob("obscurant-*.png"):
        shutil.copy(f, share / "icons")
    (share / "obscurant.desktop").write_text(DESKTOP.format(exec="obscurant"))
    (app / "start-obscurant").write_text(LAUNCHER)
    os.chmod(app / "start-obscurant", 0o755)
    (app / "install.sh").write_text(INSTALL_SH)
    os.chmod(app / "install.sh", 0o755)

    bad = scan(app)
    if bad:
        for b in bad:
            print("PERSONAL STRING FOUND:", b)
        sys.exit("refusing to finish: personal strings present")
    print("personal-string scan clean")

    tar_out = OUT / f"Obscurant-{VERSION}-linux-x86_64.tar.xz"
    subprocess.check_call(["tar", "-C", str(work), "-cJf", str(tar_out), "Obscurant"], env=dict(os.environ, XZ_OPT="-T0 -6"))
    print("wrote", tar_out)

    appdir = work / "AppDir"
    shutil.copytree(app, appdir / "obscurant", symlinks=True)
    shutil.copy(share / "icons" / "obscurant-256.png", appdir / "obscurant.png")
    (appdir / "obscurant.desktop").write_text(DESKTOP.format(exec="obscurant"))
    (appdir / "AppRun").write_text('#!/bin/sh\nHERE=$(dirname "$(readlink -f "$0")")\nexec "$HERE/obscurant/start-obscurant" "$@"\n')
    os.chmod(appdir / "AppRun", 0o755)
    appimage = OUT / f"Obscurant-{VERSION}-x86_64.AppImage"
    subprocess.check_call([APPIMAGETOOL, "--appimage-extract-and-run", "-n", "--runtime-file", os.environ.get("APPIMAGE_RUNTIME", "runtime-x86_64"), str(appdir), str(appimage)], env=dict(os.environ, ARCH="x86_64"))
    print("wrote", appimage)

    desktop_sys = work / "obscurant-system.desktop"
    desktop_sys.write_text(DESKTOP.format(exec="obscurant"))
    for kind, deps in (
        ("deb", ["libgtk-3-0t64 | libgtk-3-0", "libdbus-glib-1-2", "libasound2t64 | libasound2", "libx11-xcb1", "libxtst6", "libpulse0"]),
        ("rpm", ["gtk3", "dbus-glib", "alsa-lib", "libXtst", "libxcb"]),
    ):
        contents = [
            {"src": str(app), "dst": "/opt/obscurant", "type": "tree"},
            {"src": "/opt/obscurant/start-obscurant", "dst": "/usr/bin/obscurant", "type": "symlink"},
            {"src": str(desktop_sys), "dst": "/usr/share/applications/obscurant.desktop"},
        ]
        for s in (16, 32, 48, 64, 128, 256, 512):
            icon = share / "icons" / f"obscurant-{s}.png"
            if icon.exists():
                contents.append({"src": str(icon), "dst": f"/usr/share/icons/hicolor/{s}x{s}/apps/obscurant.png"})
        cfg = {
            "name": "obscurant", "arch": "amd64", "platform": "linux", "version": VERSION, "release": REV,
            "maintainer": "Obscurant <noreply@users.noreply.github.com>",
            "description": "Private, low-memory web browser built on Firefox ESR.",
            "homepage": "https://github.com/mrbalt/obscurant", "license": "MPL-2.0",
            "depends": deps, "recommends": ["python3-numpy", "bubblewrap", "pulseaudio-utils"] if kind == "deb" else ["python3-numpy", "bubblewrap"],
            "contents": contents,
        }
        import json
        (work / f"nfpm-{kind}.yaml").write_text(json.dumps(cfg))
        subprocess.check_call([NFPM, "package", "-f", str(work / f"nfpm-{kind}.yaml"), "-p", kind, "-t", str(OUT)])

    for p in sorted(OUT.iterdir()):
        print(p.name, p.stat().st_size // 1048576, "MB")
    shutil.rmtree(work)


main()
