import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "pkg"

with tarfile.open(PKG / "obscurant-assets.tar.xz", "w:xz") as t:
    for f in ("obscurant", "obscurant.desktop", "obscurant.js"):
        t.add(PKG / f, arcname=f"obscurant-assets/{f}")
    for name in ("easylist.txt", "easyprivacy.txt", "ublock.txt", "brave.txt", "phishing-abp.txt", "ai-sites.txt"):
        t.add(ROOT / "config" / "lists" / name, arcname=f"obscurant-assets/lists/{name}")
    t.add(ROOT / "LICENSE", arcname="obscurant-assets/LICENSE")
    t.add(ROOT / "THIRD-PARTY-NOTICES.md", arcname="obscurant-assets/THIRD-PARTY-NOTICES.md")
    t.add(ROOT / "tools" / "voice" / "obscurant-voice.py", arcname="obscurant-assets/voice/obscurant-voice.py")
    fonts = ROOT / "src" / "firefox-153.7.0" / "browser" / "base" / "content" / "fonts"
    for f in fonts.iterdir():
        t.add(f, arcname=f"obscurant-assets/fonts/{f.name}")
    for size in (16, 32, 48, 64, 128, 256, 512):
        t.add(ROOT / "assets" / "icons" / f"obscurant-{size}.png", arcname=f"obscurant-assets/icons/obscurant-{size}.png")

branding = ROOT / "src" / "firefox-153.7.0" / "browser" / "branding" / "obscurant"
with tarfile.open(PKG / "obscurant-branding.tar.xz", "w:xz") as t:
    t.add(branding, arcname="obscurant-branding/obscurant")
print("assets:", (PKG / "obscurant-assets.tar.xz").stat().st_size, "bytes | branding:", (PKG / "obscurant-branding.tar.xz").stat().st_size, "bytes")
