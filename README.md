# Obscurant

A private, low-memory, fast web browser built on Firefox ESR. Everything is built in: no extensions needed, no accounts, no sync,
no AI features, nothing sent to Mozilla. Not made, endorsed or supported by Mozilla.

Status: **Linux** (x86_64, packaged for Arch-based systems) and **Windows** (64-bit, first build, still being tested). Details for Windows are in [`windows/README.md`](windows/README.md).

## What is different from Firefox

- **Built-in blocker** (adblock-rust with EasyList, EasyPrivacy, uBlock and Brave filters), plus phishing and malware lists refreshed every 15 minutes.
- **Shield panel** per site, with one switch per area (ads and trackers, privacy protections, AI-content filters, voice, SponsorBlock).
- **Google container**: Google sign-in is isolated from the rest of your browsing.
- **Download scan**: hashes of downloads are checked against VirusTotal with your own API key. Only the hash is sent.
- **Obscurity**: an optional voice assistant that runs only on your computer (whisper.cpp). Wake phrase or push-to-talk, about 100 commands, a small robot shows what it hears.
- **SponsorBlock** skipping and **YouTube ad removal**, built in and optional.
- **No telemetry, no sync, no AI features, no sponsored tiles**; hardened defaults; its own password page with a strong primary password flow.
- Faster startup and page loads: profile-guided and link-time optimized build.
- **Update notices**, not auto-update: about once a day it fetches one signed file from this repo's latest release and tells you if a new version is out. It downloads and installs nothing.

## Install on Windows (64-bit)

Pick one. None of them needs administrator rights, and all of them install for your user only.

**Easiest: the installer.** Download **`Obscurant-Setup-153.7.0.exe`** and run it. It has a progress bar, a finish page with *Open Obscurant* and *Add a shortcut to the desktop*, and it appears under Settings, Apps.

| What | Download |
| --- | --- |
| Installer (`.exe`) | [Obscurant-Setup-153.7.0.exe](https://github.com/mrbalt/obscurant/releases/latest/download/Obscurant-Setup-153.7.0.exe) |
| MSI | [Obscurant-153.7.0-win64.msi](https://github.com/mrbalt/obscurant/releases/latest/download/Obscurant-153.7.0-win64.msi) (uninstall any older Obscurant MSI first) |
| Portable zip (no install, unzip and run `Obscurant\obscurant.exe`) | [Obscurant-win64-portable.zip](https://github.com/mrbalt/obscurant/releases/latest/download/Obscurant-win64-portable.zip) |
| Checksums | [SHA256SUMS-windows](https://github.com/mrbalt/obscurant/releases/latest/download/SHA256SUMS-windows) |

**From the command line.** Open *Command Prompt* and paste (Windows 10 and later):

    curl.exe -L -o "%TEMP%\obscurant-install.ps1" https://github.com/mrbalt/obscurant/releases/latest/download/install.ps1 && powershell -NoProfile -ExecutionPolicy Bypass -File "%TEMP%\obscurant-install.ps1"

Or in *PowerShell*:

    curl.exe -L -o "$env:TEMP\obscurant-install.ps1" https://github.com/mrbalt/obscurant/releases/latest/download/install.ps1; powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP\obscurant-install.ps1"

It downloads the zip, prints its SHA-256, installs to `%LOCALAPPDATA%\Programs\Obscurant` and adds a Start menu entry. To check the download against a hash you trust, add `-Sha256 <hash from SHA256SUMS-windows>` at the end.

**Offline or on a locked-down computer.** Put `install.cmd`, `install.ps1` and `Obscurant-win64-portable.zip` in the same folder (a USB stick works) and double-click `install.cmd`. Or just use the portable zip.

**Check a download** (recommended): compare it with `SHA256SUMS-windows`:

    certutil -hashfile Obscurant-Setup-153.7.0.exe SHA256

**Remove it:** Settings, Apps, Installed apps, Obscurant. For the script install: `powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Uninstall`.

What to expect on Windows:

- It is **not code-signed**, so Windows SmartScreen will warn ("Windows protected your PC"). Choose *More info*, then *Run anyway*, only if you checked the hash above.
- The first start is slow while Windows scans the program. Later starts are faster.
- DuckDuckGo is the default search, Brave Search is built in, AI features are off, the ad blocker and Tor button work like on Linux (Tor ships inside the install).
- Not available on Windows yet: screen-reader support. The voice assistant is included but its microphone path is untested on real hardware.
- This is a first build tested mostly under Wine. Please report what breaks: https://github.com/mrbalt/obscurant/issues

## Install on Linux (Arch, CachyOS, Manjaro and other Arch-based)

Download `obscurant-*.pkg.tar.zst` from the latest release, then:

    sudo pacman -U obscurant-*.pkg.tar.zst

Optional, for the voice assistant:

    sudo pacman -S whisper-cpp bubblewrap libpulse python-numpy
    mkdir -p ~/.local/share/obscurant/voice
    curl -L -o ~/.local/share/obscurant/voice/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

Turn it on from the shield panel (Voice group).

## Build from source

    cd pkg
    makepkg -f

This downloads the Firefox ESR source from Mozilla, applies `obscurant-full.patch`, and builds with the saved speed profile
(`obscurant-pgo.profdata`, attached to the `pgo-1` release). Expect several hours and about 30 GB of disk.

## Security updates

There is no auto-updater. When Mozilla ships a new ESR security release, Obscurant needs to be rebased and rebuilt. `tools/check_esr.py`
tells you if you are behind. If you rely on this browser, check it regularly and install new releases promptly.

## License

MPL 2.0 (see `LICENSE`). Third-party data and fonts: see `THIRD-PARTY-NOTICES.md`. The SponsorBlock feature uses data under
CC BY-NC-SA 4.0 (non-commercial).


## Download checks (VirusTotal)

See [docs/VIRUSTOTAL.md](docs/VIRUSTOTAL.md) for how to get a free key and where to put it on Linux and Windows.
