"use strict";

// Consoles exposed as catalogs, keyed by IGDB platform id.
// Edit this list to add/remove systems, then re-run the fetch script.
const PLATFORMS = [
  // Nintendo
  { id: 18, slug: "nes", name: "NES" },
  { id: 19, slug: "snes", name: "SNES" },
  { id: 4, slug: "n64", name: "Nintendo 64" },
  { id: 21, slug: "gamecube", name: "GameCube" },
  { id: 5, slug: "wii", name: "Wii" },
  { id: 33, slug: "gb", name: "Game Boy" },
  { id: 22, slug: "gbc", name: "Game Boy Color" },
  { id: 24, slug: "gba", name: "Game Boy Advance" },
  { id: 20, slug: "nds", name: "Nintendo DS" },
  // Sega
  { id: 64, slug: "sms", name: "Master System" },
  { id: 29, slug: "genesis", name: "Genesis / Mega Drive" },
  { id: 78, slug: "segacd", name: "Sega CD" },
  { id: 30, slug: "32x", name: "Sega 32X" },
  { id: 32, slug: "saturn", name: "Sega Saturn" },
  { id: 23, slug: "dreamcast", name: "Dreamcast" },
  { id: 35, slug: "gamegear", name: "Game Gear" },
  // Sony
  { id: 7, slug: "ps1", name: "PlayStation" },
  { id: 8, slug: "ps2", name: "PlayStation 2" },
  { id: 9, slug: "ps3", name: "PlayStation 3" },
  { id: 38, slug: "psp", name: "PSP" },
  // Microsoft
  { id: 11, slug: "xbox", name: "Xbox" },
  { id: 12, slug: "xbox360", name: "Xbox 360" },
  // Others
  { id: 59, slug: "atari2600", name: "Atari 2600" },
  { id: 86, slug: "tg16", name: "TurboGrafx-16" },
  { id: 80, slug: "neogeo", name: "Neo Geo" },
];

const byId = new Map(PLATFORMS.map((p) => [p.id, p]));
const bySlug = new Map(PLATFORMS.map((p) => [p.slug, p]));

module.exports = { PLATFORMS, byId, bySlug };
