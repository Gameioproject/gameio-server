# Retro Games — Stremio addon

A [Stremio](https://www.stremio.com/) addon that catalogs retro console games (NES through PS3) using
data from [IGDB](https://www.igdb.com/). Each console gets its own catalog, plus a searchable
"All Retro Games" catalog with genre filtering. A game's page shows its cover, screenshots, summary,
release year, genres and links; the stream list offers the trailer (when IGDB has one) and a
"Launch" entry that opens a URL you configure — a web emulator, a custom URI scheme handled by a
local launcher, etc.

**No ROMs are downloaded, hosted or served.** The addon only holds metadata.

## How it works

```
IGDB API ──(src/fetch-igdb.js)──▶ SQLite (data/games.db) ──(src/server.js)──▶ Stremio
```

| File                | Purpose                                                                           |
| ------------------- | --------------------------------------------------------------------------------- |
| `src/platforms.js`  | List of consoles (IGDB platform ids) — edit to add/remove systems                 |
| `src/igdb.js`       | IGDB client: Twitch auth, 4 req/s throttle, retry on 429/5xx                      |
| `src/fetch-igdb.js` | Sync script: pulls every game per platform into SQLite (re-runnable, incremental) |
| `src/db.js`         | SQLite schema and queries                                                         |
| `src/addon.js`      | Manifest + catalog/meta/stream handlers                                           |
| `src/server.js`     | HTTP server (`stremio-addon-sdk`'s `serveHTTP`)                                   |

## Requirements

- Node.js 22.9+ (or Docker)
- Twitch developer credentials for IGDB: create an app at
  <https://dev.twitch.tv/console/apps> (any OAuth redirect URL, category "Application Integration"),
  then copy its **Client ID** and generate a **Client Secret**.

## Setup

```bash
git clone <this repo> retroaddon && cd retroaddon
npm install
cp .env.example .env      # fill in IGDB_CLIENT_ID / IGDB_CLIENT_SECRET (and optionally the rest)
```

### 1. Fetch the games

```bash
npm run fetch
```

This walks every platform in `src/platforms.js`, 500 games per request, respecting IGDB's
4 requests/second limit and backing off on `429`/`5xx`. Expect ~25–40k games and a few minutes.

The script is safe to re-run:

- **Re-running** only fetches games IGDB has updated since the last completed sync for each platform.
- `npm run fetch:full` re-fetches everything (rows are upserted by IGDB id).
- `node --env-file=.env src/fetch-igdb.js --platform ps1,snes` limits the run to some platforms.

Run it periodically (cron, a scheduled `docker compose run`) to keep the catalog fresh.

### 2. Run the addon

```bash
npm start
# HTTP addon accessible at: http://127.0.0.1:7000/manifest.json
```

Open <http://127.0.0.1:7000/> for the landing/configure page, or paste the manifest URL into
Stremio (Addons → search box → paste URL).

## Manifest URL format

| URL                                       | Meaning                                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `http://HOST:7000/manifest.json`          | Default install; uses `LAUNCHER_URL_TEMPLATE` from the environment                                     |
| `http://HOST:7000/<config>/manifest.json` | Per-user config, where `<config>` is URL-encoded JSON, e.g. `{"launcher":"retro://{platform}/{slug}"}` |

The configure page at `/` (or Stremio's "Configure" button) builds the second form for you.
Example configured URL:

```
http://localhost:7000/%7B%22launcher%22%3A%22retro%3A%2F%2F%7Bplatform%7D%2F%7Bslug%7D%22%7D/manifest.json
```

Resource URLs follow the standard Stremio scheme, e.g.
`/catalog/game/retro-ps1/genre=Fighting&skip=100.json`, `/meta/game/igdb:1029.json`,
`/stream/game/igdb:1029.json`.

## Launcher URL template

The stream list contains one "Launch" entry per platform the game was released on. Its URL is the
template with these placeholders replaced (values are URL-encoded):

| Placeholder     | Example                               |
| --------------- | ------------------------------------- |
| `{igdb_id}`     | `1029`                                |
| `{name}`        | `Chrono%20Trigger`                    |
| `{slug}`        | `chrono-trigger`                      |
| `{platform}`    | `snes` (slug from `src/platforms.js`) |
| `{platform_id}` | `19` (IGDB platform id)               |
| `{year}`        | `1995`                                |

Examples:

```
https://play.example.com/?system={platform}&q={name}      # a web emulator front-end you host
retrolaunch://{platform}/{slug}                            # custom URI scheme handled by a local app
http://localhost:8080/launch?platform={platform}&igdb={igdb_id}   # a small local helper service
```

If no template is configured (neither env nor user config), only the trailer stream is returned.

## Configuration (environment)

| Variable                                | Default           | Description                                                                     |
| --------------------------------------- | ----------------- | ------------------------------------------------------------------------------- |
| `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET` | —                 | Twitch app credentials (fetch script only)                                      |
| `DB_PATH`                               | `./data/games.db` | SQLite file location                                                            |
| `PORT`                                  | `7000`            | Listen port                                                                     |
| `PUBLIC_URL`                            | —                 | Public base URL of the addon; enables in-app genre/platform links on game pages |
| `LAUNCHER_URL_TEMPLATE`                 | —                 | Default launcher template (users can override in the configure page)            |

## Hosting

Stremio requires addons to be reachable over HTTPS unless they run on `localhost`/LAN, so put the
addon behind a reverse proxy (Caddy, nginx, Traefik) with TLS and set `PUBLIC_URL` to that address.

### Docker

```bash
cp .env.example .env && edit .env
docker compose run --rm fetch            # populate the volume (add `-- --full` for a full re-sync)
docker compose up -d                     # serve on :7000
```

Or without compose:

```bash
docker build -t retro-addon .
docker run --rm --env-file .env -v retro-data:/data retro-addon node src/fetch-igdb.js
docker run -d --env-file .env -v retro-data:/data -p 7000:7000 --name retro-addon retro-addon
```

The database lives in the `/data` volume; re-run the fetch container whenever you want to refresh it
(the server picks up new rows immediately — no restart needed).

### Bare Node

Any host that runs Node 22 works (a VPS with `pm2`/systemd, Fly.io, Railway, etc.). Persist the
`DB_PATH` directory between deploys, or run the fetch script as part of the deploy.

## Adding or removing consoles

Edit `src/platforms.js` (IGDB platform ids are on each platform's IGDB page, or via the
`/platforms` endpoint), then run `npm run fetch` to pull the new platform's games. Removing an
entry hides its catalog immediately; its rows stay in the database harmlessly.

## Notes

- Game ids are `igdb:<IGDB id>`. A game released on several consoles appears in each console's
  catalog and gets one Launch entry per console.
- Stremio limits manifests to 8 KB, so per-platform catalogs only offer the most common genres (the
  count is trimmed automatically at startup); the "All Retro Games" catalog always lists every genre.
- Catalogs are sorted by popularity (IGDB rating count, then rating). Search matches substrings of
  the name, prefix matches first.
- The trailer is IGDB's video named "Trailer" when present, otherwise the game's first video.
