#!/bin/sh
# Cross-builds the Windows (x86_64) version of Obscurant on Linux. Experimental: not yet built or tested end to end.
#
# The Windows SDK and Visual C++ headers/libraries come from Microsoft and need you to accept Microsoft's license
# terms (https://go.microsoft.com/fwlink/?LinkId=2086102). This script will not accept them for you:
# run it once with --accept-microsoft-license after you have read them.
set -e
SRC=${1:?usage: build_windows.sh /path/to/patched/firefox-153.7.0 [--accept-microsoft-license]}
SYSROOT=${WINSYSROOT:-$HOME/.cache/obscurant-winsysroot}
if [ ! -d "$SYSROOT/VC" ]; then
  [ "$2" = "--accept-microsoft-license" ] || { echo "Needs the Windows SDK. Read Microsoft's terms, then re-run with --accept-microsoft-license" >&2; exit 1; }
  command -v xwin >/dev/null || cargo install xwin --locked
  xwin --accept-license --arch x86_64 --variant desktop --sdk-version 10.0.26100 splat --use-winsysroot-style --output "$SYSROOT"
fi
rm -rf "$SRC/browser/base/content/lists"; mkdir -p "$SRC/browser/base/content/lists"
for f in easylist easyprivacy ublock brave phishing-abp ai-sites; do cp "$(dirname "$0")/../config/lists/$f.txt" "$SRC/browser/base/content/lists/"; done
sed "s|@WINSYSROOT@|$SYSROOT|; s|@TOPSRCDIR@|$SRC|" "$(dirname "$0")/../windows/mozconfig" > "$SRC/mozconfig.win"
cd "$SRC"
MOZCONFIG="$SRC/mozconfig.win" ./mach build
MOZCONFIG="$SRC/mozconfig.win" ./mach package
