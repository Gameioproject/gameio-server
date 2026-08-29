"use strict";

const fs = require("fs");
const path = require("path");
const Database = require("better-sqlite3");
const config = require("./config");

const SCHEMA = `
CREATE TABLE IF NOT EXISTS games (
  id            INTEGER PRIMARY KEY,           -- IGDB game id
  name          TEXT NOT NULL,
  slug          TEXT,
  year          INTEGER,
  released      INTEGER,                        -- first release date, unix seconds
  summary       TEXT,
  cover         TEXT,                           -- IGDB image_id
  screenshots   TEXT NOT NULL DEFAULT '[]',     -- JSON array of IGDB image_ids
  genres        TEXT NOT NULL DEFAULT '[]',     -- JSON array of genre names
  rating        REAL,                           -- IGDB total_rating (0-100)
  rating_count  INTEGER NOT NULL DEFAULT 0,
  yt_id         TEXT,                           -- YouTube id of the trailer
  url           TEXT,                           -- IGDB page
  updated_at    INTEGER
);
CREATE TABLE IF NOT EXISTS game_platforms (
  game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  platform_id INTEGER NOT NULL,
  PRIMARY KEY (game_id, platform_id)
);
CREATE TABLE IF NOT EXISTS game_genres (
  game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  genre   TEXT NOT NULL,
  PRIMARY KEY (game_id, genre)
);
CREATE TABLE IF NOT EXISTS sync_state (
  platform_id INTEGER PRIMARY KEY,
  last_sync   INTEGER NOT NULL                  -- unix seconds of the last completed sync
);
CREATE INDEX IF NOT EXISTS idx_game_platforms_platform ON game_platforms(platform_id);
CREATE INDEX IF NOT EXISTS idx_game_genres_genre ON game_genres(genre);
CREATE INDEX IF NOT EXISTS idx_games_popularity ON games(rating_count DESC, rating DESC);
CREATE INDEX IF NOT EXISTS idx_games_name ON games(name COLLATE NOCASE);
`;

function open() {
  fs.mkdirSync(path.dirname(config.dbPath), { recursive: true });
  const db = new Database(config.dbPath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.exec(SCHEMA);
  return db;
}

function rowToGame(row) {
  return {
    ...row,
    screenshots: JSON.parse(row.screenshots),
    genres: JSON.parse(row.genres),
  };
}

function escapeLike(s) {
  return s.replace(/[\\%_]/g, (c) => "\\" + c);
}

// Popular games first (rating_count is a good proxy), then rating, then name.
const ORDER = "g.rating_count DESC, g.rating DESC, g.name COLLATE NOCASE";

function listGames(
  db,
  { platformId, genre, search, skip = 0, limit = 100 } = {},
) {
  const where = [];
  const params = [];
  if (platformId) {
    where.push(
      "EXISTS (SELECT 1 FROM game_platforms gp WHERE gp.game_id = g.id AND gp.platform_id = ?)",
    );
    params.push(platformId);
  }
  if (genre) {
    where.push(
      "EXISTS (SELECT 1 FROM game_genres gg WHERE gg.game_id = g.id AND gg.genre = ?)",
    );
    params.push(genre);
  }
  let order = ORDER;
  if (search && search.trim()) {
    const q = escapeLike(search.trim());
    where.push("g.name LIKE ? ESCAPE '\\'");
    params.push(`%${q}%`);
    // Prefix matches rank above substring matches.
    order = `(g.name LIKE ? ESCAPE '\\') DESC, ${ORDER}`;
    params.push(`${q}%`);
  }
  const sql = `SELECT g.* FROM games g
    ${where.length ? "WHERE " + where.join(" AND ") : ""}
    ORDER BY ${order} LIMIT ? OFFSET ?`;
  return db
    .prepare(sql)
    .all(...params, limit, skip)
    .map(rowToGame);
}

function getGame(db, id) {
  const row = db.prepare("SELECT * FROM games WHERE id = ?").get(id);
  if (!row) return null;
  const platformIds = db
    .prepare(
      "SELECT platform_id FROM game_platforms WHERE game_id = ? ORDER BY platform_id",
    )
    .pluck()
    .all(id);
  return { ...rowToGame(row), platformIds };
}

// Distinct genres, most common first.
function listGenres(db) {
  return db
    .prepare(
      "SELECT genre FROM game_genres GROUP BY genre ORDER BY COUNT(*) DESC, genre",
    )
    .pluck()
    .all();
}

function countGames(db) {
  return db.prepare("SELECT COUNT(*) FROM games").pluck().get();
}

// Prepared writers used by the fetch script. Returns a function that upserts one
// IGDB game and its platform/genre links inside the caller's transaction.
function makeUpserter(db, knownPlatformIds) {
  const upsertGame = db.prepare(`
    INSERT INTO games (id, name, slug, year, released, summary, cover, screenshots, genres,
                       rating, rating_count, yt_id, url, updated_at)
    VALUES (@id, @name, @slug, @year, @released, @summary, @cover, @screenshots, @genres,
            @rating, @rating_count, @yt_id, @url, @updated_at)
    ON CONFLICT(id) DO UPDATE SET
      name = excluded.name, slug = excluded.slug, year = excluded.year,
      released = excluded.released, summary = excluded.summary, cover = excluded.cover,
      screenshots = excluded.screenshots, genres = excluded.genres, rating = excluded.rating,
      rating_count = excluded.rating_count, yt_id = excluded.yt_id, url = excluded.url,
      updated_at = excluded.updated_at
  `);
  const addPlatform = db.prepare(
    "INSERT OR IGNORE INTO game_platforms (game_id, platform_id) VALUES (?, ?)",
  );
  const clearGenres = db.prepare("DELETE FROM game_genres WHERE game_id = ?");
  const addGenre = db.prepare(
    "INSERT OR IGNORE INTO game_genres (game_id, genre) VALUES (?, ?)",
  );

  return (game, platformIds) => {
    upsertGame.run({
      ...game,
      screenshots: JSON.stringify(game.screenshots),
      genres: JSON.stringify(game.genres),
    });
    for (const pid of platformIds) {
      if (knownPlatformIds.has(pid)) addPlatform.run(game.id, pid);
    }
    clearGenres.run(game.id);
    for (const genre of game.genres) addGenre.run(game.id, genre);
  };
}

function getLastSync(db, platformId) {
  return (
    db
      .prepare("SELECT last_sync FROM sync_state WHERE platform_id = ?")
      .pluck()
      .get(platformId) || 0
  );
}

function setLastSync(db, platformId, ts) {
  db.prepare(
    "INSERT INTO sync_state (platform_id, last_sync) VALUES (?, ?) ON CONFLICT(platform_id) DO UPDATE SET last_sync = excluded.last_sync",
  ).run(platformId, ts);
}

module.exports = {
  open,
  listGames,
  getGame,
  listGenres,
  countGames,
  makeUpserter,
  getLastSync,
  setLastSync,
};
