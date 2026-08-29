import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { CollectionSchema } from "@/__generated__";
import storeCollections from "@/stores/collections";

const { getCollections, getCollection } = vi.hoisted(() => ({
  getCollections: vi.fn(),
  getCollection: vi.fn(),
}));

vi.mock("@/services/api/collection", () => ({
  default: { getCollections, getCollection },
}));

function collection(id: number, name: string): CollectionSchema {
  return {
    id,
    name,
    description: "",
    game_igdb_ids: [],
    game_count: 0,
    url_covers: [],
    url_cover: "",
    path_cover_small: null,
    path_cover_large: null,
    is_public: false,
    is_favorite: false,
    user_id: 1,
    owner_username: "admin",
    created_at: "",
    updated_at: "",
  };
}

describe("collections store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    getCollections.mockReset();
    getCollection.mockReset();
  });

  it("fetches and clears the loading flag", async () => {
    getCollections.mockResolvedValue({ data: [collection(1, "Zelda")] });
    const store = storeCollections();
    const pending = store.fetchCollections();
    expect(store.fetchingCollections).toBe(true);
    await pending;
    expect(store.fetchingCollections).toBe(false);
    expect(store.allCollections.map((c) => c.name)).toEqual(["Zelda"]);
  });

  it("refreshes one collection in place", async () => {
    const store = storeCollections();
    store.addCollection(collection(1, "Old"));
    getCollection.mockResolvedValue({ data: collection(1, "New") });
    const result = await store.refreshCollection(1);
    expect(result?.name).toBe("New");
    expect(store.allCollections).toHaveLength(1);
    expect(store.getCollection(1)?.name).toBe("New");
  });

  it("returns null when the collection is gone", async () => {
    const store = storeCollections();
    getCollection.mockRejectedValue(new Error("404"));
    expect(await store.refreshCollection(9)).toBeNull();
  });
});
