"use strict";

const path = require("path");
const Module = require("module");

// --- Mock supabase-js before requiring track.js -------------------------
const originalLoad = Module._load;
const originalRequire = Module.prototype.require;

let capturedCreateArgs = [];
let mockInsertResult = { error: null };

Module._load = function (request, parent, isMain) {
  if (request === "@supabase/supabase-js") {
    return function createClient(url, key, options) {
      capturedCreateArgs.push([url, key, options]);
      return {
        from: () => ({
          insert: () => Promise.resolve(mockInsertResult),
        }),
      };
    };
  }
  return originalLoad(request, parent, isMain);
};

process.env.SUPABASE_URL = "https://test.supabase.co";
process.env.SUPABASE_SERVICE_ROLE_KEY = "test-key";

const handler = require(path.join(__dirname, "..", "api", "track.js"));

// --- Restore require ----------------------------------------------------
Module._load = originalLoad;

function makeReq(body) {
  return {
    method: "POST",
    headers: {},
    body: body || {},
  };
}

function makeRes() {
  const state = { code: 0, payload: null };
  return {
    status(c) { state.code = c; return this; },
    json(obj) { state.payload = obj; return this; },
    getState() { return state; },
  };
}

function runCase(label, req, expect) {
  const res = makeRes();
  return handler(req, res).then(() => {
    const s = res.getState();
    let pass = true;
    let detail = [];
    if (typeof expect.status === "number" && s.code !== expect.status) {
      pass = false;
      detail.push(`status=${s.code}`);
    }
    if (expect.stored !== undefined && s.payload && s.payload.stored !== expect.stored) {
      pass = false;
      detail.push(`stored=${s.payload.stored}`);
    }
    if (expect.error && !(s.payload && s.payload.error && expect.error.test(s.payload.error))) {
      pass = false;
      detail.push(`error=${JSON.stringify(s.payload && s.payload.error)}`);
    }
    if (pass) {
      console.log(`  ok  ${label}`);
    } else {
      console.log(`  FAIL ${label} :: ${detail.join("; ")}`);
      process.exitCode = 1;
    }
  }).catch((err) => {
    console.log(`  FAIL ${label} :: threw ${err.message}`);
    process.exitCode = 1;
  });
}

(async () => {
  await new Promise((r) => setTimeout(r, 0));

  // 1. GET -> 405
  runCase("GET returns 405", { ...makeReq(), method: "GET" }, { status: 405 });

  // 2. missing fields
  runCase("missing fields -> 400", makeReq({ event: "x" }), { status: 400, error: /Missing required fields/ });

  // 3. valid event stored=true
  {
    const res = makeRes();
    mockInsertResult = { error: null };
    capturedCreateArgs = [];
    await handler(
      makeReq({ event: "test", target: "unit", page: "/", domain: "pruweba.com", timestamp: "2025-01-01T00:00:00Z" }),
      res
    );
    const s = res.getState();
    let pass = true;
    let detail = [];
    if (s.code !== 200) { pass = false; detail.push(`status=${s.code}`); }
    if (s.payload && s.payload.stored !== true) { pass = false; detail.push(`stored=${s.payload.stored}`); }
    if (capturedCreateArgs.length !== 1) { pass = false; detail.push(`createClient_calls=${capturedCreateArgs.length}`); }
    if (pass) {
      console.log("  ok  valid event -> 200 stored=true");
    } else {
      console.log(`  FAIL valid event :: ${detail.join("; ")}`);
      process.exitCode = 1;
    }
  }

  // 4. supabase insert failure -> stored=false
  {
    const res = makeRes();
    mockInsertResult = { error: { message: "db boom" } };
    capturedCreateArgs = [];
    await handler(
      makeReq({ event: "test", target: "unit", page: "/", domain: "pruweba.com", timestamp: "2025-01-01T00:00:00Z" }),
      res
    );
    const s = res.getState();
    let pass = true;
    let detail = [];
    if (s.code !== 200) { pass = false; detail.push(`status=${s.code}`); }
    if (s.payload && s.payload.stored !== false) { pass = false; detail.push(`stored=${s.payload.stored}`); }
    if (!s.payload || !s.payload.reason || s.payload.reason !== "supabase_insert_failed") {
      pass = false;
      detail.push(`reason=${JSON.stringify(s.payload && s.payload.reason)}`);
    }
    if (pass) {
      console.log("  ok  insert failure -> 200 stored=false + reason");
    } else {
      console.log(`  FAIL insert failure :: ${detail.join("; ")}`);
      process.exitCode = 1;
    }
  }

  await new Promise((r) => setTimeout(r, 50));
})();
