"use strict";

const path = require("path");

function makeReq(body) {
  return {
    method: "POST",
    headers: { "x-forwarded-for": "1.2.3.4" },
    body: body || {},
  };
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

async function loadChatHandler() {
  const mod = await import(path.join(__dirname, "..", "api", "chat.js"));
  return mod.default;
}

function runCase(label, handler, req, expect) {
  const res = makeRes();
  return handler(req, res).then(() => {
    const s = res.getState();
    let pass = true;
    let detail = [];
    if (typeof expect.status === "number" && s.code !== expect.status) {
      pass = false;
      detail.push(`status=${s.code}`);
    }
    if (expect.reply && !(s.payload && s.payload.reply && expect.reply.test(s.payload.reply))) {
      pass = false;
      detail.push(`reply=${JSON.stringify(s.payload && s.payload.reply)}`);
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
  const handler = await loadChatHandler();

  // 1. GET -> 405
  runCase("GET returns 405", handler, { ...makeReq(), method: "GET" }, { status: 405, error: /Method not allowed/ });

  // 2. missing message
  runCase("missing message -> 400", handler, makeReq({}), { status: 400 });

  // 3. long message
  runCase("long message -> 400", handler, makeReq({ message: "x".repeat(2001) }), { status: 400 });

  // 4. valid chat -> 200 + reply
  runCase("valid message -> 200", handler, makeReq({ message: "What is Idempotency Guard?" }), {
    status: 200,
    reply: /Idempotency Guard/,
  });

  // 5. new pillar XXXII
  runCase("new pillar XXXII -> 200", handler, makeReq({ message: "XXXII" }), {
    status: 200,
    reply: /Unified Economic Continuum/,
  });

  // 6. new pillar XXXIII keyword
  runCase("new pillar XXXIII keyword -> 200", handler, makeReq({ message: "enterprise value" }), {
    status: 200,
    reply: /Enterprise Value Creation/,
  });

  // 7. new pillar XXXIV
  runCase("new pillar XXXIV keyword -> 200", handler, makeReq({ message: "position sizing" }), {
    status: 200,
    reply: /Market Trading and Position Sizing/,
  });

  // 8. rate limit -> 429 (fire 16 requests in same second window)
  {
    const res = makeRes();
    const req = makeReq({ message: "ping" });
    for (let i = 0; i < 16; i++) {
      await handler({ ...req, headers: { "x-forwarded-for": "5.6.7.8" } }, makeRes());
    }
    await handler(req, res);
    const s = res.getState();
    if (s.code === 429) {
      console.log("  ok  rate limit -> 429");
    } else {
      console.log(`  FAIL rate limit -> status=${s.code}`);
      process.exitCode = 1;
    }
  }

  await new Promise((r) => setTimeout(r, 50));
})();
