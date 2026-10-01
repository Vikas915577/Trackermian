# V24.2 QA Status

## Current repo audit

The current GitHub `main` source is V24.1. The final clean shell already exists, but the source contains multiple legacy definitions/overrides, so edits must stay surgical.

### Findings

- The final V24.1 rank loader calls `rankFetch(...)`, but the client-side helper is missing from the source. This makes the RPC-based rank path fail.
- The final rank screen already has exact-rank and active-user state variables, but active named users were not rendered in the final UI.
- Community user counts were not available in the client UI.
- The creator credit at the top requirement was not met: Today showed only a compact one-photo card at the bottom.
- The clean shell used Month/Arc in the bottom nav instead of the more useful Rank/Profile direct access used in the earlier V21-style UX.
- The backend already has deterministic leaderboard/rank/active RPCs. V24.2 adds a `get_community_stats()` RPC.
- `cloud-config.js` is blank in the repo, so central named-user storage is not configured in the deployed source.

## Verification performed on the prepared patch

- The patched JavaScript is checked with `node --check` by the patch script before it writes the new file.
- The patch adds a separate backup of the original `app.js`.

## GitHub write blocker

The GitHub connector can read the repository, but write operations currently return HTTP 403 `Resource not accessible by integration`. Because of that, the prepared V24.2 changes could not be committed to `main` from this session.
