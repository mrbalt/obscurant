// RAM diet, safe set. All names verified in Firefox ESR 153.7.0 source.

// Fewer idle spare processes
user_pref("dom.ipc.processPrelaunch.fission.number", 1);
user_pref("browser.newtab.preload", false);

// Smaller decoded-image and media buffers
user_pref("image.mem.surfacecache.max_size_kb", 262144);
user_pref("image.mem.surfacecache.min_expiration_ms", 15000);
user_pref("media.memory_caches_combined_limit_kb", 131072);

// Smaller history and session state
user_pref("browser.sessionstore.max_tabs_undo", 5);
user_pref("browser.sessionhistory.max_entries", 20);

// Built-in AI and promo features off (no ML process)
user_pref("browser.ml.enable", false);
user_pref("browser.ml.chat.enabled", false);
user_pref("browser.ml.linkPreview.enabled", false);
user_pref("browser.translations.enable", false);
user_pref("browser.tabs.groups.smart.enabled", false);
user_pref("browser.vpn_promo.enabled", false);
user_pref("browser.topsites.contile.enabled", false);

// Fewer background calls
user_pref("extensions.systemAddon.update.enabled", false);
user_pref("services.settings.poll_interval", 604800);

// Fewer idle content processes (site isolation stays on)
user_pref("dom.ipc.processPrelaunch.fission.number", 0);
user_pref("dom.ipc.processReuse.unusedGraceMs", 1000);

// Round 2: no site breakage, no security change
user_pref("browser.sessionstore.max_tabs_undo", 3);
user_pref("browser.cache.memory.capacity", 32768);
user_pref("network.dnsCacheEntries", 200);
user_pref("gfx.content.skia-font-cache-size", 10);
user_pref("extensions.formautofill.addresses.enabled", false);
user_pref("extensions.formautofill.creditCards.enabled", false);
user_pref("network.captive-portal-service.enabled", false);
user_pref("browser.tabs.hoverPreview.enabled", false);
user_pref("browser.tabs.hoverPreview.showThumbnails", false);
user_pref("browser.sessionstore.restore_tabs_lazily", true);

// Round 3: services this browser does not use (also stops outside connections)
user_pref("dom.push.enabled", false);
user_pref("identity.fxaccounts.enabled", false);

// Round 4: background tabs give memory back
user_pref("dom.memory.memory_pressure_on_background", 1);
user_pref("dom.memory.obscurant_pageout_on_background", true);
user_pref("dom.memory.obscurant_pageout_delay_ms", 20000);

// Round 5: unload background tabs when the whole computer runs low on memory
// (under 20% or under 1500 MB free). Firefox's own version is off on Linux.
user_pref("obscurant.memory.lowmem_unload", true);
user_pref("obscurant.memory.low_percent", 20);
user_pref("obscurant.memory.low_mb", 1500);
user_pref("obscurant.memory.low_min_inactive_ms", 30000);
user_pref("obscurant.memory.min_tabs_kept", 4);

// Downloads: block files disguised as documents (no network needed).
user_pref("obscurant.downloads.filecheck", true);
