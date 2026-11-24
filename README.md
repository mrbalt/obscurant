# Obscurant

A private, low-memory, fast web browser built on Firefox ESR. Everything is built in: no extensions needed, no accounts, no sync,
no AI features, nothing sent to Mozilla. Not made, endorsed or supported by Mozilla.

Status: works on Linux (x86_64, packaged for Arch-based systems). Windows is experimental and not released yet.

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

## Install (Arch, CachyOS, Manjaro and other Arch-based)

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
