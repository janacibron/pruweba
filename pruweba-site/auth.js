/* Shared Supabase auth client for the Pruweba Client Portal.
 *
 * Static hosting has no build step, so `process.env` does not exist in the
 * browser. Public config is fetched from /api/config, which returns only the
 * URL and the publishable/anon key (safe to expose; guarded by RLS).
 *
 * Exposes window.PruwebaAuth = { client, getSession, requireSession, signOut }.
 */
(function () {
  "use strict";

  let _clientPromise = null;

  async function client() {
    if (_clientPromise) return _clientPromise;
    _clientPromise = (async () => {
      const res = await fetch("/api/config");
      const cfg = await res.json();
      if (!res.ok || !cfg.ok) throw new Error(cfg.error || "config unavailable");
      if (!window.supabase || !window.supabase.createClient) {
        throw new Error("supabase-js failed to load");
      }
      return window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
      });
    })();
    return _clientPromise;
  }

  async function getSession() {
    const sb = await client();
    const { data: { session } } = await sb.auth.getSession();
    return session;
  }

  /** Redirect to login.html when there is no session. Returns the session. */
  async function requireSession(redirectTo) {
    const session = await getSession();
    if (!session) {
      location.replace(redirectTo || "/login.html");
      return null;
    }
    return session;
  }

  async function signOut() {
    const sb = await client();
    await sb.auth.signOut();
    location.replace("/login.html");
  }

  window.PruwebaAuth = { client, getSession, requireSession, signOut };

  // ---- login page behaviour (only when the form is present) --------------
  const form = document.getElementById("loginForm");
  if (!form) return;

  const emailInput = document.getElementById("email");
  const btn = document.getElementById("submitBtn");
  const alertEl = document.getElementById("alert");

  function notify(msg, kind) {
    if (!msg) { alertEl.className = "hidden"; alertEl.textContent = ""; return; }
    const tone =
      kind === "error"
        ? "border-red-500/40 bg-red-500/10 text-red-300"
        : "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
    alertEl.className = "mt-4 rounded-md border px-4 py-3 mono text-xs " + tone;
    alertEl.textContent = msg;
  }

  // Already signed in? Skip the form.
  getSession()
    .then((s) => { if (s) location.replace("/portal.html"); })
    .catch(() => { /* config errors surface on submit */ });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (emailInput.value || "").trim();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      notify("Enter a valid work email address.", "error");
      emailInput.focus();
      return;
    }

    btn.disabled = true;
    const original = btn.textContent;
    btn.textContent = "Sending…";
    notify("");

    try {
      const sb = await client();
      const { error } = await sb.auth.signInWithOtp({
        email: email,
        options: { emailRedirectTo: location.origin + "/portal.html" },
      });
      if (error) throw error;
      notify("Check your email for the access link.", "ok");
      btn.textContent = "Link sent";
      emailInput.setAttribute("readonly", "readonly");
    } catch (err) {
      notify("Could not send link: " + (err.message || err), "error");
      btn.disabled = false;
      btn.textContent = original;
    }
  });
})();
