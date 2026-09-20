# Gameio Server

The backend for [Gameio](https://github.com/Gameioproject/gameio), the "Stremio for games" Android launcher, and the home of [playgameio.com](https://playgameio.com).

The server knows *about* games but never stores them. It keeps a catalog of games with IGDB metadata, the players' accounts and their saves. Download links come from add-ons that players import in the app.

## What it does

- **Catalog:** games per platform with covers, summaries, genres, ratings and trailers, with search, filters and discovery sections
- **Accounts:** sign-in, device tokens and permissions for the Gameio app, plus open sign-up from inside the app, capped by `GAMEIO_SIGNUP_MAX_USERS` (100 by default). Once the cap is reached the endpoint refuses new accounts and the app says so; `/api/heartbeat` reports whether sign-up is open and how many seats are left.
- **Account deletion:** `POST /users/delete-account` from the web page and `DELETE /users/me` from the app, both removing the account, its saves and its comments
- **Save sync:** stores save files and save states per game and device
- **Community:** comments on game pages, with replies, likes, reports and blocks
- **Add-on export:** `backend/tools/export_catalog_addon.py` publishes the server's source mappings as importable add-ons (see [docs/addon-format.md](docs/addon-format.md)). The two published samples, an Internet Archive one and a Real-Debrid one restricted to RetroAchievements-supported games, are built with it.
- **Website:** the landing page, the privacy, terms and account-deletion pages, and the APK downloads at playgameio.com

## Stack

FastAPI, SQLAlchemy and Alembic on MariaDB, with RQ and Valkey for background jobs, and nginx in front. The web frontend and landing page are built with Vite.

## Running it

- **Development:** `docker compose up -d gameio-dev` (API on port 5000, frontend on port 3000). See [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md).
- **Production image:**
  ```bash
  docker buildx build -f docker/Dockerfile --target full-image -t gameio:prod .
  ```
  The image needs MariaDB and the settings in [env.template](env.template). Production runs this image on a VPS behind a Cloudflare tunnel, with no ports open to the internet.

### APK hosting

nginx serves builds from two volumes: `/var/www/apk`, which the download button on the landing page points at, and `/var/www/test-apk`, served at `/test/` and marked `noindex` for builds that are handed out by link only.

More documentation is in [docs/](docs/): architecture, save sync, comments API and the add-on cutover.

## Credits and license

Gameio Server is a fork of [RomM](https://github.com/rommapp/romm) and is licensed under the [GNU AGPL v3](LICENSE).
