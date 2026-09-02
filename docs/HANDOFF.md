# Handoff: continuing Gameio work on a new machine

Written 2026-09-03 by the Claude Code session that did the Gameio rebrand. Read this
first when picking the project up on a different device. The paired client repo is
`naifqarni/gameio` (public); this repo (`gameio-server`, private) holds the server,
the landing page, and this note.

## What Gameio is

"Stremio for retro games" (domain: **playgameio.com**, bought, not yet deployed).
A catalog server (this repo, a RomM fork, branch `catalog-compat`) plus an Android
launcher (`gameio`, an Argosy fork, branch `catalog-browse-ux`). The server holds
metadata only: 29,183 games / 38,302 platform listings from an IGDB snapshot, ROM
downloads 302-redirect to Internet Archive hosts, covers hotlink to IGDB's CDN.

## State at handoff — done and verified

- **Rebrand**: applicationId `com.playgameio.app` (namespace stays `com.nendo.argosy`
  on purpose — upstream merges), label Gameio, `gameio://` scheme, Rack launcher icon
  (adaptive vectors + monochrome), all locales, splash, themes, notification channel,
  Steam/UPnP/User-Agent names. Server: title, containers `gameio-*`, version
  `5.1.0-gameio` (the client splits versions on `-`, so this parses fine).
- **Auth**: username/password → `POST /api/client-tokens` with HTTP Basic → long-lived
  `rmm_` token. Device pairing/QR is deleted. Scope negotiation: non-admins cannot hold
  `platforms.write`/`roms.write`/`firmware.write`; on 403 the client drops exactly the
  refused scopes and retries once. **Always test auth with a non-admin** — admins
  bypass scope checks and hide these bugs.
- **Sign-in / welcome screens**: branded dark (ground #0B0E13, coral #FF6B4A, Rack
  mark, two-pane in landscape). Verified on the emulator from a wiped first-run as
  user `naif`: 403 → retry with 13 scopes → 201 → "Connected successfully".
- **Save sync**: works end-to-end on the catalog fork (battery saves). `game_assets`
  blobs are LONGBLOB, `max_allowed_packet=128M`, `GET /states` exists. The
  download-direction restore on real hardware and the RA smoke test remain untested.
- **Landing page**: `landing/index.html` (nuvio-style, real app screenshot in
  `landing/brand/app-home.jpg`). nginx template routes `= /` → landing, `/brand/`,
  `/apk/` (volume, correct APK MIME), then the web app and `/api`.
  `scripts/publish-apk.sh` writes content-hashed APKs + `latest.json`.

## The unfinished piece: the RELEASE build

Debug builds work and were user-tested. A **release** build has never completed:
lint OOM (fixed: 7g heap), missing translations (fixed), config-cache (fixed) — the
final attempt died when the machine shut down mid-compile. On the new machine:

```bash
cd argosy-launcher && ./gradlew :app:assembleRelease
```

Expect ~1h cold (Compose IR pass is single-threaded). Then **verify the R8-minified
APK on an emulator with a real sign-in before publishing** (minification can break
what debug didn't), publish via `scripts/publish-apk.sh`, and only then hand the APK
to the user's handheld. The published debug APK is intentionally labelled Gameio DBG;
users should get the release, labelled Gameio.

**Signing**: `keystore.properties` + `release.keystore` are gitignored and did NOT
travel with this repo. Either copy both files from the old machine
(`argosy-launcher/` root; storeFile is `../release.keystore`, alias `gameio`), or —
since **no release has ever shipped, so the key has signed nothing** — regenerate:

```bash
keytool -genkeypair -keystore release.keystore -alias gameio -keyalg RSA \
  -keysize 4096 -validity 10950 -dname "CN=Gameio, O=Gameio, C=SA"
# then write keystore.properties (storeFile=../release.keystore, alias gameio)
```

Whichever key builds the first *distributed* release becomes permanent — back it up.

## Rebuilding the dev environment

1. `cp env.template .env`, fill: `DB_HOST=gameio-db-dev`, `REDIS_HOST=gameio-valkey-dev`,
   IGDB creds (Naif has them), generated `ROMM_AUTH_SECRET_KEY`.
2. `docker compose up -d` — backend :5000, Vite :3000. Note: the db volume is pinned
   to `romm-lite_romm-db-dev` in docker-compose.yml (legacy name, kept so the old
   machine's data survived the rename). A fresh machine just gets an empty one.
3. Catalog: download the `games.db` release asset (release tag `catalog`) and run the
   importer the previous sessions used (`backend/tools/`), or re-run host indexing.
4. Users + host configs: `docs/dev-state/users-and-hosts.sql` restores the `users`
   and `game_hosts` tables (test accounts: admin `claudetest`/`REDACTED`, non-admin
   `naif`/`REDACTED`).
5. Android toolchain on the old machine lived at `~/.local/toolchain/env.sh`
   (JDK 17, SDK, node). Emulator AVD was `argosy-test`; needs /dev/kvm access.
6. LAN testing: Windows portproxy maps `192.168.8.106:{3000,5000}` → WSL. Vite serves
   `/landing.html`, `/apk` (listing), `/brand/` from `frontend/public/` in dev.

## Deploy plan (agreed, not started)

DigitalOcean $12 droplet (Bangalore), Docker Compose + the production image
(nginx+gunicorn; set `WEB_SERVER_CONCURRENCY=4`), Caddy or nginx for TLS on
playgameio.com, server URL then hardcoded in the app (one constant:
`RomMConnectionManager` / first-run default). Accounts are admin-created; no
self-registration. QuayPass ships dark (no server for it; release gate only warns).

## Known loose ends

- Release build + R8 verification + publish (above).
- The user's GitHub PAT and IGDB secret were pasted into old session transcripts —
  advise rotating the PAT; new pushes need a fresh token or credential helper.
- `.env.template-backup` (untracked, this repo) and `gradle.properties.bak`
  (untracked, launcher) are leftovers; delete when convenient.
- First-run success screen says "38302 games" (sum of per-platform listings, not
  distinct games — verified correct data, just ambiguous wording; user hasn't chosen
  between "29,183 games" and "38,302 titles").
- Landing page + APK route are dev-served only; production needs the droplet.
