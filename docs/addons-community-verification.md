# Add-ons and community verification

Verified on 14 September 2026 on `feature/addons-community`. These checks cover
the server implementation and contract. Handheld interaction, final APK signing,
publication and the deployment cutover remain separate release checks.

## Backend regression

The final isolated PostgreSQL run passed **244 tests** in 29 seconds:

| Area                                                                      | Tests |
| ------------------------------------------------------------------------- | ----: |
| Comments, ownership, replies, pagination, moderation and rate limits      |    16 |
| Optional support URL                                                      |     8 |
| Source cutover endpoints                                                  |    21 |
| Source cutover handler policy                                             |    11 |
| Static add-on export                                                      |    34 |
| Catalog, discovery, play and assets                                       |    48 |
| Hosts and compatibility                                                   |    16 |
| Client-token authentication and isolation                                 |    33 |
| Existing source matching, indexing, platforms, preferences and resolution |    57 |

The test paths were `tests/endpoints/test_comments.py`, `test_support.py`,
`test_client_addon_cutover.py`, `test_catalog.py`, `test_hosts.py`,
`test_compat_argosy.py`, `test_client_tokens.py`, and `tests/handler/sources`.
The run used the configured PostgreSQL test container and test-only database.
It did not connect to the MariaDB device-QA database or production database.

Migration `0123_game_comments` was previously verified through fresh upgrades and
an upgrade/downgrade/upgrade cycle on both MariaDB and PostgreSQL test databases.
It adds four comment tables and preserves catalog rows. PostgreSQL's existing
binary asset column needs no MySQL LONGBLOB conversion; the unreleased `0119`
migration now skips that MySQL-only operation on PostgreSQL, with a regression
test. These isolated checks preceded the live application recorded below.

## Live comments migration

The authorized live deployment applied `0123_game_comments` on 14 September 2026.
Before applying it, the release operator verified a full SQL backup at
`/tmp/gameio-before-comments-migration-tx59m8as/database.sql.gz` (approximately
310 MB uncompressed, 19 MB compressed) and recorded the original table counts.
That backup is a private local recovery artifact and is not part of the repository.

The first attempt on MariaDB 11.3.2 stalled while committing
`CREATE INDEX IF NOT EXISTS idx_game_comments_parent ON game_comments
(parent_id, deleted_at)`. InnoDB reported two transactions belonging to the same
DDL connection, and an isolated QA token update also became blocked while opening
its table. Killing the DDL query did not release the stalled operation. The exact
engine cause was not established. MariaDB's
[MDEV-34253](https://jira.mariadb.org/browse/MDEV-34253) describes a related foreign
key DDL symptom, but is not confirmed as the cause of this incident.

The release operator restarted the database container after verifying the backup.
Recovery completed the parent index durably; the migration revision remained at
`0122`. Re-running the existing idempotent upgrade then finished in 0.56 seconds,
advanced to `0123`, and created all four comment tables. No migration-code
workaround, table removal, or data restore was required. The production counts
remained **29,183 catalog games, 2 users and 10,403 sources**; `game_comments` was
empty after recovery.

Use a quiet maintenance window for this DDL on the tested MariaDB version, with a
verified backup and database-operator access. The earlier fresh and reversible
test migrations passed without concurrent device-QA traffic. They demonstrate
schema compatibility, but do not rule out an engine stall under other conditions.

## Static checks and API contract

- Black 26.5.1, isort 8.0.1 and Ruff 0.15.22 pass for all 34 changed/new Python
  files. The final review corrected import ordering and the exporter's explicit
  URL-port validation expression.
- Mypy 2.3.0 checked the same 34 files. Its nine findings are all in existing
  task-list code: eight TypedDict expansions and a registry variable inferred as
  the wrong registry subtype. Checking the unchanged `HEAD` version reproduces
  the same nine findings. No unrelated task-list change was made.
- Bandit 1.9.4 reports no medium/high findings. Four low-severity assertion
  findings are on existing lines in catalog, compatibility and host endpoints.
- Trunk is unavailable in this environment, so the checks above use the
  repository-pinned tools and configuration directly. This is not a claim that
  the Trunk wrapper completed successfully.
- Regenerating OpenAPI types into a temporary directory matches all 134 checked-in
  TypeScript files, apart from insignificant trailing whitespace. The new comment
  types include moderation game context, and heartbeat exposes optional
  `FRONTEND.SUPPORT_URL`.
- `npm run typecheck` and all six landing-support tests pass.
- ESLint passes for the changed landing TypeScript and its test. Prettier 3.9.5
  with the configured sort-imports plugin formats the changed landing files and
  new documentation.
- `git diff --check` passes. Private environment and Compose backup files remain
  untracked and are excluded from the implementation artifacts.

## Isolated running-API checks

The Android QA setup authenticates through the real client-token flow and syncs
the isolated N64 catalog. Its opt-in helper excludes the built-in local Android
platform, and a rerun accepts only the same isolated account and loopback URL.

The two QA catalog rows received actual catalog metadata from a read-only query;
their database IDs, comments and account rows stayed intact. Their real HTTP
responses then passed through the compiled Android `RomMRom` Moshi adapter,
including IGDB identity, cover URLs, ratings, genres, screenshots, video IDs and
viewer properties. Both fixture games still have no server download sources.

A 39-byte test save uploaded to a separate QA channel passed list, detail and
content GET checks with the same asset ID, hash and bytes. Two subsequent
identical-hash `POST /api/sync/reconcile` calls both returned `no_op`. This catalog
backend advertises reconciliation rather than the legacy negotiate protocol.
These requests used only the isolated QA account and database.

## Deployment boundary

`GAMEIO_CLIENT_ADDONS_ONLY` defaults to false. Endpoint tests exercise both values:
legacy sources still work with false; true suppresses source locators and rejects
server source operations before database, network or queue work. Catalog identity,
metadata, comments and saves remain independent of that switch.

The controlled source export remains private test data. No add-on was published
or automatically installed by these checks. No support payment destination was
configured. Follow [the cutover guide](client-addon-cutover.md) only after the
verified APK is available, and preserve the existing source rows for rollback.
