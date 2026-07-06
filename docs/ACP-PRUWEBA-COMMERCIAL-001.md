# RPES Compliance Report — Pruweba Commercialization

**ACP-ID:** ACP-PRUWEBA-COMMERCIAL-001
**Date:** 2026-07-06
**Status:** ACHIEVED
**Classification:** RESTRICTED — RPES Foundation Internal

---

## 1. Executive Summary

The Pruweba verification engine has been packaged for commercial distribution with a three-repository strategy, tiered pricing, full legal documentation, and public SDKs.

| Metric | Count |
|--------|-------|
| Repositories created | 3 (public, core, infra) |
| License files deployed | 3 |
| Legal documents drafted | 4 |
| SDKs created | 2 (TypeScript, Python) |
| Marketing pages | 2 (landing, pricing) |
| Copyright headers added | 8/8 engine files |
| Evidence records | See Section 7 |

## 2. Repository Structure

### pruweba-public
```
pruweba-public/
├── LICENSE              — PolyForm Noncommercial 1.0.0
├── README.md            — Source-available notice + badges
├── CONTRIBUTING.md      — Contribution guidelines
├── site/public/
│   ├── index.html       — Landing page (polished)
│   ├── pricing.html     — Pricing page
│   └── docs/index.html  — API documentation (polished)
├── sdks/
│   ├── typescript/src/index.ts  — @pruweba/sdk TS client
│   └── python/pruweba_sdk/      — pruweba-sdk Python client
└── examples/            — (directory ready)
```

### pruweba-core
```
pruweba-core/
├── LICENSE              — Proprietary
├── README.md            — Access control notice
└── packages/engine/src/
    ├── types.ts         — [Copyright header]
    ├── claim.ts         — [Copyright header]
    ├── verify.ts        — [Copyright header]
    ├── prove.ts         — [Copyright header]
    ├── attest.ts        — [Copyright header]
    ├── evidence-store.ts — [Copyright header]
    ├── index.ts         — [Copyright header]
    └── engine.test.ts   — [Copyright header]
```

### pruweba-infra
```
pruweba-infra/
├── README.md
├── docker/
├── ci/
├── terraform/
└── monitoring/
```

## 3. Licensing

| Repository | License | Access |
|------------|---------|--------|
| pruweba-public | PolyForm Noncommercial 1.0.0 | Public (source-available) |
| pruweba-core | Proprietary | Authorized only |
| pruweba-infra | Proprietary | Authorized only |

## 4. Commercial Tiers

| Tier | Price | Claims/mo | Key Differentiator |
|------|-------|-----------|--------------------|
| Free | $0 | 5 (lifetime) | Evaluation only |
| Developer | $29/mo | 1,000 | API + commercial license |
| Pro | $99/mo | 10,000 | Priority support |
| Enterprise | $499/mo | Unlimited | Self-hosted + source access |

## 5. Legal Documents

| Document | Path | Status |
|----------|------|--------|
| PolyForm Noncommercial License | pruweba-public/LICENSE | Deployed |
| Proprietary License | pruweba-core/LICENSE | Deployed |
| Commercial License Agreement | docs/legal/COMMERCIAL-LICENSE-AGREEMENT.md | Drafted |
| Terms of Service | docs/legal/TERMS-OF-SERVICE.md | Drafted |
| Privacy Policy | docs/legal/PRIVACY-POLICY.md | Drafted |
| NDA Template | docs/legal/NDA-TEMPLATE.md | Drafted |

## 6. Verification Gates

| Gate | Status | Evidence |
|------|--------|----------|
| Engine tests | PASS | 18/18 passing (engine.test.ts) |
| API health | PASS | `{"status":"ok","chainValid":true}` |
| Copyright headers | PASS | 8/8 engine files |
| License files | PASS | 3 repos with correct licenses |
| Public README badges | PASS | License + Source Available + Commercial badges |
| Pricing page | PASS | All 4 tiers with feature comparison |
| SDK shells | PASS | TypeScript + Python with verify() method |
| Website renders | PASS | Semantic HTML, responsive, accessible |

## 7. Evidence Records

| ID | Artifact | Location |
|----|----------|----------|
| E-001 | Engine integration tests | pruweba-core/packages/engine/src/engine.test.ts |
| E-002 | API health check | `curl localhost:3100/health` — `{"status":"ok"}` |
| E-003 | Verdict: VERIFIED | `att-000003` — claim-002 verified with confidence 0.6 |
| E-004 | Chain integrity | `GET /chain/verify` — `{"valid":true}` |
| E-005 | Copyright headers | 8 files in pruweba-core/packages/engine/src/ |
| E-006 | PolyForm license | pruweba-public/LICENSE — deployed |
| E-007 | Proprietary license | pruweba-core/LICENSE — deployed |
| E-008 | Commercial License Agreement | docs/legal/COMMERCIAL-LICENSE-AGREEMENT.md |
| E-009 | ToS | docs/legal/TERMS-OF-SERVICE.md |
| E-010 | Privacy Policy | docs/legal/PRIVACY-POLICY.md |
| E-011 | NDA Template | docs/legal/NDA-TEMPLATE.md |
| E-012 | Pricing page | pruweba-public/site/public/pricing.html |
| E-013 | TypeScript SDK | pruweba-public/sdks/typescript/src/index.ts |
| E-014 | Python SDK | pruweba-public/sdks/python/pruweba_sdk/client.py |

## 8. Next Steps (Deferred)

| Item | Trigger |
|------|---------|
| Stripe billing integration | When Stripe account is provisioned |
| API key management system | When api.pruweba.com is deployed |
| npm publish (@pruweba/sdk) | When npm org is created |
| Customer portal | When first paying customer onboarded |
| Usage monitoring dashboard | Post-launch |

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| License non-compliance | Medium | High | Clear README badges, domain verification |
| Source leak (core) | Low | Critical | Private repo, access control, NDA |
| Pricing pushback | Low | Low | Free tier for evaluation, 7-day trial |
| RPES exposure | N/A | High | RPES name removed from all public pages. Referenced as "proprietary verification framework." Licensed separately. |

## 10. RPES Privacy Decision

**Date:** 2026-07-06
**Decision:** RPES is not disclosed publicly. All public Pruweba assets refer to a "proprietary verification framework (licensed separately)." RPES will remain private until market validation confirms demand.

**Updated files:**
- Landing page footer — "Governed by a proprietary verification framework (licensed separately)"
- Brand brief — "Compliance with proprietary verification framework"
- Launch assets — "Proprietary verification framework (licensed separately)"
- Public README — Governance section added, RPES not named
- Docs page — No RPES references (already clean)

---

**Classification:** ACHIEVED
**Re-audit trigger:** On first paid customer or 30 days
