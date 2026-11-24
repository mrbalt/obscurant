// Built-in adblock-rust content classifier (ships in Firefox ESR 153, off by default).
// Lists are read from disk via file:// URLs, no network.
// test_block: ads and trackers. test_phish: phishing/malware, shows the native warning page.

user_pref("privacy.trackingprotection.content.protection.enabled", true);
user_pref("privacy.trackingprotection.content.protection.engines", "test_block,test_phish");
user_pref("privacy.trackingprotection.content.protection.engines.pbmode", "test_block,test_phish");
user_pref("privacy.trackingprotection.content.protection.test_list_urls", "file:///home/USER/Projects/browser/config/lists/easylist.txt|file:///home/USER/Projects/browser/config/lists/easyprivacy.txt|file:///home/USER/Projects/browser/config/lists/ublock.txt|file:///home/USER/Projects/browser/config/lists/brave.txt");
user_pref("privacy.trackingprotection.content.protection.phishing_list_urls", "file:///home/USER/Projects/browser/config/lists/phishing-abp.txt");
