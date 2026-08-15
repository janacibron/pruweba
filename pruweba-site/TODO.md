# Client Portal — Open TODO

Status as of 2026-08-11. Auth code is written and verified (`npm run test` = 9/9,
`npm run test:auth` = LIVE_AUTH_OK). Production at https://pruweba.com is already
running the authenticated build. Remaining work is Supabase dashboard config,
not code.

## 1. BLOCKING — Supabase Auth URL configuration
Magic-link login cannot work until this is fixed.

Evidence: `admin/generate_link` was asked for four different `redirect_to`
targets and **all four** were overridden to `https://pruweba-ainovationtracker.vercel.app/`:

    https://pruweba.com/portal.html                   OVERRIDDEN
    https://pruweba.com/                              OVERRIDDEN
    https://pruweba-ainovationtracker.vercel.app/...  OVERRIDDEN
    http://localhost:3000/portal.html                 OVERRIDDEN

Supabase falls back to **Site URL** when `redirect_to` is not on the allow-list.
Everything falling back means the allow-list is not matching at all.

Fix in **Authentication → URL Configuration**:
- Site URL: `https://pruweba.com`
- Redirect URLs: add `https://pruweba.com/**`
  (the `/**` wildcard matters — an exact path often will not match the
  `#`-fragment callback)

## 2. Verify the fix (deterministic, no inbox needed)
Re-run `admin/generate_link` and confirm `redirect_to` comes back as
`https://pruweba.com/portal.html` instead of being overridden.

## 3. The `otp_expired` error was a symptom, not a separate bug
The link landed on `vercel.app` (HTTP 302, not the app), so nothing ran
`detectSessionInUrl` and the single-use token was never consumed. Fixing #1
resolves this.

## 4. Email delivery — still unproven
`generate_link` works (admin API, does not send), so the token pipeline is
healthy. Actual *sending* is untested. Supabase's built-in mailer is rate
limited to ~3–4/hour and frequently fails to Gmail. If mail still does not
arrive after #1, configure custom SMTP (Resend / SendGrid) under
**Authentication → Emails**.

## 5. Assign the project owner
No project currently has `assigned_user_email` set, so every authenticated
request returns 403.

```sql
update public.client_projects
set assigned_user_email = 'jan377acibron@gmail.com'
where client_name = 'Paydora_Payments';
```

## 6. End-to-end browser test
Sign in at https://pruweba.com/login.html and confirm the dashboard renders
with the session email in the header.

## 7. Commit (not yet done — nothing is committed)
Three separate commits, each through the governance hook:
1. `api/` + `tests/`
2. frontend: `login.html`, `auth.js`, `portal.html`, `portal.js`
3. `supabase_schema.sql`

## 8. Optional — reset the demo
`Paydora_Payments` is at **5/5 (100%)**; the seals are real and the chain
verifies (root `aab2fe8b7153bfd3…`). Nothing is left to sign off, so a live
demo has nothing to click. Consider `npm run reset:demo` to restore it to 0/5.

## Notes / gotchas
- `.env` is gitignored and holds real keys. Never commit it.
- npm scripts must not use forward-slash paths to `.venv` — npm shells out to
  cmd.exe on Windows, which rejects them. Current scripts go through
  `python -c subprocess.call([os.path.join(...)])`.
- `typecheck` / `build` scripts intentionally do not exist: static HTML +
  vanilla JS + Python functions, nothing to compile or bundle.
- Live tests are non-destructive — they provision a sandbox project and
  throwaway users, then delete them in a `finally` block.
