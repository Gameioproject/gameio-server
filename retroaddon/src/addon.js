"use strict";

const { addonBuilder } = require("stremio-addon-sdk");
const pkg = require("../package.json");
const config = require("./config");
const db = require("./db");
const { PLATFORMS, byId, bySlug } = require("./platforms");

const PAGE_SIZE = 100;
const ALL_CATALOG_ID = "retro-all";
const ID_PREFIX = "igdb:";
const CACHE = {
  cacheMaxAge: 6 * 3600,
  staleRevalidate: 24 * 3600,
  staleError: 7 * 24 * 3600,
};

// Used until the database has been populated.
const FALLBACK_GENRES = [
  "Adventure",
  "Arcade",
  "Fighting",
  "Platform",
  "Puzzle",
  "Racing",
  "Role-playing (RPG)",
  "Shooter",
  "Simulator",
  "Sport",
  "Strategy",
];

const image = (id, size) =>
  `https://images.igdb.com/igdb/image/upload/t_${size}/${id}.jpg`;
const manifestUrl = () =>
  config.publicUrl ? `${config.publicUrl}/manifest.json` : null;

function discoverLink(catalogId, extra) {
  const base = manifestUrl();
  if (!base) return null;
  const qs = new URLSearchParams(extra).toString();
  return `stremio:///discover/${encodeURIComponent(base)}/game/${catalogId}${qs ? `?${qs}` : ""}`;
}

// Replace {placeholders} in a launcher template with URL-encoded values.
function fillTemplate(template, vars) {
  return template.replace(/\{(\w+)\}/g, (match, key) =>
    key in vars && vars[key] != null
      ? encodeURIComponent(String(vars[key]))
      : match,
  );
}

function toMetaPreview(game) {
  return {
    id: ID_PREFIX + game.id,
    type: "game",
    name: game.name,
    poster: game.cover ? image(game.cover, "cover_big") : undefined,
    posterShape: "poster",
    description: game.summary || undefined,
    releaseInfo: game.year ? String(game.year) : undefined,
    genres: game.genres,
    imdbRating: game.rating != null ? (game.rating / 10).toFixed(1) : undefined,
  };
}

function toMeta(game) {
  const platforms = game.platformIds.map((id) => byId.get(id)).filter(Boolean);
  const description = [
    game.summary,
    platforms.length
      ? `Platforms: ${platforms.map((p) => p.name).join(", ")}`
      : null,
  ]
    .filter(Boolean)
    .join("\n\n");

  const links = [];
  for (const g of game.genres) {
    const url = discoverLink(ALL_CATALOG_ID, { genre: g });
    if (url) links.push({ name: g, category: "Genres", url });
  }
  for (const p of platforms) {
    const url = discoverLink(`retro-${p.slug}`);
    if (url) links.push({ name: p.name, category: "Platforms", url });
  }
  if (game.url) links.push({ name: "IGDB", category: "Links", url: game.url });
  if (game.yt_id)
    links.push({
      name: "Trailer",
      category: "Links",
      url: `https://www.youtube.com/watch?v=${game.yt_id}`,
    });

  return {
    ...toMetaPreview(game),
    description: description || undefined,
    background: game.screenshots.length
      ? image(game.screenshots[0], "1080p")
      : game.cover
        ? image(game.cover, "720p")
        : undefined,
    released: game.released
      ? new Date(game.released * 1000).toISOString()
      : undefined,
    trailers: game.yt_id
      ? [{ source: game.yt_id, type: "Trailer" }]
      : undefined,
    links,
  };
}

// Stremio rejects manifests over 8 KB, so per-platform catalogs only list the most common
// genres (platformGenreCount); the "All" catalog always gets the full list.
function buildManifest(genres, platformGenreCount = genres.length) {
  const genreExtra = (options) => ({
    name: "genre",
    options,
    isRequired: false,
  });
  const skipExtra = { name: "skip" };
  return {
    id: "community.retro-games.igdb",
    version: pkg.version,
    name: "Retro Games",
    description:
      "Retro console game catalogs (NES through PS3) powered by IGDB. Shows trailers and opens games in your own launcher — no ROMs are served.",
    resources: ["catalog", "meta", "stream"],
    types: ["game"],
    idPrefixes: [ID_PREFIX],
    catalogs: [
      {
        type: "game",
        id: ALL_CATALOG_ID,
        name: "All Retro Games",
        extra: [{ name: "search" }, genreExtra(genres), skipExtra],
      },
      ...PLATFORMS.map((p) => ({
        type: "game",
        id: `retro-${p.slug}`,
        name: p.name,
        extra: [genreExtra(genres.slice(0, platformGenreCount)), skipExtra],
      })),
    ],
    config: [
      {
        key: "launcher",
        type: "text",
        title:
          "Launcher URL template ({igdb_id} {name} {slug} {platform} {platform_id} {year})",
        default: config.launcherTemplate,
      },
    ],
    behaviorHints: { configurable: true, configurationRequired: false },
  };
}

const MANIFEST_MAX_CHARS = 8000; // SDK enforces 8192

// Largest per-platform genre list that keeps the manifest under the size limit.
function fitManifest(genres) {
  for (let n = Math.min(genres.length, 12); n >= 0; n--) {
    const manifest = buildManifest(genres, n);
    if (JSON.stringify(manifest).length <= MANIFEST_MAX_CHARS) return manifest;
  }
  throw new Error(
    "Manifest exceeds 8 KB even without genre filters — remove some entries from src/platforms.js",
  );
}

function createAddon() {
  const database = db.open();
  const genres = db.listGenres(database);
  if (!genres.length) {
    console.warn(
      `Database at ${config.dbPath} is empty — run "npm run fetch" to populate it.`,
    );
  }
  const builder = new addonBuilder(
    fitManifest(genres.length ? genres : FALLBACK_GENRES),
  );

  builder.defineCatalogHandler(({ id, extra = {} }) => {
    let platformId;
    if (id !== ALL_CATALOG_ID) {
      const platform = bySlug.get(id.replace(/^retro-/, ""));
      if (!platform) return Promise.resolve({ metas: [] });
      platformId = platform.id;
    }
    const games = db.listGames(database, {
      platformId,
      genre: extra.genre,
      search: extra.search,
      skip: Number(extra.skip) || 0,
      limit: PAGE_SIZE,
    });
    return Promise.resolve({ metas: games.map(toMetaPreview), ...CACHE });
  });

  builder.defineMetaHandler(({ id }) => {
    const game = db.getGame(database, parseId(id));
    return Promise.resolve({ meta: game ? toMeta(game) : null, ...CACHE });
  });

  builder.defineStreamHandler(({ id, config: userConfig }) => {
    const game = db.getGame(database, parseId(id));
    if (!game) return Promise.resolve({ streams: [] });

    const streams = [];
    if (game.yt_id) {
      streams.push({
        ytId: game.yt_id,
        name: "Trailer",
        title: `${game.name} — Trailer`,
      });
    }
    const template =
      (userConfig && userConfig.launcher) || config.launcherTemplate;
    if (template) {
      const platforms = game.platformIds
        .map((pid) => byId.get(pid))
        .filter(Boolean);
      for (const p of platforms) {
        streams.push({
          name: "Launch",
          title: `Play on ${p.name}`,
          externalUrl: fillTemplate(template, {
            igdb_id: game.id,
            name: game.name,
            slug: game.slug,
            platform: p.slug,
            platform_id: p.id,
            year: game.year,
          }),
        });
      }
    }
    return Promise.resolve({ streams, ...CACHE });
  });

  return builder;
}

function parseId(id) {
  return Number(String(id).replace(ID_PREFIX, ""));
}

module.exports = { createAddon, buildManifest, fillTemplate };
