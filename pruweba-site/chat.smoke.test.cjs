const mod = require('./chat.js');
function makeRes() {
  const state = { code: 0, payload: null };
  return {
    status(c) { state.code = c; return this; },
    json(obj) { state.payload = obj; return this; },
    getState() { return state; }
  };
}
(async () => {
  const cases = [
    ['XXV', /every outcome is explained/],
    ['idempotency', /No duplicate shipments/],
    ['audit', /audit call/],
    ['random outside scope', /31 pillars/],
  ];
  let errs = [];
  for (const [msg, re] of cases) {
    const res = makeRes();
    await mod({ method: 'POST', headers: {}, body: { message: msg, history: [] } }, res);
    const s = res.getState();
    if (s.code !== 200) errs.push(`status ${s.code} for ${msg}`);
    else if (!s.payload || !s.payload.reply) errs.push(`missing reply for ${msg}`);
    else if (!re.test(s.payload.reply)) errs.push(`reply mismatch for ${msg}: ${s.payload.reply}`);
  }
  if (errs.length) {
    console.error('FAIL');
    errs.forEach(e => console.error('- ' + e));
    process.exit(1);
  }
  console.log(`PASS: ${cases.length} chat smoke tests green`);
})();
