# Catalog source add-ons, version 1

Gameio imports a JSON manifest supplied by the user. There is no add-on store,
browser, remote installation, or executable add-on code. The metadata catalog
remains independent of add-ons. Local files remain playable with no add-on enabled.

Opening a game fetches one small mapping shard for that game's IGDB id and platform.
Import and home scrolling do not fetch or index the full source library. The client
caches results and resolves a download only when the user selects a source.

## Manifest

```json
{
  "schemaVersion": 1,
  "id": "org.example.my-sources",
  "name": "My sources",
  "version": "2026-09-14",
  "adapter": "catalog-shards-v1",
  "lookup": {
    "key": "igdbId:platformSlug",
    "partition": "sha256-prefix-2",
    "urlTemplate": "https://sources.example.org/2026-09-14/{shard}.json"
  },
  "allowedHosts": ["sources.example.org", "files.example.org"]
}
```

`id` identifies the add-on across reimports. `version` identifies an immutable
snapshot. Publish a new version directory and reimport its manifest to update a
snapshot. Never overwrite a live version's shards while clients are using them.

`allowedHosts` contains exact HTTPS hostnames for the mapping files and any `http`
source downloads. It does not grant arbitrary scripts, request headers, credentials,
or access to other hosts. Internet Archive and Real-Debrid use fixed adapters; the
manifest cannot supply alternative API hosts for them. Redirect handling remains
subject to the client's network rules.

The manifest is limited to 64 KiB and 64 allowed hosts. Names are at most 100 characters, versions at most
100, and add-on ids at most 100 lowercase letters, digits, dots, underscores or
hyphens, starting with a letter or digit. URLs must use HTTPS and must not embed
credentials, query parameters or fragments in exported snapshots.

## Looking up one game

1. Form a key from the decimal IGDB id, a colon, and the exact platform slug. For
   example, `7344:snes`. This is the existing metadata identity, not a database row
   id, game title, add-on-specific game id, or downloaded file name.
2. Hash the UTF-8 key with SHA-256. Take the first two lowercase hexadecimal
   characters and replace `{shard}` in the URL template with them.
3. Fetch that shard and select only the exact key in `entries`. Preserve the other
   games' catalog metadata independently of the returned mappings.

Each snapshot contains all 256 files, `00.json` through `ff.json`. Empty shards have
an empty `entries` object. An absent key in a valid shard is a confirmed miss. A
404, timeout, malformed response or failed download is an error, not a confirmed
missing game. A valid shard contains at most 1 MiB of uncompressed JSON, 1,000 mapped
keys and 200 sources for any one key.

```json
{
  "schemaVersion": 1,
  "entries": {
    "7344:snes": [
      {
        "id": "stable-source-id",
        "kind": "internet_archive",
        "filename": "Test Game (USA).zip",
        "size": 1234,
        "region": "USA",
        "locator": {
          "item": "example-archive-item",
          "path": "Games/Test Game (USA).zip"
        }
      }
    ]
  }
}
```

Source ids must remain stable for the same locator. The exporter computes the id as
SHA-256 of a UTF-8 JSON object containing just `kind` and `locator`, with sorted keys,
compact separators, unescaped Unicode, and a final newline. File sizes, regions,
checksums and catalog membership do not change this id. The client treats it as an
opaque value and does not need to recompute it.

`filename` is a leaf name, at most 500 characters. `size`, `md5`, `sha1` and `region`
are optional. Unknown or zero sizes are omitted. Checksums, when provided, must be
32 hexadecimal characters for MD5 and 40 for SHA-1. A platform slug has 1 to 100
lowercase letters, digits or hyphens, starting with a letter or digit. Paths must be
relative and cannot contain empty segments, `.` or `..` segments, backslashes or
control characters.

## Source locators

| `kind`             | `locator` fields                | Resolution                                                                                                                         |
| ------------------ | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `internet_archive` | `item`, `path`                  | Construct an encoded file URL on `archive.org/download`. An item id has at most 200 letters, digits, underscores, dots or hyphens. |
| `http`             | `url`                           | Download the explicit HTTPS URL. Its host must be declared in `allowedHosts`.                                                      |
| `torrent`          | `infoHash`, `fileIndex`, `path` | Resolve the selected file using the client's own Real-Debrid account.                                                              |

An HTTP locator looks like:

```json
{ "url": "https://files.example.org/Games/Test%20Game.zip" }
```

A torrent locator looks like:

```json
{
  "infoHash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "fileIndex": 0,
  "path": "Games/Test Game.zip"
}
```

The info hash is 40 hexadecimal characters and the file index is zero-based. The
path identifies the exact file when a debrid service uses its own file ids. The
exporter does not contact a debrid service, mint download URLs or include the
server's account credentials. A source requiring a client account must show that
requirement and cannot silently fall back to the server's account.

## Exporting the existing server mappings

Run from `backend/` with the normal server database configuration:

```sh
uv run python tools/export_catalog_addon.py \
  --output /private/addon-exports/2026-09-14 \
  --base-url https://sources.example.org/2026-09-14 \
  --id org.example.my-sources \
  --name 'My sources' \
  --version 2026-09-14
```

The output directory must not exist. The tool reads enabled mappings, validates the
complete snapshot and writes a new directory atomically. It leaves the catalog,
source hosts, index jobs and runtime download endpoints unchanged. It never scans
remote archives. Invalid or unsupported mappings fail the export instead of being
silently dropped.

The output contains `manifest.json` and 256 shard files. The command prints counts
and byte sizes, not source paths or credentials. It does not upload or publish the
output. Serve the chosen version directory separately when ready, then transfer
the manifest to the client and import it explicitly. Removing or disabling that
manifest must not delete local files, favorites, metadata or saves.

The controlled export of the current enabled dataset on 2026-09-14 produced:

| Measurement               |          Result |
| ------------------------- | --------------: |
| Source mappings           |          10,403 |
| Distinct catalog games    |           5,915 |
| Game and platform keys    |           6,064 |
| Platforms                 |               6 |
| Internet Archive mappings |           3,121 |
| Torrent mappings          |           7,282 |
| Manifest size             |       324 bytes |
| Total shard bytes         | 3,660,948 bytes |
| Largest shard             |    28,011 bytes |

The dataset is strongly skewed by platform: 7,560 mappings are for PS2. Hash
partitioning keeps one lookup small without downloading a whole platform's index.
The controlled artifact is private test data and is not committed to this repository
or automatically installed into client builds.
