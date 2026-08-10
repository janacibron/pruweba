/* Client Portal — authenticated front-end for /api/portal.
 * Requires a Supabase session; every request carries the access token.
 */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const API = "/api/portal";
  const SIGN = "/api/portal/sign";

  const ICON = { done: "\u2705", active: "\uD83D\uDFE1", pending: "\u23F3" };

  let session = null;
  let currentClient = new URLSearchParams(location.search).get("client") || "";

  function alertBox(msg, kind) {
    const el = $("alert");
    if (!msg) { el.className = "hidden"; el.textContent = ""; return; }
    const tone =
      kind === "error"
        ? "border-red-500/40 bg-red-500/10 text-red-300"
        : "border-emerald-500/40 bg-emerald-500/10 text-emerald-300";
    el.className = "rounded-md border px-4 py-3 mono text-xs " + tone;
    el.textContent = msg;
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }

  /** Authenticated fetch. Bounces to login on 401. */
  async function api(url, options) {
    const opts = Object.assign({ headers: {} }, options || {});
    opts.headers = Object.assign({}, opts.headers, {
      Authorization: "Bearer " + session.access_token,
    });
    const res = await fetch(url, opts);
    let data = {};
    try { data = await res.json(); } catch (e) { /* non-JSON error body */ }
    if (res.status === 401) {
      location.replace("/login.html");
      throw new Error("session expired");
    }
    if (!res.ok || !data.ok) throw new Error(data.error || "HTTP " + res.status);
    return data;
  }

  function renderMilestones(p) {
    const ul = $("milestones");
    ul.innerHTML = "";
    (p.milestones || []).forEach((m, i) => {
      const li = document.createElement("li");
      const tone =
        m.status === "done"
          ? "border-emerald-500/25 bg-emerald-500/[0.04]"
          : m.status === "active"
          ? "border-amber-500/30 bg-amber-500/[0.04]"
          : "border-[#1c202b] bg-[#0a0c11]";
      li.className = "flex items-center justify-between gap-4 rounded-lg border px-4 py-3 " + tone;

      li.innerHTML =
        '<div class="flex items-center gap-3 min-w-0">' +
          '<span class="mono text-[11px] text-slate-600 w-5 text-right">' + (i + 1) + "</span>" +
          '<span class="text-base leading-none">' + (ICON[m.status] || "\u2753") + "</span>" +
          '<div class="min-w-0">' +
            '<div class="mono text-sm truncate">' + esc(m.name) + "</div>" +
            '<div class="mono text-[10px] text-slate-500">' +
              (m.completed_at ? esc(m.completed_at) : "not sealed") +
            "</div>" +
          "</div>" +
        "</div>";

      if (m.status !== "done") {
        const btn = document.createElement("button");
        btn.className =
          "mono text-[11px] shrink-0 px-3 py-1.5 rounded-md bg-emerald-500/15 border " +
          "border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 disabled:opacity-40";
        btn.textContent = "Sign Off";
        btn.addEventListener("click", () => signOff(m.name, btn));
        li.appendChild(btn);
      } else {
        const tag = document.createElement("span");
        tag.className = "mono text-[10px] shrink-0 text-emerald-400/70";
        tag.textContent = "SEALED";
        li.appendChild(tag);
      }
      ul.appendChild(li);
    });
    if (!ul.children.length) {
      ul.innerHTML = '<li class="mono text-xs text-slate-500">No milestones defined.</li>';
    }
  }

  function renderProofs(p) {
    const ul = $("proofs");
    ul.innerHTML = "";
    (p.proofs || []).forEach((pr) => {
      const li = document.createElement("li");
      li.className = "rounded-md bg-[#0a0c11] border border-[#1c202b] px-3 py-2";
      li.innerHTML =
        '<div class="text-slate-300 truncate">' + esc(pr.milestone) + "</div>" +
        '<div class="text-emerald-400/80 break-all mt-1">' + esc(pr.hash) + "</div>" +
        '<div class="text-slate-600 mt-1">' + esc(pr.sealed_at || "") + "</div>";
      ul.appendChild(li);
    });
    if (!ul.children.length) {
      ul.innerHTML = '<li class="text-slate-500">No proofs sealed yet.</li>';
    }
  }

  function render(data) {
    const p = data.progress || {};
    currentClient = data.client || currentClient;
    $("clientName").textContent = data.client || "—";
    $("pct").textContent = (p.percent != null ? p.percent : 0) + "%";
    $("counts").textContent = (p.completed || 0) + " / " + (p.total || 0) + " milestones sealed";
    $("bar").style.width = (p.percent || 0) + "%";
    $("verdict").textContent = p.verdict || "—";
    $("advice").textContent = p.advice || "—";
    $("root").textContent = p.seal_root || "—";
    const chain = $("chain");
    chain.textContent = "chain: " + (p.chain_valid ? "VALID" : "INVALID");
    chain.className =
      "mono text-[10px] mt-2 " + (p.chain_valid ? "text-emerald-400/70" : "text-red-400");
    $("terminal").textContent = data.client_view || "";
    renderMilestones(p);
    renderProofs(p);
  }

  async function load() {
    alertBox("");
    $("terminal").textContent = "loading…";
    try {
      const qs = currentClient ? "?client=" + encodeURIComponent(currentClient) : "";
      render(await api(API + qs));
    } catch (err) {
      alertBox("Load failed: " + err.message, "error");
      $("terminal").textContent = "unavailable";
      $("milestones").innerHTML = "";
      $("proofs").innerHTML = "";
    }
  }

  async function signOff(milestone, btn) {
    btn.disabled = true;
    btn.textContent = "sealing…";
    alertBox("");
    try {
      const data = await api(SIGN, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client: currentClient, milestone: milestone }),
      });
      render(data);
      alertBox(
        "Sealed \u201c" + milestone + "\u201d \u2192 " +
          (data.proof ? data.proof.hash.slice(0, 24) + "\u2026" : ""),
        "ok"
      );
    } catch (err) {
      alertBox("Sign-off failed: " + err.message, "error");
      btn.disabled = false;
      btn.textContent = "Sign Off";
    }
  }

  // ---- boot: guard the page behind a session ----------------------------
  (async function boot() {
    try {
      session = await window.PruwebaAuth.requireSession("/login.html");
      if (!session) return; // redirecting
    } catch (err) {
      location.replace("/login.html");
      return;
    }
    const who = $("userEmail");
    if (who) who.textContent = session.user.email;
    const out = $("signOutBtn");
    if (out) out.addEventListener("click", () => window.PruwebaAuth.signOut());
    load();
  })();
})();
