"use strict";

const path = require("path");

// All runtime configuration comes from environment variables (see .env.example).
module.exports = {
  port: Number(process.env.PORT) || 7000,
  dbPath: process.env.DB_PATH || path.join(__dirname, "..", "data", "games.db"),
  publicUrl: (process.env.PUBLIC_URL || "").replace(/\/+$/, ""),
  launcherTemplate: process.env.LAUNCHER_URL_TEMPLATE || "",
  igdb: {
    clientId: process.env.IGDB_CLIENT_ID || "",
    clientSecret: process.env.IGDB_CLIENT_SECRET || "",
  },
};
