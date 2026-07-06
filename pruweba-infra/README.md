# Pruweba Infrastructure — Proprietary

Deployment and operations for Pruweba API and services.

## Contents

| Directory | Purpose |
|-----------|---------|
| `docker/` | Dockerfiles and compose configs |
| `ci/` | GitHub Actions / CI pipelines |
| `terraform/` | Infrastructure as Code |
| `monitoring/` | Prometheus, Grafana, alerting |

## Quick Deploy

```bash
# Build and run with Docker
cd docker
docker compose up -d

# API available at http://localhost:3100
curl http://localhost:3100/health
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| PORT | No | 3100 | API server port |
| API_KEY_SECRET | Yes | — | Secret for signing API keys |
| STRIPE_SECRET_KEY | Yes* | — | Stripe API key (for billing) |
| STRIPE_WEBHOOK_SECRET | Yes* | — | Stripe webhook signing secret |

*Required for commercial deployment with billing.

## Architecture

```
Client → api.pruweba.com (Nginx) → Pruweba API (Node.js) → Evidence Store (in-memory)
                                                              ↓
                                                         Stripe (billing)
                                                              ↓
                                                         Prometheus (metrics)
```

## Monitoring

- Health check: `GET /health`
- Metrics: `GET /metrics` (Prometheus format)
- Chain integrity: `GET /chain/verify`

## License

Proprietary. Unauthorized use prohibited.
