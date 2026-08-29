#!/usr/bin/env node
"use strict";

// Pulls every game for the platforms in src/platforms.js from IGDB into SQLite.
//
//   node --env-file=.env src/fetch-igdb.js            # incremental (only games updated since last run)
//   node --env-file=.env src/fetch-igdb.js --full     # re-fetch everything
//   node --env-file=.env src/fetch-igdb.js --platform ps1,snes
//
// Safe to re-run: rows are upserted by IGDB id.

const config = require("./config");
const db = require("./db");
const { IgdbClient } = require("./igdb");
const { PLATFORMS, bySlug } = require("./platforms");

const PAGE_SIZE = 500; // IGDB max
// game_type: 0 main game, 8 remake, 9 remaster, 11 port. (Older API versions used `category`.)
const GAME_TYPE_FILTER = "game_type = (0, 8, 9, 11)";
const FIELDS = [
  "id",
  "name",
  "slug",
  "summary",
  "first_release_date",
  "total_rating",
  "total_rating_count",
  "updated_at",
  "url",
  "platforms",
  "genres.name",
  "cover.image_id",
  "screenshots.image_id",
  "videos.name",
  "videos.video_id",
].join(",");

function parseArgs(argv) {
  const args = { full: false, platforms: PLATFORMS };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--full") args.full = true;
    else if (argv[i] === "--platform") {
      const slugs = (argv[++i] || "").split(",").filter(Boolean);
      args.platforms = slugs.map((s) => {
        const p = bySlug.get(s);
        if (!p)
          throw new Error(
            `Unknown platform slug "${s}". Known: ${PLATFORMS.map((x) => x.slug).join(", ")}`,
          );
        return p;
      });
    } else throw new Error(`Unknown argument ${argv[i]}`);
  }
  return args;
}

function pickTrailer(videos) {
  if (!videos || !videos.length) return null;
  const trailer =
    videos.find((v) => /trailer/i.test(v.name || "")) || videos[0];
  return trailer.video_id || null;
}

function normalize(g) {
  const released = g.first_release_date || null;
  return {
    id: g.id,
    name: g.name,
    slug: g.slug || null,
    year: released ? new Date(released * 1000).getUTCFullYear() : null,
    released,
    summary: g.summary || null,
    cover: g.cover?.image_id || null,
    screenshots: (g.screenshots || []).map((s) => s.image_id).filter(Boolean),
    genres: (g.genres || []).map((x) => x.name).filter(Boolean),
    rating:
      g.total_rating != null ? Math.round(g.total_rating * 10) / 10 : null,
    rating_count: g.total_rating_count || 0,
    yt_id: pickTrailer(g.videos),
    url: g.url || null,
    updated_at: g.updated_at || null,
  };
}

async function syncPlatform(client, database, upsert, platform, full) {
  const startedAt = Math.floor(Date.now() / 1000);
  const since = full ? 0 : db.getLastSync(database, platform.id);
  let lastId = 0;
  let total = 0;

  console.log(
    `[${platform.slug}] ${since ? `incremental since ${new Date(since * 1000).toISOString()}` : "full sync"}`,
  );

  // Keyset pagination on id (stable, no offset limit).
  for (;;) {
    const where = [
      `platforms = (${platform.id})`,
      GAME_TYPE_FILTER,
      `id > ${lastId}`,
    ];
    if (since) where.push(`updated_at > ${since}`);
    const query = `fields ${FIELDS}; where ${where.join(" & ")}; sort id asc; limit ${PAGE_SIZE};`;
    const page = await client.query("games", query);
    if (!page.length) break;

    const insertPage = database.transaction((rows) => {
      for (const raw of rows)
        upsert(normalize(raw), [platform.id, ...(raw.platforms || [])]);
    });
    insertPage(page);

    total += page.length;
    lastId = page[page.length - 1].id;
    process.stdout.write(`[${platform.slug}] ${total} games\r`);
    if (page.length < PAGE_SIZE) break;
  }

  db.setLastSync(database, platform.id, startedAt);
  console.log(
    `[${platform.slug}] done — ${total} games ${since ? "updated" : "fetched"}`,
  );
  return total;
}

async function main() {
  const { full, platforms } = parseArgs(process.argv.slice(2));
  const client = new IgdbClient(config.igdb);
  const database = db.open();
  const upsert = db.makeUpserter(database, new Set(PLATFORMS.map((p) => p.id)));

  let total = 0;
  for (const platform of platforms) {
    total += await syncPlatform(client, database, upsert, platform, full);
  }
  console.log(
    `\nFinished. ${total} games processed, ${db.countGames(database)} games in ${config.dbPath}`,
  );
  database.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
