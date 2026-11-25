#!/usr/bin/env python3
# Removes the build user's home folder from a finished Arch package. Run it after makepkg, before the
# package is published. The path is replaced by one of exactly the same length, so nothing moves inside
# the compiled files. Checksums and sizes in .MTREE and .PKGINFO are updated to match.
# usage: scrub_arch_pkg.py <in.pkg.tar.zst> <out.pkg.tar.zst>
#        scrub_arch_pkg.py --check <pkg.tar.zst>
# Extra strings to refuse can be given in OBSCURANT_SCAN_EXTRA (comma separated).
import gzip, hashlib, io, os, re, subprocess, sys, tarfile, tempfile, zipfile
from contextlib import contextmanager
from pathlib import Path

HOME = str(Path.home()).encode()
USER = Path.home().name.encode()
FAKE = (b"/home/" + b"builder".ljust(len(HOME), b"_"))[: len(HOME)]
SECRETS = [USER, HOME] + [s.encode() for s in os.environ.get("OBSCURANT_SCAN_EXTRA", "").split(",") if s]
ZIPS = (".ja", ".jar", ".zip", ".xpi")


@contextmanager
def members(path):
    proc = subprocess.Popen(["zstd", "-dcq", path], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tar:
            yield ((m, tar.extractfile(m).read() if m.isfile() else None) for m in tar)
        proc.stdout.read()
    finally:
        proc.stdout.close()
    if proc.wait():
        sys.exit("could not decompress " + path)


def found(name, data):
    bad = [(name, s.decode()) for s in SECRETS if s in data]
    if name.endswith(ZIPS):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for info in z.infolist():
                    bad += found(name + "!" + info.filename, z.read(info))
        except zipfile.BadZipFile:
            pass
    if name == ".MTREE":
        bad += found(".MTREE contents", gzip.decompress(data))
    return bad


def check(path):
    bad = []
    with members(path) as items:
        for m, data in items:
            bad += [(m.name, s.decode()) for s in SECRETS if s in (m.name + m.linkname + m.uname + m.gname).encode()]
            if data is not None:
                bad += found(m.name, data)
    return bad


def clean_zip(data):
    src = zipfile.ZipFile(io.BytesIO(data))
    if not any(HOME in src.read(i) for i in src.infolist()):
        return data
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as dst:
        for info in src.infolist():
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            dst.writestr(zi, src.read(info).replace(HOME, FAKE), compresslevel=9)
    return out.getvalue()


def clean(name, data):
    if name.endswith(ZIPS):
        return clean_zip(data)
    return data.replace(HOME, FAKE)


def fix_mtree(data, changed):
    lines = gzip.decompress(data).decode().split("\n")
    done = set()
    for i, line in enumerate(lines):
        name = line.split(" ", 1)[0].removeprefix("./")
        if name in changed:
            new = changed[name]
            for key, value in (
                ("size", str(len(new))),
                ("md5digest", hashlib.md5(new).hexdigest()),
                ("sha256digest", hashlib.sha256(new).hexdigest()),
            ):
                line = re.sub(rf"\b{key}=\S+", f"{key}={value}", line)
            lines[i] = line
            done.add(name)
    if done != set(changed):
        sys.exit("not listed in .MTREE: " + ", ".join(sorted(set(changed) - done)))
    return gzip.compress("\n".join(lines).encode(), 9, mtime=0)


def scrub(src, out):
    changed, delta = {}, 0
    with members(src) as items:
        for m, data in items:
            if data is None or m.name in (".MTREE", ".PKGINFO"):
                continue
            new = clean(m.name, data)
            if new != data:
                changed[m.name] = new
                if not m.name.startswith("."):
                    delta += len(new) - len(data)
    with members(src) as items:
        for m, data in items:
            if m.name == ".PKGINFO":
                new = re.sub(rb"(?m)^size = (\d+)$", lambda g: b"size = %d" % (int(g[1]) + delta), data.replace(HOME, FAKE))
                if new != data:
                    changed[m.name] = new
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(out))) as tmp:
        plain, packed = os.path.join(tmp, "pkg.tar"), os.path.join(tmp, "pkg.tar.zst")
        with members(src) as items, tarfile.open(plain, "w", format=tarfile.PAX_FORMAT) as dst:
            for m, data in items:
                if data is None:
                    dst.addfile(m)
                    continue
                new = fix_mtree(data, changed) if m.name == ".MTREE" else changed.get(m.name, data)
                m.size = len(new)
                m.pax_headers.pop("size", None)
                dst.addfile(m, io.BytesIO(new))
        subprocess.check_call(["zstd", "-q", "-19", "-T0", plain, "-o", packed])
        bad = check(packed)
        if bad:
            for b in bad:
                print("PERSONAL STRING FOUND:", b)
            sys.exit("refusing to finish: personal strings present")
        os.replace(packed, out)
    print("changed:", len(changed), "files plus .MTREE; installed size delta:", delta)
    print("wrote", out, "; personal-string scan clean")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        problems = check(sys.argv[2])
        for p in problems:
            print("PERSONAL STRING FOUND:", p)
        sys.exit(1 if problems else 0)
    if len(sys.argv) != 3:
        sys.exit("usage: scrub_arch_pkg.py <in> <out> | --check <pkg>")
    scrub(sys.argv[1], sys.argv[2])
