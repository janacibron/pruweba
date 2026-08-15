/* Headless test for auth-callback.js using jsdom + REAL Supabase tokens.
 *
 * Verifies:
 *   1. no-op on a clean URL (no auth payload)
 *   2. #error=... renders the error banner and offers a new link
 *   3. #access_token=... establishes a session and redirects to /portal.html
 *   4. the established session is accepted by the real /api/portal
 *
 * Run: node tests/callback_test.cjs   (after tests/_mint_tokens.py)
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const ROOT = path.resolve(__dirname, "..");
const SCRIPT = fs.readFileSync(path.join(ROOT, "auth-callback.js"), "utf8");
const TOKENS = JSON.parse(fs.readFileSync(path.join(ROOT, "tests", "_tokens.json"), "utf8"));
const SUPA_UMD = fs.readFileSync(
  path.join(ROOT, "node_modules", "@supabase", "supabase-js", "dist", "umd", "supabase.js"),
  "utf8"
);

function makeDom(url) {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", {
    url: url,
    runScripts: "outside-only",
    pretendToBeVisual: true,
  });
  const w = dom.window;

  // jsdom does not implement navigation and window.location cannot be
  // redefined, so build a recording stand-in that is injected as a shadowing
  // parameter when the script is evaluated (see run()).
  w.__redirects = [];
  const real = w.location;
  w.__loc = {
    get href() { return real.href; },
    get origin() { return real.origin; },
    get pathname() { return real.pathname; },
    get search() { return real.search; },
    hash: real.hash,
    replace: (u) => w.__redirects.push(u),
    assign: (u) => w.__redirects.push(u),
  };
  // history.replaceState clears the hash the way a browser does.
  const realReplaceState = w.history.replaceState.bind(w.history);
  w.history.replaceState = (a, b, url) => { w.__loc.hash = ""; return realReplaceState(a, b, url); };

  // /api/config is served by the deployed function; stub it with real values.
  w.fetch = (input, init) => {
    const u = String(input);
    if (u === "/api/config") {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ok: true,
            supabaseUrl: TOKENS.supabase_url,
            supabaseAnonKey: TOKENS.anon_key,
          }),
      });
    }
    return globalThis.fetch(u, init);
  };
  return dom;
}

function run(dom) {
  const w = dom.window;
  w.eval(SUPA_UMD); // provides window.supabase
  // auth-callback.js is an IIFE; wrap it so `location` resolves to the stub.
  w.eval("(function(location){\n" + SCRIPT + "\n})(window.__loc);");
  return w;
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  let failures = 0;
  const check = (name, cond, detail) => {
    if (cond) {
      console.log("  ok  " + name);
    } else {
      failures++;
      console.log("  FAIL " + name + (detail ? " :: " + detail : ""));
    }
  };

  // --- 1. clean URL: must do nothing at all ---
  {
    const dom = makeDom("https://pruweba.com/");
    const w = run(dom);
    await wait(150);
    check(
      "clean URL is a no-op",
      w.__redirects.length === 0 && w.document.body.children.length === 0,
      "redirects=" + JSON.stringify(w.__redirects)
    );
  }

  // --- 2. the exact failure the user hit ---
  {
    const dom = makeDom(
      "https://pruweba.com/#error=access_denied&error_code=otp_expired" +
        "&error_description=Email+link+is+invalid+or+has+expired"
    );
    const w = run(dom);
    await wait(150);
    const text = w.document.body.textContent || "";
    check(
      "expired link shows readable error",
      text.includes("Email link is invalid or has expired"),
      JSON.stringify(text.slice(0, 80))
    );
    check("expired link offers a new one", text.includes("Request a new link"));
    check("expired link does not redirect", w.__redirects.length === 0);
    check("hash is scrubbed from the URL", w.__loc.hash === "");
  }

  // --- 3. real tokens: establish a session and forward to the portal ---
  let established = null;
  {
    const dom = makeDom(
      "https://pruweba.com/#access_token=" +
        TOKENS.access_token +
        "&refresh_token=" +
        TOKENS.refresh_token +
        "&token_type=bearer&type=magiclink"
    );
    const w = run(dom);
    for (let i = 0; i < 60 && w.__redirects.length === 0; i++) await wait(100);

    check(
      "valid callback redirects to /portal.html",
      w.__redirects[0] === "/portal.html",
      JSON.stringify(w.__redirects)
    );

    // the session must be persisted where portal.js will look for it
    const keys = Object.keys(w.localStorage).filter((k) => k.includes("auth-token"));
    check("session persisted to localStorage", keys.length > 0, JSON.stringify(keys));
    if (keys.length) {
      const stored = JSON.parse(w.localStorage.getItem(keys[0]));
      established = stored.access_token;
      check("stored token matches the issued one", stored.access_token === TOKENS.access_token);
      check("stored user email is correct", (stored.user || {}).email === TOKENS.email);
    }
  }

  // --- 4. that session is actually usable against the live API ---
  if (established) {
    const res = await fetch("https://pruweba.com/api/portal", {
      headers: { Authorization: "Bearer " + established },
    });
    const body = await res.json().catch(() => ({}));
    // 403 = authenticated but no project assigned. Anything but 401 proves the
    // token was accepted by the deployed verifier.
    check(
      "live API accepts the session token (not 401)",
      res.status !== 401,
      "status=" + res.status + " " + JSON.stringify(body).slice(0, 90)
    );
    console.log("       live /api/portal -> " + res.status + " " + (body.error || "ok"));
  }

  console.log(failures === 0 ? "\nCALLBACK_OK" : "\nCALLBACK_FAILURES=" + failures);
  process.exit(failures === 0 ? 0 : 1);
})();
