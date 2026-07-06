# @pruweba/client

Pruweba API client for JavaScript/TypeScript. Submit claims, verify evidence, check chain integrity.

```bash
npm install @pruweba/client
```

## Quick Start

```ts
import { pruweba } from "@pruweba/client";

// Submit a claim
const att = await pruweba.verify({
  id: "my-claim-001",
  subject: "system-health",
  predicate: "status",
  object: "operational",
  origin: "my-agent",
  timestamp: new Date().toISOString(),
});

console.log(att.verdict.status); // "VERIFIED" | "REJECTED" | "UNVERIFIABLE"

// Verify the chain
const chain = await pruweba.verifyChain();
console.log(chain.valid); // true

// List all attestations
const all = await pruweba.getAttestations();

// Health check
const health = await pruweba.health();
```

## API

| Method | Endpoint | Description |
|---|---|---|
| `verify(claim)` | `POST /verify` | Submit a claim for verification |
| `getAttestations()` | `GET /attestations` | List all attestations |
| `getAttestation(id)` | `GET /attestations/:id` | Get attestation by claim ID |
| `getChain()` | `GET /chain` | Full evidence chain |
| `verifyChain()` | `GET /chain/verify` | Verify chain integrity |
| `health()` | `GET /health` | Health check |
| `getInvariants()` | `GET /invariants` | List registered invariants |

## Custom Base URL

```ts
import { PruwebaClient } from "@pruweba/client";
const client = new PruwebaClient("https://dev.pruweba.com");
```

## License

MIT
