// Pruweba API Server
// REST endpoints for claim verification.

import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import { createEngine } from './engine/index.js';
import type { Claim, Invariant } from './engine/types.js';
import { TIERS, getTier, incrementUsage, getUsage } from './tiers.js';

// ─── App Setup ───────────────────────────────────────────────

const app = express();
const port = process.env.PORT ? parseInt(process.env.PORT, 10) : 3100;

app.use(cors());
app.use(express.json({ limit: '1mb' }));

// ─── Usage Tracking Middleware ────────────────────────────────

function trackUsage(req: Request, _res: Response, next: Function) {
  const key = (req.headers['x-api-key'] as string) || req.ip || 'anonymous';
  (req as any).apiKey = key;
  (req as any).usageCount = incrementUsage(key);
  (req as any).tier = getTier(key as string | undefined);
  next();
}

function usageHeaders(req: Request, res: Response) {
  const tier = (req as any).tier || TIERS.free;
  const used = (req as any).usageCount || 0;
  res.set('X-Tier', tier.name);
  res.set('X-Usage-Limit', String(tier.limit));
  res.set('X-Usage-Remaining', String(Math.max(0, tier.limit - used)));
  res.set('X-Usage-Used', String(used));
}

// ─── Engine & Invariants ─────────────────────────────────────

const engine = createEngine();

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

// ─── Routes ──────────────────────────────────────────────────

/** GET / — API information and available endpoints */
app.get('/', (_req: Request, res: Response) => {
  res.json({
    name: 'Pruweba API',
    version: '1.0.0',
    status: 'ok',
    endpoints: [
      { method: 'POST', path: '/verify', description: 'Submit a claim for verification' },
      { method: 'GET',  path: '/attestations', description: 'List all attestations' },
      { method: 'GET',  path: '/attestations/:claimId', description: 'Get attestation by claim ID' },
      { method: 'GET',  path: '/chain', description: 'Full evidence chain' },
      { method: 'GET',  path: '/chain/verify', description: 'Verify chain integrity' },
      { method: 'GET',  path: '/health', description: 'Health check' },
      { method: 'GET',  path: '/invariants', description: 'List registered invariants' },
      { method: 'GET',  path: '/usage', description: 'Check API usage against tier limit' },
    ],
  });
});

/** GET /health — Health check */
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'ok',
    name: 'Pruweba API',
    version: '0.1.0',
    attestations: engine.getAttestations().length,
    chainValid: engine.verifyChainIntegrity().valid,
  });
});

/** POST /verify — Submit a claim for verification */
app.post('/verify', trackUsage, async (req: Request, res: Response) => {
  // Check tier limit
  const tier = (req as any).tier || TIERS.free;
  const used = (req as any).usageCount || 0;
  if (used > tier.limit) {
    usageHeaders(req, res);
    return res.status(429).json({
      error: 'Usage limit exceeded',
      tier: tier.name,
      limit: tier.limit,
      used,
      message: `Free tier allows ${tier.limit.toLocaleString()} verifications per day. Upgrade coming soon.`,
    });
  }

  try {
    const claim = req.body as Claim;
    const attestation = await engine.verify(claim);
    usageHeaders(req, res);
    res.status(201).json(attestation);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Verification failed';
    usageHeaders(req, res);
    res.status(400).json({ error: message });
  }
});

/** GET /attestations — List all attestations */
app.get('/attestations', (_req: Request, res: Response) => {
  res.json(engine.getAttestations());
});

/** GET /attestations/:claimId — Get attestation by claim ID */
app.get('/attestations/:claimId', (req: Request, res: Response) => {
  const att = engine.getAttestation(req.params.claimId);
  if (!att) {
    res.status(404).json({ error: 'Attestation not found' });
    return;
  }
  res.json(att);
});

/** GET /chain — Get the full evidence chain */
app.get('/chain', (_req: Request, res: Response) => {
  res.json(engine.getEvidenceChain());
});

/** GET /chain/verify — Verify chain integrity */
app.get('/chain/verify', (_req: Request, res: Response) => {
  const result = engine.verifyChainIntegrity();
  res.json(result);
});

/** GET /invariants — List registered invariants (metadata only) */
app.get('/invariants', (_req: Request, res: Response) => {
  res.json([
    { id: 'INV-TIMESTAMP', description: 'Claim timestamp must not be in the future', severity: 'violation' },
    { id: 'INV-IDENTITY', description: 'Claim origin must be a known source', severity: 'warning' },
  ]);
});

/** GET /usage — Check current usage against tier limit */
app.get('/usage', (req: Request, res: Response) => {
  const key = (req.headers['x-api-key'] as string) || req.ip || 'anonymous';
  const tier = getTier(key);
  const used = getUsage(key);
  res.json({
    tier: tier.name,
    limit: tier.limit,
    used,
    remaining: Math.max(0, tier.limit - used),
    window: '1 day',
    message: 'All tiers free during beta.',
  });
});

/** GET /favicon.ico — Serve branded favicon inline (no file dependency) */
app.get('/favicon.ico', (_req: Request, res: Response) => {
  res.setHeader('Content-Type', 'image/svg+xml');
  res.send(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#0F172A"/>
  <polygon points="16,6 25,16 16,26 7,16" fill="none" stroke="#22D3EE" stroke-width="2"/>
  <circle cx="16" cy="16" r="2" fill="#22D3EE"/>
</svg>`);
});

/** Catch‑all 404 for undefined routes */
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// ─── Start Server (local) or Export for Vercel ──────────────

if (!process.env.VERCEL) {
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
}

// Serverless export for Vercel
export default (req: Request, res: Response) => {
  app(req, res);
};