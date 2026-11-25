# Obscurant

A private, low-memory, fast web browser built on Firefox ESR. Everything is built in: no extensions needed, no accounts, no sync,
no AI features, nothing sent to Mozilla. Not made, endorsed or supported by Mozilla.

Status: **Linux** (x86_64: `.deb`, `.rpm`, AppImage, tarball and an optimized Arch package) and **Windows** (64-bit, first build, still being tested). Details for Windows are in [`windows/README.md`](windows/README.md).

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

## How much memory does it use?

Measured on one Linux laptop (12 cores, 14 GB RAM), same eight pages in every browser, a fresh profile each time, real memory use (PSS, summed over every process the browser started), run in a hidden display so nothing else competed for the screen.

| Browser | Memory at 45 s | at 90 s | at 150 s | Processes at 150 s |
| --- | --- | --- | --- | --- |
| **Obscurant** (153 ESR base, optimized build) | 911 MB | 1,076 MB | 698 MB* | 8 |
| Brave 158 | 1,065 MB | 1,023 MB | 986 MB | 21 |
| Firefox 160 (stock, default settings) | 2,538 MB | 2,529 MB | 2,433 MB | 54 |

\* Obscurant frees background tabs after 2 minutes (click one to reload it), so the 150 s figure is not the same state as the other two. With every tab still loaded (45 s and 90 s), Obscurant is about the same as Brave and well under half of stock Firefox.

How to read this, honestly:

- **One run per browser on one machine.** Treat differences under about 15% as noise. Results will differ on your computer and with other pages.
- Pages: Wikipedia, GitHub, Hacker News, BBC, The Guardian, Stack Overflow, Arch Linux, YouTube.
- Obscurant and Brave block ads and trackers out of the box, which saves memory on ad-heavy pages. Stock Firefox does not block ads by default, so part of its gap comes from loading them.
- Other browsers (Chrome, Edge and so on) were not installed on the test machine, so they are not listed. No Windows numbers yet.
- Repeat it yourself: `tools/ram_compare.py` (Linux; edit the binary paths at the top and the browser list in `main()`).

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

## Install on Linux

Pick the one for your distro. All files are on the [latest release](https://github.com/mrbalt/obscurant/releases/latest), and `SHA256SUMS-linux` lists their checksums (`sha256sum -c SHA256SUMS-linux`).

| Your distro | What to do |
| --- | --- |
| **Ubuntu, Debian, Linux Mint, Pop!_OS** | Download `obscurant_153.7.0-1_amd64.deb`, then `sudo apt install ./obscurant_153.7.0-1_amd64.deb` |
| **Fedora** | Download `obscurant-153.7.0-1.x86_64.rpm`, then `sudo dnf install ./obscurant-153.7.0-1.x86_64.rpm` (the package is unsigned) |
| **Any distro (one file)** | Download `Obscurant-153.7.0-x86_64.AppImage`, then `chmod +x Obscurant-153.7.0-x86_64.AppImage` and run it |
| **Any distro (unpack and run)** | Download `Obscurant-153.7.0-linux-x86_64.tar.xz`, `tar xf` it, run `Obscurant/start-obscurant`. Run `Obscurant/install.sh` once to add it to your applications menu |
| **Arch, CachyOS, Manjaro** | The optimized package below (faster start), or any of the above |

What to know about the portable builds (`.deb`, `.rpm`, AppImage, tarball):

- They are built with Mozilla's own toolchain and need only **glibc 2.18 or newer** (2014), so they run on practically every current distro.
- Tested by installing and starting in containers: Debian 12, Ubuntu 22.04 and Ubuntu 24.04 (`.deb`), plus the AppImage and tarball on Ubuntu 24.04. **The `.rpm` was checked but not install-tested on Fedora.** Real-desktop testing is limited, so please report problems: https://github.com/mrbalt/obscurant/issues
- They are **not profile-optimized yet**, so they start somewhat slower than the Arch package.
- The blocker lists, search engine policy (DuckDuckGo, Brave Search) and AI switches are built in, same as everywhere else.
- **Voice assistant (optional):** the speech engine is included, but you also need `python3` with `numpy`, `bubblewrap` and PulseAudio/PipeWire's `parecord`, plus the speech model (see `voice/README.txt` in the install folder).
- Not code-signed.

### Arch, CachyOS, Manjaro and other Arch-based (optimized package)

Download `obscurant-*.pkg.tar.zst` from the latest release, then:

    sudo pacman -U obscurant-*.pkg.tar.zst

Optional, for the voice assistant:

    sudo pacman -S whisper-cpp bubblewrap libpulse python-numpy
    mkdir -p ~/.local/share/obscurant/voice
    curl -L -o ~/.local/share/obscurant/voice/ggml-base.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin

Note: this package is built for very new systems (it needs glibc 2.44), so it only runs on Arch-like distros that are fully up to date. Everyone else should use one of the portable builds above.

## Obscurant for Android (early test build)

An Android version built from Firefox for Android (Fenix) and its engine, with the same privacy goals. **This is an early test build (build 3) for 64-bit ARM phones, Android 8.0 or newer, which covers practically every Samsung phone in use.** It has been tested only in Waydroid so far, not yet on a real phone, so expect rough edges and please report problems: https://github.com/mrbalt/obscurant/issues

**Install (Samsung and other phones):**

1. On your phone, download `Obscurant-153.7.0-arm64-v8a.apk` from the [Android release](https://github.com/mrbalt/obscurant/releases/tag/android-153.7.0-1). If you installed an older build, this one installs over it.
2. Samsung blocks installs from outside the Play Store by default. In *Settings, Security and privacy, Auto Blocker*, turn Auto Blocker off while you install. Then allow *Install unknown apps* for the browser or Files app you downloaded it with.
3. Tap the downloaded file and install. If Google Play Protect offers to send the app to Google for scanning, you can choose *Don't send*.
4. Check the file before you install (recommended): its SHA-256 is in `SHA256SUMS-android`, and the signing certificate fingerprint should be `8585a142582dfadb1b6177d90f461de8672598b5296bcd7d51b6598fa7cf28d4`.

How to tell it is Obscurant and not Firefox: a gray hexagon icon, the name "Obscurant", a dark navy look with blue accents, no welcome tour, no sign-in button.

What it does today:

- Its own name, icon, colors and dark theme, and its own app id (`org.obscurant.browser`), so it installs next to Firefox without touching it.
- **No telemetry:** the part of the app that uploads usage data is switched off in the code, not just by a setting. Mozilla's settings server, experiments, sponsored tiles, Pocket, Firefox Suggest and the Mozilla VPN are off. No sign-in, account or sync screens, and no AI features.
- DuckDuckGo is the default search engine, with Brave Search added.
- The built-in ad, tracker and phishing blocker lists are bundled in the app (not yet verified on a real page).
- **VirusTotal download check:** at the bottom of Settings, add your free key (the steps are shown there; also see [docs/VIRUSTOTAL.md](docs/VIRUSTOTAL.md)). Only a download's hash is sent.
- In a clean first-launch test (a fresh install left alone for 150 seconds in Waydroid), the app contacted no Mozilla server.

What it does **not** do yet (honest list):

- None of the other desktop extras: shields panel, themes chooser, new tab page, passwords page, voice assistant, Tor button, update notice, SponsorBlock, Google container.
- The speed-optimized build (this one is a plain build).
- No automatic updates: you install new versions by hand.

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
