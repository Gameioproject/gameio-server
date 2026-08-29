<script setup lang="ts">
// CatalogIndex: the Discover page. Search, sort and the drawer facets live
// in the URL so a filtered view is shareable.
import { RBadge, RBtn, RDivider, RSelect, RTextField } from "@v2/lib";
import { computed, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { type LocationQueryValue, useRoute, useRouter } from "vue-router";
import type { CatalogOrderBy, CatalogOrderDir } from "@/__generated__";
import type { CatalogQuery } from "@/services/api/catalog";
import CatalogFilterDrawer from "@/v2/components/Catalog/CatalogFilterDrawer.vue";
import CatalogGrid from "@/v2/components/Catalog/CatalogGrid.vue";
import IndexShell from "@/v2/components/shared/IndexShell.vue";
import PageHeader from "@/v2/components/shared/PageHeader.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { usePageTitle } from "@/v2/composables/usePageTitle";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";
import { patchQuery } from "@/v2/utils/routeQuery";

const SORT_KEYS = ["rating", "popular", "name", "newest", "oldest"] as const;
type SortKey = (typeof SORT_KEYS)[number];
const SORT_ORDER: Record<
  SortKey,
  { orderBy: CatalogOrderBy; orderDir: CatalogOrderDir }
> = {
  rating: { orderBy: "rating", orderDir: "desc" },
  popular: { orderBy: "rating_count", orderDir: "desc" },
  name: { orderBy: "name", orderDir: "asc" },
  newest: { orderBy: "release_year", orderDir: "desc" },
  oldest: { orderBy: "release_year", orderDir: "asc" },
};

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const { filters, load: loadFilters } = useCatalogFilters();
const { hidden: hiddenPlatforms } = usePlatformPreferences();

const LINK_VALUES = ["all", "yes", "no"] as const;
type LinkFilter = (typeof LINK_VALUES)[number];

usePageTitle(() => t("catalog.title"));

// --- URL-backed state ---------------------------------------------------

function queryString(value: LocationQueryValue | LocationQueryValue[]): string {
  return typeof value === "string" ? value : "";
}

function queryNumber(value: LocationQueryValue | LocationQueryValue[]): number {
  const parsed = Number(queryString(value));
  return Number.isFinite(parsed) ? parsed : 0;
}

function readSort(): SortKey {
  const value = queryString(route.query.sort);
  return (SORT_KEYS as readonly string[]).includes(value)
    ? (value as SortKey)
    : "rating";
}

function readLink(): LinkFilter {
  const value = queryString(route.query.link);
  return (LINK_VALUES as readonly string[]).includes(value)
    ? (value as LinkFilter)
    : "all";
}

const search = ref(queryString(route.query.search));
const platform = ref(queryString(route.query.platform));
const genre = ref(queryString(route.query.genre));
const minRating = ref(queryNumber(route.query.rating));
const decade = ref(queryNumber(route.query.decade));
const sort = ref<SortKey>(readSort());
const link = ref<LinkFilter>(readLink());

watch(
  () => route.query,
  () => {
    search.value = queryString(route.query.search);
    platform.value = queryString(route.query.platform);
    genre.value = queryString(route.query.genre);
    minRating.value = queryNumber(route.query.rating);
    decade.value = queryNumber(route.query.decade);
    sort.value = readSort();
    link.value = readLink();
  },
);

watch([search, platform, genre, minRating, decade, sort, link], () => {
  patchQuery(router, {
    search: search.value || undefined,
    platform: platform.value || undefined,
    genre: genre.value || undefined,
    rating: minRating.value ? String(minRating.value) : undefined,
    decade: decade.value ? String(decade.value) : undefined,
    sort: sort.value === "rating" ? undefined : sort.value,
    link: link.value === "all" ? undefined : link.value,
  });
});

const query = computed<CatalogQuery>(() => ({
  search: search.value,
  platformSlug: platform.value,
  genre: genre.value,
  minRating: minRating.value || undefined,
  yearFrom: decade.value || undefined,
  yearTo: decade.value ? decade.value + 9 : undefined,
  owned: link.value === "all" ? undefined : link.value === "yes",
  // A platform picked on purpose shows even when it is hidden elsewhere.
  excludePlatforms: platform.value ? undefined : [...hiddenPlatforms.value],
  ...SORT_ORDER[sort.value],
}));

const total = ref(0);
const drawerOpen = ref(false);

const activeFilterCount = computed(
  () =>
    [platform.value, genre.value].filter(Boolean).length +
    [minRating.value, decade.value].filter((v) => v > 0).length +
    (link.value === "all" ? 0 : 1),
);

// Totals shift as the library changes, so the page always refreshes them.
onMounted(() => {
  loadFilters(true).catch(() => {
    // The grid reports the load failure; the subtitle just stays hidden.
  });
});

// --- Toolbar ------------------------------------------------------------

const sortItems = computed(() =>
  SORT_KEYS.map((key) => ({ title: t(`catalog.sort-${key}`), value: key })),
);

function onSort(value: unknown) {
  sort.value = (SORT_KEYS as readonly unknown[]).includes(value)
    ? (value as SortKey)
    : "rating";
}
</script>

<template>
  <IndexShell>
    <template #header>
      <PageHeader :title="t('catalog.title')" :count="total" />
      <p v-if="filters" class="r-v2-cat__subtitle">
        {{
          t("catalog.subtitle", {
            total: filters.total_games,
            platforms: filters.platforms.length,
          })
        }}
      </p>
      <RDivider class="r-v2-cat__header-divider" />
    </template>

    <template #toolbar>
      <div class="r-v2-cat__toolbar">
        <RTextField
          class="r-v2-cat__search"
          :model-value="search"
          variant="outlined"
          density="compact"
          prepend-inner-icon="mdi-magnify"
          :placeholder="t('catalog.search-placeholder')"
          clearable
          hide-details
          @update:model-value="search = $event"
        />
        <RBadge
          :model-value="activeFilterCount > 0"
          :content="activeFilterCount"
          color="primary"
          floating
        >
          <RBtn
            variant="outlined"
            surface
            icon="mdi-filter-variant"
            rounded="circle"
            :aria-label="t('gallery.filters')"
            @click="drawerOpen = true"
          />
        </RBadge>
        <RSelect
          class="r-v2-cat__sort"
          :model-value="sort"
          :items="sortItems"
          density="compact"
          prepend-inner-icon="mdi-sort"
          hide-details
          @update:model-value="onSort"
        />
      </div>
    </template>

    <CatalogGrid :query="query" @update:total="total = $event" />

    <CatalogFilterDrawer
      v-model="drawerOpen"
      v-model:platform="platform"
      v-model:genre="genre"
      v-model:min-rating="minRating"
      v-model:decade="decade"
      v-model:link="link"
    />
  </IndexShell>
</template>

<style scoped>
.r-v2-cat__subtitle {
  margin: -12px 0 0;
  padding-bottom: var(--r-space-4);
  font-size: 13.5px;
  color: var(--r-color-fg-muted);
}

.r-v2-cat__header-divider {
  margin-bottom: var(--r-space-4);
}

.r-v2-cat__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--r-space-2);
}

.r-v2-cat__search {
  flex: 1 1 240px;
  min-width: 180px;
}

.r-v2-cat__sort {
  flex: 0 1 170px;
  min-width: 150px;
}
</style>
