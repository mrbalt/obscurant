# Installs Obscurant for the current user only. No administrator rights needed.
#
# Online:   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1
# Offline:  powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Zip D:\Obscurant-win64-portable.zip
# Remove:   powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1 -Uninstall
#
# Pass -Sha256 <hash> to check the download against a hash you got from a trusted place.
param(
  [string]$Zip,
  [string]$Url = "https://github.com/mrbalt/obscurant/releases/latest/download/Obscurant-win64-portable.zip",
  [string]$Sha256,
  [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$dir = Join-Path $env:LOCALAPPDATA "Programs\Obscurant"
$start = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Obscurant.lnk"
$key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Obscurant"

if ($Uninstall) {
  Get-Process obscurant -ErrorAction SilentlyContinue | Stop-Process -Force
  Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
  Remove-Item -Force $start -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force $key -ErrorAction SilentlyContinue
  Write-Host "Obscurant removed. Your browser profile (bookmarks, passwords) was left alone."
  return
}

$tmp = $null
if (-not $Zip) {
  $tmp = Join-Path $env:TEMP "Obscurant-win64-portable.zip"
  Write-Host "Downloading $Url"
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $tmp
  $Zip = $tmp
}
if (-not (Test-Path $Zip)) { throw "File not found: $Zip" }
$hash = (Get-FileHash -Algorithm SHA256 $Zip).Hash.ToLower()
Write-Host "SHA-256: $hash"
if ($Sha256 -and $hash -ne $Sha256.ToLower()) { throw "SHA-256 does not match the one you gave. Not installing." }

Get-Process obscurant -ErrorAction SilentlyContinue | Stop-Process -Force
$stage = Join-Path $env:TEMP ("obscurant-" + [guid]::NewGuid().ToString("N"))
Expand-Archive -Path $Zip -DestinationPath $stage -Force
if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
New-Item -ItemType Directory -Force -Path (Split-Path $dir) | Out-Null
Move-Item (Join-Path $stage "Obscurant") $dir
Remove-Item -Recurse -Force $stage
if ($tmp) { Remove-Item -Force $tmp }

$exe = Join-Path $dir "obscurant.exe"
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($start)
$lnk.TargetPath = $exe
$lnk.WorkingDirectory = $dir
$lnk.Save()

New-Item -Path $key -Force | Out-Null
Set-ItemProperty $key DisplayName "Obscurant"
Set-ItemProperty $key DisplayVersion "153.7.0"
Set-ItemProperty $key Publisher "Obscurant"
Set-ItemProperty $key InstallLocation $dir
Set-ItemProperty $key DisplayIcon $exe
Set-ItemProperty $key UninstallString "powershell -NoProfile -ExecutionPolicy Bypass -File `"$dir\uninstall.ps1`" -Uninstall"
Set-ItemProperty $key NoModify 1
Set-ItemProperty $key NoRepair 1

$self = $MyInvocation.MyCommand.Path
if ($self) { Copy-Item $self (Join-Path $dir "uninstall.ps1") -Force }
Write-Host "Installed to $dir. Open it from the Start menu."
