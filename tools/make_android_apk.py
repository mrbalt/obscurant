#!/usr/bin/env python3
# Turns the Gradle release APK into the one that gets published: removes the build folder paths from
# omni.ja, aligns, signs, and refuses to leave an output file if any personal string is still inside.
# usage: make_android_apk.py <gradle apk> <out apk> <build-tools dir> <keystore> <key alias> <password file>
# Extra strings to refuse can be given in OBSCURANT_SCAN_EXTRA (comma separated).
import io, os, subprocess, sys, tempfile, zipfile
from pathlib import Path

SRC, OUT, TOOLS, KEYSTORE, ALIAS, PASSFILE = sys.argv[1:7]
HOME = str(Path.home())
SECRETS = [Path(HOME).name.encode(), HOME.encode()] + [
    s.encode() for s in os.environ.get("OBSCURANT_SCAN_EXTRA", "").split(",") if s
]


def rewrite(data, change):
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as dst:
        for info in src.infolist():
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            dst.writestr(zi, change(info.filename, src.read(info)), compresslevel=9)
    return out.getvalue()


def scrub_omni(name, raw):
    return raw.replace(HOME.encode(), b"/build")


def scrub_apk(name, raw):
    return rewrite(raw, scrub_omni) if name == "assets/omni.ja" else raw


def scan(data, where=""):
    bad = []
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            raw = z.read(info)
            bad += [(where + info.filename, s.decode()) for s in SECRETS if s in raw]
            if info.filename.endswith((".ja", ".jar", ".zip", ".apk", ".xpi")):
                try:
                    bad += scan(raw, where + info.filename + "!")
                except zipfile.BadZipFile:
                    pass
    return bad


def main():
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(OUT))) as tmp:
        clean, aligned, signed = (os.path.join(tmp, n) for n in ("clean.apk", "aligned.apk", "signed.apk"))
        Path(clean).write_bytes(rewrite(Path(SRC).read_bytes(), scrub_apk))
        subprocess.check_call([os.path.join(TOOLS, "zipalign"), "-f", "-p", "4", clean, aligned])
        subprocess.check_call([
            os.path.join(TOOLS, "apksigner"), "sign", "--ks", KEYSTORE, "--ks-key-alias", ALIAS,
            "--ks-pass", "file:" + PASSFILE, "--v4-signing-enabled", "false", "--out", signed, aligned,
        ])
        bad = scan(Path(signed).read_bytes())
        if bad:
            for b in bad:
                print("PERSONAL STRING FOUND:", b)
            sys.exit("refusing to finish: personal strings present")
        subprocess.check_call([os.path.join(TOOLS, "zipalign"), "-c", "-p", "4", signed])
        os.replace(signed, OUT)
    print("wrote", OUT, os.path.getsize(OUT), "bytes; personal-string scan clean")


main()
