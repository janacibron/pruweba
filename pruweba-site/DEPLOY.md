# Deploying this to pruweba.com

This folder is a plain Node.js/Vercel project: a static `index.html`
plus one serverless function at `api/chat.js`. No build step, no
framework — Vercel serves `index.html` as-is and auto-detects
`api/chat.js` as a serverless endpoint.

## First time on this machine

```bash
npm install -g vercel
vercel login
```

## Link to the existing project (don't create a new one)

From inside this folder:

```bash
vercel link
```

When prompted, choose the **ainovationtracker** team and the
existing **pruweba** project — this points your local folder at the
same project currently live at pruweba.com, instead of creating a
duplicate.

## Set the API key (one-time, do this in the dashboard, not in code)

Vercel dashboard → project **pruweba** → Settings → Environment
Variables → add:

```
ANTHROPIC_API_KEY = <your key>
```

Apply it to both **Production** and **Preview** environments. Never
put the key in `chat.js`, `index.html`, or anywhere committed —
that's the whole point of moving the chatbot to a serverless
function instead of calling Anthropic from the browser.

## Deploy

```bash
vercel --prod
```

This uploads the folder and replaces the production deployment at
pruweba.com — the same mechanism (`vercel deploy`) that put the
current site live, so it'll behave the same way you're used to.

## Optional: connect Git for auto-deploy later

The project's production checklist flagged "Connect Git Repository"
as unchecked. If you'd rather push to a GitHub repo and have Vercel
auto-deploy on every push (instead of running `vercel --prod`
manually each time), that's a one-time setup in the dashboard under
Settings → Git. Not required for this deploy — just an option if you
want it going forward.

## Verify after deploy

1. Visit pruweba.com and open the chat widget (bottom-right "?").
2. Ask a pillar question — e.g. "what does Idempotency Guard do?"
3. If you get a 502 error in the widget, check Vercel → Logs for the
   `api/chat` function — most likely cause is a missing/incorrect
   `ANTHROPIC_API_KEY`.
