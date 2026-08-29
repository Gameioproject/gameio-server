<script setup lang="ts">
// CatalogFilterDrawer — the catalog page's facet filters (platform,
// genre, rating floor, decade). Mirrors the gallery FilterDrawer so the
// toolbar stays search + sort + show, and the rest lives behind one
// badge-counted button.
import { RBtn, RDrawer, RIcon, RSelect, RTag } from "@v2/lib";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";

const RATING_STEPS = [90, 80, 70, 60] as const;
const DECADES = [1970, 1980, 1990, 2000, 2010] as const;

const props = defineProps<{
  modelValue: boolean;
  platform: string;
  genre: string;
  minRating: number;
  decade: number;
  link: "all" | "yes" | "no";
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "update:platform", value: string): void;
  (e: "update:genre", value: string): void;
  (e: "update:minRating", value: number): void;
  (e: "update:decade", value: number): void;
  (e: "update:link", value: "all" | "yes" | "no"): void;
}>();

const { t } = useI18n();
const { filters } = useCatalogFilters();
const { sortPlatforms, isHidden } = usePlatformPreferences();

const activeCount = computed(
  () =>
    [props.platform, props.genre].filter(Boolean).length +
    [props.minRating, props.decade].filter((v) => v > 0).length +
    (props.link === "all" ? 0 : 1),
);

// Hidden platforms stay listed at the end so they remain reachable on purpose.
const platformItems = computed(() =>
  sortPlatforms(filters.value?.platforms ?? [])
    .sort((a, b) => Number(isHidden(a.slug)) - Number(isHidden(b.slug)))
    .map((p) => ({
      title: `${p.name} (${p.game_count})`,
      value: p.slug,
    })),
);

const linkItems = computed(() => [
  { title: t("catalog.link-any"), value: "all" },
  { title: t("catalog.link-yes"), value: "yes" },
  { title: t("catalog.link-no"), value: "no" },
]);

function pickLink(value: unknown): "all" | "yes" | "no" {
  return value === "yes" || value === "no" ? value : "all";
}

const genreItems = computed(() =>
  (filters.value?.genres ?? []).map((g) => ({
    title: `${g.name} (${g.game_count})`,
    value: g.name,
  })),
);

const ratingItems = computed(() => [
  { title: t("catalog.any-rating"), value: 0 },
  ...RATING_STEPS.map((value) => ({
    title: t("catalog.rating-min", { value }),
    value,
  })),
]);

const decadeItems = computed(() => [
  { title: t("catalog.any-decade"), value: 0 },
  ...DECADES.map((value) => ({ title: `${value}s`, value })),
]);

function pickString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function pickNumber(value: unknown): number {
  return typeof value === "number" ? value : 0;
}

function reset() {
  emit("update:platform", "");
  emit("update:genre", "");
  emit("update:minRating", 0);
  emit("update:decade", 0);
  emit("update:link", "all");
}
</script>

<template>
  <RDrawer
    :model-value="modelValue"
    side="right"
    :width="400"
    icon="mdi-filter-variant"
    hide-close
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #header>
      <span>{{ t("gallery.filters") }}</span>
      <RTag v-if="activeCount > 0" tone="brand" size="x-small">
        {{ activeCount }}
      </RTag>
      <div style="flex: 1" />
      <RBtn
        size="small"
        variant="text"
        prepend-icon="mdi-filter-remove-outline"
        :disabled="activeCount === 0"
        @click="reset"
      >
        {{ t("platform.reset-filters") }}
      </RBtn>
    </template>

    <div class="cat-fd">
      <RSelect
        :model-value="link"
        :items="linkItems"
        hide-details
        prefix-label="stacked"
        @update:model-value="emit('update:link', pickLink($event))"
      >
        <template #prefix-label>
          <RIcon icon="mdi-link-variant" size="14" />
          {{ t("catalog.link-filter") }}
        </template>
      </RSelect>
      <RSelect
        :model-value="platform || null"
        :items="platformItems"
        searchable
        clearable
        hide-details
        prefix-label="stacked"
        @update:model-value="emit('update:platform', pickString($event))"
      >
        <template #prefix-label>
          <RIcon icon="mdi-controller" size="14" />
          {{ t("catalog.platform") }}
        </template>
      </RSelect>

      <RSelect
        :model-value="genre || null"
        :items="genreItems"
        searchable
        clearable
        hide-details
        prefix-label="stacked"
        @update:model-value="emit('update:genre', pickString($event))"
      >
        <template #prefix-label>
          <RIcon icon="mdi-shape-outline" size="14" />
          {{ t("catalog.genre") }}
        </template>
      </RSelect>

      <RSelect
        :model-value="minRating"
        :items="ratingItems"
        hide-details
        prefix-label="stacked"
        @update:model-value="emit('update:minRating', pickNumber($event))"
      >
        <template #prefix-label>
          <RIcon icon="mdi-star-outline" size="14" />
          {{ t("catalog.rating") }}
        </template>
      </RSelect>

      <RSelect
        :model-value="decade"
        :items="decadeItems"
        hide-details
        prefix-label="stacked"
        @update:model-value="emit('update:decade', pickNumber($event))"
      >
        <template #prefix-label>
          <RIcon icon="mdi-calendar-range-outline" size="14" />
          {{ t("catalog.decade") }}
        </template>
      </RSelect>
    </div>
  </RDrawer>
</template>

<style scoped>
.cat-fd {
  display: flex;
  flex-direction: column;
  gap: var(--r-space-4);
  padding: var(--r-space-4);
}
</style>
