import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "config" / "themes"
POLICIES = ROOT / "config" / "policies.json"
SETUP_JS = ROOT / "src" / "firefox-153.7.0" / "browser" / "components" / "aboutwelcome" / "content" / "obscurant-themes.js"
URL_BASE = "file:///home/USER/Projects/browser/config/themes/"

# name, frame, toolbar, field, text, subtext, accent, border
PALETTES = [
    ("BlackGlass", "#121212", "#1f1f1f", "#343434", "#eeeeee", "#cacaca", "#ff5500", "#4e5050"),
    ("Utterly Nord", "#242933", "#2e3440", "#3b4252", "#eceff4", "#d8dee9", "#88c0d0", "#4c566a"),
    ("Nord Light", "#d8dee9", "#e5e9f0", "#eceff4", "#2e3440", "#4c566a", "#5e81ac", "#b8c0d0"),
    ("Dracula", "#21222c", "#282a36", "#44475a", "#f8f8f2", "#b6b8c8", "#bd93f9", "#44475a"),
    ("Gruvbox Dark", "#1d2021", "#282828", "#3c3836", "#ebdbb2", "#a89984", "#fabd2f", "#504945"),
    ("Gruvbox Light", "#ebdbb2", "#fbf1c7", "#f2e5bc", "#3c3836", "#665c54", "#d65d0e", "#d5c4a1"),
    ("Solarized Dark", "#00212b", "#002b36", "#073642", "#93a1a1", "#839496", "#b58900", "#0b4350"),
    ("Solarized Light", "#eee8d5", "#fdf6e3", "#eee8d5", "#586e75", "#657b83", "#268bd2", "#d6cfb8"),
    ("Catppuccin Mocha", "#11111b", "#1e1e2e", "#313244", "#cdd6f4", "#a6adc8", "#cba6f7", "#45475a"),
    ("Catppuccin Macchiato", "#181926", "#24273a", "#363a4f", "#cad3f5", "#a5adcb", "#c6a0f6", "#494d64"),
    ("Catppuccin Frappe", "#232634", "#303446", "#414559", "#c6d0f5", "#a5adce", "#ca9ee6", "#51576d"),
    ("Catppuccin Latte", "#dce0e8", "#eff1f5", "#e6e9ef", "#4c4f69", "#6c6f85", "#8839ef", "#ccd0da"),
    ("Tokyo Night", "#16161e", "#1a1b26", "#24283b", "#c0caf5", "#a9b1d6", "#7aa2f7", "#3b4261"),
    ("One Dark", "#21252b", "#282c34", "#2c313a", "#abb2bf", "#828997", "#61afef", "#3e4451"),
    ("Rose Pine", "#16141f", "#191724", "#26233a", "#e0def4", "#908caa", "#c4a7e7", "#403d52"),
    ("Rose Pine Dawn", "#f2e9e1", "#faf4ed", "#fffaf3", "#575279", "#797593", "#d7827e", "#dfdad9"),
    ("Monokai", "#1e1f1c", "#272822", "#3e3d32", "#f8f8f2", "#cfcfc2", "#a6e22e", "#49483e"),
    ("Everforest Dark", "#232a2e", "#2d353b", "#343f44", "#d3c6aa", "#9da9a0", "#a7c080", "#475258"),
    ("Kanagawa", "#16161d", "#1f1f28", "#2a2a37", "#dcd7ba", "#c8c093", "#7e9cd8", "#363646"),
    ("Ayu Dark", "#090d13", "#0b0e14", "#131721", "#bfbdb6", "#acb6bf", "#e6b450", "#1f2430"),
    ("Ayu Mirage", "#171b24", "#1f2430", "#272d38", "#cccac2", "#a0a3a8", "#ffcc66", "#343b4d"),
    ("Ayu Light", "#e7e8e9", "#fcfcfc", "#f0f0f0", "#5c6166", "#787b80", "#ff9940", "#d9d8d7"),
    ("Material Ocean", "#090b10", "#0f111a", "#1a1c25", "#a6accd", "#8f93a2", "#84ffff", "#292d3e"),
    ("Oceanic", "#162229", "#1b2b34", "#343d46", "#d8dee9", "#a7adba", "#6699cc", "#4f5b66"),
    ("Midnight Blue", "#070b19", "#0d1330", "#18214a", "#e6ecff", "#a9b4e0", "#5b8cff", "#26306a"),
    ("Terminal Green", "#000000", "#050a05", "#0d1a0d", "#33ff66", "#29cc52", "#66ff99", "#145214"),
    ("Amber CRT", "#0a0600", "#120b00", "#1f1400", "#ffb000", "#cc8d00", "#ffd166", "#4a3000"),
    ("Cyberpunk", "#0d0221", "#150535", "#240b50", "#f3e9ff", "#c3a8ff", "#ff2a6d", "#3b1a78"),
    ("Sunset", "#1f1220", "#2b1b2e", "#3d2640", "#ffe3cc", "#e0b9a0", "#ff7a59", "#5a3a5e"),
    ("Deep Forest", "#0b1510", "#112018", "#1b3326", "#dff5e6", "#a9cdb5", "#6fcf97", "#285038"),
    ("Ocean Deep", "#04141c", "#082230", "#0f3347", "#d6f0ff", "#9cc7df", "#2bb3d6", "#1b516b"),
    ("Crimson Night", "#140608", "#1d0a0e", "#2e1117", "#ffe5e8", "#d9a6ad", "#e63946", "#4a1c25"),
    ("Lavender Dusk", "#17142a", "#1f1b38", "#2d2850", "#eae6ff", "#b9b0e8", "#9d8cff", "#433c7a"),
    ("Graphite", "#1a1a1a", "#242424", "#303030", "#e6e6e6", "#b0b0b0", "#9e9e9e", "#3d3d3d"),
    ("High Contrast Dark", "#000000", "#000000", "#1a1a1a", "#ffffff", "#e0e0e0", "#ffff00", "#ffffff"),
    ("High Contrast Light", "#ffffff", "#ffffff", "#f0f0f0", "#000000", "#202020", "#0000ee", "#000000"),
    ("Paper", "#e9e6df", "#f6f4ee", "#ffffff", "#2b2b2b", "#5c5c5c", "#b5543a", "#d6d2c8"),
    ("Sepia", "#e6d9bd", "#f4ecd8", "#fbf5e6", "#5b4636", "#7d6551", "#a0522d", "#d3c4a2"),
    ("Mint", "#d8efe3", "#eaf8f1", "#ffffff", "#1d3b2f", "#46695a", "#2e9e6f", "#bfe0d0"),
    ("Rose Quartz", "#f2d9df", "#fbeaee", "#ffffff", "#4a2631", "#774f5b", "#d6527a", "#e6c4cc"),
    ("Sky", "#d6e8fa", "#e9f3fd", "#ffffff", "#14304d", "#48688a", "#2f80ed", "#bcd3ea"),
    ("Lemon", "#f6efc2", "#fcf8dc", "#ffffff", "#3d3a1b", "#66622f", "#c9a800", "#e5dc9c"),
]


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def lum(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def slug(name):
    return name.lower().replace(" ", "-")


def manifest(p):
    name, frame, toolbar, field, text, sub, accent, border = p
    light = lum(toolbar) > 0.4
    colors = {
        "frame": frame, "frame_inactive": frame,
        "toolbar": toolbar, "toolbar_text": text,
        "tab_text": text, "tab_background_text": sub,
        "tab_selected": field, "tab_line": accent,
        "toolbar_field": field, "toolbar_field_text": text,
        "toolbar_field_border": border, "toolbar_field_focus": field,
        "toolbar_field_text_focus": text,
        "popup": toolbar, "popup_text": text, "popup_border": border,
        "sidebar": toolbar, "sidebar_text": text,
        "ntp_background": frame, "ntp_text": text, "icons": text,
    }
    return {
        "manifest_version": 2,
        "name": name,
        "version": "1.0",
        "description": f"{name} theme for Obscurant",
        "browser_specific_settings": {"gecko": {"id": f"{slug(name)}@local"}},
        "theme": {
            "colors": {k: rgb(v) for k, v in colors.items()},
            "properties": {"color_scheme": "light" if light else "dark"},
        },
    }


def main():
    src = ROOT / "src" / "firefox-153.7.0" / "browser" / "themes"
    addons = src / "addons" / "obscurant"
    addons.mkdir(parents=True, exist_ok=True)
    weak = []
    jar = ["# Generated by tools/make_themes.py. Do not edit.", "", "browser.jar:"]
    cfg = []
    for p in PALETTES:
        s_ = slug(p[0])
        d = addons / s_
        d.mkdir(exist_ok=True)
        (d / "manifest.json").write_text(json.dumps(manifest(p), indent=2) + "\n")
        jar.append(f"  content/builtin-themes/obscurant/{s_}/manifest.json (obscurant/{s_}/manifest.json)")
        cfg.append(f'  [\n    "{s_}@local",\n    {{\n      version: "1.0",\n      path: "resource://builtin-themes/obscurant/{s_}/",\n    }},\n  ],')
        _, frame, toolbar, field, text, sub, accent, border = p
        checks = {"text/toolbar": contrast(text, toolbar), "text/field": contrast(text, field),
                  "sub/toolbar": contrast(sub, toolbar), "text/frame": contrast(text, frame)}
        bad = {k: round(v, 1) for k, v in checks.items() if v < (3.0 if k.startswith("sub") else 4.5)}
        if bad:
            weak.append((p[0], bad))
    jarfile = src / "addons" / "jar.mn"
    jt = jarfile.read_text()
    jb, je = "# BEGIN OBSCURANT\n", "# END OBSCURANT\n"
    jblock = jb + "\n".join(jar[3:]) + "\n" + je
    if jb in jt:
        jt = jt[:jt.index(jb)] + jblock + jt[jt.index(je) + len(je):]
    else:
        jt = jt.rstrip("\n") + "\n\n" + jblock
    jarfile.write_text(jt)

    conf = src / "BuiltInThemeConfig.sys.mjs"
    text_ = conf.read_text()
    begin, end = "  // BEGIN OBSCURANT\n", "  // END OBSCURANT\n"
    block = begin + "\n".join(cfg) + "\n" + end
    if begin in text_:
        a = text_.index(begin)
        b = text_.index(end) + len(end)
        text_ = text_[:a] + block + text_[b:]
    else:
        text_ = text_.replace("]);", block + "]);", 1) if text_.rstrip().endswith("]);") else text_
    conf.write_text(text_)

    js = ["/* This Source Code Form is subject to the terms of the Mozilla Public", " * License, v. 2.0. If a copy of the MPL was not distributed with this", " * file, You can obtain one at http://mozilla.org/MPL/2.0/. */", "", "/* Generated by tools/make_themes.py. Do not edit. */", "window.OBSCURANT_THEMES = ["]
    for q in PALETTES:
        n, fr, tb, fd, tx, sb, ac, bd = q
        js.append(f'  {{ id: "{slug(n)}@local", name: "{n}", frame: "{fr}", toolbar: "{tb}", field: "{fd}", text: "{tx}", sub: "{sb}", accent: "{ac}", border: "{bd}" }},')
    js.append("];")
    SETUP_JS.write_text("\n".join(js) + "\n")

    policy = json.loads(POLICIES.read_text())
    policy["policies"]["ExtensionSettings"] = {"*": {"installation_mode": "blocked"}}
    POLICIES.write_text(json.dumps(policy, indent=2) + "\n")
    print(f"built {len(PALETTES)} built-in themes")
    print("low contrast:" if weak else "all contrast checks passed")
    for n, b in weak:
        print(" ", n, b)


main()
