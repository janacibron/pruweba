<<<<<<< HEAD
# Pruweba

> **Proof, immutable.** — The verification layer of MetaLoop.

Pruweba is a deterministic proof engine that verifies claims, enforces invariants, and produces immutable evidence records. Named from the Cebuano word for "proof."

## Pipeline

```
CLAIM → VERIFY → PROVE → ATTEST
```

## Quick Start

```bash
# Install
npm install

# Build engine
npx tsc -p packages/engine/tsconfig.json

# Run tests
npx tsx packages/engine/src/engine.test.ts

# Start API
npm run dev:api

# Verify it works
curl -X POST http://localhost:3100/verify \
  -H "Content-Type: application/json" \
  -d '{"id":"demo","subject":"test","predicate":"produced_output","object":"ok","origin":"cli","timestamp":"2026-01-01T00:00:00Z"}'

curl http://localhost:3100/chain/verify
```

## Packages

| Package | Path | Purpose |
|---------|------|---------|
| `@pruweba/engine` | `packages/engine` | Core verification engine |
| `@pruweba/api` | `packages/api` | REST API server |
| `@pruweba/site` | `packages/site` | Landing page + docs |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/verify` | Submit a claim for verification |
| GET | `/attestations` | List all attestations |
| GET | `/attestations/:id` | Get attestation by claim ID |
| GET | `/chain` | Full evidence chain |
| GET | `/chain/verify` | Verify chain integrity |
| GET | `/health` | Health check |

## Domains

| Domain | Content |
|--------|---------|
| pruweba.com | Landing page |
| dev.pruweba.com | API server |
| docs.pruweba.com | Documentation |

## Governance

RPES v1.0 compliant. Every claim traces to evidence. Every evidence record has a source.
=======
# 34-Pillar Framework

The implementation backbone of Pruweba's governed automation practice.

## What this is

This repository contains the concrete pillar definitions used in Pruweba's 34-pillar operations governance framework. Each pillar is a single testable responsibility. Together they form verification, recovery, lineage, anti-corruption, and enterprise-value controls for e-commerce operations automation.

## Structure

- `pillars/` — pillar implementations grouped by family
- `README.md` — this file
- `LICENSE` — MIT

## Pillar groups

- Federation — constitutional core and data federation
- Truth — verification, evidence, and provenance
- Research — prediction, exploration, and knowledge
- Operations — scheduling, orchestration, delivery, and mutation policy
- Intelligence — data sources, confidence, coupling, planning, coordination
- Boundary — execution isolation, governance gates, recovery, telemetry
- Enterprise — economic continuum, enterprise value, risk-aware trading

## Relationship to Pruweba

Pruweba is a solo engineering practice owned by Jan Michael Acibron.
Website: https://pruweba.com
GitHub: https://github.com/rankfixer-ai
LinkedIn: https://linkedin.com/in/jan-michael-acibron

## License

MIT
>>>>>>> 1d691a18627001e31e56452bb3e4096500ed35ea
