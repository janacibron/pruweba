/* Magic-link callback catcher.
 *
 * Supabase sends every auth link to the project's Site URL (https://pruweba.com/),
 * and per-path redirect targets are only honoured when they are on the Redirect
 * URLs allow-list. Rather than depend on that config, this script runs on the
 * landing page: if it sees an auth callback in the URL, it completes the session
 * and forwards to the portal.
 *
 * Handles both shapes:
 *   #access_token=...&refresh_token=...  (implicit)
 *   ?code=...                            (PKCE)
 *   #error=...                           (expired/invalid link)
 *
 * Safe to include on any page: it no-ops when there is no auth payload.
 */
(function () {
  "use strict";

  const hash = (location.hash || "").replace(/^#/, "");
  const search = (location.search || "").replace(/^\?/, "");
  const hp = new URLSearchParams(hash);
  const sp = new URLSearchParams(search);

  const hasTokens = hp.get("access_token") && hp.get("refresh_token");
  const hasCode = sp.get("code");
  const hasError = hp.get("error") || sp.get("error");

  if (!hasTokens && !hasCode && !hasError) return; // normal page load

  const DEST = "/portal.html";

  function banner(text, isError) {
    const el = document.createElement("div");
    el.style.cssText =
      "position:fixed;inset:0;z-index:9999;display:grid;place-items:center;" +
      "background:#08090c;color:" + (isError ? "#fca5a5" : "#6ee7b7") +
      ";font:14px ui-monospace,'IBM Plex Mono',monospace;text-align:center;padding:24px;";
    el.innerHTML =
      "<div><div>" + text + "</div>" +
      (isError
        ? '<div style="margin-top:16px"><a href="/login.html" style="color:#34d399">Request a new link</a></div>'
        : "") +
      "</div>";
    document.body.appendChild(el);
  }

  if (hasError) {
    const desc =
      hp.get("error_description") || sp.get("error_description") || "Sign-in link failed";
    history.replaceState(null, "", location.pathname);
    if (document.body) banner(decodeURIComponent(desc.replace(/\+/g, " ")), true);
    else document.addEventListener("DOMContentLoaded", () =>
      banner(decodeURIComponent(desc.replace(/\+/g, " ")), true));
    return;
  }

  function start() {
    banner("Signing you in…", false);
    fetch("/api/config")
      .then((r) => r.json())
      .then((cfg) => {
        if (!cfg.ok) throw new Error(cfg.error || "config unavailable");
        if (!window.supabase || !window.supabase.createClient) {
          throw new Error("supabase-js not loaded");
        }
        const sb = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey, {
          auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
        });
        if (hasTokens) {
          return sb.auth.setSession({
            access_token: hp.get("access_token"),
            refresh_token: hp.get("refresh_token"),
          });
        }
        return sb.auth.exchangeCodeForSession(hasCode);
      })
      .then((res) => {
        if (res && res.error) throw res.error;
        history.replaceState(null, "", location.pathname);
        location.replace(DEST);
      })
      .catch((err) => {
        history.replaceState(null, "", location.pathname);
        banner("Sign-in failed: " + (err.message || err), true);
      });
  }

  if (document.body) start();
  else document.addEventListener("DOMContentLoaded", start);
})();
