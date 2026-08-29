/* eslint-disable vue/one-component-per-file */
import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { defineComponent, ref } from "vue";
import type { CatalogGameSchema } from "@/__generated__";
import storeCollections from "@/stores/collections";
import Home from "./Home.vue";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

vi.mock("@/plugins/router", () => ({
  ROUTES: { LIBRARY: "library", DOWNLOAD_HOSTS: "download-hosts" },
}));

// Plain holder (no Vue import) because vi.hoisted runs before imports.
const { getCatalogGames, filters } = vi.hoisted(() => ({
  getCatalogGames: vi.fn(),
  filters: {
    value: null as { total_games: number; owned_games: number } | null,
  },
}));

vi.mock("@/services/api/catalog", () => ({
  default: { getCatalogGames },
}));

vi.mock("@/v2/composables/useCatalogFilters", () => ({
  useCatalogFilters: () => ({
    filters,
    platformNames: ref({}),
    load: vi.fn().mockResolvedValue(undefined),
  }),
}));

vi.mock("@/v2/composables/useCan", () => ({
  useCan: () => ref(true),
}));

vi.mock("@/v2/composables/useSnackbar", () => ({
  useSnackbar: () => ({ error: vi.fn() }),
}));

vi.mock("@/v2/composables/usePlatformPreferences", () => ({
  usePlatformPreferences: () => ({ hidden: ref(new Set<string>()) }),
}));

vi.mock("@/v2/composables/useGridNav", () => ({
  useGridNav: vi.fn(),
}));

vi.mock("@v2/lib", () => ({
  RBtn: defineComponent({ template: "<button><slot /></button>" }),
  RIcon: defineComponent({ template: "<i />" }),
  RSkeletonBlock: defineComponent({ template: "<div />" }),
}));

vi.mock("@/v2/components/Catalog/CatalogCard.vue", () => ({
  default: defineComponent({
    props: { game: { type: Object, required: true } },
    template: '<div class="card">{{ game.name }}</div>',
  }),
}));

vi.mock("@/v2/components/Catalog/CatalogGameDialog.vue", () => ({
  default: defineComponent({ template: "<div />" }),
}));

vi.mock("@/v2/components/Collections/CollectionTile.vue", () => ({
  default: defineComponent({
    props: { name: { type: String, required: true } },
    template: '<div class="collection">{{ name }}</div>',
  }),
}));

vi.mock("@/v2/components/Home/CardRow.vue", () => ({
  default: defineComponent({
    props: { title: { type: String, default: "" } },
    template:
      '<section class="row"><h2>{{ title }}</h2><slot name="title-append" /><slot /></section>',
  }),
}));

vi.mock("@/v2/components/shared/EmptyState.vue", () => ({
  default: defineComponent({
    props: { message: { type: String, default: "" } },
    template: '<div class="empty">{{ message }}<slot /></div>',
  }),
}));

function game(igdbId: number, name: string, owned = true): CatalogGameSchema {
  return {
    id: igdbId,
    igdb_id: igdbId,
    name,
    slug: null,
    summary: null,
    release_year: null,
    first_release_date: null,
    url_cover: null,
    url_cover_small: null,
    url_screenshots: [],
    genres: [],
    platform_slugs: ["n64"],
    rating: null,
    rating_count: 0,
    youtube_video_id: null,
    igdb_url: null,
    owned,
    sources: [],
    is_favorite: false,
    last_played_at: null,
    play_time_seconds: 0,
  };
}

function page(items: CatalogGameSchema[]) {
  return { data: { items, total: items.length, limit: 12, offset: 0 } };
}

describe("Home", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    getCatalogGames.mockReset();
    filters.value = { total_games: 100, owned_games: 2 };
    const store = storeCollections();
    store.fetchCollections = vi.fn().mockResolvedValue(undefined);
  });

  it("renders one row per catalog query", async () => {
    getCatalogGames.mockImplementation(
      (params: {
        favorite?: boolean;
        played?: boolean;
        ownedPlatforms?: boolean;
      }) => {
        if (params.favorite) return Promise.resolve(page([game(1, "Fav")]));
        if (params.played) return Promise.resolve(page([game(2, "Recent")]));
        if (params.ownedPlatforms)
          return Promise.resolve(page([game(3, "Top", false)]));
        return Promise.resolve(page([]));
      },
    );
    const wrapper = mount(Home);
    await flushPromises();
    const rows = wrapper.findAll(".row h2").map((h) => h.text());
    expect(rows).toEqual([
      "home.continue-playing",
      "catalog.favorites",
      "catalog.top-for-you",
    ]);
    expect(wrapper.text()).toContain("Fav");
    expect(wrapper.text()).toContain("Recent");
    expect(wrapper.text()).toContain("Top");
    expect(wrapper.find(".empty").exists()).toBe(false);
  });

  it("falls back to the whole catalog when no platform has a host", async () => {
    getCatalogGames.mockImplementation(
      (params: {
        favorite?: boolean;
        played?: boolean;
        ownedPlatforms?: boolean;
      }) =>
        Promise.resolve(
          page(
            params.favorite || params.played || params.ownedPlatforms
              ? []
              : [game(4, "Anything")],
          ),
        ),
    );
    const wrapper = mount(Home);
    await flushPromises();
    expect(wrapper.findAll(".row h2").map((h) => h.text())).toEqual([
      "catalog.top-rated",
    ]);
    expect(wrapper.text()).toContain("Anything");
  });

  it("points at the hosts page when nothing is owned", async () => {
    filters.value = { total_games: 100, owned_games: 0 };
    getCatalogGames.mockResolvedValue(page([]));
    const wrapper = mount(Home);
    await flushPromises();
    expect(wrapper.find(".empty").text()).toContain("catalog.hosts-none");
    expect(wrapper.findAll(".row")).toHaveLength(0);
  });

  it("shows the empty-catalog message instead of rows", async () => {
    filters.value = { total_games: 0, owned_games: 0 };
    getCatalogGames.mockResolvedValue(page([]));
    const wrapper = mount(Home);
    await flushPromises();
    expect(wrapper.find(".empty").text()).toContain("catalog.empty");
  });
});
