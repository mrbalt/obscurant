@echo off
rem Installs Obscurant for this user only. No administrator rights needed.
rem Put this file next to Obscurant-win64-portable.zip for an offline install, or run it alone to download.
set "ZIP=%~dp0Obscurant-win64-portable.zip"
if exist "%ZIP%" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -Zip "%ZIP%"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
)
pause
