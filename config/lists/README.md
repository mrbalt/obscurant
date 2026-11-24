# Filter lists

- easylist.txt, easyprivacy.txt from https://easylist.to/ (version 202611220945, downloaded 2026-11-22).
- Licence: dual licensed GPLv3 and CC BY-SA 3.0. Keep attribution and this notice when redistributing.
- Update by re-downloading; lists expire after about 4 days. The browser never fetches them by itself.

## Phishing and malware lists (replace Google Safe Browsing)

- phishing-filter.txt: https://curbengh.github.io/malware-filter/phishing-filter.txt, from gitlab.com/malware-filter/phishing-filter. Sources: OpenPhish, PhishTank, ipthreat. Licence: CC BY-SA 4.0 for the published list. Expires every 12 hours.
- phishing-abp.txt: the same list converted to `||host^` rules for the blocker. This one is enabled.
- urlhaus-filter-online.txt: malware hosts from abuse.ch URLhaus (CC0 and MIT). 112k mostly-IP entries, 12 MB. Downloaded but NOT enabled: measure its memory cost in the engine first.
