# Save and state sync on the catalog server

How the Gameio launcher and this server keep battery saves and save states in step,
across sign-outs and across devices. This replaces the RomM design the shim used to
imitate. Read this before touching `endpoints/compat_saves.py`, the `game_assets`
table, or the client's `CatalogSyncStrategy`.

## Why not RomM's protocol

RomM's sync was built for a server that owns ROM files on disk, is driven from a web
UI, and can push saves over SSH. Its negotiate protocol keys saves on `(rom, slot)`,
identifies save states by a timestamped file name, tracks per-device revisions in a
`device_save_sync` table, and falls back to comparing the client's clock with the
server's when hashes disagree. None of those foundations exist here: the server holds
metadata plus one blob per save, devices are registered without a stable fingerprint,
and every client is the launcher. Carrying the old protocol over produced two saves per
channel, states that never uploaded, and downloads that were cached but never placed.

## The model

**A sync unit** is one blob the user owns for one game:

```
(user, catalog_game, kind, emulator, channel, slot)
```

- `kind`: `save` (battery save) or `state` (emulator snapshot).
- `emulator`: the server label of what wrote the bytes. For the built-in libretro
  core and RetroArch it is the core slug (`mupen64plus_next`, `snes9x`); for a
  standalone emulator its id. Saves and states use the same label.
- `channel`: the named save channel. `autosave` is the default channel. Never null.
- `slot`: for states, the launcher's slot number (`-1` auto, `0..9` numbered,
  `100..109` the quick-save ring). For saves always `0`.

Assets are per catalog game, not per platform: a multi-platform game shares its
units across platforms, the way one cartridge would. The classic `rom_id` on the wire
still packs `catalog_game_id * 100000 + platform_id`; the server maps it to the game
and echoes the caller's rom id back.

`game_assets` stores the unit key as `unit_key = "{kind}|{emulator}|{channel}|{slot}"`
with a unique index on `(user_id, catalog_game_id, unit_key)`. Every row carries
`content_hash` (sha256 of the stored bytes), `updated_at`, and `updated_by_device_id`.
There is one row per unit and no history. The legacy `slot` column mirrors `channel`
for saves and stays null for states so the old listing shape keeps working.

## The rule

Clocks are never compared. The client keeps, per unit, the hash of the server version
it last synced (`base_hash`) and whether its local bytes changed since then
(`local_changed`). The server compares hashes only:

| server has unit | client has local | relation | action |
|---|---|---|---|
| no | yes | | upload |
| no | no | | no_op |
| yes | no | | download |
| yes | yes | `local_hash == server_hash` | no_op |
| yes | yes | `base_hash == server_hash`, `local_changed` | upload |
| yes | yes | `base_hash == server_hash`, unchanged | no_op |
| yes | yes | `base_hash != server_hash`, unchanged | download |
| yes | yes | `base_hash != server_hash`, `local_changed` | conflict |
| yes | yes | no `base_hash` (never synced) | conflict |

Units the client did not mention, for games it listed as present on the device, are
`download`. Deletion is explicit (`POST /saves/delete`, `/states/delete`); it is never
inferred from a missing item.

Conflicts are decided by the client. For saves the launcher's existing conflict UI
applies. For states, which are snapshots and cannot be merged, the newer of the two
wins: the client compares its capture time with the server's `updated_at` and either
uploads with `overwrite=true` or downloads.

## Endpoints

All under `/api`, authenticated, scope `assets.read` or `assets.write`.

### `POST /sync/reconcile`

```json
{
  "device_id": "uuid",
  "present_roms": [182300004, 184400004],
  "items": [
    {"rom_id": 182300004, "kind": "save", "emulator": "mupen64plus_next",
     "channel": "autosave", "slot": 0,
     "has_local": true, "local_hash": "sha256|null", "base_hash": "sha256|null",
     "local_changed": true}
  ]
}
```

`present_roms` lists every game on the device; server-only units for those games are
offered as downloads. Response:

```json
{"operations": [
  {"action": "upload|download|conflict|no_op", "rom_id": 182300004, "kind": "save",
   "emulator": "mupen64plus_next", "channel": "autosave", "slot": 0,
   "asset_id": 7, "file_name": "...", "server_hash": "...", "server_updated_at": "...Z",
   "server_size": 296960, "reason": "..."}
]}
```

### Uploads

- `POST /saves?rom_id&emulator&channel[&slot=<legacy alias of channel>]&base_hash&overwrite&device_id`
- `POST /states?rom_id&emulator&channel&slot&base_hash&overwrite&device_id`
- `PUT /saves/{id}` and `PUT /states/{id}` with `base_hash&overwrite&device_id`

Multipart `saveFile` / `stateFile` plus optional `screenshotFile`. An upload replaces
the unit's row. If `base_hash` is given and the row's current hash differs and
`overwrite` is false, the server answers **409** with
`{"detail": {"error": "stale_base", "asset": {...}}}` so the client can reconcile
instead of clobbering another device's work. Responses are the asset in the classic
shape plus `kind`, `game_id`, `channel`, `state_slot`, `content_hash`,
`updated_by_device_id`.

### Listings and content

`GET /saves`, `GET /states` (`rom_id` or `platform_id` filters), `GET /{kind}/{id}`,
`GET /{kind}/{id}/content`, `POST /{kind}/delete` are unchanged in shape and gain the
fields above. Timestamps are UTC with a `Z`.

## Client contract

The launcher's `CatalogSyncStrategy` builds the reconcile inventory from its own
bookkeeping (`save_sync` and `state_cache` rows plus the games on disk), sends one
request for saves and states together, and applies the operations through its
existing upload, download and conflict machinery. It reconciles on connect, after a
play session ends, when the Save Sync screen opens or scans, and on the periodic
worker. `base_hash` moves only when the client uploads or downloads; it is never
refreshed from a listing.
