# Pruweba — Source Available

> **Proof, immutable.** — The verification layer of MetaLoop.

[![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-blue)](LICENSE)
[![Source Available](https://img.shields.io/badge/source-available-green)](https://pruweba.com)
[![Commercial](https://img.shields.io/badge/commercial-license%20required-red)](https://pruweba.com/pricing)

Pruweba is a deterministic proof engine that verifies claims, enforces invariants, and produces immutable evidence records. Named from the Cebuano word for "proof."

**⚠️ This repository is source-available, not open-source.** You may view, fork, and modify for noncommercial purposes only. Commercial use requires a [paid license](https://pruweba.com/pricing).

---

## What's in this repo

| Directory | Contents |
|-----------|----------|
| `site/` | Landing page (pruweba.com) and documentation (docs.pruweba.com) |
| `sdks/` | API client SDKs (TypeScript, Python) |
| `examples/` | Integration examples and tutorials |

## What's NOT in this repo

The verification engine (`@pruweba/engine`), API server, and evidence store are proprietary and maintained in a private repository. Commercial license holders receive access.

---

## Quick Start

### Landing Page
```bash
cd site/public
npx serve .   # Serves pruweba.com
```

### TypeScript SDK
```bash
npm install @pruweba/sdk
```

```typescript
import { PruwebaClient } from '@pruweba/sdk';

const client = new PruwebaClient({ apiKey: 'pw_live_...' });

const attestation = await client.verify({
  id: 'claim-001',
  subject: 'agent-alpha',
  predicate: 'produced_output',
  object: { hash: 'abc123' },
  origin: 'my-app',
  timestamp: new Date().toISOString(),
});

console.log(attestation.verdict.status); // "VERIFIED"
```

### Python SDK
```bash
pip install pruweba-sdk
```

```python
from pruweba_sdk import PruwebaClient

client = PruwebaClient(api_key="pw_live_...")

attestation = client.verify(
    id="claim-001",
    subject="agent-alpha",
    predicate="produced_output",
    object={"hash": "abc123"},
    origin="my-app",
)

print(attestation.verdict.status)  # "VERIFIED"
```

---

## API

The Pruweba API is available at `api.pruweba.com`. All endpoints require an API key passed as a `X-API-Key` header.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/verify` | Submit a claim for verification |
| GET | `/attestations` | List attestations (your API key's claims only) |
| GET | `/attestations/:id` | Get attestation by claim ID |
| GET | `/chain` | Full evidence chain |
| GET | `/chain/verify` | Verify chain integrity |
| GET | `/usage` | Current billing period usage |

---

## Pricing

| Tier | Price | Claims/mo | API Access | Support |
|------|-------|-----------|------------|---------|
| **Free** | $0 | 5 (one-time) | No | — |
| **Developer** | $29/mo | 1,000 | Yes | Email |
| **Pro** | $99/mo | 10,000 | Yes | Priority |
| **Enterprise** | $499/mo | Unlimited | Yes + Self-hosted | Dedicated |

[View full pricing →](https://pruweba.com/pricing)

---

## Contributing

We welcome noncommercial contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

By contributing, you agree that your contributions will be licensed under the same PolyForm Noncommercial 1.0.0 license.

---

## Governance

Pruweba's verification pipeline is governed by a proprietary evidence-based framework. Every claim must trace to source evidence. Every attestation is cryptographically verifiable. The governance framework is **licensed separately** and is not included in this public repository.

---

## License

**Source Available — PolyForm Noncommercial 1.0.0**

You may view, fork, and modify this code for noncommercial purposes only. Commercial use requires a paid license agreement with Pruweba.

[View full license →](LICENSE)
[Get commercial license →](https://pruweba.com/pricing)

Copyright (c) 2026 Pruweba. All rights reserved.
