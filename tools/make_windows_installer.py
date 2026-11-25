#!/usr/bin/env python3
# Builds the per-user Setup.exe (NSIS) from the portable zip. Needs makensis; set MAKENSIS and NSISDIR if it is not on PATH.
import os, shutil, subprocess, sys, tempfile, zipfile

ZIP, OUT = sys.argv[1:3]
VERSION = os.environ.get("OBSCURANT_VERSION", "153.7.0")
MAKENSIS = os.environ.get("MAKENSIS", "makensis")

NSI = r'''Unicode true
!include "MUI2.nsh"
Name "Obscurant"
OutFile "@OUT@"
RequestExecutionLevel user
InstallDir "$LOCALAPPDATA\Programs\Obscurant"
SetCompressor /SOLID lzma
SetCompressorDictSize 64
VIProductVersion "@VER@.0"
VIAddVersionKey "ProductName" "Obscurant"
VIAddVersionKey "FileDescription" "Obscurant installer"
VIAddVersionKey "FileVersion" "@VER@"
VIAddVersionKey "LegalCopyright" "Mozilla Public License 2.0"

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\obscurant.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Open Obscurant"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Add a shortcut to the desktop"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION AddDesktopShortcut
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function AddDesktopShortcut
  CreateShortcut "$DESKTOP\Obscurant.lnk" "$INSTDIR\obscurant.exe"
FunctionEnd

Section "Install"
  nsExec::Exec 'taskkill /F /IM obscurant.exe'
  RMDir /r "$INSTDIR"
  SetOutPath "$INSTDIR"
  File /r "@SRC@\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateShortcut "$SMPROGRAMS\Obscurant.lnk" "$INSTDIR\obscurant.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "DisplayName" "Obscurant"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "DisplayVersion" "@VER@"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "Publisher" "Obscurant"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "DisplayIcon" "$INSTDIR\obscurant.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant" "NoRepair" 1
  WriteRegStr HKCU "Software\Classes\ObscurantURL" "" "Obscurant URL"
  WriteRegStr HKCU "Software\Classes\ObscurantURL" "URL Protocol" ""
  WriteRegStr HKCU "Software\Classes\ObscurantURL\DefaultIcon" "" "$INSTDIR\obscurant.exe,0"
  WriteRegStr HKCU "Software\Classes\ObscurantURL\shell\open\command" "" '"$INSTDIR\obscurant.exe" -osint -url "%1"'
  WriteRegStr HKCU "Software\Classes\ObscurantHTML" "" "Obscurant HTML Document"
  WriteRegStr HKCU "Software\Classes\ObscurantHTML\DefaultIcon" "" "$INSTDIR\obscurant.exe,0"
  WriteRegStr HKCU "Software\Classes\ObscurantHTML\shell\open\command" "" '"$INSTDIR\obscurant.exe" -osint -url "%1"'
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant" "" "Obscurant"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\DefaultIcon" "" "$INSTDIR\obscurant.exe,0"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\shell\open\command" "" '"$INSTDIR\obscurant.exe"'
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities" "ApplicationName" "Obscurant"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities" "ApplicationDescription" "Private, low-memory web browser"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities\URLAssociations" "http" "ObscurantURL"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities\URLAssociations" "https" "ObscurantURL"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities\FileAssociations" ".htm" "ObscurantHTML"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities\FileAssociations" ".html" "ObscurantHTML"
  WriteRegStr HKCU "Software\Clients\StartMenuInternet\Obscurant\Capabilities\FileAssociations" ".xhtml" "ObscurantHTML"
  WriteRegStr HKCU "Software\RegisteredApplications" "Obscurant" "Software\Clients\StartMenuInternet\Obscurant\Capabilities"
SectionEnd

Section "Uninstall"
  nsExec::Exec 'taskkill /F /IM obscurant.exe'
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\Obscurant.lnk"
  Delete "$DESKTOP\Obscurant.lnk"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant"
  DeleteRegKey HKCU "Software\Classes\ObscurantURL"
  DeleteRegKey HKCU "Software\Classes\ObscurantHTML"
  DeleteRegKey HKCU "Software\Clients\StartMenuInternet\Obscurant"
  DeleteRegValue HKCU "Software\RegisteredApplications" "Obscurant"
SectionEnd
'''


def main():
    work = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(work)
    src = os.path.join(work, "Obscurant")
    out = os.path.abspath(OUT)
    nsi = NSI.replace("@OUT@", out).replace("@SRC@", src).replace("@VER@", VERSION)
    path = os.path.join(work, "setup.nsi")
    open(path, "w").write(nsi)
    subprocess.check_call([MAKENSIS, "-V2", path])
    raw = open(out, "rb").read()
    for s in (os.path.basename(os.path.expanduser("~")).encode(), os.path.expanduser("~").encode()):
        if s in raw:
            os.remove(out)
            sys.exit("personal string in installer binary: " + s.decode())
    shutil.rmtree(work)
    print("wrote", out, os.path.getsize(out) // 1048576, "MB")


main()
