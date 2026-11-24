// Aggressive additions: bigger RAM saving, some isolation and speed cost.
// Site isolation (Fission) stays on.

// Hard cap on processes per site: tabs share processes beyond 2
user_pref("dom.ipc.processCount.webIsolated", 2);
user_pref("dom.ipc.processCount", 4);

// No spare process at all, no warm-up
user_pref("dom.ipc.processPrelaunch.enabled", false);
user_pref("browser.tabs.remote.warmup.enabled", false);

// Smaller in-memory cache
user_pref("browser.cache.memory.capacity", 32768);
