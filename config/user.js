// Hardening prefs, every name verified to exist in Firefox ESR 153.7.0 source.
// Test-profile version; later these become build-time defaults.

// Telemetry and reporting
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.server", "data:,");
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("browser.newtabpage.activity-stream.telemetry", false);

// Studies / experiments
user_pref("app.normandy.enabled", false);
user_pref("app.normandy.api_url", "");
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("nimbus.rollouts.enabled", false);

// Safe Browsing fully off (no Google contact). Replaced locally by malware
// and phishing lists in the built-in blocker, and VirusTotal for downloads.
user_pref("browser.safebrowsing.malware.enabled", false);
user_pref("browser.safebrowsing.phishing.enabled", false);
user_pref("browser.safebrowsing.downloads.enabled", false);
user_pref("browser.safebrowsing.downloads.remote.enabled", false);

// Background connectivity and location
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
user_pref("browser.region.update.enabled", false);
user_pref("geo.provider.use_geoclue", false);
user_pref("browser.discovery.enabled", false);

// New tab sponsored content
user_pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);

// Search suggestions and speculative connections
user_pref("browser.search.suggest.enabled", false);
user_pref("browser.urlbar.suggest.searches", false);
user_pref("network.prefetch-next", false);
user_pref("network.dns.disablePrefetch", true);
user_pref("network.http.speculative-parallel-limit", 0);
user_pref("browser.places.speculativeConnect.enabled", false);
user_pref("browser.urlbar.speculativeConnect.enabled", false);

// DNS over HTTPS off (uses system DNS); no accounts; updates via pacman
user_pref("network.trr.mode", 5);
user_pref("identity.fxaccounts.enabled", false);
user_pref("app.update.auto", false);
user_pref("extensions.update.enabled", false);

// WebRTC stays enabled, local-address leak closed
user_pref("media.peerconnection.ice.default_address_only", true);
user_pref("media.peerconnection.ice.no_host", false);

// Fingerprinting: lighter protection (no resistFingerprinting, avoids breakage)
user_pref("privacy.fingerprintingProtection", true);
user_pref("privacy.resistFingerprinting", false);

// Cookie partitioning (Total Cookie Protection) and containers
user_pref("network.cookie.cookieBehavior", 5);
user_pref("privacy.userContext.enabled", true);

// RAM
user_pref("browser.tabs.unloadOnLowMemory", false);
user_pref("browser.sessionhistory.max_total_viewers", 2);

// BlackGlass theme (built in)
user_pref("extensions.activeThemeID", "blackglass@local");

// DRM on demand: off until a site needs it, then one click (see policies.json)
user_pref("media.eme.enabled", false);

// No location at all: no geolocation API, no Wi-Fi/IP location lookups
user_pref("geo.enabled", false);
user_pref("geo.provider.network.url", "");
user_pref("geo.provider.use_geoclue", false);

// New tab: no weather, no location lookups, no Mozilla ad/story/recommendation services
user_pref("browser.newtabpage.activity-stream.showWeather", false);
user_pref("browser.newtabpage.activity-stream.system.showWeather", false);
user_pref("browser.newtabpage.activity-stream.weather.locationSearchEnabled", false);
user_pref("browser.newtabpage.activity-stream.feeds.weatherfeed", false);
user_pref("browser.newtabpage.activity-stream.feeds.adsfeed", false);
user_pref("browser.newtabpage.activity-stream.feeds.wallpaperfeed", false);
user_pref("browser.newtabpage.activity-stream.feeds.inferredpersonalizationfeed", false);
user_pref("browser.newtabpage.activity-stream.discoverystream.enabled", false);
user_pref("browser.newtabpage.activity-stream.unifiedAds.tiles.enabled", false);
user_pref("browser.newtabpage.activity-stream.unifiedAds.spocs.enabled", false);
user_pref("browser.newtabpage.activity-stream.discoverystream.merino-provider.endpoint", "");
user_pref("browser.urlbar.merino.endpointURL", "");
user_pref("browser.urlbar.merino.weather.reportEndpointURL", "");
user_pref("browser.urlbar.merino.weather.hourlyEndpointURL", "");
user_pref("browser.newtabpage.activity-stream.discoverystream.endpointSpocsClear", "");
user_pref("browser.newtabpage.activity-stream.discoverystream.endpoints", "");

// Firefox's own tracker and ad blocking is off. Only the built-in
// Brave-style (adblock-rust) blocker blocks anything.
user_pref("browser.contentblocking.category", "custom");
user_pref("privacy.trackingprotection.enabled", false);
user_pref("privacy.trackingprotection.pbmode.enabled", false);
user_pref("privacy.trackingprotection.fingerprinting.enabled", false);
user_pref("privacy.trackingprotection.cryptomining.enabled", false);
user_pref("privacy.trackingprotection.socialtracking.enabled", false);
user_pref("privacy.trackingprotection.emailtracking.enabled", false);
user_pref("privacy.trackingprotection.emailtracking.pbmode.enabled", false);
user_pref("privacy.trackingprotection.harmfuladdon.enabled", false);
user_pref("privacy.trackingprotection.annotate_channels", false);
user_pref("privacy.annotate_channels.strict_list.enabled", false);
user_pref("privacy.socialtracking.block_cookies.enabled", false);
user_pref("urlclassifier.trackingTable", "");
user_pref("urlclassifier.trackingWhitelistTable", "");
user_pref("urlclassifier.trackingAnnotationTable", "");
user_pref("urlclassifier.trackingAnnotationWhitelistTable", "");
user_pref("urlclassifier.features.fingerprinting.blacklistTables", "");
user_pref("urlclassifier.features.fingerprinting.annotate.blacklistTables", "");
user_pref("urlclassifier.features.cryptomining.blacklistTables", "");
user_pref("urlclassifier.features.cryptomining.annotate.blacklistTables", "");
user_pref("urlclassifier.features.socialtracking.blacklistTables", "");
user_pref("urlclassifier.features.socialtracking.annotate.blacklistTables", "");
user_pref("urlclassifier.features.emailtracking.blocklistTables", "");
user_pref("urlclassifier.features.emailtracking.datacollection.blocklistTables", "");
user_pref("urlclassifier.features.consentmanager.annotate.blocklistTables", "");
user_pref("urlclassifier.features.antifraud.annotate.blocklistTables", "");
user_pref("urlclassifier.features.harmfuladdon.blocklistTables", "");
user_pref("browser.safebrowsing.provider.mozilla.updateURL", "");
user_pref("browser.safebrowsing.provider.mozilla.gethashURL", "");
user_pref("browser.safebrowsing.provider.mozilla.lists", "");

// Tab bar hides until the mouse reaches the top edge
user_pref("obscurant.tabs.autohide", true);
user_pref("browser.startup.homepage.abouthome_cache.enabled", false);
user_pref("privacy.query_stripping.enabled", true);
user_pref("security.tls.enable_0rtt_data", false);
user_pref("extensions.htmlaboutaddons.recommendations.enabled", false);
user_pref("signon.rememberSignons", false);

// Dark by default: websites that support it get their dark version (0 dark, 1 light, 2 system).
user_pref("layout.css.prefers-color-scheme.content-override", 0);
user_pref("browser.theme.toolbar-theme", 0);
user_pref("browser.theme.content-theme", 0);

// Phishing list refresh: downloads one public list file hourly (no page addresses are sent).
user_pref("obscurant.lists.autoupdate", true);
user_pref("obscurant.lists.interval_min", 15);
user_pref("obscurant.lists.phishing_url", "https://curbengh.github.io/malware-filter/phishing-filter.txt");

// Launch animation (overlay, never blocks startup)
user_pref("obscurant.splash.enabled", true);

// No per-site certificate revocation lookups (they tell a third party which site you visit).
// CRLite (local list via Remote Settings) stays on.
user_pref("security.OCSP.enabled", 0);

// AI filters (shield panel). Off by default; each is its own switch.
user_pref("obscurant.ai.hide", false);
user_pref("obscurant.ai.skip", false);
user_pref("obscurant.ai.images", false);
user_pref("obscurant.ai.block_sites", false);

// SponsorBlock (built in). Off by default: it contacts sponsor.ajay.app.
user_pref("obscurant.sponsorblock.enabled", false);
user_pref("obscurant.sponsorblock.cat.sponsor", true);
user_pref("obscurant.sponsorblock.cat.selfpromo", true);
user_pref("obscurant.sponsorblock.cat.interaction", true);
user_pref("obscurant.sponsorblock.cat.intro", false);
user_pref("obscurant.sponsorblock.cat.outro", false);
user_pref("obscurant.sponsorblock.cat.preview", false);
user_pref("obscurant.sponsorblock.cat.music_offtopic", false);

// Voice assistant "Obscurity": off by default. Everything runs on this computer.
user_pref("obscurant.voice.enabled", false);
user_pref("obscurant.voice.wake", "hey obscurity");
user_pref("obscurant.voice.confirm_new_sites", true);
user_pref("obscurant.voice.require_focus", true);
user_pref("obscurant.voice.dictation", false);
user_pref("obscurant.voice.during_sound", false);
user_pref("obscurant.voice.wake_enabled", true);
user_pref("obscurant.voice.key", "Ctrl+Shift+Space");

// Present as stock Firefox to sites (Discord and others refuse unknown browser names)
user_pref("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0");

// Update notices (notify only; nothing is downloaded or installed by the browser).
// The address stays empty until builds are published. The key verifies the signed version file.
user_pref("obscurant.update.enabled", true);
user_pref("obscurant.update.url", "https://github.com/mrbalt/obscurant/releases/latest/download/latest.json");
user_pref("obscurant.update.pubkey", "2dCa341JCuEBKU5C01zE84AJ0StigPwY/3/XIVOfmJY=");
user_pref("obscurant.update.build", 1);
