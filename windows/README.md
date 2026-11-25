# Obscurant for Windows (64-bit)

Status: **first build, tested only under Wine and by one person on a real Windows PC.** Expect rough edges. Please report problems.

## Downloads (in the Releases page)

| File | What it is |
| --- | --- |
| `Obscurant-win64-portable.zip` | Unzip anywhere and run `Obscurant\obscurant.exe`. No install, no admin rights. |
| `Obscurant-Setup-153.7.0.exe` | Installs for the current user only (no admin rights). Start menu entry, optional desktop shortcut, uninstaller. |
| `Obscurant-153.7.0-win64.msi` | The same files as a per-user MSI. Uninstall any older Obscurant MSI first. |
| `install.cmd`, `install.ps1` | Put them next to the zip for an offline install, or run alone to download the zip. |
| `SHA256SUMS-windows` | Checksums for all of the above. Compare before you run anything. |

## What is Windows-specific

- Installs register Obscurant under **Settings > Apps > Default apps** (current user only).
- The **Hide my IP with Tor** button uses the official `tor.exe` shipped in the `tor` folder (unmodified Tor Expert Bundle).
- The **VirusTotal key** is stored in `%APPDATA%\Obscurant\vt-api-key`. How to get one: [docs/VIRUSTOTAL.md](../docs/VIRUSTOTAL.md).
- Search engines (DuckDuckGo default, Brave Search) and the AI switches come from `distribution\policies.json`, same as on Linux.
- `default-browser-agent.exe` (a Mozilla helper) is removed.

## Known limits

- **Not signed.** Windows SmartScreen will warn. Signing needs a paid certificate.
- **No screen-reader support** (the accessibility component was not built).
- **First start is slow** while Windows scans the program. Later starts are faster.
- Not tuned like the Linux build (no profile-guided optimization), so it is somewhat slower.
- A few Windows 11 window effects are missing (the Windows App SDK DLLs are not included).
- **Voice assistant:** runs the speech engine with reduced Windows rights and a memory cap, but it can still reach the network (the Linux version cannot). The helper writes each phrase to a short-lived file in `%LOCALAPPDATA%\Obscurant\voice-tmp` and deletes it right after. Needs a CPU with AVX2. Microphone capture is untested on real hardware.
- The update notice checks the same version file as the Linux build and does not yet know about Windows releases.

## Building it yourself (Linux host)

This is a cross-build. It needs the Microsoft Windows SDK and Visual C++ tools, which come with Microsoft's license terms: read and accept them yourself.

1. Get the SDK and CRT with `xwin` (`--include-atl`), splat into a folder, and set `WINSYSROOT` to it.
2. Fix the layout Firefox expects: `atlmfc/include` and `atlmfc/lib` links, `x64` links beside the `x86_64` library folders, case-variant header links for names the Mozilla code spells differently.
3. Add the real `ml64.exe` (from the MSVC tools package) and the real `fxc.exe` plus `d3dcompiler_47.dll` (from the Windows SDK installers) under the SDK bin folders. Run with Wine.
4. Provide `MOZ_WINDOWS_RS_DIR` (the `windows` crate source) and a placeholder `MOZ_WINDOWS_APP_SDK_DIR`.
5. Use `mozconfig` here as a template (fill in the `@...@` markers). Build with `./mach build`, then `./mach package`.
6. `tools/make_windows_dist.py` adds the runtime DLLs, voice pack and default settings, scrubs build paths, and refuses to finish if your username is found. `make_windows_installer.py` (needs NSIS) and `make_windows_msi.py` (needs `wixl`) make the installers.

`patches/obscurant-full-with-windows.patch` is the complete source change set for these Windows builds.
