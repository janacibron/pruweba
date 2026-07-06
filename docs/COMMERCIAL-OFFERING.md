# Pruweba Commercial Offering

## Pricing

| Feature | Free | Developer | Pro | Enterprise |
|---------|------|-----------|-----|------------|
| **Price** | $0 | $29/mo | $99/mo | $499/mo |
| **Claims/month** | 5 (one-time) | 1,000 | 10,000 | Unlimited |
| **API Access** | — | ✓ | ✓ | ✓ |
| **Attestation Storage** | 24h | 30 days | 1 year | Permanent |
| **Rate Limit** | 1/min | 10/sec | 100/sec | 1,000/sec |
| **SLA** | — | — | — | 99.9% |
| **Support** | — | Email | Priority | Dedicated |
| **Self-hosted** | — | — | — | ✓ |
| **Custom Invariants** | — | — | — | ✓ |
| **White-label** | — | — | — | ✓ |
| **Source Access** | Public only | — | — | ✓ |
| **Commercial License** | — | ✓ | ✓ | ✓ |

## Feature Details

### Free Tier
- 5 one-time verification claims per IP
- No sign-up required
- For evaluation only — not for commercial use
- Attestations purged after 24 hours

### Developer Tier ($29/mo)
- 1,000 claims per month
- Full API access with API key
- Email support (48-hour response)
- 7-day free trial
- Overage: $0.05/claim

### Pro Tier ($99/mo)
- 10,000 claims per month
- Priority support (4-hour response)
- Higher rate limits
- 1-year attestation storage
- Overage: $0.05/claim

### Enterprise Tier ($499/mo)
- Unlimited claims
- Self-hosted deployment option
- Custom invariant rules
- White-label integration
- Dedicated support engineer
- 99.9% SLA with credits
- Source code access
- Annual billing available (2 months free)

## API Endpoints

### Free Access (no API key)
```
POST api.pruweba.com/verify
  - Rate limit: 1/min per IP
  - Max 5 claims per IP (lifetime)
  - Attestations purged after 24h
```

### Paid Access (API key required)
```
POST api.pruweba.com/v1/verify
GET  api.pruweba.com/v1/attestations
GET  api.pruweba.com/v1/attestations/:id
GET  api.pruweba.com/v1/chain
GET  api.pruweba.com/v1/chain/verify
GET  api.pruweba.com/v1/usage
```

All paid endpoints require: `X-API-Key: pw_live_...`

## Trial

7-day free trial on Developer tier. No credit card required to start. Upgrade to Pro or Enterprise anytime.

## Enterprise Self-Hosted

Enterprise customers may deploy Pruweba on their own infrastructure:

- Docker container provided
- Kubernetes Helm chart available
- Runs on any Linux server (2GB RAM minimum)
- Connects to your existing monitoring stack
- Full source code access for audit

## Contact

commercial@pruweba.com
pruweba.com/pricing
