export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const ip = (req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown').split(',')[0].trim();
  const { message, history } = req.body || {};
  if (!message || typeof message !== 'string' || message.length > 2000) {
    return res.status(400).json({ error: 'Invalid message' });
  }

  try {
    const reply = pickReply(message);
    return res.status(200).json({ reply });
  } catch (err) {
    console.error('Chat error:', err);
    return res.status(500).json({ error: 'Internal error' });
  }
}

const PILLARS = [
  ['XI', 'Federation', 'Connects siloed systems — WMS, TMS, Excel, email — into one unified data layer.'],
  ['XII', 'Entropy Detector', 'Finds invisible bottlenecks costing you money before they become crises.'],
  ['XIII', 'Ethics Constraint', 'Ensures every automation and AI model is fair, transparent, and cannot be manipulated.'],
  ['XIV', 'Lineage Notary', 'Every shipment, decision, and cost change has a traceable history.'],
  ['XV', 'Capacity Planner', 'Optimizes truck, warehouse, and freezer utilization in real time.'],
  ['XVI', 'Adversarial Forge', 'Stress-tests operations against worst-case scenarios — strikes, fuel spikes, weather.'],
  ['XVII', 'Graceful Degrader', 'When things fail, operations degrade gracefully, not catastrophically.'],
  ['XVIII', 'Knowledge Distiller', 'Extracts patterns from historical data so mistakes stop repeating.'],
  ['XIX', 'Temporal Sandbox', 'Simulates operational changes before they are deployed in the real world.'],
  ['XX', 'Sovereign Root', 'You retain ultimate control over every system deployed. I build it. You own it.'],
  ['XXI', 'Schema Validator', 'Ensures every BOL, invoice, and customs document is valid before it causes delays.'],
  ['XXII', 'Idempotency Guard', 'No duplicate shipments. No double-billed freight. No operational waste.'],
  ['XXIII', 'Provenance Tracker', 'Full audit trail across every shipment, decision, and cost change.'],
  ['XXIV', 'Cost Estimator', 'Predicts freight costs, equipment failures, and lane profitability.'],
  ['XXV', 'Explainability Engine', 'You will never ask "why did that happen?" again — every outcome is explained.'],
  ['XXVI', 'Bias Detector', 'No hidden biases in pricing, routing, or carrier selection.'],
  ['XXVII', 'Redundancy Planner', 'Backup carriers, backup lanes, backup systems — built-in resilience.'],
  ['XXVIII', 'Version Migrator', 'Ops systems evolve without breaking. No downtime. No data loss.'],
  ['XXIX', 'Dead Letter Handler', 'Lost shipments and broken processes are captured and fixed, not dropped.'],
  ['XXX', 'Universal Exporter', 'Reports, dashboards, and data exports in whatever format you need.'],
  ['XXXI', 'Anti-Corruption Engine', 'Once built, a system cannot be gamed, bypassed, or corrupted — by anyone.'],
];

const PILLAR_INDEX = PILLARS.reduce((acc, [num, name, desc]) => {
  acc[num] = { name, desc };
  acc[name.toLowerCase()] = { num, name, desc };
  acc[`${num} ${name}`.toLowerCase()] = { num, name, desc };
  acc[`${num}-${name}`.toLowerCase()] = { num, name, desc };
  return acc;
}, {});

const GENERIC_KEYWORDS = {
  pillars: 'Pillars XI through XXXI make up the Pruweba ops framework. Pick one and I will explain it.',
  xi: PILLARS[0][2], xii: PILLARS[1][2], xiii: PILLARS[2][2], xiv: PILLARS[3][2], xv: PILLARS[4][2],
  xvi: PILLARS[5][2], xvii: PILLARS[6][2], xviii: PILLARS[7][2], xix: PILLARS[8][2], xx: PILLARS[9][2],
  xxi: PILLARS[10][2], xxii: PILLARS[11][2], xxiii: PILLARS[12][2], xxiv: PILLARS[13][2], xxv: PILLARS[14][2],
  xxvi: PILLARS[15][2], xxvii: PILLARS[16][2], xxviii: PILLARS[17][2], xxix: PILLARS[18][2], xxx: PILLARS[19][2], xxxi: PILLARS[20][2],
  federation: PILLARS[0][2], entropy: PILLARS[1][2], ethics: PILLARS[2][2], lineage: PILLARS[3][2], capacity: PILLARS[4][2],
  adversarial: PILLARS[5][2], degrade: PILLARS[6][2], knowledge: PILLARS[7][2], temporal: PILLARS[8][2], sovereign: PILLARS[9][2],
  schema: PILLARS[10][2], idempotency: PILLARS[11][2], provenance: PILLARS[12][2], cost: PILLARS[13][2], explainability: PILLARS[14][2],
  bias: PILLARS[15][2], redundancy: PILLARS[16][2], migrator: PILLARS[17][2], 'dead letter': PILLARS[18][2], exporter: PILLARS[19][2], 'anti-corruption': PILLARS[20][2],
  audit: 'The free audit call is where I diagnose your bottleneck and map the right pillar mix. Book it from the site instead of asking me to improvise a custom scope.',
  pricing: 'Tier 1 is $1,500/mo, Tier 2 is $4,500–$8,000/project, Tier 3 is $6,000–$12,000/project. Exact scope is set during the audit call.',
  deploy: 'Most projects deploy in 3–6 weeks after scoping, depending on data access and integration complexity.',
  wms: 'Yes — integration is scoped during the audit call so I build against your actual WMS/TMS/Shopify stack.',
};

function pickReply(message) {
  const text = message.toLowerCase().replace(/[^a-z0-9\s-]/g, ' ').replace(/\s+/g, ' ').trim();
  for (const key of Object.keys(PILLAR_INDEX)) {
    if (!key || key.length < 3) continue;
    if (text === key || text.includes(` ${key} `) || text.startsWith(`${key} `) || text.endsWith(` ${key}`)) {
      const p = PILLAR_INDEX[key];
      return `${p.num} — ${p.name}: ${p.desc}`;
    }
  }
  for (const [k, v] of Object.entries(GENERIC_KEYWORDS)) {
    if (k.length < 3) continue;
    if (text.includes(k)) return v;
  }
  return 'I can explain any of the 31 pillars, or how the framework fits your ops. Ask about a specific pillar number or topic, or book the free audit to get a custom scope.';
}
