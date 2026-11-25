#!/usr/bin/env python3
# Builds a per-user MSI (no administrator rights needed) from the portable zip, using wixl from msitools.
import os, shutil, subprocess, sys, tempfile, uuid, zipfile
from xml.sax.saxutils import quoteattr

ZIP, OUT = sys.argv[1:3]
VERSION = os.environ.get("OBSCURANT_MSI_VERSION", "153.7.0.7")
NS = uuid.UUID("6f1c2b9e-5a41-4c8b-9a73-2e5d0c7b1a10")


def guid(s):
    return str(uuid.uuid5(NS, s)).upper()


def main():
    work = tempfile.mkdtemp()
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(work)
    root = os.path.join(work, "Obscurant")
    lines = []
    comps = []
    counter = [0]
    exe_id = [None]

    def nid(prefix):
        counter[0] += 1
        return f"{prefix}{counter[0]}"

    def walk(path, rel):
        out = []
        for name in sorted(os.listdir(path)):
            p = os.path.join(path, name)
            if os.path.isdir(p):
                did = nid("D")
                out.append(f'<Directory Id="{did}" Name={quoteattr(name)}>')
                out += walk(p, rel + "/" + name)
                out.append("</Directory>")
            else:
                cid = nid("C")
                comps.append(cid)
                src = quoteattr(p)
                key = rel + "/" + name
                extra = ""
                if key == "Obscurant/obscurant.exe":
                    exe_id[0] = f"F{counter[0]}"
                    extra = (f'<Shortcut Id="StartMenuShortcut" Directory="ProgramMenuFolder" Name="Obscurant" '
                             f'WorkingDirectory="INSTALLDIR" Advertise="no"/>'
                             f'<Shortcut Id="DesktopShortcut" Directory="DesktopFolder" Name="Obscurant" '
                             f'WorkingDirectory="INSTALLDIR" Advertise="no"/>')
                out.append(f'<Component Id="{cid}" Guid="{guid(key)}">')
                out.append(f'<RegistryValue Root="HKCU" Key="Software\\Obscurant\\Components" Name="{cid}" Type="integer" Value="1" KeyPath="yes"/>')
                out.append(f'<File Id="F{counter[0]}" Name={quoteattr(name)} Source={src}>{extra}</File>')
                out.append("</Component>")
        return out

    body = walk(root, "Obscurant")
    exe = '"[INSTALLDIR]obscurant.exe"'
    CL = "Software\\Clients\\StartMenuInternet\\Obscurant"
    regs = [
        ("Software\\Classes\\ObscurantURL", "", "Obscurant URL"),
        ("Software\\Classes\\ObscurantURL", "URL Protocol", ""),
        ("Software\\Classes\\ObscurantURL\\DefaultIcon", "", "[INSTALLDIR]obscurant.exe,0"),
        ("Software\\Classes\\ObscurantURL\\shell\\open\\command", "", exe + ' -osint -url "%1"'),
        ("Software\\Classes\\ObscurantHTML", "", "Obscurant HTML Document"),
        ("Software\\Classes\\ObscurantHTML\\DefaultIcon", "", "[INSTALLDIR]obscurant.exe,0"),
        ("Software\\Classes\\ObscurantHTML\\shell\\open\\command", "", exe + ' -osint -url "%1"'),
        (CL, "", "Obscurant"),
        (CL + "\\DefaultIcon", "", "[INSTALLDIR]obscurant.exe,0"),
        (CL + "\\shell\\open\\command", "", exe),
        (CL + "\\Capabilities", "ApplicationName", "Obscurant"),
        (CL + "\\Capabilities", "ApplicationDescription", "Private, low-memory web browser"),
        (CL + "\\Capabilities\\URLAssociations", "http", "ObscurantURL"),
        (CL + "\\Capabilities\\URLAssociations", "https", "ObscurantURL"),
        (CL + "\\Capabilities\\FileAssociations", ".htm", "ObscurantHTML"),
        (CL + "\\Capabilities\\FileAssociations", ".html", "ObscurantHTML"),
        (CL + "\\Capabilities\\FileAssociations", ".xhtml", "ObscurantHTML"),
        ("Software\\RegisteredApplications", "Obscurant", "Software\\Clients\\StartMenuInternet\\Obscurant\\Capabilities"),
    ]
    reg_xml = [f'<Component Id="CRegistry" Guid="{guid("registry")}">']
    for i, (k, n, v) in enumerate(regs):
        name = f' Name={quoteattr(n)}' if n else ""
        kp = ' KeyPath="yes"' if i == 0 else ""
        reg_xml.append(f'<RegistryValue Root="HKCU" Key={quoteattr(k)}{name} Type="string" Value={quoteattr(v)}{kp}/>')
    reg_xml.append("</Component>")
    comps.append("CRegistry")
    body += reg_xml
    refs = "".join(f'<ComponentRef Id="{c}"/>' for c in comps)
    lic = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "LICENSE"), encoding="utf-8").read()
    rtf_path = os.path.join(work, "License.rtf")
    esc = lic.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\par\n")
    open(rtf_path, "w", encoding="ascii", errors="replace").write("{\\rtf1\\ansi\\deff0{\\fonts{\\f0 Segoe UI;}}\\f0\\fs18 " + esc.encode("ascii", "replace").decode() + "}")
    wxs = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="Obscurant" Language="1033" Version="{VERSION}" Manufacturer="Obscurant" UpgradeCode="{guid("upgrade")}">
    <Package InstallerVersion="500" Compressed="yes" InstallScope="perUser" Platform="x64"/>
    <MajorUpgrade AllowSameVersionUpgrades="yes" DowngradeErrorMessage="A newer version of Obscurant is already installed."/>
    <Media Id="1" Cabinet="obscurant.cab" EmbedCab="yes"/>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="LocalAppDataFolder">
        <Directory Id="ProgramsDir" Name="Programs">
          <Directory Id="INSTALLDIR" Name="Obscurant">
            {"".join(body)}
          </Directory>
        </Directory>
      </Directory>
      <Directory Id="ProgramMenuFolder"/>
      <Directory Id="DesktopFolder"/>
    </Directory>
    <Feature Id="Main" Title="Obscurant" Level="1">{refs}</Feature>
    <Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOXTEXT" Value="Open Obscurant"/>
    <Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOX" Value="1"/>
    <CustomAction Id="LaunchObscurant" FileKey="{exe_id[0]}" ExeCommand="" Return="asyncNoWait"/>
    <UIRef Id="WixUI_Minimal"/>
  </Product>
  <Fragment>
    <UI>
      <Publish Dialog="ExitDialog" Control="Finish" Event="DoAction" Value="LaunchObscurant" Order="999">WIXUI_EXITDIALOGOPTIONALCHECKBOX = 1 AND NOT Installed</Publish>
    </UI>
  </Fragment>
</Wix>
'''
    wxs_path = os.path.join(work, "obscurant.wxs")
    open(wxs_path, "w").write(wxs)
    subprocess.check_call(["wixl", "-v", "-a", "x64", "--ext", "ui", "-I", work, "-o", os.path.abspath(OUT), wxs_path], cwd=work)
    shutil.rmtree(work)
    print("wrote", OUT, os.path.getsize(OUT) // 1048576, "MB")


main()
