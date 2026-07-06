# Pruweba — Deployment Config

## Architecture

```
pruweba.com       → Static landing page (packages/site/public/)
docs.pruweba.com  → Static docs (packages/site/public/docs/)
dev.pruweba.com   → API server (packages/api/)
```

## Deployment

### Prerequisites

- Node.js 22+
- npm 10+
- pruweba.com domain with DNS configured

### DNS Records

| Type | Name | Value |
|------|------|-------|
| A | pruweba.com | [server IP] |
| CNAME | dev | pruweba.com |
| CNAME | docs | pruweba.com |

### Static Site (pruweba.com + docs.pruweba.com)

Deploy `packages/site/public/` to any static host:

**Option A: Vercel**
```
vercel --prod
```

**Option B: GitHub Pages**
Push to `gh-pages` branch.

**Option C: Nginx**
```nginx
server {
    server_name pruweba.com docs.pruweba.com;
    root /var/www/pruweba-site/public;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### API Server (dev.pruweba.com)

```bash
# Build
cd packages/engine && npx tsc
cd ../api && npx tsc

# Run
node packages/api/dist/index.js
```

**systemd service:**
```ini
[Unit]
Description=Pruweba API
After=network.target

[Service]
Type=simple
User=www
WorkingDirectory=/opt/pruweba
ExecStart=/usr/bin/node packages/api/dist/index.js
Restart=on-failure
Environment=PORT=3100

[Install]
WantedBy=multi-user.target
```

**Nginx reverse proxy:**
```nginx
server {
    server_name dev.pruweba.com;

    location / {
        proxy_pass http://127.0.0.1:3100;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 3100 | API server port |
