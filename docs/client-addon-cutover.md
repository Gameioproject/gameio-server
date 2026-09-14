# Client add-on cutover

`GAMEIO_CLIENT_ADDONS_ONLY` defaults to `false` so an API update can be staged before the new APK is available. Set it to `true` for the final release after the APK passes device verification and has been published. Restart the API and every queue worker together so queued jobs use the same policy. This change does not enable the switch in a live environment.

With the switch enabled:

- Catalog search, genres, platforms, favorites, play history, comments, and metadata remain available. Synthetic compatibility ROM IDs and save routes keep their existing identity.
- Catalog responses return `sources: []` and `owned: false`. Compatibility ROMs return `files: []`, `has_download: false`, zero source file size, and no source path. These compatibility values mean the server offers no file; the client determines availability from its own add-ons and local folder.
- `owned` and `owned_platforms` filters no longer narrow the metadata catalog. Source ownership counts are zero, and the compatibility `added` sort uses catalog identity order rather than source timestamps.
- The host list returns an empty list. Source/host mutations, redirect downloads, GET/HEAD streaming proxies, compatibility content downloads, and manual source-index enqueue return HTTP 410 before accessing a host or queue.
- Source resolution, index execution, and source database mutations also reject at their handler entry points. Already queued index jobs cannot resume source work in a worker running the new policy.

The existing source database remains intact. The private `backend/tools/export_catalog_addon.py` migration utility still reads the stored mappings and writes an explicit private output directory. It neither publishes a manifest nor serves credentials. A migration operator can prepare the controlled test add-on before the final cutover.

The switch intentionally leaves metadata ingestion and saves operational. It does not delete source records, edit the live environment, install an add-on for a user, or expose a provider store.

## Rollout sequence

1. Keep `GAMEIO_CLIENT_ADDONS_ONLY=false` while staging the server code. Verify the new APK on a handheld: import a controlled test add-on, resolve a game, cancel/retry a download, discover a copied local game, and retain its existing save identity. Publish that verified APK before disabling the legacy server sources.
2. Keep the source database and its normal backup. Prepare any migration export in a private directory using [the add-on format and export guide](addon-format.md). An export is not an installed add-on: replace any placeholder manifest URL with the approved test host and explicitly import it on the test client.
3. Build the server image while the existing service continues to run. From this repository's Compose directory:

   ```sh
   docker compose build gameio-dev
   ```

4. Set the deployment's existing `.env` entry to `GAMEIO_CLIENT_ADDONS_ONLY=true`. Recreate the application container to load the changed environment into the API, scheduler, and RQ worker together:

   ```sh
   docker compose up -d --no-deps --force-recreate gameio-dev
   ```

   A plain `docker compose restart` does not reload `.env` into an existing container. This repository's `entrypoint.sh` starts the API and workers inside `gameio-dev`; a deployment with separate worker services must recreate all of those services in the same cutover. Stop old workers so an already-running index job cannot continue with the old policy. Do not remove database volumes or flush the task queue.

5. Confirm the application has restarted successfully and verify the flag without printing the environment or credentials:

   ```sh
   docker exec -w /app/backend gameio-dev uv run python -c 'from config import GAMEIO_CLIENT_ADDONS_ONLY; print(GAMEIO_CLIENT_ADDONS_ONLY)'
   ```

   The output must be `True`. With an authenticated client, check that a known catalog game retains its IGDB and compatibility ROM IDs, returns no source locators, and remains discoverable with either `owned` filter value. The host list must be empty; a known source download and an index request must return HTTP 410. Confirm add-on/local launch and save access still work. `/heartbeat` alone is insufficient to verify this switch because `CATALOG_ONLY` also describes the catalog architecture before cutover.

## Rollback sequence

1. Restore `GAMEIO_CLIENT_ADDONS_ONLY=false` in the same deployment environment.
2. Recreate the same application and worker services, using the `docker compose up -d --no-deps --force-recreate gameio-dev` command above for this repository's stack.
3. Repeat the flag check and expect `False`. Verify that a previously known source is exposed and resolves through the legacy client, while catalog IDs and saves remain unchanged.

The retained source rows support rollback without a database restore or reindex. Index jobs rejected during cutover remain failed jobs; retry any still-needed jobs explicitly after rollback. The new client's installed add-ons and local files remain on the device.
