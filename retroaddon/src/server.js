#!/usr/bin/env node
"use strict";

const { serveHTTP } = require("stremio-addon-sdk");
const config = require("./config");
const { createAddon } = require("./addon");

serveHTTP(createAddon().getInterface(), {
  port: config.port,
  cacheMaxAge: 6 * 3600,
});
