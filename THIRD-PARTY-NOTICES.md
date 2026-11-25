# Obscurant: licenses and third-party notices

Obscurant is a modified build of Mozilla Firefox ESR 153.7.0. It is not made, endorsed or supported by Mozilla.
Firefox and the Mozilla logos are trademarks of the Mozilla Foundation. Obscurant uses its own name and artwork.

## The browser and our changes

- Firefox source: Mozilla Public License 2.0 (see `LICENSE`, and `about:license` inside the browser for the full set of licenses
  covering the third-party code Firefox contains).
- Our changes are published under the same MPL 2.0. New source files carry the MPL header. The complete set of changes is the
  patch `pkg/obscurant-full.patch`, applied to the unmodified source tarball from archive.mozilla.org.
- Corresponding source for any binary release: that tarball plus this repository (patch, `config/`, `tools/`, `pkg/`).
- The browser reports a stock Firefox user-agent string for web-site compatibility only. This does not mean it is Firefox.

## Bundled data (shipped as separate files, with their own licenses)

| What | Source | License |
| --- | --- | --- |
| EasyList, EasyPrivacy | easylist.to | GPLv3 or CC BY-SA 3.0 |
| uBlock Origin filter lists (rules our engine does not support removed) | github.com/uBlockOrigin/uAssets | GPLv3 |
| Brave adblock lists (script rules removed) | github.com/brave/adblock-lists | MPL 2.0 |
| Phishing URL blocklist (converted to blocker rules) | gitlab.com/malware-filter/phishing-filter, built from OpenPhish, PhishTank and ipthreat | CC BY-SA 4.0 for the list; see upstream for its sources |
| URLhaus malicious URL list (optional, not enabled by default) | gitlab.com/malware-filter/urlhaus-filter, from abuse.ch | CC0 and MIT |
| AI generator site list | written for Obscurant | MPL 2.0 |

The ad blocking engine is `adblock-rust` (github.com/brave/adblock-rust, MPL 2.0), which is part of the Firefox source tree.

## Fonts (new tab page)

Akronim, Alumni Sans Collegiate One, Astloch, Bungee Hairline, Danfo, Honk, Kablammo, Londrina Sketch, Raleway Dots,
Rubik 80s Fade, Rubik Distressed, Rubik Puddles, Silkscreen and Sixtyfour are licensed under the SIL Open Font License 1.1.
Each license text ships next to the font files (`fonts/OFL-*.txt`). The fonts are not sold on their own.

## Theme colors

The color themes (Nord, Dracula, Gruvbox, Solarized, Catppuccin, Tokyo Night, One Dark, Rose Pine, Monokai, Everforest, Kanagawa,
Ayu and others) reproduce the published color palettes of those projects. Names belong to their authors. No theme code is copied.

## Optional services and programs (not shipped; used only if you turn them on)

- **SponsorBlock** (sponsor.ajay.app): the browser can ask the SponsorBlock API for skip segments. The data is by the SponsorBlock
  contributors, CC BY-NC-SA 4.0 (non-commercial). Off by default. Do not use this feature in a commercial product.
- **VirusTotal**: download scans use your own API key and are subject to VirusTotal's terms. Do not share keys, and the free key is
  for personal, non-commercial use. Obscurant sends only the file hash.
- **whisper.cpp** (MIT) and OpenAI Whisper model weights (MIT): used by the Obscurity voice assistant, installed separately.
  Speech is processed on your computer only.
- **Tor**: installed separately, used only if you start it from Settings.

## Warranty

No warranty. There is no automatic update service. Security fixes arrive only when a new package is installed.

## Windows voice assistant pack
- **Python embeddable distribution** (Python Software Foundation License): runs the voice helper on Windows.
- **NumPy** (BSD-3-Clause): audio maths in the voice helper.
- **python-sounddevice** (MIT) and **PortAudio** (MIT): microphone access on Windows.
- **CFFI** (MIT) and **pycparser** (BSD-3-Clause): needed by python-sounddevice.
- **whisper.cpp** (MIT) and OpenAI Whisper `base.en` weights (MIT): speech recognition, built from the same release as the Linux package.
- **Microsoft Visual C++ runtime** (vcruntime140, msvcp140): redistributed under Microsoft's redistribution terms for Visual Studio.
