"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const root = path.join(__dirname, "..");
let failures = 0;

function check(label, ok, detail) {
  if (ok) {
    console.log("  ok  " + label);
  } else {
    console.log("  FAIL " + label + (detail ? " :: " + detail : ""));
    failures++;
  }
}

// --- syntax checks ---------------------------------------------------
check("chat.js syntax", spawnSync("node", ["--check", "chat.js"], { cwd: root, encoding: "utf8" }).status === 0);
check("api/chat.js syntax", spawnSync("node", ["--check", "api/chat.js"], { cwd: root, encoding: "utf8" }).status === 0);
check("api/track.js syntax", spawnSync("node", ["--check", "api/track.js"], { cwd: root, encoding: "utf8" }).status === 0);

// --- helpers ---------------------------------------------------------
function makeReq(body, method) {
  return { method: method || "POST", headers: { "x-forwarded-for": "1.2.3.4" }, body: body || {} };
}
function makeRes() {
  const state = { code: 0, headers: {}, payload: null };
  return {
    status(c) { state.code = c; return this; },
    setHeader(k, v) { state.headers[k] = v; return this; },
    json(obj) { state.payload = obj; return this; },
    getState() { return state; },
  };
}

function loadChatHandler() {
  const mod = require(path.join(root, "chat.js"));
  return mod;
}

// --- mock supabase ---------------------------------------------------
const Module = require("module");
const originalLoad = Module._load;
function mockSupabase() {
  let capturedCreateArgs = [];
  let mockInsertResult = { error: null };
  Module._load = function (request, parent, isMain) {
    if (request === "@supabase/supabase-js") {
      return { createClient: function createClient(url, key, options) {
        capturedCreateArgs.push([url, key, options]);
        return { from: () => ({ insert: () => Promise.resolve(mockInsertResult) }) };
      }};
    }
    return originalLoad(request, parent, isMain);
  };
  return { setResult: (r) => { mockInsertResult = r; }, calls: () => capturedCreateArgs, restore: () => { Module._load = originalLoad; } };
}

// --- chat.js tests ---------------------------------------------------
async function chatCases() {
  const handler = loadChatHandler();

  const cases = [
    ["GET returns 405", { ...makeReq({}, "GET") }, { status: 405 }],
    ["missing message -> 400", makeReq({}), { status: 400 }],
    ["long message -> 400", makeReq({ message: "x".repeat(2001) }), { status: 400 }],
    ["valid message -> 200", makeReq({ message: "What is Idempotency Guard?" }), { status: 200, reply: /Idempotency Guard/ }],
    ["new pillar XXXII -> 200", makeReq({ message: "XXXII" }), { status: 200, reply: /Unified Economic Continuum/ }],
    ["new pillar XXXIII keyword -> 200", makeReq({ message: "enterprise value creation" }), { status: 200, reply: /Links operational decisions/ }],
    ["new pillar XXXIV keyword -> 200", makeReq({ message: "market trading" }), { status: 200, reply: /Risk-aware execution/ }],
  ];

  for (const [label, req, expect] of cases) {
    const res = makeRes();
    await handler(req, res);
    const s = res.getState();
    let pass = true;
    const detail = [];
    if (typeof expect.status === "number" && s.code !== expect.status) { pass = false; detail.push(`status=${s.code}`); }
    if (expect.reply && !(s.payload && s.payload.reply && expect.reply.test(s.payload.reply))) { pass = false; detail.push(`reply=${JSON.stringify(s.payload && s.payload.reply)}`); }
    check(label, pass, detail.join("; "));
  }

  // rate limit
  {
    const res = makeRes();
    for (let i = 0; i < 16; i++) {
      await handler({ ...makeReq({ message: "ping" }), headers: { "x-forwarded-for": "5.6.7.8" } }, makeRes());
    }
    await handler({ ...makeReq({ message: "ping" }), headers: { "x-forwarded-for": "5.6.7.8" } }, res);
    check("rate limit -> 429", res.getState().code === 429, "status=" + res.getState().code);
  }
}

// --- api/chat.js compile + load check ---------------------------------
async function apiChatCases() {
  check("api/chat.js syntax", spawnSync("node", ["--check", "api/chat.js"], { cwd: root, encoding: "utf8" }).status === 0);
  let apiHandler;
  try {
    apiHandler = require(path.join(root, "api", "chat.js"));
  } catch (err) {
    check("api/chat.js require", false, err.message);
    return;
  }
  check("api/chat.js require", typeof apiHandler === "function");
  if (typeof apiHandler !== "function") return;

  const cases = [
    ["api chat GET returns 405", { ...makeReq({}, "GET") }, { status: 405 }],
    ["api chat valid -> 200", makeReq({ message: "Explain Bias Detector" }), { status: 200, reply: /Bias Detector/ }],
    ["api chat new pillar XXXIV -> 200", makeReq({ message: "XXXIV" }), { status: 200, reply: /Market Trading and Position Sizing/ }],
  ];

  for (const [label, req, expect] of cases) {
    const res = makeRes();
    await apiHandler(req, res);
    const s = res.getState();
    let pass = true;
    const detail = [];
    if (typeof expect.status === "number" && s.code !== expect.status) { pass = false; detail.push(`status=${s.code}`); }
    if (expect.reply && !(s.payload && s.payload.reply && expect.reply.test(s.payload.reply))) { pass = false; detail.push(`reply=${JSON.stringify(s.payload && s.payload.reply)}`); }
    check(label, pass, detail.join("; "));
  }
}

// --- track.js tests --------------------------------------------------
async function trackCases() {
  const validBody = { event: "test", target: "unit", page: "/", domain: "pruweba.com", timestamp: "2025-01-01T00:00:00Z" };
  process.env.SUPABASE_URL = "https://test.supabase.co";
  process.env.SUPABASE_SERVICE_ROLE_KEY = "test-key";

  {
    const supabase = mockSupabase();
    let trackHandler;
    delete require.cache[path.join(root, "api", "track.js")];
    try {
      trackHandler = require(path.join(root, "api", "track.js"));
    } finally {
      supabase.restore();
    }

    supabase.setResult({ error: null });
    const res = makeRes();
    await trackHandler({ ...makeReq(validBody), method: "POST" }, res);
    const s = res.getState();
    const detail = [];
    if (s.code !== 200) detail.push(`status=${s.code}`);
    if (s.payload && s.payload.stored !== true) detail.push(`stored=${s.payload.stored}`);
    if (supabase.calls().length < 1) detail.push(`createClient_calls=${supabase.calls().length}`);
    check("track valid event -> 200 stored=true", detail.length === 0, detail.join("; "));
  }

  {
    const supabase = mockSupabase();
    let trackHandler;
    delete require.cache[path.join(root, "api", "track.js")];
    try {
      trackHandler = require(path.join(root, "api", "track.js"));
    } finally {
      supabase.restore();
    }

    supabase.setResult({ error: { message: "db boom" } });
    const res = makeRes();
    await trackHandler({ ...makeReq(validBody), method: "POST" }, res);
    const s = res.getState();
    const detail = [];
    if (s.code !== 200) detail.push(`status=${s.code}`);
    if (s.payload && s.payload.stored !== false) detail.push(`stored=${s.payload.stored}`);
    if (!s.payload || !s.payload.reason || s.payload.reason !== "supabase_insert_failed") detail.push(`reason=${JSON.stringify(s.payload && s.payload.reason)}`);
    check("track insert failure -> 200 stored=false", detail.length === 0, detail.join("; "));
  }
}

(async () => {
  await chatCases();
  await apiChatCases();
  await trackCases();

  console.log("");
  if (failures === 0) {
    console.log("SELFTEST_OK (chat + api/chat + track endpoint tests)");
  } else {
    console.log("SELFTEST_FAILURES=" + failures);
    process.exitCode = 1;
  }
})();
