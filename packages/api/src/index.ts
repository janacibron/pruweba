// Pruweba API Server — dev.pruweba.com
// REST endpoints for claim verification.

import express from 'express';
import cors from 'cors';
import { createEngine } from '@pruweba/engine';
import type { Claim, Invariant } from '@pruweba/engine';

const app = express();
const port = process.env.PORT ? parseInt(process.env.PORT) : 3100;

app.use(cors());
app.use(express.json());

// ── Engine ────────────────────────────────────────────
const engine = createEngine();

// Built-in invariants
const TIMESTAMP_INVARIANT: Invariant = {
  id: 'INV-TIMESTAMP',
  description: 'Claim timestamp must not be in the future',
  severity: 'violation',
  check: (claim: Claim) => new Date(claim.timestamp) <= new Date(),
};

const IDENTITY_INVARIANT: Invariant = {
  id: 'INV-IDENTITY',
  description: 'Claim origin must be a known source',
  severity: 'warning',
  check: (claim: Claim) =>
    claim.origin.length > 0 && !claim.origin.startsWith('unknown'),
};

engine.registerInvariant(TIMESTAMP_INVARIANT);
engine.registerInvariant(IDENTITY_INVARIANT);

// ── Routes ───────────────────────────────────────────

/** POST /verify — Submit a claim for verification */
app.post('/verify', async (req, res) => {
  try {
    const claim = req.body as Claim;
    const attestation = await engine.verify(claim);
    res.status(201).json(attestation);
  } catch (err) {
    res.status(400).json({
      error: err instanceof Error ? err.message : 'Verification failed',
    });
  }
});

/** GET /attestations — List all attestations */
app.get('/attestations', (_req, res) => {
  res.json(engine.getAttestations());
});

/** GET /attestations/:claimId — Get attestation by claim ID */
app.get('/attestations/:claimId', (req, res) => {
  const att = engine.getAttestation(req.params.claimId);
  if (!att) {
    res.status(404).json({ error: 'Attestation not found' });
    return;
  }
  res.json(att);
});

/** GET /chain — Get the full evidence chain */
app.get('/chain', (_req, res) => {
  res.json(engine.getEvidenceChain());
});

/** GET /chain/verify — Verify chain integrity */
app.get('/chain/verify', (_req, res) => {
  const result = engine.verifyChainIntegrity();
  res.json(result);
});

/** GET /invariants — List registered invariants */
app.get('/invariants', (_req, res) => {
  const invariants: Invariant[] = [];
  // Access private invariants via a direct check
  // We expose the invariant metadata (not the function)
  res.json([
    { id: 'INV-TIMESTAMP', description: 'Claim timestamp must not be in the future', severity: 'violation' },
    { id: 'INV-IDENTITY', description: 'Claim origin must be a known source', severity: 'warning' },
  ]);
});

/** GET /health — Health check */
app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    name: 'Pruweba API',
    version: '0.1.0',
    attestations: engine.getAttestations().length,
    chainValid: engine.verifyChainIntegrity().valid,
  });
});

// ── Start ───────────────────────────────────────────
app.listen(port, () => {
  console.log(`◈ Pruweba API running on http://localhost:${port}`);
  console.log(`   Endpoints:`);
  console.log(`   POST /verify          — Submit a claim`);
  console.log(`   GET  /attestations     — List all attestations`);
  console.log(`   GET  /attestations/:id — Get attestation by claim ID`);
  console.log(`   GET  /chain            — Full evidence chain`);
  console.log(`   GET  /chain/verify     — Verify chain integrity`);
  console.log(`   GET  /health           — Health check`);
});

export { app, engine };
