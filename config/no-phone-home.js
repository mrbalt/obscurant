// Found by the network leak test (idle new tab, fresh profile): these were contacted at startup.

// Region lookup (location.services.mozilla.com). Runs when no region is set.
user_pref("browser.search.region", "US");
user_pref("browser.region.network.url", "");

// Plugin downloads (aus5.mozilla.org, update.googleapis.com for Widevine, ciscobinary.openh264.org).
// DRM is switched on from Settings, which turns the Widevine part back on.
user_pref("media.gmp-provider.enabled", false);
user_pref("media.gmp-gmpopenh264.enabled", false);
user_pref("media.gmp-gmpopenh264.visible", false);
user_pref("media.gmp-widevinecdm.enabled", false);
user_pref("media.gmp-widevinecdm.visible", false);
user_pref("media.gmp-widevinecdm-l1.enabled", false);
user_pref("media.gmp-widevinecdm-l1.visible", false);

// Add-on metadata check (services.addons.mozilla.org) when nothing is installed.
user_pref("extensions.getAddons.cache.enabled", false);

// The plugin manager address stays empty until DRM is switched on in Settings.
user_pref("media.gmp-manager.url", "");

// System add-on update address (aus5.mozilla.org): no system add-on updates are wanted.
user_pref("extensions.systemAddon.update.url", "");

// Defence in depth for the plugin and Safe Browsing updaters.
user_pref("media.gmp-manager.updateEnabled", false);
user_pref("browser.safebrowsing.update.enabled", false);

// Firefox Suggest downloads its data through its own Remote Settings client.
user_pref("browser.urlbar.quicksuggest.enabled", false);
user_pref("browser.urlbar.quicksuggest.rustEnabled", false);
user_pref("browser.urlbar.suggest.quicksuggest.nonsponsored", false);
user_pref("browser.urlbar.suggest.quicksuggest.sponsored", false);

// Help and feedback links point at Firefox pages; with these empty they open nothing.
user_pref("app.support.baseURL", "");
user_pref("app.feedback.baseURL", "");
user_pref("browser.geolocation.warning.infoURL", "");
user_pref("browser.search.searchEnginesURL", "");
user_pref("app.normandy.shieldLearnMoreUrl", "");
