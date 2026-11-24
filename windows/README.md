# Windows (experimental, not built yet)

State of the port, honestly:

- **Done in the source** (kept out of the Linux release patch until the next build): the voice assistant and its settings stay hidden and off
  on non-Linux systems, the memory readout falls back safely, and the blocker lists load from inside the app (`chrome://browser/content/lists/`)
  through a Windows-only section in `browser/base/jar.mn`. `windows/mozconfig` is the cross-build configuration.
- **Not done:** an actual Windows build has not been produced or run. Getting the Windows SDK needs Microsoft's license terms to be accepted by
  a person; `tools/build_windows.sh` does that only if you pass `--accept-microsoft-license`.
- **Known gaps for Windows:** no installer yet (a zip of the build folder), no code signing, the VirusTotal scan and update notice are untested
  there, and the speed-optimized (profile-guided) build is Linux only for now.
- Testing on Wine is possible for a first look, but Firefox under Wine is not reliable; a real Windows machine is needed to call it working.
