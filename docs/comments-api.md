# Game comments

Comments attach to the catalog's IGDB game ID and are shared across platforms and installed files. Bodies are plain text, up to 2,000 characters. A user may post several comments on the same game.

All routes use the existing authenticated session, bearer token, or client token. Reads require `roms.read`. Posting, editing, deleting, liking, and reporting also require `roms.user.write`. Kiosk guests can read but cannot participate.

| Method | Route under `/api`            | Body or query                              | Response                        |
| ------ | ----------------------------- | ------------------------------------------ | ------------------------------- |
| GET    | `/catalog/{igdb_id}/comments` | `sort=top\|newest`, `limit=20`, `offset=0` | Comment page                    |
| POST   | `/catalog/{igdb_id}/comments` | `{body, spoiler:false, parent_id:null}`    | 201, comment                    |
| GET    | `/comments/{id}/replies`      | `limit=20`, `offset=0`                     | Comment page, oldest first      |
| PATCH  | `/comments/{id}`              | `{body, spoiler:false}`                    | Updated comment                 |
| DELETE | `/comments/{id}`              | None                                       | 204                             |
| PUT    | `/comments/{id}/like`         | `{liked:true}`                             | Updated comment                 |
| PUT    | `/comments/{id}/report`       | `{reason}`                                 | 204                             |
| GET    | `/comments/blocks`            | None                                       | Author list, requires `me.read` |
| PUT    | `/comments/blocks/{user_id}`  | None                                       | 204, requires `me.write`        |
| DELETE | `/comments/blocks/{user_id}`  | None                                       | 204, requires `me.write`        |

Comment pages contain `{items,total,limit,offset}`. The maximum page size is 50. The root page's `total` counts top-level conversations; a reply page's `total` counts visible replies. Top sorts by likes, then newest creation time and ID. Clients should deduplicate IDs if rankings change while paging.

A comment contains `id`, `igdb_id`, `parent_id`, `author`, `body`, `spoiler`, `created_at`, `updated_at`, `edited`, `deleted`, `like_count`, `reply_count`, `liked`, `can_edit`, and `can_delete`. Timestamps include UTC. An author contains only `id`, `username`, and `avatar_url`. Avatar URLs use the existing authenticated `/api/users/{id}/avatar` route; clients should show their normal avatar fallback on a missing image.

Replies have one level. Replying to a reply attaches to its root. Replies cannot cross games. Deleted roots with surviving replies become placeholders with an empty body and null author. Deleted comments cannot receive new replies or likes. Existing replies remain readable. `author:null` with `deleted:false` means the account was deleted; the comment remains unattributed.

Blocks hide that author's conversations and replies from both participants, including direct reply requests and interactions. Counts respect those blocks. Removing a block restores visibility. Blocks do not affect game catalog data, downloads, or saves.

## Moderation

Administrators can delete any comment. Reports are private to administrators and include the original text as a moderation snapshot even if a comment is later edited. Each user can report a comment once. Reports do not automatically remove comments.

| Method | Route under `/api`       | Body or query                                                       | Response    |
| ------ | ------------------------ | ------------------------------------------------------------------- | ----------- |
| GET    | `/comments/reports`      | `report_status=pending\|dismissed\|removed`, `limit=20`, `offset=0` | Report page |
| PATCH  | `/comments/reports/{id}` | `{action:"dismiss"\|"remove"}`                                      | 204         |

Both moderation routes require administrator role, `roms.read`, and `roms.user.write`. Resolving a report is idempotent. Removing a comment resolves its pending reports. A report contains `id`, `comment_id`, `igdb_id`, `reporter`, `author`, `reason`, `body_snapshot`, `status`, `created_at`, and `updated_at`.

Posting is limited to 20 requests per 10 minutes; reporting to 10 per 10 minutes. Edits and block changes allow 30 requests per minute, and likes allow 120. A 429 includes `Retry-After` seconds. A 503 means temporary service unavailability; retain the user's draft. Invalid bodies return 422, unknown or blocked comments return 404, and unauthorized ownership changes return 403.

Migration `0123_game_comments` adds four tables without rewriting catalog, installed-game, or save data. Upgrades, downgrades, and endpoint tests are exercised against separate MariaDB and PostgreSQL test databases.

Moderation report items include `game_title` and the stable `igdb_id`, so the reviewer sees the game context together with the reported text. Android reaches moderation through Comments → Options → Reported comments for an admin account.
