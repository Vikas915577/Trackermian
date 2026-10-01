# Winter Arc V24.2 — Senior QA Fix Pack

This pack is based on the current `V24.1` GitHub source that was audited.

## What is fixed

- Exact Top 20 is driven through the Supabase RPCs already present in the backend schema.
- Adds the missing client-side `rankFetch()` RPC helper.
- Loads exact personal rank, active named users, and community counts.
- Active users show their exact global rank, including a user outside Top 20.
- Search keeps the original Top-20 rank numbers.
- Adds `Community users`, `Public profiles`, `Active now`, and `Active 24h` counters.
- Moves the creator credit to the top of Today and shows the 3 creator photos as a clean card.
- Shows the creator card on the new-user/local-profile screen too.
- Restores direct Rank and Profile bottom navigation; Month and Arc remain available from More.
- Bumps the app version to V24.2.

## Central user data

The app only knows named users centrally when Community Sync is enabled and the Supabase backend is configured. `cloud-config.js` in the current repo is blank, so the deployed repo currently has no configured Supabase URL/anon key.

GitHub Pages/repository traffic is separate from app users. It can show visitor/clone traffic, but it does not provide the app's display names. GitHub documents repository traffic separately from application-level user data.

## Apply

1. Put the repository files in a local folder.
2. Run `python3 app-v24.2-patch.py` from the repo root.
3. Run `community-stats.sql` in Supabase SQL Editor.
4. Configure `cloud-config.js` with the Supabase URL + public anon key (never a service-role key).
5. Make sure Supabase Anonymous Sign-Ins are enabled.

The Python patch keeps a backup as `app.js.v24.1-backup` before replacing `app.js`.
