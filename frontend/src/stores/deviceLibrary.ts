// Games stored on this device (IndexedDB). The server only knows where a
// game can be fetched from; whether it is here is a per-browser fact.
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { GameSourceSchema } from "@/__generated__";
import catalogApi, { type CatalogGame } from "@/services/api/catalog";

const DB_NAME = "romm-device-library";
const DB_VERSION = 1;
const GAMES_STORE = "games";
const FILES_STORE = "files";

export interface DeviceGame {
  igdb_id: number;
  name: string;
  slug: string | null;
  platform_slug: string;
  source_id: number;
  file_name: string;
  size: number;
  url_cover: string | null;
  url_cover_small: string | null;
  added_at: string;
}

export interface DownloadProgress {
  loaded: number;
  total: number | null;
}

interface FileRow {
  igdb_id: number;
  blob: Blob;
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(GAMES_STORE)) {
        db.createObjectStore(GAMES_STORE, { keyPath: "igdb_id" });
      }
      if (!db.objectStoreNames.contains(FILES_STORE)) {
        db.createObjectStore(FILES_STORE, { keyPath: "igdb_id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function run<T>(
  db: IDBDatabase,
  store: string,
  mode: IDBTransactionMode,
  op: (s: IDBObjectStore) => IDBRequest<T>,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const request = op(db.transaction(store, mode).objectStore(store));
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export default defineStore("deviceLibrary", () => {
  const supported = typeof indexedDB !== "undefined";
  const games = ref<DeviceGame[]>([]);
  const progress = ref<Record<number, DownloadProgress>>({});
  const ready = ref(false);
  const controllers = new Map<number, AbortController>();
  let dbPromise: Promise<IDBDatabase> | null = null;

  function db(): Promise<IDBDatabase> {
    dbPromise ??= openDb();
    return dbPromise;
  }

  async function init() {
    if (ready.value || !supported) return;
    try {
      games.value = await run<DeviceGame[]>(
        await db(),
        GAMES_STORE,
        "readonly",
        (s) => s.getAll(),
      );
    } catch (err) {
      console.error("[deviceLibrary] Could not open the device library", err);
    } finally {
      ready.value = true;
    }
  }

  const byId = computed(
    () => new Map(games.value.map((g) => [g.igdb_id, g] as const)),
  );
  const totalBytes = computed(() =>
    games.value.reduce((sum, g) => sum + g.size, 0),
  );

  function has(igdbId: number): boolean {
    return byId.value.has(igdbId);
  }

  function get(igdbId: number): DeviceGame | null {
    return byId.value.get(igdbId) ?? null;
  }

  function isDownloading(igdbId: number): boolean {
    return igdbId in progress.value;
  }

  /** Fetch the file through the server relay and keep it in IndexedDB. */
  async function download(game: CatalogGame, source: GameSourceSchema) {
    const id = game.igdb_id;
    if (!supported || has(id) || isDownloading(id)) return;
    const controller = new AbortController();
    controllers.set(id, controller);
    progress.value[id] = { loaded: 0, total: source.size ?? null };
    try {
      const res = await fetch(
        catalogApi.getCatalogStreamUrl({ igdbId: id, sourceId: source.id }),
        { credentials: "same-origin", signal: controller.signal },
      );
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const headerLength = Number(res.headers.get("content-length"));
      const total = headerLength > 0 ? headerLength : (source.size ?? null);
      const reader = res.body.getReader();
      const chunks: BlobPart[] = [];
      let loaded = 0;
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        loaded += value.byteLength;
        progress.value[id] = { loaded, total };
      }
      const blob = new Blob(chunks);
      const entry: DeviceGame = {
        igdb_id: id,
        name: game.name,
        slug: game.slug,
        platform_slug: source.platform_slug,
        source_id: source.id,
        file_name: source.filename,
        size: blob.size,
        url_cover: game.url_cover,
        url_cover_small: game.url_cover_small,
        added_at: new Date().toISOString(),
      };
      const d = await db();
      await run(d, FILES_STORE, "readwrite", (s) =>
        s.put({ igdb_id: id, blob } satisfies FileRow),
      );
      await run(d, GAMES_STORE, "readwrite", (s) => s.put(entry));
      games.value = [...games.value.filter((g) => g.igdb_id !== id), entry];
    } finally {
      delete progress.value[id];
      controllers.delete(id);
    }
  }

  function cancel(igdbId: number) {
    controllers.get(igdbId)?.abort();
  }

  async function remove(igdbId: number) {
    const d = await db();
    await run(d, FILES_STORE, "readwrite", (s) => s.delete(igdbId));
    await run(d, GAMES_STORE, "readwrite", (s) => s.delete(igdbId));
    games.value = games.value.filter((g) => g.igdb_id !== igdbId);
  }

  async function getFile(igdbId: number): Promise<Blob | null> {
    const row = await run<FileRow | undefined>(
      await db(),
      FILES_STORE,
      "readonly",
      (s) => s.get(igdbId),
    );
    return row?.blob ?? null;
  }

  return {
    supported,
    games,
    progress,
    ready,
    totalBytes,
    init,
    has,
    get,
    isDownloading,
    download,
    cancel,
    remove,
    getFile,
  };
});
