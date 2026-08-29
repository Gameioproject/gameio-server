<script setup lang="ts">
// CatalogPlatforms: every system in the catalog; a tile opens Discover
// filtered to it.
import { RSkeletonBlock } from "@v2/lib";
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import PlatformTile from "@/v2/components/Platforms/PlatformTile.vue";
import EmptyState from "@/v2/components/shared/EmptyState.vue";
import IndexShell from "@/v2/components/shared/IndexShell.vue";
import PageHeader from "@/v2/components/shared/PageHeader.vue";
import { useCatalogFilters } from "@/v2/composables/useCatalogFilters";
import { usePageTitle } from "@/v2/composables/usePageTitle";
import { usePlatformPreferences } from "@/v2/composables/usePlatformPreferences";
import { useWrapGridNav } from "@/v2/composables/useWrapGridNav";

const { t } = useI18n();
const { filters, load } = useCatalogFilters();
const { visiblePlatforms } = usePlatformPreferences();

usePageTitle(() => t("common.platforms"));

const loading = ref(true);

onMounted(async () => {
  try {
    await load(true);
  } catch {
    // The empty state covers a failed load.
  } finally {
    loading.value = false;
  }
});

const platforms = computed(() =>
  visiblePlatforms(
    [...(filters.value?.platforms ?? [])].sort((a, b) =>
      a.name.localeCompare(b.name),
    ),
  ),
);

const gridRoot = ref<HTMLElement | null>(null);
useWrapGridNav(gridRoot, { cellSelector: ".plat-tile" });
</script>

<template>
  <IndexShell>
    <template #header>
      <PageHeader :title="t('common.platforms')" :count="platforms.length" />
    </template>

    <div ref="gridRoot">
      <div v-if="loading" class="r-v2-cplat__grid">
        <RSkeletonBlock
          v-for="n in 12"
          :key="`sk-${n}`"
          width="100%"
          height="140px"
          rounded="card"
        />
      </div>
      <EmptyState
        v-else-if="!platforms.length"
        icon="mdi-controller-off"
        :message="t('catalog.empty')"
      />
      <div v-else class="r-v2-cplat__grid">
        <PlatformTile
          v-for="(p, i) in platforms"
          :key="p.slug"
          class="r-v2-card-fade"
          :style="{ '--card-fade-i': i }"
          :slug="p.slug"
          :fs-slug="p.slug"
          :display-name="p.name"
          :rom-count="p.game_count"
          :to="{ name: 'catalog', query: { platform: p.slug } }"
          variant="grid"
        />
      </div>
    </div>
  </IndexShell>
</template>

<style scoped>
.r-v2-cplat__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--r-space-4);
}
</style>
