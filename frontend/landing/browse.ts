/**
 * Shelves of real covers, browsed the way the launcher browses them: hover, tap, arrow keys or a
 * gamepad move the focus; the hero shows whatever is focused; A (or Enter) goes to the download.
 */
import { SHELVES, type Game, type Shelf } from "./shelves";

type Input = "up" | "down" | "left" | "right" | "confirm";

const IGDB = "https://images.igdb.com/igdb/image/upload";
const GAMEPAD_BUTTON: Record<number, Input> = {
  0: "confirm",
  9: "confirm",
  12: "up",
  13: "down",
  14: "left",
  15: "right",
};
const AXIS_DEADZONE = 0.5;

const PLATFORM: Record<string, [string, string]> = {
  atari2600: ["2600", "Atari 2600"],
  dc: ["DC", "Dreamcast"],
  gamegear: ["GG", "Game Gear"],
  gb: ["GB", "Game Boy"],
  gba: ["GBA", "Game Boy Advance"],
  gbc: ["GBC", "Game Boy Color"],
  genesis: ["MD", "Mega Drive"],
  n64: ["N64", "Nintendo 64"],
  nds: ["DS", "Nintendo DS"],
  neogeoaes: ["NEO", "Neo Geo"],
  nes: ["NES", "NES"],
  ngc: ["GC", "GameCube"],
  ps2: ["PS2", "PlayStation 2"],
  ps3: ["PS3", "PlayStation 3"],
  psp: ["PSP", "PlayStation Portable"],
  psx: ["PS1", "PlayStation"],
  saturn: ["SAT", "Saturn"],
  sega32: ["32X", "32X"],
  segacd: ["SCD", "Sega CD"],
  sms: ["SMS", "Master System"],
  snes: ["SNES", "Super NES"],
  tg16: ["TG16", "TurboGrafx-16"],
  wii: ["WII", "Wii"],
  xbox: ["XBOX", "Xbox"],
  xbox360: ["X360", "Xbox 360"],
};

function platformLabel(slug: string, long = false): string {
  const entry = PLATFORM[slug];
  return entry ? entry[long ? 1 : 0] : slug.toUpperCase();
}

interface Hero {
  backdrop: HTMLImageElement | null;
  cover: HTMLImageElement | null;
  platform: HTMLElement | null;
  year: HTMLElement | null;
  rating: HTMLElement | null;
  shelf: HTMLElement | null;
  name: HTMLElement | null;
  summary: HTMLElement | null;
}

function renderShelf(shelf: Shelf): {
  section: HTMLElement;
  cards: HTMLButtonElement[];
  now: HTMLElement;
} {
  const section = document.createElement("section");
  section.className = "shelf";
  const title = document.createElement("h2");
  title.className = "shelf-title";
  title.innerHTML = `${shelf.title} <span class="mono">${shelf.games.length}</span><span class="shelf-now mono"></span>`;
  const row = document.createElement("div");
  row.className = "row";
  const cards = shelf.games.map((game) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "card";
    card.setAttribute(
      "aria-label",
      `${game.name}, ${platformLabel(game.platforms[0], true)}, ${game.year}`,
    );
    const img = document.createElement("img");
    img.src = `${IGDB}/t_cover_big/${game.cover}.jpg`;
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    img.width = 264;
    img.height = 374;
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = platformLabel(game.platforms[0]);
    card.append(img, tag);
    row.append(card);
    return card;
  });
  section.append(title, row);
  return {
    section,
    cards,
    now: title.querySelector<HTMLElement>(".shelf-now") as HTMLElement,
  };
}

export function mountShelves(
  root: HTMLElement,
  hero: Hero,
  status: HTMLElement | null,
  onConfirm: () => void,
): void {
  const shelves = SHELVES.filter((shelf) => shelf.games.length > 0);
  const grid: HTMLButtonElement[][] = [];
  const nows: HTMLElement[] = [];
  shelves.forEach((shelf) => {
    const { section, cards, now } = renderShelf(shelf);
    root.append(section);
    grid.push(cards);
    nows.push(now);
  });

  let row = 0;
  let col = 0;
  let current: HTMLButtonElement | null = null;

  function showGame(game: Game, shelf: Shelf): void {
    if (hero.platform)
      hero.platform.textContent = platformLabel(game.platforms[0], true);
    if (hero.year) hero.year.textContent = game.year ? String(game.year) : "";
    if (hero.rating)
      hero.rating.textContent = game.rating ? `${game.rating} / 100` : "";
    if (hero.shelf) hero.shelf.textContent = shelf.title;
    if (hero.name) hero.name.textContent = game.name;
    if (hero.summary) hero.summary.textContent = game.summary;
    swap(hero.backdrop, `${IGDB}/t_cover_big/${game.cover}.jpg`);
    swap(hero.cover, `${IGDB}/t_720p/${game.cover}.jpg`);
  }

  /** Loads the next image off-screen first, so a slow cover never leaves a blank frame. */
  function swap(img: HTMLImageElement | null, next: string): void {
    if (!img || img.dataset.src === next) return;
    img.dataset.src = next;
    img.classList.remove("is-ready");
    const loader = new Image();
    loader.onload = () => {
      if (img.dataset.src !== next) return;
      img.src = next;
      img.classList.add("is-ready");
    };
    loader.src = next;
  }

  function focusCard(r: number, c: number, scroll = true): void {
    row = Math.max(0, Math.min(grid.length - 1, r));
    col = Math.max(0, Math.min(grid[row].length - 1, c));
    const card = grid[row][col];
    if (card === current) return;
    current?.classList.remove("is-focus");
    card.classList.add("is-focus");
    current = card;
    const game = shelves[row].games[col];
    // The hero is off-screen on lower shelves, so the row header names the focused game too.
    nows.forEach((now, i) => {
      now.textContent =
        i === row
          ? `${game.name} · ${platformLabel(game.platforms[0])} · ${game.year}`
          : "";
    });
    showGame(game, shelves[row]);
    if (scroll)
      card.scrollIntoView({
        block: "nearest",
        inline: "nearest",
        behavior: "smooth",
      });
  }

  function press(input: Input): void {
    switch (input) {
      case "left":
        focusCard(row, col - 1);
        break;
      case "right":
        focusCard(row, col + 1);
        break;
      case "up":
        focusCard(row - 1, col);
        break;
      case "down":
        focusCard(row + 1, col);
        break;
      case "confirm":
        onConfirm();
        break;
    }
  }

  grid.forEach((cards, r) => {
    cards.forEach((card, c) => {
      card.addEventListener("mouseenter", () => focusCard(r, c, false));
      card.addEventListener("focus", () => focusCard(r, c, false));
      card.addEventListener("click", () => {
        focusCard(r, c, false);
        press("confirm");
      });
    });
  });

  const keys: Record<string, Input> = {
    ArrowLeft: "left",
    ArrowRight: "right",
    ArrowUp: "up",
    ArrowDown: "down",
    Enter: "confirm",
    " ": "confirm",
  };
  window.addEventListener("keydown", (event) => {
    const input = keys[event.key];
    if (!input || event.metaKey || event.ctrlKey || event.altKey) return;
    const active = document.activeElement;
    if (
      active instanceof HTMLInputElement ||
      active instanceof HTMLTextAreaElement
    )
      return;
    // Enter on a link or a card is that element's own click.
    if (
      input === "confirm" &&
      (active instanceof HTMLAnchorElement ||
        active instanceof HTMLButtonElement)
    )
      return;
    event.preventDefault();
    press(input);
  });

  watchGamepads(press, (text) => {
    if (status) status.textContent = text;
  });

  // Land on a different game each visit, like the launcher's own "something you never played".
  const startRow = Math.floor(Math.random() * grid.length);
  const startCol = Math.floor(Math.random() * grid[startRow].length);
  focusCard(startRow, startCol, false);
}

/** Polls the Gamepad API and turns edges (not held buttons) into presses. */
function watchGamepads(
  press: (input: Input) => void,
  say: (text: string) => void,
): void {
  if (!("getGamepads" in navigator)) return;
  const held = new Set<string>();
  let announced = false;
  let raf = 0;

  function axisInput(x: number, y: number): Input | null {
    if (x < -AXIS_DEADZONE) return "left";
    if (x > AXIS_DEADZONE) return "right";
    if (y < -AXIS_DEADZONE) return "up";
    if (y > AXIS_DEADZONE) return "down";
    return null;
  }

  function poll(): void {
    let any = false;
    for (const pad of navigator.getGamepads()) {
      if (!pad) continue;
      any = true;
      pad.buttons.forEach((button, i) => {
        const input = GAMEPAD_BUTTON[i];
        if (!input) return;
        const key = `${pad.index}:${i}`;
        if (button.pressed && !held.has(key)) {
          held.add(key);
          press(input);
        } else if (!button.pressed) {
          held.delete(key);
        }
      });
      const dir = axisInput(pad.axes[0] ?? 0, pad.axes[1] ?? 0);
      const axisKey = `${pad.index}:axis`;
      if (dir && !held.has(axisKey)) {
        held.add(axisKey);
        press(dir);
      } else if (!dir) {
        held.delete(axisKey);
      }
    }
    if (any && !announced) {
      announced = true;
      say("Controller connected");
    }
    raf = window.requestAnimationFrame(poll);
  }

  window.addEventListener("gamepadconnected", () => {
    if (!raf) poll();
  });
  window.addEventListener("gamepaddisconnected", () => {
    if (navigator.getGamepads().every((pad) => !pad)) {
      window.cancelAnimationFrame(raf);
      raf = 0;
      announced = false;
      say("");
    }
  });
  if (navigator.getGamepads().some((pad) => pad)) poll();
}
