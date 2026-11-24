#!/usr/bin/env python3
"""Signs the small version file that the browser's update notice checks.

  make_release.py keygen
      One time. Creates the private key in ~/.config/obscurant-release/ (never commit or share it)
      and prints the public key that goes into config/user.js as obscurant.update.pubkey.

  make_release.py sign --version 153.7.0 --build 2 --url https://github.com/OWNER/REPO/releases/tag/v153.7.0-2 --notes "Security fixes" [--package FILE]
      Writes latest.json. Upload it, and the package, to the GitHub release.
      The browser asks for .../releases/latest/download/latest.json.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

KEYDIR = Path.home() / ".config" / "obscurant-release"
KEY = KEYDIR / "update-signing-key.pem"


def raw_public():
    der = subprocess.run(["openssl", "pkey", "-in", str(KEY), "-pubout", "-outform", "DER"], check=True, capture_output=True).stdout
    return base64.b64encode(der[-32:]).decode()


def keygen():
    if KEY.exists():
        print("A key already exists. Public key:", raw_public())
        return
    KEYDIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    subprocess.run(["openssl", "genpkey", "-algorithm", "ed25519", "-out", str(KEY)], check=True)
    KEY.chmod(0o600)
    print("Private key written to", KEY)
    print("Public key (obscurant.update.pubkey):", raw_public())


def sign(a):
    manifest = {
        "version": a.version,
        "build": a.build,
        "released": a.released or datetime.date.today().isoformat(),
        "url": a.url,
        "notes": a.notes,
    }
    msg = "\n".join(str(manifest[k]) for k in ("version", "build", "released", "url", "notes")).encode()
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "msg"
        f.write_bytes(msg)
        sig = subprocess.run(["openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(KEY), "-in", str(f)], check=True, capture_output=True).stdout
    manifest["sig"] = base64.b64encode(sig).decode()
    if a.package:
        manifest["sha256"] = hashlib.sha256(Path(a.package).read_bytes()).hexdigest()
    out = Path(a.out)
    out.write_text(json.dumps(manifest, indent=1) + "\n")
    print("wrote", out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("keygen")
    s = sub.add_parser("sign")
    s.add_argument("--version", required=True)
    s.add_argument("--build", type=int, required=True)
    s.add_argument("--url", required=True)
    s.add_argument("--notes", default="")
    s.add_argument("--released")
    s.add_argument("--package")
    s.add_argument("--out", default="latest.json")
    a = p.parse_args()
    keygen() if a.cmd == "keygen" else sign(a)


main()
